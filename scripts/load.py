from sqlalchemy import create_engine, URL, text
from sqlalchemy.exc import SQLAlchemyError
from logger_config import logger

import pandas as pd

import config


def save_cleaned_dataframe(converted_cols_dataframe):
    converted_cols_dataframe.to_csv(config.CLEANED_CSV_FILE_PATH, index=False)


def create_database_url():
    database_url = URL.create(
        drivername=config.DB_DRIVER_NAME,
        username=config.DB_CONFIG["user"],
        password=config.DB_CONFIG["password"],
        host=config.DB_CONFIG["host"],
        database=config.DB_CONFIG["dbname"],
        port=config.DB_CONFIG["port"]
    )
    logger.info("Database URL created")
    return database_url


def make_engine(db_url):
    engine = create_engine(db_url)
    logger.info("Engine created")
    return engine


def convert_dataframe_to_records(data):
    if isinstance(data, pd.DataFrame):
        logger.info("Dataframe converted to records")
        return data.to_dict(orient="records")

    if isinstance(data, dict):
        records_dict = {}
        for name, dataframe in data.items():
            records_dict[name] = dataframe.to_dict(orient="records")
        logger.info("Dataframes dictionary converted to records")
        return records_dict

    raise TypeError("Input must be a pandas DataFrame or a dictionary of DataFrames")


def upsert_query(engine, records):
    for key_table, cols in config.TABLES_AND_COLUMNS_MAPPING.items():
        columns = ", ".join(cols)
        values = ", ".join(f":{col}" for col in cols)
        lines = [f"{col} = EXCLUDED.{col}" for col in cols if
                 col not in config.MAIN_TABLE_UNIQUE_KEY and config.LOOKUP_TABLE_UNIQUE_KEY]
        value_set = ", ".join(lines)
        unique_key = config.MAIN_TABLE_UNIQUE_KEY if key_table == "steam_games" else config.LOOKUP_TABLE_UNIQUE_KEY

        if not records:
            return

        sql_text = (f"""
            INSERT INTO {key_table} ({columns})
            VALUES ({values})
            ON CONFLICT ({unique_key})
            DO UPDATE SET
            {value_set}
        """)

        try:
            with engine.begin() as conn:
                conn.execute(sql_text, records)
            logger.info("Rows upserted successfully")
        except SQLAlchemyError:
            logger.exception("Failed to upsert a table in PostgreSQL")
            raise


def prepare_bridge_load_dataframe(connection, bridge_df, lookup_table, output_col, fk_col):
    sql_text = text(f"""
        SELECT id AS lookup_id, {output_col}
        FROM {lookup_table}
    """)
    lookup_map = pd.read_sql_query(sql_text, connection)

    merged_df = bridge_df.merge(
        lookup_map,
        on=output_col,
        how="inner"
    )

    final_to_load_df = merged_df[[config.MAIN_TABLE_UNIQUE_KEY, "lookup_id"]].rename(
        columns={"lookup_id": fk_col}
    )

    final_to_load_df = final_to_load_df.drop_duplicates()

    return final_to_load_df


def insert_bridge_dataframe(connection, target_bridge_table, final_to_load_df, fk_col):
    if final_to_load_df.empty:
        logger.info(f"No rows to load for bridge table: {target_bridge_table}")
        return

    records = final_to_load_df.to_dict(orient="records")

    insert_sql = text(f"""
        INSERT INTO {target_bridge_table} ({config.MAIN_TABLE_UNIQUE_KEY}, {fk_col})
        VALUES (:{config.MAIN_TABLE_UNIQUE_KEY}, :{fk_col})
        ON CONFLICT ({config.MAIN_TABLE_UNIQUE_KEY}, {fk_col}) DO NOTHING
    """)

    connection.execute(insert_sql, records)
    logger.info(f"Loaded bridge table: {target_bridge_table}")


def load_bridge_tables(engine, bridge_dataframes, bridge_table_mapping):
    target_bridge_table = ""

    try:
        with engine.begin() as connection:
            for source_name, config_values in bridge_table_mapping.items():
                lookup_table = config_values["lookup_table"]
                target_bridge_table = config_values["bridge_table"]
                output_col = config_values["output_column"]
                fk_col = config_values["id_column"]

                bridge_df = bridge_dataframes[source_name].copy()

                final_to_load_df = prepare_bridge_load_dataframe(
                    connection=connection,
                    bridge_df=bridge_df,
                    lookup_table=lookup_table,
                    output_col=output_col,
                    fk_col=fk_col,
                )

                insert_bridge_dataframe(
                    connection=connection,
                    target_bridge_table=target_bridge_table,
                    final_to_load_df=final_to_load_df,
                    fk_col=fk_col,
                )

    except SQLAlchemyError:
        logger.exception(f"Failed to load bridge table: {target_bridge_table}")
        raise

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


def nan_to_none(dataframe):
    """
    Convert all missing values (np.nan, NaT, None) to None for SQL insertion.

    Purpose:
        pandas uses np.nan as its missing-value marker, but psycopg cannot
        convert float('nan') to SQL NULL — it lands in the database as a
        literal 'NaN' string in text columns. Only Python None becomes a
        proper SQL NULL. This is the single translation point at the
        DataFrame → database boundary.

    Why both steps (order matters):
        .astype(object)
            Numeric dtypes (float64) cannot hold None — pandas silently
            converts None back to NaN. Casting to object dtype first
            allows columns to hold None. Does NOT change any values.
        .where(pd.notnull(dataframe), None)
            Keeps values where not-null, substitutes None where null.
            This is the actual NaN → None swap.

    Do NOT call this earlier in the pipeline — transform functions
    depend on np.nan (dropna, isna, coerce), and object dtype is slow.
    Only use at the final hop before .to_dict(orient="records").

    Example:
        Input:   price: [1.99, NaN],  url: [NaN, "steam.com"]
        Output:  price: [1.99, None], url: [None, "steam.com"]
    """
    return dataframe.astype(object).where(pd.notnull(dataframe), None)


def convert_dataframe_to_records(data):
    if isinstance(data, pd.DataFrame):
        logger.info("Dataframe converted to records")
        return nan_to_none(data).to_dict(orient="records")

    if isinstance(data, dict):
        records_dict = {}
        for name, dataframe in data.items():
            records_dict[name] = nan_to_none(dataframe).to_dict(orient="records")
        logger.info("Dataframes dictionary converted to records")
        return records_dict

    raise TypeError("Input must be a pandas DataFrame or a dictionary of DataFrames")


def upsert_one_table(engine, table_name, columns_list, conflict_column, records):
    if not records:
        logger.info("No records to upsert for table: %s", table_name)
        return

    columns = ", ".join(columns_list)
    values = ", ".join(f":{col}" for col in columns_list)
    update_lines = [f"{col} = EXCLUDED.{col}" for col in columns_list if col != conflict_column]
    if update_lines:
        conflict_action = f"DO UPDATE SET {', '.join(update_lines)}"
    else:
        conflict_action = "DO NOTHING"

    sql_text = text(f"""
            INSERT INTO {table_name} ({columns})
            VALUES ({values})
            ON CONFLICT ({conflict_column})
            {conflict_action}
        """)

    try:
        with engine.begin() as conn:
            conn.execute(sql_text, records)
        logger.info("Rows upserted successfully to table: %s", table_name)
    except SQLAlchemyError:
        logger.exception("Failed to upsert table: %s", table_name)
        raise


def upsert_lookup_tables(engine, lookup_records):
    for table_name, records in lookup_records.items():
        columns_list = config.TABLES_AND_COLUMNS_MAPPING[table_name]
        conflict_column = config.LOOKUP_TABLE_CONFLICT_COLUMNS[table_name]

        upsert_one_table(
            engine=engine,
            table_name=table_name,
            columns_list=columns_list,
            conflict_column=conflict_column,
            records=records,
        )


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

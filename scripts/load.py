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


def convert_dataframe_to_records(converted_cols_dataframe):
    dataframe_to_dict = converted_cols_dataframe.to_dict(orient="records")
    logger.info("Dataframe converted to records")
    return dataframe_to_dict


# def upsert_query():
#     logger.info("Upsert started")
#     columns = ", ".join(config.SELECTED_COLUMNS)
#     values = ", ".join(f":{col}" for col in config.SELECTED_COLUMNS)
#     lines = [f"{col} = EXCLUDED.{col}" for col in config.SELECTED_COLUMNS if col != config.UNIQUE_KEY]
#     value_set = ", ".join(lines)
#
#     if not records:
#         return
#
#     sql_text = text(f"""
#     INSERT INTO {config.TABLE_NAME} ({columns})
#     VALUES ({values})
#     ON CONFLICT ({config.UNIQUE_KEY})
#     DO UPDATE SET
#     {value_set}
#     """)
#
#     try:
#         with engine.begin() as conn:
#             conn.execute(sql_text, records)
#         logger.info("Rows upserted successfully")
#     except SQLAlchemyError:
#         logger.exception("Failed to upsert a table in PostgreSQL")
#         raise


def load_bridge_tables(engine, bridge_dataframes, bridge_table_mapping):
    target_bridge_table = ""
    try:
        for source_name, config_values in bridge_table_mapping.items():
            lookup_table = config_values["lookup_table"]
            target_bridge_table = config_values["bridge_table"]
            output_col = config_values["output_column"]
            fk_col = config_values["id_column"]

            sql_text = text(f"""
                SELECT id AS lookup_id, {output_col}
                FROM {lookup_table}
            """)
            lookup_map = pd.read_sql_query(sql_text, engine)

            bridge_df = bridge_dataframes[source_name].copy()

            merged_df = bridge_df.merge(
                lookup_map,
                on=output_col,
                how="inner"
            )

            final_to_load_df = merged_df[[config.UNIQUE_KEY, "lookup_id"]].rename(
                columns={"lookup_id": fk_col}
            )

            final_to_load_df = final_to_load_df.drop_duplicates()

            final_to_load_df.to_sql(
                target_bridge_table,
                con=engine,
                if_exists="append",
                index=False
            )

            logger.info(f"Loaded bridge table: {target_bridge_table}")
    except SQLAlchemyError:
        logger.exception(f"Failed to load bridge table: {target_bridge_table}")
        raise

from sqlalchemy import create_engine, URL, text
from sqlalchemy.exc import SQLAlchemyError

from logger_config import logger

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


def upsert_dataframe(engine, records):
    logger.info("Upsert started")
    columns = ", ".join(config.SELECTED_COLUMNS)
    values = ", ".join(f":{col}" for col in config.SELECTED_COLUMNS)
    lines = [f"{col} = EXCLUDED.{col}" for col in config.SELECTED_COLUMNS if col != config.UNIQUE_KEY]
    value_set = ", ".join(lines)

    if not records:
        return

    sql_text = text(f"""
    INSERT INTO {config.TABLE_NAME} ({columns})
    VALUES ({values})
    ON CONFLICT ({config.UNIQUE_KEY})
    DO UPDATE SET
    {value_set}
    """)

    try:
        with engine.begin() as conn:
            conn.execute(sql_text, records)
        logger.info("Rows upserted successfully")
    except SQLAlchemyError:
        logger.exception("Failed to upsert to steam_games table in PostgreSQL")
        raise

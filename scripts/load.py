from sqlalchemy import create_engine, URL, text
from sqlalchemy.exc import SQLAlchemyError

import config


def save_cleaned_dataframe(converted_cols_dataframe):
    converted_cols_dataframe.to_csv(config.CLEANED_CSV_FILE_PATH, index=False)


def create_database_url():
    database_url = URL.create(
        drivername="postgresql+psycopg2",
        username=config.DB_CONFIG["user"],
        password=config.DB_CONFIG["password"],
        host=config.DB_CONFIG["host"],
        database=config.DB_CONFIG["dbname"],
        port=config.DB_CONFIG["port"]
    )

    return database_url


def make_engine(db_url):
    engine = create_engine(db_url)
    return engine


def clear_database_table(engine):
    try:
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE steam_games"))
    except SQLAlchemyError as exc:
        print("Failed to clear steam_games table in PostgreSQL")
        print(exc)
        raise


def load_dataframe(engine, converted_cols_dataframe):
    try:
        converted_cols_dataframe.to_sql(
            name="steam_games",
            con=engine,
            if_exists="append",
            index=False
        )
    except SQLAlchemyError as exc:
        print("Failed to load steam_games dataframe into PostgreSQL")
        print(exc)
        raise

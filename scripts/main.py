import config, extract, transform, validate, load
from logger_config import logger


def main():
    try:
        logger.info("Pipeline started")
        input_file_path = config.RAW_CSV_FILE_PATH
        logger.info(f"Input file selected: {input_file_path}")

        raw_games_dataframe, file_type = extract.read_raw_games_file(
            input_file_path,
            correct_column_names=config.CORRECT_COLUMNS_NAMES
        )
        logger.info("Extraction completed")

        renamed_columns_dataframe = transform.rename_columns(
            raw_dataframe=raw_games_dataframe,
            source_file=file_type
        )


        selected_columns_dataframe = transform.select_columns(
            raw_dataframe=renamed_columns_dataframe,
            selected_cols=config.SELECTED_COLUMNS
        )

        cleaned_columns_dataframe = transform.remove_empty_strings_and_lists(
            selected_cols_dataframe=selected_columns_dataframe
        )

        normalized_columns_dataframe = transform.normalize_list_like_columns(
            cleaned_cols_dataframe=cleaned_columns_dataframe,
            list_like_column_names=config.LIST_LIKE_COLUMN_NAMES
        )

        converted_columns_dataframe = transform.convert_column_types(
            normalized_cols_dataframe=normalized_columns_dataframe,
            numeric_columns=config.NUMERIC_COLUMN_NAMES,
            date_column=config.DATE_COLUMN_NAME
        )
        logger.info("Transform completed")

        database_url = load.create_database_url()
        engine = load.make_engine(db_url=database_url)
        records = load.convert_dataframe_to_records(
            converted_cols_dataframe=converted_columns_dataframe
        )

        load.upsert_dataframe(
            engine=engine,
            records=records
        )
        logger.info("Upsert completed")
    except Exception:
        logger.exception("Pipeline failed")
        raise


if __name__ == "__main__":
    main()




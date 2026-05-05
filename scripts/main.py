import config, extract, transform, validate, load
from logger_config import logger

from pprint import pprint


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

        language_cleaned_dataframe = transform.clean_language_columns(
            dataframe=normalized_columns_dataframe,
            language_column_names=config.LANGUAGE_LOOKUP_SOURCE_COLUMNS
        )

        converted_columns_dataframe = transform.convert_column_types(
            normalized_cols_dataframe=language_cleaned_dataframe,
            numeric_columns=config.NUMERIC_COLUMN_NAMES,
            date_column=config.DATE_COLUMN_NAME
        )

        split_column_dataframe = transform.add_estimated_owners_columns(
            converted_cols_dataframe = converted_columns_dataframe
        )

        steam_games_df, lookup_dfs, bridge_dfs = transform.build_separate_dataframes(
            split_col_dataframe=split_column_dataframe,
            lookup_mapping=config.LOOKUP_MAPPING,
            bridge_mapping=config.BRIDGE_MAPPING,
        )

        logger.info("Transform completed")

        steam_games_records = load.convert_dataframe_to_records(steam_games_df)
        lookup_records = load.convert_dataframe_to_records(lookup_dfs)

        database_url = load.create_database_url()
        engine = load.make_engine(db_url=database_url)

        load.upsert_one_table(
            engine=engine,
            table_name=config.TABLE_NAME,
            columns_list=config.TABLES_AND_COLUMNS_MAPPING["steam_games"],
            conflict_column=config.MAIN_TABLE_UNIQUE_KEY,
            records=steam_games_records,
        )

        load.upsert_lookup_tables(
            engine=engine,
            lookup_records=lookup_records,
        )

        load.load_bridge_tables(
            engine=engine,
            bridge_dataframes=bridge_dfs,
            bridge_table_mapping=config.BRIDGE_TABLES_CONFIG
        )
        logger.info("Upsert completed")
    except Exception:
        logger.exception("Pipeline failed")
        raise


if __name__ == "__main__":
    main()




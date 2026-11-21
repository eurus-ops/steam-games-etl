"""Runs the full ETL pipeline in order: extract, transform, validate, load."""

import config, validate, extract, transform, load
import sys
from logger_config import logger


def main():
    """Entry point.
    Exits with code 1 on any failure, so a scheduler or shell script can tell the run failed instead
    of seeing a normal exit.
    """
    try:
        logger.info("Pipeline started")
        input_file_path = config.RAW_CSV_FILE_PATH
        logger.info(f"Input file selected: {input_file_path}")

        raw_games_dataframe, file_type = extract.read_raw_games_file(
            input_file_path,
            last_row_count_file_path=config.LAST_ROW_COUNT_FILE_PATH,
            max_drop_percent=config.MAX_ROW_COUNT_DROP_PERCENT,
            correct_column_names=config.CORRECT_COLUMNS_NAMES,
            expected_header_count=config.RAW_CSV_EXPECTED_HEADER_COUNT,
            saved_header_file_path=config.SAVED_HEADER_FILE_PATH
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

        filled_game_names_dataframe = transform.log_and_fill_missing_game_names(
            dataframe=cleaned_columns_dataframe
        )

        normalized_columns_dataframe = transform.normalize_list_like_columns(
            cleaned_cols_dataframe=filled_game_names_dataframe,
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

        validate.validate_transformed_data(
            steam_games_dataframe=steam_games_df,
            main_table_unique_key=config.MAIN_TABLE_UNIQUE_KEY,
            min_release_date=config.MIN_RELEASE_DATE,
            max_date_years_ahead=config.MAX_RELEASE_DATE_YEARS_AHEAD,
            critical_nan_columns=config.CRITICAL_NAN_COLUMNS,
            value_range_rules=config.VALUE_RANGE_RULES,
        )

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
        sys.exit(1)


if __name__ == "__main__":
    main()




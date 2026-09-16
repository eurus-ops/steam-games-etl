import csv
import io

from logger_config import logger


def inspect_dataframe(dataframe):
    print("Shape:")
    print(dataframe.shape)

    print("\nColumns:")
    print(dataframe.columns.tolist())

    print("\nInfo:")
    dataframe.info()

    print("\nNull counts:")
    print(dataframe.isnull().sum())

    print("\nFirst 5 rows:")
    print(dataframe.head())


def check_duplicates_and_nulls(dataframe):
    game_id_duplicate_count = dataframe.duplicated(subset="game_id").sum()
    null_column_counts = dataframe.isnull().sum()

    print("\nDuplicated game_id count:")
    print(game_id_duplicate_count)

    print("\nNull columns count:")
    print(null_column_counts)

    print("\nInfo after rename:")
    dataframe.info()


def validate_csv_columns(raw_csv_file_path, expected_column_names):
    expected_column_count = len(expected_column_names)

    with open(raw_csv_file_path, "r", encoding="utf-8", newline="") as csv_file:
        csv_reader = csv.reader(csv_file)
        header_row = next(csv_reader, None)
        first_data_row = next(csv_reader, None)

    if header_row is None:
        logger.error("Raw CSV file is empty: %s", raw_csv_file_path)
        raise ValueError(f"Raw CSV file is empty: {raw_csv_file_path}")

    if first_data_row is None:
        logger.error("Raw CSV file has a header but no data rows: %s", raw_csv_file_path)
        raise ValueError(f"Raw CSV file has no data rows: {raw_csv_file_path}")

    header_column_count = len(header_row)
    data_column_count = len(first_data_row)

    if header_column_count != expected_column_count:
        logger.info(
            "Raw CSV header has %d fields, expected %d. "
            "This is the known malformed header and does not affect the data.",
            header_column_count,
            expected_column_count,
        )
    else:
        logger.info(
            "Raw CSV header now has %d fields and appears to have been fixed "
            "upstream. No action needed, but the source file has changed.",
            header_column_count,
        )

    if data_column_count != expected_column_count:
        logger.error(
            "Raw CSV column count mismatch: data rows have %d fields but %d "
            "column names are configured. Applying the configured names would "
            "misalign every column. Update CORRECT_COLUMNS_NAMES in config.py "
            "to match the current source file.",
            data_column_count,
            expected_column_count,
        )
        raise ValueError(
            f"Raw CSV column count mismatch: expected {expected_column_count} "
            f"columns, found {data_column_count}"
        )

    logger.info("CSV column count validated: %d columns", data_column_count)

    return data_column_count


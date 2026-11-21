import csv
import pandas as pd
from pathlib import Path

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


def validate_csv_columns(raw_csv_file_path, expected_column_names, raw_csv_expected_header_count):
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

    if raw_csv_expected_header_count == header_column_count:
        logger.info(
            "Raw CSV header has %d fields, expected %d. "
            "This is the known malformed header and does not affect the data.",
            header_column_count,
            raw_csv_expected_header_count,
        )
    else:
        logger.warning(
            "Raw CSV header now has %d fields instead of the expected %d. "
            "The source file's header has changed.",
            header_column_count,
            raw_csv_expected_header_count,
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


def read_current_header(raw_csv_file_path):
    with open(raw_csv_file_path, "r", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file)
        header_row = next(csv_reader, None)
    return header_row


def load_saved_header(saved_header_file_path):
    if not Path(saved_header_file_path).exists():
        return None

    return read_current_header(saved_header_file_path)


def save_header(header_row, saved_header_file_path):
    Path(saved_header_file_path).parent.mkdir(parents=True, exist_ok=True)

    with open(saved_header_file_path, "w", encoding="utf-8", newline="") as csv_file:
        csv.writer(csv_file).writerow(header_row)

    logger.info("Saved header: %s", saved_header_file_path)


def compare_header_names(current_header, saved_header, raw_csv_file_path, saved_header_file_path):
    added_names = set(current_header) - set(saved_header)
    removed_names = set(saved_header) - set(current_header)

    if not added_names and not removed_names:
        return

    logger.error(
        "Raw CSV header names changed since the last run.\n"
        "  added:   %s\n"
        "  removed: %s\n"
        "Stopped because a renamed column may also mean the data under it was "
        "replaced, and the code cannot tell the difference.\n"
        "To resolve:\n"
        "  1. Open %s and check whether the data under these columns "
        "actually changed.\n"
        "  2. If the data moved or was replaced, update CORRECT_COLUMNS_NAMES "
        "in config.py. If only the labels changed, no config change is needed.\n"
        "  3. Delete %s so the current header becomes the new baseline.\n"
        "  4. Rerun the pipeline.",
        sorted(added_names),
        sorted(removed_names),
        raw_csv_file_path,
        saved_header_file_path,
    )

    raise ValueError(
        f"Raw CSV header names changed since the last run. "
        f"Added: {sorted(added_names)}. Removed: {sorted(removed_names)}."
    )


def compare_header_order(current_header, saved_header, saved_header_file_path):
    if current_header == saved_header:
        return

    logger.error(
        "Raw CSV header columns were reordered since the last run.\n"
        "  saved order: %s\n"
        "  current order: %s\n"
        "the data moved with the header, so the positional override in "
        "read_raw_games_csv would stamp the wrong name on every column "
        "after the first moved one.\n"
        "To resolve:\n"
        "  1. Reorder CORRECT_COLUMNS_NAMES in config.py to match the "
        "current source order.\n"
        "  2. Delete %s\n"
        "  3. Rerun the pipeline.",
        saved_header,
        current_header,
        saved_header_file_path
    )

    raise ValueError(
        f"Raw CSV header columns were reordered since the last run. "
        f"See the log and {saved_header_file_path}"
    )


def validate_header_against_previous_run(raw_csv_file_path, saved_header_file_path):
    current_header = read_current_header(raw_csv_file_path)

    if current_header is None:
        logger.error("Raw CSV file is empty: %s", raw_csv_file_path)
        raise ValueError(f"Raw CSV file is empty: {raw_csv_file_path}")

    saved_header = load_saved_header(saved_header_file_path)

    if saved_header is None:
        logger.info(f"No previous header found, baseline created, nothing to compare on this run.")
        save_header(current_header, saved_header_file_path)
        return

    compare_header_names(current_header, saved_header, raw_csv_file_path, saved_header_file_path)
    compare_header_order(current_header, saved_header, saved_header_file_path)

    logger.info("Header unchanged since the last run.")
    save_header(current_header, saved_header_file_path)


def read_saved_row_count(row_count_file_path):
    if not Path(row_count_file_path).exists():
        return None

    text = Path(row_count_file_path).read_text(encoding="utf-8")

    return int(text.strip())


def save_row_count(row_count, row_count_file_path):
    Path(row_count_file_path).parent.mkdir(parents=True, exist_ok=True)

    Path(row_count_file_path).write_text(str(row_count), encoding="utf-8")
    logger.info("Saved row count to %s", row_count_file_path)


def compare_row_count(current_row_count, saved_row_count, max_drop_percent, row_count_file_path):
    if current_row_count >= saved_row_count:
        increase = current_row_count - saved_row_count
        logger.info("Row count went from %s to %s, (+%s) ",
                    saved_row_count,
                    current_row_count,
                    increase)
        return

    drop = saved_row_count - current_row_count
    drop_percent = drop / saved_row_count * 100

    if drop_percent <= max_drop_percent:
        logger.info("Row count dropped by %s rows (%.1f%%), "
                    "within the %.1f%% tolerance - normal delisting churn ",
                    drop,
                    drop_percent,
                    max_drop_percent)
        return

    logger.error(
        "Row count dropped from %s to %s (%s rows, %.1f%%), beyond the %s%% "
        "tolerance.\n"
        "The source file is probably truncated or incomplete.\n"
        "Stopped because the load uses upserts and never deletes, so a short "
        "file would silently leave the missing rows stale in the database "
        "instead of removing them.\n"
        "To resolve:\n"
        "  1. Check the size of the raw CSV and re-download it if it looks "
        "short.\n"
        "  2. If the drop is real and expected, delete %s so the current count "
        "becomes the new baseline.\n"
        "  3. Rerun the pipeline.",
        saved_row_count,
        current_row_count,
        drop,
        drop_percent,
        max_drop_percent,
        row_count_file_path,
    )

    raise ValueError(
        f"Row count dropped from {saved_row_count} to {current_row_count} "
        f"({drop_percent:.1f}%), beyond the {max_drop_percent}% tolerance"
    )


def validate_row_count_against_previous_run(dataframe, row_count_file_path, max_drop_percent):
    current_count = len(dataframe)
    saved_row_count = read_saved_row_count(row_count_file_path)

    if saved_row_count is None:
        logger.info("No previous row count found, baseline created. Nothing to compare on this run.")
        save_row_count(current_count, row_count_file_path)
        return

    compare_row_count(current_count, saved_row_count, max_drop_percent, row_count_file_path)

    save_row_count(current_count, row_count_file_path)


def check_required_fields(dataframe, required_field):
    if required_field not in dataframe.columns:
        logger.error("Required field %s not found in dataframe", required_field)
        raise ValueError(f"Required field {required_field} not found in dataframe")

    null_count = dataframe[required_field].isnull().sum()
    if null_count == 0:
        logger.info("All rows have a %s", required_field)
        return

    bad_rows = dataframe[dataframe[required_field].isnull()].index.tolist()[:20]
    logger.error(
        "%s rows have no %s (rows: %s).\n"
        "Stopped because %s is the primary key — those rows cannot be "
        "loaded, and they would lose every bridge-table link.\n"
        "Check whether the source file changed shape, or filter the rows "
        "out in transform and log what was dropped.",
        null_count,
        required_field,
        bad_rows,
        required_field,
    )

    raise ValueError(f"{null_count} rows have no {required_field}")


def check_nan_counts(dataframe, critical_nan_columns):
    total_rows = len(dataframe)
    breaches = {}

    for column in dataframe.columns:
        nan_count = dataframe[column].isnull().sum()
        nan_percent = nan_count / total_rows * 100

        logger.info("%s: %s NaN (%.1f%%)",
                    column,
                    nan_count,
                    nan_percent
        )

        if column in critical_nan_columns:
            allowed = critical_nan_columns[column]
            if nan_percent > allowed:
                breaches[column] = (nan_count, nan_percent, allowed)

    if not breaches:
        return

    for column, (count, percent, allowed) in breaches.items():
        logger.error("%s is %.1f%% NaN, above the %s%% limit (%s of %s rows)",
                     column,
                     percent,
                     allowed,
                     count,
                     total_rows
        )

    logger.error(
        "Stopped because a column that should be populated is mostly empty — "
        "usually a source format change that errors=\"coerce\" silently turned "
        "into NaN.\n"
        "Open the raw CSV and check the actual values. If the format changed, "
        "fix the conversion in transform.py. If the data is genuinely gone, "
        "raise the limit in CRITICAL_NAN_COLUMNS.",
    )

    raise ValueError(
        f"NaN rate above limit in: {', '.join(breaches)}"
    )


def check_impossible_values(dataframe, main_table_unique_key,
                            value_range_rules, min_release_date, max_date_years_ahead):
    findings = []

    for column, (minimum, maximum) in value_range_rules.items():
        if column not in dataframe.columns:
            continue

        if minimum is not None:
            mask = dataframe[column] < minimum
            count = mask.sum()
            if count > 0:
                findings.append((
                    column,
                    f"below minimum {minimum}",
                    count,
                    dataframe[mask][main_table_unique_key].tolist()[:20],
                ))

        if maximum is not None:
            mask = dataframe[column] > maximum
            count = mask.sum()
            if count > 0:
                findings.append((
                    column,
                    f"above maximum {maximum}",
                    count,
                    dataframe[mask][main_table_unique_key].tolist()[:20],
                ))

    # min / max owners the wrong way round
    mask = dataframe["estimated_owners_min"] > dataframe["estimated_owners_max"]
    count = mask.sum()
    if count > 0:
        findings.append((
            "estimated_owners",
            "min above max",
            count,
            dataframe[mask][main_table_unique_key].tolist()[:20],
        ))

    # release dates outside sane bounds
    earliest = pd.Timestamp(min_release_date)
    latest = pd.Timestamp.today() + pd.DateOffset(years=max_date_years_ahead)

    mask = dataframe["release_date"] < earliest
    count = mask.sum()
    if count > 0:
        findings.append((
            "release_date",
            f"before {earliest.date()}",
            count,
            dataframe[mask][main_table_unique_key].tolist()[:20],
        ))

    mask = dataframe["release_date"] > latest
    count = mask.sum()
    if count > 0:
        findings.append((
            "release_date",
            f"after {latest.date()}",
            count,
            dataframe[mask][main_table_unique_key].tolist()[:20],
        ))

    if not findings:
        logger.info("No impossible values found")
        return

    for column, problem, count, game_ids in findings:
        logger.warning(
            "%s %s: %s rows. game_ids: %s",
            column,
            problem,
            count,
            game_ids,
        )

    logger.warning(
        "These rows will still be loaded. Check the game_ids above on Steam, "
        "and if the values are wrong in the source, filter or correct them "
        "in transform.py."
    )


def check_duplicates(dataframe, main_table_unique_key):
    # main table
    duplicate_mask = dataframe.duplicated(subset=main_table_unique_key)
    duplicate_count = duplicate_mask.sum()

    if duplicate_count > 0:
        duplicate_ids = dataframe[duplicate_mask][main_table_unique_key].tolist()[:20]
        logger.error("%s duplicate game_id rows. game_ids: %s",
                     duplicate_count,
                     duplicate_ids
        )
        logger.error(
            "Stopped because the upsert processes both rows and the "
            "second overwrites the first, so one game's data is lost "
            "with no error.\n "
            "To resolve:\n "
            "Check the drop_duplicates step in transform.py "
            "and whether the source now ships duplicate AppIDs."
        )
        raise ValueError(f"{duplicate_count} duplicate {main_table_unique_key} rows")

    logger.info("No duplicate %s rows", main_table_unique_key)
    return


def validate_transformed_data(steam_games_dataframe, main_table_unique_key, min_release_date,
                              max_date_years_ahead, critical_nan_columns, value_range_rules):
    logger.info("Gate 2 validation started")

    check_required_fields(steam_games_dataframe, main_table_unique_key)

    check_nan_counts(steam_games_dataframe, critical_nan_columns)

    check_impossible_values(steam_games_dataframe, main_table_unique_key, value_range_rules,
                            min_release_date, max_date_years_ahead)

    check_duplicates(steam_games_dataframe, main_table_unique_key)

    logger.info("Gate 2 validation finished")

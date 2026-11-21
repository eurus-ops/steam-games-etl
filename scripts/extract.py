"""Reads the raw games file (CSV or JSON) and runs the checks that must pass before transform."""

import validate

import json
import csv
from pathlib import Path

import pandas as pd
from pandas.errors import ParserError

from logger_config import logger


def read_raw_games_file(raw_file_path, last_row_count_file_path, max_drop_percent,
                        correct_column_names=None, expected_header_count=None, saved_header_file_path=None):
    """Entry point.
    Gives main.py one entry point for either file type, and stops early on a format the rest of the
    pipeline cannot handle.
    """
    file_suffix = Path(raw_file_path).suffix.lower()

    if file_suffix == ".csv":
        logger.info("Detected CSV file")
        return read_raw_games_csv(raw_file_path, last_row_count_file_path, max_drop_percent,
                                  correct_column_names, expected_header_count, saved_header_file_path)
    elif file_suffix == ".json":
        logger.info("Detected JSON file")
        return read_raw_games_json(raw_file_path, last_row_count_file_path, max_drop_percent)
    else:
        logger.error("Unsupported file format: %s", file_suffix)
        raise ValueError(f"Unsupported file format: {file_suffix}")


def read_raw_games_csv(raw_file_path, last_row_count_file_path, max_drop_percent,
                       correct_column_names, expected_header_count, saved_header_path):
    """Helper.
    Runs the cheap checks that read only one or two lines before the expensive full read, so a bad
    file is rejected before pandas spends time loading it.
    """
    try:
        validate.validate_csv_columns(
            raw_csv_file_path=raw_file_path,
            expected_column_names=correct_column_names,
            raw_csv_expected_header_count=expected_header_count
        )

        validate.validate_header_against_previous_run(
            raw_csv_file_path=raw_file_path,
            saved_header_file_path=saved_header_path
        )

        # header=0 together with names= reads the source header row and throws it away,
        # then applies the 40 configured names by position. The source header is
        # malformed: a missing comma fuses two columns, giving 39 header fields against
        # 40 data fields. Because the header is discarded, an upstream fix to it changes
        # nothing. The real risk is a change to the DATA: a column added, removed or
        # reordered would shift the data under the fixed names with no error. The two
        # checks above exist to catch that.
        raw_games_dataframe = pd.read_csv(
            raw_file_path,
            header=0,
            names=correct_column_names,
            index_col=False
        )

        # The row count check runs after the read because it needs the full DataFrame.
        validate.validate_row_count_against_previous_run(
            dataframe=raw_games_dataframe,
            row_count_file_path=last_row_count_file_path,
            max_drop_percent=max_drop_percent
        )

        logger.info("File read success")

        return raw_games_dataframe, "csv"
    except FileNotFoundError as exc:
        logger.exception(f"Raw CSV file not found: {raw_file_path}")
        raise
    except ParserError as exc:
        logger.exception(f"Failed to parse CSV file: {raw_file_path}")
        raise
    except PermissionError as exc:
        logger.exception(f"Permission denied while reading file: {raw_file_path}")
        raise


def read_raw_games_json(raw_json_file_path, last_row_count_file_path, max_drop_percent):
    """Helper.
    The JSON file stores each game's AppID as a dictionary key rather than a field, so this moves it
    into a column to give the JSON source the same shape as the CSV.
    """
    try:
        with open(raw_json_file_path, "r", encoding="utf-8") as json_file:
            raw_json_data = json.load(json_file)

        games_list = []

        for game_key, game_data in raw_json_data.items():
            row_data = game_data.copy()
            row_data["AppID"] = game_key
            games_list.append(row_data)

        raw_games_dataframe = pd.DataFrame(games_list)

        validate.validate_row_count_against_previous_run(
            dataframe=raw_games_dataframe,
            row_count_file_path=last_row_count_file_path,
            max_drop_percent=max_drop_percent
        )
        logger.info("File read success")

        return raw_games_dataframe, "json"
    except FileNotFoundError as exc:
        logger.exception(f"Raw JSON file not found: {raw_json_file_path}")
        raise
    except json.JSONDecodeError as exc:
        logger.exception(f"Failed to parse JSON file: {raw_json_file_path}")
        raise
    except PermissionError as exc:
        logger.exception(f"Permission denied while reading file: {raw_json_file_path}")
        raise

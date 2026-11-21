import validate

import json
import csv
from pathlib import Path

import pandas as pd
from pandas.errors import ParserError

from logger_config import logger


def read_raw_games_file(raw_file_path, last_row_count_file_path, max_drop_percent,
                        correct_column_names=None, expected_header_count=None, saved_header_file_path=None):
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

        raw_games_dataframe = pd.read_csv(
            raw_file_path,
            header=0,
            names=correct_column_names,
            index_col=False
        )

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

import json
from pathlib import Path

import pandas as pd
from pandas.errors import ParserError


def read_raw_games_file(raw_file_path, correct_column_names=None):
    file_suffix = Path(raw_file_path).suffix.lower()

    if file_suffix == ".csv":
        return read_raw_games_csv(raw_file_path, correct_column_names)
    elif file_suffix == ".json":
        return read_raw_games_json(raw_file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_suffix}")


def read_raw_games_csv(raw_file_path, correct_column_names):
    try:
        raw_games_dataframe = pd.read_csv(
            raw_file_path,
            header=0,
            names=correct_column_names,
            index_col=False
        )
        return raw_games_dataframe, "csv"
    except FileNotFoundError as exc:
        print(f"Raw CSV file not found: {raw_file_path}")
        print(exc)
        raise
    except ParserError as exc:
        print(f"Failed to parse CSV file: {raw_file_path}")
        print(exc)
        raise
    except PermissionError as exc:
        print(f"Permission denied while reading file: {raw_file_path}")
        print(exc)
        raise


def read_raw_games_json(raw_file_path):
    try:
        with open(raw_file_path, "r", encoding="utf-8") as json_file:
            raw_json_data = json.load(json_file)

        games_list = []

        for game_key, game_data in raw_json_data.items():
            row_data = game_data.copy()
            row_data["AppID"] = game_key
            games_list.append(row_data)

        raw_games_dataframe = pd.DataFrame(games_list)

        return raw_games_dataframe, "json"

    except FileNotFoundError as exc:
        print(f"Raw JSON file not found: {raw_file_path}")
        print(exc)
        raise
    except json.JSONDecodeError as exc:
        print(f"Failed to decode JSON file: {raw_file_path}")
        print(exc)
        raise
    except PermissionError as exc:
        print(f"Permission denied while reading file: {raw_file_path}")
        print(exc)
        raise
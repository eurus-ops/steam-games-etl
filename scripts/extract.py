from pathlib import Path
import pandas as pd
from pandas.errors import ParserError

def read_raw_games_csv(raw_file_path, correct_column_names):
    try:
        raw_games_dataframe = pd.read_csv(
            raw_file_path,
            header=0,
            names=correct_column_names,
            index_col=False
        )
        return raw_games_dataframe
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
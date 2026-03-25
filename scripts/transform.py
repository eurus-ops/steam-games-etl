import numpy as np
import pandas as pd
import config


def rename_columns(raw_dataframe, source_file):
    if source_file == "csv":
        renamed_columns_dataframe = raw_dataframe.rename(
            columns=config.COLUMN_RENAME_MAPPING
        )
        return renamed_columns_dataframe
    elif source_file == "json":
        rename_to_csv_columns_dataframe = raw_dataframe.rename(
            columns=config.JSON_TO_CSV_RENAME
        )
        renamed_columns_dataframe = rename_to_csv_columns_dataframe.rename(
            columns=config.COLUMN_RENAME_MAPPING
        )
        return renamed_columns_dataframe
    else:
        raise ValueError(f"Unsupported file format: {source_file}")


def select_columns(raw_dataframe, selected_cols):
    selected_columns_dataframe = raw_dataframe[selected_cols]
    return selected_columns_dataframe


def remove_empty_strings_and_lists(selected_cols_dataframe):
    selected_columns_dataframe = selected_cols_dataframe.replace("", np.nan)
    selected_columns_dataframe = selected_columns_dataframe.replace([], np.nan)
    return selected_columns_dataframe


def normalize_list_like_value(value):
    if isinstance(value, list):
        if len(value) == 0:
            return np.nan
        return ", ".join(map(str, value))
    return value


def normalize_list_like_columns(cleaned_cols_dataframe, list_like_column_names):
    normalized_dataframe = cleaned_cols_dataframe.copy()

    for column in list_like_column_names:
        if column in normalized_dataframe.columns:
            normalized_dataframe[column] = normalized_dataframe[column].apply(normalize_list_like_value)

    return normalized_dataframe


def convert_column_types(normalized_cols_dataframe, numeric_columns, date_column):
    for column in numeric_columns:
        normalized_cols_dataframe[column] = pd.to_numeric(normalized_cols_dataframe[column], errors="coerce")

    normalized_cols_dataframe[date_column] = pd.to_datetime(normalized_cols_dataframe[date_column], errors="coerce")

    return normalized_cols_dataframe

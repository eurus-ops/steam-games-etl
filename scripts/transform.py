import pandas as pd
import config


def select_v1_columns(raw_dataframe, selected_cols):
    selected_columns_dataframe = raw_dataframe[selected_cols]
    return selected_columns_dataframe


def rename_v1_columns(selected_cols_dataframe):
    renamed_columns_dataframe = selected_cols_dataframe.rename(
        columns=config.COLUMN_RENAME_MAPPING
    )
    return renamed_columns_dataframe


def convert_column_types(renamed_cols_dataframe, numeric_columns, date_column):
    for column in numeric_columns:
        renamed_cols_dataframe[column] = pd.to_numeric(renamed_cols_dataframe[column], errors="coerce")

    renamed_cols_dataframe[date_column] = pd.to_datetime(renamed_cols_dataframe[date_column], errors="coerce")

    return renamed_cols_dataframe

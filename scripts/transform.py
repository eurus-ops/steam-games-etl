import numpy as np
import pandas as pd
import config
import ast
import re

from logger_config import logger


def rename_columns(raw_dataframe, source_file):
    if source_file == "csv":
        renamed_columns_dataframe = raw_dataframe.rename(
            columns=config.COLUMN_RENAME_MAPPING
        )
        logger.info("Columns renamed")
        return renamed_columns_dataframe
    elif source_file == "json":
        rename_to_csv_columns_dataframe = raw_dataframe.rename(
            columns=config.JSON_TO_CSV_RENAME
        )
        renamed_columns_dataframe = rename_to_csv_columns_dataframe.rename(
            columns=config.COLUMN_RENAME_MAPPING
        )
        logger.info("Columns renamed")
        return renamed_columns_dataframe
    else:
        logger.error("Unsupported file format: %s", source_file)
        raise ValueError(f"Unsupported file format: {source_file}")


def select_columns(raw_dataframe, selected_cols):
    selected_columns_dataframe = raw_dataframe[selected_cols]
    logger.info("Columns selected")
    return selected_columns_dataframe


def remove_empty_strings_and_lists(selected_cols_dataframe):
    selected_columns_dataframe = selected_cols_dataframe.replace("", np.nan)
    selected_columns_dataframe = selected_columns_dataframe.replace([], np.nan)
    logger.info("Empty values normalized")
    return selected_columns_dataframe


def clean_list_items(items):
    cleaned_items = [str(item).strip() for item in items if str(item).strip()]

    if len(cleaned_items) == 0:
        return np.nan

    return cleaned_items


def normalize_list_like_value(value):
    if pd.isna(value):
        return np.nan

    if isinstance(value, list):
        return clean_list_items(value)

    if isinstance(value, str):
        list_value = value.strip()
        if not list_value:
            return np.nan

        if not (list_value.startswith("[") and list_value.endswith("]")):
            string_to_list = list_value.split(",")
            return clean_list_items(string_to_list)
        try:
            parsed_value = ast.literal_eval(list_value)
            if isinstance(parsed_value, list):
                return clean_list_items(parsed_value)
            return value
        except (ValueError, SyntaxError):
            try:
                fixed_list_value = re.sub(
                    r"([\[,]\s*)([A-Za-z][A-Za-z']*)(?=\s*[,\]])",
                    r'\1"\2"',
                    list_value
                )
                parsed_fixed_value = ast.literal_eval(fixed_list_value)
                if isinstance(parsed_fixed_value, list):
                    return clean_list_items(parsed_fixed_value)
                return value
            except (ValueError, SyntaxError):
                return value if value else np.nan
    return value


def normalize_list_like_columns(cleaned_cols_dataframe, list_like_column_names):
    normalized_dataframe = cleaned_cols_dataframe.copy()

    for column in list_like_column_names:
        if column in normalized_dataframe.columns:
            normalized_dataframe[column] = normalized_dataframe[column].apply(normalize_list_like_value)
    logger.info("List-like columns normalized")
    return normalized_dataframe


def convert_column_types(normalized_cols_dataframe, numeric_columns, date_column):
    for column in numeric_columns:
        normalized_cols_dataframe[column] = pd.to_numeric(normalized_cols_dataframe[column], errors="coerce")

    normalized_cols_dataframe[date_column] = pd.to_datetime(normalized_cols_dataframe[date_column], errors="coerce")
    logger.info("Type conversion completed")
    return normalized_cols_dataframe


def split_estimated_owners(value):
    if pd.isna(value):
        return pd.Series([np.nan, np.nan])

    text = str(value).strip()

    if "-" not in text:
        return pd.Series([np.nan, np.nan])

    split_text = text.split("-")

    if len(split_text) != 2:
        return pd.Series([np.nan, np.nan])

    minimum = split_text[0].strip().replace(",", "")
    maximum = split_text[1].strip().replace(",", "")

    try:
        estimated_owners_min = int(minimum)
        estimated_owners_max = int(maximum)
        return pd.Series([estimated_owners_min, estimated_owners_max])
    except ValueError:
        logger.exception("Invalid estimated_owners value: %s", value)
        return pd.Series([np.nan, np.nan])


def add_estimated_owners_columns(converted_cols_dataframe):
    split_column_dataframe = converted_cols_dataframe.copy()

    logger.info("Started splitting estimated_owners columns")

    split_column_dataframe[["estimated_owners_min", "estimated_owners_max"]] = (
        split_column_dataframe["estimated_owners"].apply(split_estimated_owners)
    )

    logger.info("Finished splitting estimated_owners columns")

    return split_column_dataframe


def build_steam_games_dataframe(split_col_dataframe):
    copy_dataframe = split_col_dataframe.copy()
    steam_games_df = copy_dataframe[config.STEAM_GAMES_DF_COLUMNS]

    return steam_games_df


def build_lookup_dataframe(dataframe, source_column, output_column):
    copy_dataframe = dataframe[[source_column]].copy()

    explode_df = copy_dataframe.explode(source_column)
    non_null_df = explode_df.dropna(subset=[source_column])
    non_null_df[source_column] = non_null_df[source_column].astype(str).str.strip()
    no_dupes_df = non_null_df.drop_duplicates(subset=[source_column], keep="first")
    rename_col_lookup_df = no_dupes_df.rename(columns={source_column: output_column})
    final_lookup_df = rename_col_lookup_df.reset_index(drop=True)

    return final_lookup_df


def build_bridge_dataframe(dataframe, source_column, output_column):
    copy_dataframe = dataframe[[config.UNIQUE_KEY, source_column]].copy()

    explode_df = copy_dataframe.explode(source_column)
    non_null_df = explode_df.dropna(subset=[source_column])
    non_null_df[source_column] = non_null_df[source_column].astype(str).str.strip()
    no_dupes_df = non_null_df.drop_duplicates(
        subset=[config.UNIQUE_KEY, source_column],
        keep="first"
    )
    rename_col_bridge_df = no_dupes_df.rename(columns={source_column: output_column})
    final_bridge_df = rename_col_bridge_df.reset_index(drop=True)

    return final_bridge_df


def build_separate_dataframes(split_col_dataframe, lookup_mapping):
    lookup_dataframes = {}
    bridge_dataframes = {}

    for source, output in lookup_mapping.items():
        lookup_dataframes[source] = build_lookup_dataframe(
            split_col_dataframe,
            source,
            output
        )

        bridge_dataframes[source] = build_bridge_dataframe(
            split_col_dataframe,
            source,
            output
        )

    return lookup_dataframes, bridge_dataframes



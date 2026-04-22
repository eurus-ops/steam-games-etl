import numpy as np
import pandas as pd
import config
import ast
import re
import html

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
    """
    Clean the contents of an existing Python list.

    Purpose:
        Takes a list of raw items and returns a cleaned list where:
        - each item is converted to string
        - leading/trailing spaces are removed
        - empty items are removed

        If nothing usable remains, return np.nan.

    Parameters:
        items (list):
            A Python list containing raw values.

    Returns:
        list | np.nan:
            A cleaned list of strings, or np.nan if the list becomes empty.

    Example:
        Input:
            [" Action ", "", "RPG", "   "]

        Output:
            ["Action", "RPG"]

        Input:
            ["", "   "]

        Output:
            np.nan
    """
    cleaned_items = [str(item).strip() for item in items if str(item).strip()]

    if len(cleaned_items) == 0:
        return np.nan

    return cleaned_items


def normalize_list_like_value(value):
    """
    Normalize one dataframe cell into a clean Python list if it represents list-like data.

    Purpose:
        Handles one raw cell value that may be:
        - np.nan
        - an actual Python list
        - a comma-separated string
        - a string representation of a Python list
        - a malformed list string that may need repair

        The goal is to return:
        - a clean Python list of strings
        - or np.nan if the value is empty/unusable

    Parameters:
        value (Any):
            One cell value from a dataframe column.

    Returns:
        list | np.nan | original value:
            Usually a cleaned Python list or np.nan.
            In some fallback cases, returns the original value if parsing fails.

    Example:
        Input:
            [" Action ", "RPG", ""]

        Output:
            ["Action", "RPG"]

        Input:
            "Action, RPG"

        Output:
            ["Action", "RPG"]

        Input:
            "['Action', 'RPG']"

        Output:
            ["Action", "RPG"]

        Input:
            np.nan

        Output:
            np.nan
    """
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
    """
    Normalize multiple dataframe columns that contain list-like values.

    Purpose:
        Applies normalize_list_like_value() to every cell in the specified columns.

        This is the dataframe-level wrapper around the one-cell normalizer.

    Parameters:
        cleaned_cols_dataframe (pd.DataFrame):
            The dataframe containing raw/cleaned columns before full normalization.

        list_like_column_names (list[str]):
            Column names that should be treated as list-like columns.

    Returns:
        pd.DataFrame:
            A copy of the dataframe where the specified columns are normalized
            into clean Python lists or np.nan.

    Example:
        Input dataframe:
            genres
            -------------------
            "['Action', 'RPG']"
            "Adventure, Puzzle"
            np.nan

        Output dataframe:
            genres
            -------------------
            ["Action", "RPG"]
            ["Adventure", "Puzzle"]
            np.nan
    """
    normalized_dataframe = cleaned_cols_dataframe.copy()

    for column in list_like_column_names:
        if column in normalized_dataframe.columns:
            normalized_dataframe[column] = normalized_dataframe[column].apply(normalize_list_like_value)
    logger.info("List-like columns normalized")
    return normalized_dataframe


def clean_language_item(language):
    """
    Clean one raw language value.

    Purpose:
        Takes one language item and removes messy formatting/noise such as:
        - HTML entities like &amp;lt;strong&amp;gt;
        - BBCode tags like [b][/b]
        - HTML tags like <strong>, <br />
        - the text marker "(full audio)"
        - extra spaces and repeated line breaks

    Important:
        This function cleans only ONE item.
        It does not split a combined string into multiple languages.
        That job belongs to split_cleaned_language_text().

    Parameters:
        language (Any):
            One raw language value, usually a string like:
            "English[b][/b]"
            "English (full audio)"
            "English&amp;lt;strong&amp;gt;&amp;lt;/strong&amp;gt;"
            or a missing value like np.nan / None

    Returns:
        str | np.nan:
            - Cleaned language text as a string
            - np.nan if the value is empty or missing

    Example:
        Input:
            "English[b][/b]"
        Output:
            "English"

        Input:
            "English (full audio)"
        Output:
            "English"

        Input:
            "Japanese &amp;lt;br /&amp;gt;&amp;lt;br /&amp;gt;&amp;lt;strong&amp;gt;&amp;lt;/strong&amp;gt;"
        Output:
            "Japanese"

        Input:
            np.nan
        Output:
            np.nan
    """
    if isinstance(language, list):
        return np.nan

    if language is None:
        return np.nan

    if isinstance(language, float) and pd.isna(language):
        return np.nan

    text = str(language).strip()

    if not text:
        return np.nan

    # Decode HTML entities multiple times because some values are double/triple encoded
    previous_text = None
    while text != previous_text:
        previous_text = text
        text = html.unescape(text)

    # Remove BBCode and HTML tags
    text = re.sub(r"\[/?b\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</?strong>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)

    # Remove "(full audio)" marker
    text = re.sub(r"\(full audio\)", "", text, flags=re.IGNORECASE)

    # Normalize line breaks and spaces
    text = text.replace("\r", "\n")
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return np.nan

    return text


def split_cleaned_language_text(text):
    """
    Split one cleaned language string into multiple language items if needed.

    Purpose:
        Takes a cleaned string and checks if it actually contains multiple
        languages joined together by line breaks.

        Example:
            "English\\nRussian\\nSpanish - Spain"
        should become:
            ["English", "Russian", "Spanish - Spain"]

        If there are no line breaks, this function keeps the value as
        a one-item list.

    Parameters:
        text (Any):
            A cleaned language string, or a missing value.

    Returns:
        list[str] | np.nan:
            - A list of one or more cleaned language values
            - np.nan if the value is empty or missing

    Example:
        Input:
            "English\\nRussian\\nSpanish - Spain"
        Output:
            ["English", "Russian", "Spanish - Spain"]

        Input:
            "English"
        Output:
            ["English"]

        Input:
            np.nan
        Output:
            np.nan
    """
    if text is None:
        return np.nan

    if isinstance(text, float) and pd.isna(text):
        return np.nan

    text = str(text).strip()

    if not text:
        return np.nan

    # Split by line breaks if present
    if "\n" in text:
        parts = [part.strip() for part in text.split("\n") if part.strip()]
        return parts if parts else np.nan

    # Otherwise keep as one item
    return [text]


def clean_language_list(value):
    """
    Clean one language column cell and return a normalized list of languages.

    Purpose:
        This function handles one dataframe cell from a language column
        such as supported_languages or full_audio_languages.

        It:
        1. makes sure the value is handled as a list of raw items
        2. cleans each item using clean_language_item()
        3. splits combined text using split_cleaned_language_text()
        4. removes duplicates while preserving order
        5. returns a final clean list of languages

    This function is the main cell-level cleaner for language columns.

    Parameters:
        value (Any):
            One cell from a language column.
            It may already be:
            - a Python list
            - a single string
            - a missing value

    Returns:
        list[str] | np.nan:
            - A cleaned list of languages
            - np.nan if nothing usable remains

    Example:
        Input:
            ["English[b][/b]", "French", "Italian \\r\\n\\r\\n[b][/b] "]
        Output:
            ["English", "French", "Italian"]

        Input:
            ["English (full audio)", "French", "English"]
        Output:
            ["English", "French"]

        Input:
            "English\\nRussian\\nSpanish - Spain"
        Output:
            ["English", "Russian", "Spanish - Spain"]

        Input:
            np.nan
        Output:
            np.nan
    """
    if isinstance(value, list):
        raw_values = value
    elif value is None:
        return np.nan
    elif isinstance(value, float) and pd.isna(value):
        return np.nan
    else:
        raw_values = [value]

    cleaned_languages = []

    for item in raw_values:
        cleaned_item = clean_language_item(item)

        if cleaned_item is None:
            continue
        if isinstance(cleaned_item, float) and pd.isna(cleaned_item):
            continue

        split_items = split_cleaned_language_text(cleaned_item)

        if split_items is None:
            continue
        if isinstance(split_items, float) and pd.isna(split_items):
            continue

        cleaned_languages.extend(split_items)

    # Final cleanup: deduplicate while preserving order
    final_languages = []
    seen = set()

    for lang in cleaned_languages:
        lang = str(lang).strip()
        if not lang:
            continue
        if lang not in seen:
            seen.add(lang)
            final_languages.append(lang)

    if not final_languages:
        return np.nan

    return final_languages


def clean_language_columns(dataframe, language_column_names):
    """
    Apply language cleaning to selected dataframe columns.

    Purpose:
        This is the dataframe-level wrapper for clean_language_list().

        It loops through the specified language columns and cleans each cell.

        Typical target columns:
            - supported_languages
            - full_audio_languages

    Parameters:
        dataframe (pd.DataFrame):
            The dataframe containing language columns to clean.

        language_column_names (list[str]):
            Column names that should be processed by clean_language_list().

    Returns:
        pd.DataFrame:
            A copy of the dataframe where the selected language columns
            now contain:
            - cleaned Python lists of language names
            - or np.nan if empty

    Example:
        Input dataframe:
            supported_languages
            ---------------------------------------------
            ["English[b][/b]", "French", "Italian \\r\\n\\r\\n[b][/b] "]
            ["English (full audio)", "French", "English"]

        Output dataframe:
            supported_languages
            --------------------------------
            ["English", "French", "Italian"]
            ["English", "French"]

    Example call:
        clean_language_columns(
            dataframe=dataframe,
            language_column_names=["supported_languages", "full_audio_languages"]
        )
    """
    cleaned_dataframe = dataframe.copy()

    for column in language_column_names:
        if column in cleaned_dataframe.columns:
            cleaned_dataframe[column] = cleaned_dataframe[column].apply(clean_language_list)

    logger.info("Language columns cleaned")
    return cleaned_dataframe


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
    copy_dataframe = dataframe[[config.MAIN_TABLE_UNIQUE_KEY, source_column]].copy()

    explode_df = copy_dataframe.explode(source_column)
    non_null_df = explode_df.dropna(subset=[source_column])
    non_null_df[source_column] = non_null_df[source_column].astype(str).str.strip()
    no_dupes_df = non_null_df.drop_duplicates(
        subset=[config.MAIN_TABLE_UNIQUE_KEY, source_column],
        keep="first"
    )
    rename_col_bridge_df = no_dupes_df.rename(columns={source_column: output_column})
    final_bridge_df = rename_col_bridge_df.reset_index(drop=True)

    return final_bridge_df


def build_combined_lookup_dataframe(dataframe, source_columns, output_column):
    lookup_frames = []

    for source_column in source_columns:
        lookup_df = build_lookup_dataframe(dataframe, source_column, output_column)
        lookup_frames.append(lookup_df)

    combined_lookup_df = pd.concat(lookup_frames, ignore_index=True)
    combined_lookup_df = combined_lookup_df.drop_duplicates(subset=[output_column], keep="first")
    combined_lookup_df = combined_lookup_df.reset_index(drop=True)

    return combined_lookup_df


def build_separate_dataframes(split_col_dataframe, lookup_mapping, bridge_mapping):
    lookup_dataframes = {}
    bridge_dataframes = {}
    copy_dataframe = split_col_dataframe.copy()

    steam_games_dataframe = copy_dataframe[config.STEAM_GAMES_COLUMNS]

    for source_column, output_column in lookup_mapping.items():
        lookup_dataframes[source_column] = build_lookup_dataframe(
            split_col_dataframe,
            source_column,
            output_column,
        )

    lookup_dataframes["languages"] = build_combined_lookup_dataframe(
        split_col_dataframe,
        config.LANGUAGE_LOOKUP_SOURCE_COLUMNS,
        config.LANGUAGE_LOOKUP_OUTPUT_COLUMN,
    )

    for source_column, output_column in bridge_mapping.items():
        bridge_dataframes[source_column] = build_bridge_dataframe(
            split_col_dataframe,
            source_column,
            output_column,
        )

    return steam_games_dataframe, lookup_dataframes, bridge_dataframes



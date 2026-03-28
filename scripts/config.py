from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT"))
}

DB_DRIVER_NAME = "postgresql+psycopg2"

PROJECT_ROOT_PATH = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT_PATH / "data" / "raw"
CLEANED_DATA_DIR = PROJECT_ROOT_PATH / "data" / "cleaned"

RAW_CSV_FILE_PATH = RAW_DATA_DIR / "games.csv"
RAW_JSON_FILE_PATH = RAW_DATA_DIR / "games.json"
CLEANED_CSV_FILE_PATH = CLEANED_DATA_DIR / "steam_games_cleaned.csv"

LOGS_DIR = PROJECT_ROOT_PATH / "logs"
LOG_FILE_PATH = LOGS_DIR / "etl_pipeline.log"

TABLE_NAME = "steam_games"
UNIQUE_KEY = "game_id"

CORRECT_COLUMNS_NAMES = [
    "AppID", "Name", "Release date", "Estimated owners",
    "Peak CCU", "Required age", "Price", "Discount",
    "DLC count", "About the game", "Supported languages", "Full audio languages",
    "Reviews", "Header image", "Website", "Support url",
    "Support email", "Windows", "Mac", "Linux",
    "Metacritic score", "Metacritic url", "User score", "Positive",
    "Negative", "Score rank", "Achievements", "Recommendations",
    "Notes", "Average playtime forever", "Average playtime two weeks", "Median playtime forever",
    "Median playtime two weeks", "Developers", "Publishers", "Categories",
    "Genres", "Tags", "Screenshots", "Movies"
]

JSON_TO_CSV_RENAME = {
    "name": "Name",
    "release_date": "Release date",
    "estimated_owners": "Estimated owners",
    "peak_ccu": "Peak CCU",
    "required_age": "Required age",
    "price": "Price",
    "discount": "Discount",
    "dlc_count": "DLC count",
    "supported_languages": "Supported languages",
    "full_audio_languages": "Full audio languages",
    "windows": "Windows",
    "mac": "Mac",
    "linux": "Linux",
    "metacritic_score": "Metacritic score",
    "metacritic_url": "Metacritic url",
    "user_score": "User score",
    "positive": "Positive",
    "negative": "Negative",
    "achievements": "Achievements",
    "recommendations": "Recommendations",
    "average_playtime_forever": "Average playtime forever",
    "average_playtime_2weeks": "Average playtime two weeks",
    "median_playtime_forever": "Median playtime forever",
    "median_playtime_2weeks": "Median playtime two weeks",
    "developers": "Developers",
    "publishers": "Publishers",
    "categories": "Categories",
    "genres": "Genres"
}

COLUMN_RENAME_MAPPING = {
    "AppID": "game_id",
    "Name": "game_name",
    "Release date": "release_date",
    "Estimated owners": "estimated_owners",
    "Peak CCU": "peak_ccu",
    "Required age": "required_age",
    "Price": "price",
    "Discount": "discount",
    "DLC count": "dlc_count",
    "Supported languages": "supported_languages",
    "Full audio languages": "full_audio_languages",
    "Windows": "windows",
    "Mac": "mac",
    "Linux": "linux",
    "Metacritic score": "metacritic_score",
    "Metacritic url": "metacritic_url",
    "User score": "user_score",
    "Positive": "positive",
    "Negative": "negative",
    "Achievements": "achievements",
    "Recommendations": "recommendations",
    "Average playtime forever": "average_playtime_forever",
    "Average playtime two weeks": "average_playtime_2weeks",
    "Median playtime forever": "median_playtime_forever",
    "Median playtime two weeks": "median_playtime_2weeks",
    "Developers": "developers",
    "Publishers": "publishers",
    "Categories": "categories",
    "Genres": "genres"
}

SELECTED_COLUMNS = [
    "game_id", "game_name", "release_date", "estimated_owners",
    "peak_ccu", "required_age", "price", "discount",
    "dlc_count", "supported_languages", "full_audio_languages",
    "windows", "mac", "linux", "metacritic_score",
    "metacritic_url", "user_score", "positive", "negative",
    "achievements", "recommendations", "average_playtime_forever", "average_playtime_2weeks",
    "median_playtime_forever", "median_playtime_2weeks", "developers", "publishers",
    "categories", "genres"
]

LIST_LIKE_COLUMN_NAMES = [
    "supported_languages",
    "full_audio_languages",
    "developers",
    "publishers",
    "categories",
    "genres"
]

NUMERIC_COLUMN_NAMES = [
    "game_id", "required_age", "price","discount",
    "dlc_count", "metacritic_score", "user_score", "positive",
    "negative", "achievements","recommendations", "average_playtime_forever",
    "average_playtime_2weeks", "median_playtime_forever","median_playtime_2weeks", "peak_ccu"
]

DATE_COLUMN_NAME = "release_date"

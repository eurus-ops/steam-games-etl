from pathlib import Path

DB_CONFIG = {
    "host": "localhost",
    "dbname": "steam_games_etl",
    "user": "postgres",
    "password": "0321-5674",
    "port": 5432
}

PROJECT_ROOT_PATH = Path(__file__).resolve().parent.parent
RAW_CSV_FILE_PATH = PROJECT_ROOT_PATH / "data" / "raw" / "games.csv"
CLEANED_CSV_FILE_PATH = PROJECT_ROOT_PATH / "data" / "cleaned" / "steam_games_cleaned.csv"

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

SELECTED_COLUMNS = [
    "AppID", "Name", "Release date", "Estimated owners",
    "Peak CCU", "Required age", "Price", "Discount",
    "DLC count", "Supported languages", "Full audio languages",
    "Windows", "Mac", "Linux", "Metacritic score",
    "Metacritic url", "User score", "Positive", "Negative",
    "Achievements","Recommendations", "Average playtime forever", "Average playtime two weeks",
    "Median playtime forever", "Median playtime two weeks", "Developers", "Publishers",
    "Categories", "Genres"
]

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

NUMERIC_COLUMN_NAMES = [
    "game_id", "required_age", "price","discount",
    "dlc_count", "metacritic_score", "user_score", "positive",
    "negative", "achievements","recommendations", "average_playtime_forever",
    "average_playtime_2weeks", "median_playtime_forever","median_playtime_2weeks", "peak_ccu"
]

DATE_COLUMN_NAME = "release_date"

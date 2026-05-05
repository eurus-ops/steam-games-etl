# Steam Games ETL Pipeline

This project builds an ETL pipeline for a Steam games dataset from Kaggle and loads cleaned, standardized data into a PostgreSQL database.

The pipeline supports **CSV and JSON** input formats, applies data cleaning and schema standardization, and loads the data into a **normalized PostgreSQL schema** using upsert logic for the main and lookup tables plus bridge-table loading for many-to-many relationships.

Source:  
https://www.kaggle.com/datasets/fronkongames/steam-games-dataset/data

## Project Goal

The goal of this project is to practice and demonstrate core data engineering skills through a structured ETL workflow:

- extracting data from raw **CSV and JSON** sources
- cleaning messy real-world data
- transforming different source formats into a unified schema
- converting values into database-ready types
- normalizing one large flat dataset into relational tables
- loading cleaned data into PostgreSQL using **upsert** logic
- loading many-to-many bridge tables for repeated/list-like attributes
- validating the loaded data with SQL
- improving maintainability with modular pipeline components and environment-based configuration

## Tech Stack

- Python
- pandas
- NumPy
- PostgreSQL
- pgAdmin 4
- SQLAlchemy
- psycopg2
- Git / GitHub

## Current Pipeline Version

### V3 — Normalized Schema

The pipeline now loads data into a normalized relational design instead of a single flat table.

### Main table
- `steam_games`

### Lookup tables
- `languages`
- `developers`
- `publishers`
- `categories`
- `genres`

### Bridge tables
- `game_supported_languages`
- `game_full_audio_languages`
- `game_developers`
- `game_publishers`
- `game_categories`
- `game_genres`

## Key Features

- Supports **two input formats**:
  - CSV
  - JSON
- Modular ETL workflow:
  - extract
  - transform
  - load
  - validate
- JSON-to-tabular transformation aligned with the CSV pipeline structure
- Data cleaning for:
  - empty strings
  - empty lists
  - list-like text fields
  - messy language values
  - numeric/date conversion
- Splits `estimated_owners` into:
  - `estimated_owners_min`
  - `estimated_owners_max`
- Normalizes repeated text fields into lookup tables
- Builds bridge tables for many-to-many relationships
- PostgreSQL upsert logic for:
  - main table
  - lookup tables
- Bridge table loading with conflict-safe inserts
- Duplicate handling using:
  - `game_id` for the main table
  - unique text columns for lookup tables
  - composite keys for bridge tables
- Environment-based database credentials using `.env`
- Console and file logging for pipeline monitoring and debugging

## Data Modeling Improvements in V3

Compared to the earlier flat-table design, V3 improves the schema by:

- splitting one large table into multiple related tables
- reducing repeated text values
- properly modeling many-to-many relationships
- separating list-like attributes into lookup and bridge tables
- making the database easier to query and maintain

## Example Transform Flow

The transform step now includes:

1. rename source columns
2. select required columns
3. normalize empty values
4. normalize list-like fields into Python lists
5. clean language fields
6. convert numeric and date columns
7. split estimated owners into min/max columns
8. build:
   - `steam_games` dataframe
   - lookup table dataframes
   - bridge table dataframes

## Load Flow

The load step now works in three stages:

1. upsert the `steam_games` table
2. upsert lookup tables
3. load bridge tables by mapping lookup values to lookup IDs

## Project Structure

```text
steam_games_etl/
├── data/
│   ├── raw/
│   │   ├── games.csv
│   │   └── games.json
│   └── cleaned/
├── logs/
│   └── etl_pipeline.log
├── scripts/
│   ├── config.py
│   ├── extract.py
│   ├── load.py
│   ├── logger_config.py
│   ├── main.py
│   ├── test_connection.py
│   ├── transform.py
│   └── validate.py
├── sql/
│   └── create_steam_games_table.sql
├── .env
├── .gitignore
├── README.md
└── requirements.txt

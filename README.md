# Steam Games ETL Pipeline

This project builds an ETL pipeline for a Steam games dataset from Kaggle and loads cleaned, standardized data into a PostgreSQL database.

The pipeline supports **CSV and JSON** input formats, applies data cleaning and schema standardization, and uses **upsert/incremental-style loading** to handle duplicate `game_id` values more realistically.

Source:  
https://www.kaggle.com/datasets/fronkongames/steam-games-dataset/data

## Project Goal

The goal of this project is to practice and demonstrate core data engineering skills through a structured ETL workflow:

- extracting data from raw **CSV and JSON** sources
- cleaning messy real-world data
- transforming different source formats into a unified schema
- converting values into database-ready types
- loading cleaned data into PostgreSQL using **upsert** logic
- validating the loaded data with SQL
- improving maintainability with modular pipeline components and environment-based configuration

## Tech Stack

- Python
- pandas
- PostgreSQL
- pgAdmin 4
- SQLAlchemy
- psycopg2
- Git / GitHub

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
  - numeric/date conversion
- PostgreSQL **upsert/incremental-style loading**
- Duplicate handling using `game_id` conflict resolution
- Environment-based database credentials using `.env`
- Console and file logging for pipeline monitoring and debugging

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
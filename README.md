# Steam Games ETL Pipeline

This project uses a Steam games CSV dataset from Kaggle and builds an ETL pipeline that cleans, transforms, and loads the data into a PostgreSQL database.

Source:  
https://www.kaggle.com/datasets/fronkongames/steam-games-dataset/data

## Project Goal

The goal of this project is to practice and demonstrate core data engineering skills through a structured ETL workflow:

- extracting data from a raw CSV file
- cleaning messy real-world data
- transforming columns into a structured format
- loading cleaned data into PostgreSQL
- validating the loaded data with SQL

## Tech Stack

- Python
- pandas
- PostgreSQL
- pgAdmin 4
- SQLAlchemy
- psycopg2
- Git / GitHub

## Project Structure

```text
steam_games_etl/
├── data/
│   ├── raw/
│   └── cleaned/
├── scripts/
│   ├── config.py
│   ├── extract.py
│   ├── load.py
│   ├── main.py
│   ├── test_connection.py
│   ├── transform.py
│   └── validate.py
├── sql/
│   └── create_steam_games_table.sql
├── .gitignore
├── README.md
└── requirements.txt

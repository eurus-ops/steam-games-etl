import config, extract, transform, validate, load


def main():
    try:
        raw_games_dataframe = extract.read_raw_games_csv(
            raw_file_path=config.RAW_CSV_FILE_PATH,
            correct_column_names=config.CORRECT_COLUMNS_NAMES
        )

        selected_columns_dataframe = transform.select_v1_columns(
            raw_dataframe=raw_games_dataframe,
            selected_cols=config.SELECTED_COLUMNS
        )

        renamed_columns_dataframe = transform.rename_v1_columns(
            selected_cols_dataframe=selected_columns_dataframe
        )

        converted_columns_dataframe = transform.convert_column_types(
            renamed_cols_dataframe=renamed_columns_dataframe,
            numeric_columns=config.NUMERIC_COLUMN_NAMES,
            date_column=config.DATE_COLUMN_NAME
        )

        load.save_cleaned_dataframe(converted_cols_dataframe=converted_columns_dataframe)

        database_url = load.create_database_url()
        engine = load.make_engine(db_url=database_url)

        load.clear_database_table(engine=engine)
        load.load_dataframe(engine=engine, converted_cols_dataframe=converted_columns_dataframe)
    except Exception as exc:
        print("Pipeline failed.")
        print(exc)
        raise


if __name__ == "__main__":
    main()




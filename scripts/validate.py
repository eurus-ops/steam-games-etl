def inspect_dataframe(dataframe):
    print("Shape:")
    print(dataframe.shape)

    print("\nColumns:")
    print(dataframe.columns.tolist())

    print("\nInfo:")
    dataframe.info()

    print("\nNull counts:")
    print(dataframe.isnull().sum())

    print("\nFirst 5 rows:")
    print(dataframe.head())


def check_duplicates_and_nulls(dataframe):
    game_id_duplicate_count = dataframe.duplicated(subset="game_id").sum()
    null_column_counts = dataframe.isnull().sum()

    print("\nDuplicated game_id count:")
    print(game_id_duplicate_count)

    print("\nNull columns count:")
    print(null_column_counts)

    print("\nInfo after rename:")
    dataframe.info()

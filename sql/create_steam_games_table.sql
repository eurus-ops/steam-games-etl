CREATE TABLE steam_games (
    game_id BIGINT PRIMARY KEY,
    game_name TEXT NOT NULL,
    release_date DATE,
    estimated_owners_min BIGINT,
    estimated_owners_max BIGINT,
    peak_ccu INTEGER,
    required_age INTEGER,
    price NUMERIC(10,2) CHECK (price >= 0),
    discount INTEGER,
    dlc_count INTEGER,
    windows BOOLEAN,
    mac BOOLEAN,
    linux BOOLEAN,
    metacritic_score INTEGER,
    metacritic_url TEXT,
    user_score INTEGER,
    positive INTEGER,
    negative INTEGER,
    achievements INTEGER,
    recommendations INTEGER,
    average_playtime_forever INTEGER,
    average_playtime_2weeks INTEGER,
    median_playtime_forever INTEGER,
    median_playtime_2weeks INTEGER,
    CHECK (
        estimated_owners_min IS NULL
        OR estimated_owners_max IS NULL
        OR estimated_owners_min <= estimated_owners_max
    )
);

CREATE TABLE languages (
    id BIGSERIAL PRIMARY KEY,
    language_name TEXT NOT NULL UNIQUE
);

CREATE TABLE developers (
    id BIGSERIAL PRIMARY KEY,
    developer_name TEXT NOT NULL UNIQUE
);

CREATE TABLE publishers (
    id BIGSERIAL PRIMARY KEY,
    publisher_name TEXT NOT NULL UNIQUE
);

CREATE TABLE categories (
    id BIGSERIAL PRIMARY KEY,
    category_name TEXT NOT NULL UNIQUE
);

CREATE TABLE genres (
    id BIGSERIAL PRIMARY KEY,
    genre_name TEXT NOT NULL UNIQUE
);

CREATE TABLE game_supported_languages (
    game_id BIGINT NOT NULL,
    language_id BIGINT NOT NULL,
    PRIMARY KEY (game_id, language_id),
    FOREIGN KEY (game_id) REFERENCES steam_games(game_id) ON DELETE CASCADE,
    FOREIGN KEY (language_id) REFERENCES languages(id) ON DELETE CASCADE
);

CREATE TABLE game_full_audio_languages (
    game_id BIGINT NOT NULL,
    language_id BIGINT NOT NULL,
    PRIMARY KEY (game_id, language_id),
    FOREIGN KEY (game_id) REFERENCES steam_games(game_id) ON DELETE CASCADE,
    FOREIGN KEY (language_id) REFERENCES languages(id) ON DELETE CASCADE
);

CREATE TABLE game_developers (
    game_id BIGINT NOT NULL,
    developer_id BIGINT NOT NULL,
    PRIMARY KEY (game_id, developer_id),
    FOREIGN KEY (game_id) REFERENCES steam_games(game_id) ON DELETE CASCADE,
    FOREIGN KEY (developer_id) REFERENCES developers(id) ON DELETE CASCADE
);

CREATE TABLE game_publishers (
    game_id BIGINT NOT NULL,
    publisher_id BIGINT NOT NULL,
    PRIMARY KEY (game_id, publisher_id),
    FOREIGN KEY (game_id) REFERENCES steam_games(game_id) ON DELETE CASCADE,
    FOREIGN KEY (publisher_id) REFERENCES publishers(id) ON DELETE CASCADE
);

CREATE TABLE game_categories (
    game_id BIGINT NOT NULL,
    category_id BIGINT NOT NULL,
    PRIMARY KEY (game_id, category_id),
    FOREIGN KEY (game_id) REFERENCES steam_games(game_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

CREATE TABLE game_genres (
    game_id BIGINT NOT NULL,
    genre_id BIGINT NOT NULL,
    PRIMARY KEY (game_id, genre_id),
    FOREIGN KEY (game_id) REFERENCES steam_games(game_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
);
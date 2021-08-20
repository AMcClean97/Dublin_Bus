import os


class APIKeys:
    WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
    MAP_API_KEY = os.environ.get("MAP_API_KEY")
    GTFS_API_KEY = os.environ.get("GFTS_API_KEY")


class MySQL:
    host = os.getenv("DB_URI")
    port = os.getenv("DB_PORT")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    database = os.getenv("DB_NAME")
    URI = f'mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}'

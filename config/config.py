import os


class APIKeys:
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    MAP_API_KEY = os.getenv("MAP_API_KEY")
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
    GTFS_API_KEY = os.getenv("GFTS_API_KEY")

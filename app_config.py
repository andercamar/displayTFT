import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

class Config:
    # OpenWeather
    WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    LAT = os.getenv("LAT", "-23.5505")
    LONG = os.getenv("LONG", "-46.6333")

    # Spotify
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")
    SPOTIFY_TOKEN = os.getenv("SPOTIFY_TOKEN") # Fallback/Initial

    # Printer Settings (OctoPrint / Moonraker)
    PRINTER_API_KEY = os.getenv("PRINTER_API_KEY")
    PRINTER_URL = os.getenv("PRINTER_URL", "http://octopi.local") # Ou IP da impressora
    PRINTER_TYPE = os.getenv("PRINTER_TYPE", "octoprint") # octoprint ou moonraker

    
    # Hardware settings
    DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"
    
    # TFT Pins (Padrão Raspberry Pi)
    TFT_DC = 24
    TFT_RST = 25
    TFT_SPI_PORT = 0
    TFT_SPI_DEVICE = 0
    TFT_SPEED_HZ = 4000000

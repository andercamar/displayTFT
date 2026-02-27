import requests
from app_config import Config

class WeatherService:
    def __init__(self):
        self.api_key = Config.WEATHER_API_KEY
        self.lat = Config.LAT
        self.long = Config.LONG

    def get_weather(self):
        if not self.api_key:
            return {"temp": "N/A", "feels": "N/A", "weather": "API Key Faltando"}
        
        try:
            link = f'https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.long}&appid={self.api_key}&lang=pt_br&units=metric'
            response = requests.get(link, timeout=10)
            response.raise_for_status()
            json_resp = response.json()
            
            temp = json_resp['main']['temp']
            feels = json_resp['main']['feels_like']
            weather = json_resp['weather'][0]['description']
            
            return {
                "temp": temp,
                "feels": feels,
                "weather": weather
            }
        except Exception as e:
            print(f"Erro ao buscar clima: {e}")
            return {"temp": "Erro", "feels": "Erro", "weather": "Erro de Conexão"}

class SpotifyService:
    def __init__(self):
        self.token = Config.SPOTIFY_TOKEN

    def get_playing(self):
        if not self.token:
            return None
        
        link = "https://api.spotify.com/v1/me/player/currently-playing"
        try:
            response = requests.get(
                link,
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=5
            )
            
            if response.status_code == 200:
                json_resp = response.json()
                if not json_resp.get('item'):
                    return None
                    
                artists = [artist['name'] for artist in json_resp['item']['artists']]
                artists_names = ', '.join(artists)
                music = json_resp['item']['name']
                playing = json_resp['is_playing']
                
                return {
                    "artists": artists_names,
                    "music": music,
                    "playing": playing
                }
class PrinterService:
    def __init__(self):
        self.api_key = Config.PRINTER_API_KEY # Opcional no Moonraker
        self.url = Config.PRINTER_URL
        self.type = Config.PRINTER_TYPE

    def get_status(self):
        if not self.url:
            return None
            
        try:
            # Endpoint do Moonraker para K1 Max / Klipper
            link = f"{self.url}/printer/objects/query?print_stats&display_status"
            response = requests.get(link, timeout=3)
            
            if response.status_code == 200:
                data = response.json()['result']['status']
                print_stats = data.get('print_stats', {})
                display_status = data.get('display_status', {})
                
                state = print_stats.get('state') # "printing", "paused", "standby", "complete"
                
                if state in ["printing", "paused"]:
                    progress = display_status.get('progress', 0)
                    duration = print_stats.get('print_duration', 0)
                    
                    # Calcular tempo restante estimado
                    if progress > 0:
                        total_est_time = duration / progress
                        remaining = total_est_time - duration
                        time_left_str = f"{int(remaining // 60)}m"
                    else:
                        time_left_str = "Calc..."

                    return {
                        "state": state.capitalize(),
                        "progress": progress,
                        "time_left": time_left_str
                    }
            return None
        except Exception:
            return None

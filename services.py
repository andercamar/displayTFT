import requests
import os
import psutil
import time
import base64
from app_config import Config

class SystemService:
    def __init__(self):
        self.last_update = 0
        self.cache = None

    def get_stats(self):
        # Throttle: Atualiza a cada 2 segundos
        if self.cache and time.time() - self.last_update < 2:
            return self.cache

        try:
            temp = 0
            if os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
                with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                    temp = int(f.read()) / 1000
            
            cpu_usage = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory()
            
            self.cache = {
                "temp": temp,
                "cpu": cpu_usage,
                "ram_usage": ram.percent,
                "ram_free_gb": ram.available / (1024 * 1024 * 1024),
                "ip": self.get_ip()
            }
            self.last_update = time.time()
            return self.cache
        except Exception as e:
            print(f"Erro SystemService: {e}")
            return self.cache

    def get_ip(self):
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

class WeatherService:
    def __init__(self):
        self.api_key = Config.WEATHER_API_KEY
        self.lat = Config.LAT
        self.long = Config.LONG
        self.last_update = 0
        self.cache = None

    def get_weather(self):
        # Throttle: Atualiza a cada 10 minutos (OpenWeather free limit)
        if self.cache and time.time() - self.last_update < 600:
            return self.cache

        if not self.api_key:
            return {"temp": "N/A", "feels": "N/A", "weather": "API Key Faltando"}
        
        try:
            link = f'https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.long}&appid={self.api_key}&lang=pt_br&units=metric'
            response = requests.get(link, timeout=10)
            response.raise_for_status()
            self.cache = response.json()
            
            # Formata o retorno
            temp = self.cache['main']['temp']
            res = {
                "temp": temp,
                "feels": self.cache['main']['feels_like'],
                "humidity": self.cache['main'].get('humidity', 0),
                "weather": self.cache['weather'][0]['description'],
                "icon_id": self.cache['weather'][0]['icon']
            }
            self.cache = res
            self.last_update = time.time()
            return res
        except Exception as e:
            print(f"Erro ao buscar clima: {e}")
            return self.cache

class SpotifyService:
    def __init__(self):
        self.token = Config.SPOTIFY_TOKEN
        self.client_id = Config.SPOTIFY_CLIENT_ID
        self.client_secret = Config.SPOTIFY_CLIENT_SECRET
        self.refresh_token = Config.SPOTIFY_REFRESH_TOKEN
        self.last_update = 0
        self.cache = None

    def refresh_access_token(self):
        if not self.refresh_token or not self.client_id or not self.client_secret:
            return False
        url = "https://accounts.spotify.com/api/token"
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        payload = {"grant_type": "refresh_token", "refresh_token": self.refresh_token}
        headers = {"Authorization": f"Basic {auth_header}", "Content-Type": "application/x-www-form-urlencoded"}
        try:
            response = requests.post(url, data=payload, headers=headers)
            if response.status_code == 200:
                self.token = response.json().get('access_token')
                return True
            return False
        except: return False

    def get_playing(self):
        # Throttle: Atualiza a cada 3 segundos
        if self.cache is not None and time.time() - self.last_update < 3:
            return self.cache

        if not self.token and not self.refresh_access_token():
            return None
        
        link = "https://api.spotify.com/v1/me/player/currently-playing"
        try:
            response = requests.get(link, headers={"Authorization": f"Bearer {self.token}"}, timeout=5)
            if response.status_code == 401 and self.refresh_access_token():
                return self.get_playing()

            if response.status_code == 200:
                json_resp = response.json()
                if not json_resp.get('item'):
                    self.cache = None
                else:
                    artists = [artist['name'] for artist in json_resp['item']['artists']]
                    self.cache = {
                        "artists": ', '.join(artists),
                        "music": json_resp['item']['name'],
                        "playing": json_resp['is_playing']
                    }
            else:
                self.cache = None
            
            self.last_update = time.time()
            return self.cache
        except:
            return self.cache

class PrinterService:
    def __init__(self):
        self.url = Config.PRINTER_URL
        self.last_update = 0
        self.cache = None

    def get_status(self):
        # Throttle: Atualiza a cada 2 segundos
        if self.cache and time.time() - self.last_update < 2:
            return self.cache

        if not self.url: return None
        try:
            link = f"{self.url}/printer/objects/query?print_stats&display_status&extruder&heater_bed"
            response = requests.get(link, timeout=3)
            if response.status_code == 200:
                data = response.json()['result']['status']
                print_stats = data.get('print_stats', {})
                display_status = data.get('display_status', {})
                res = {
                    "state": print_stats.get('state', 'standby').capitalize(),
                    "temp_extruder": data.get('extruder', {}).get('temperature', 0),
                    "temp_bed": data.get('heater_bed', {}).get('temperature', 0),
                    "progress": display_status.get('progress', 0)
                }
                if res['state'].lower() in ["printing", "paused"]:
                    duration = print_stats.get('print_duration', 0)
                    if res['progress'] > 0:
                        remaining = (duration / res['progress']) - duration
                        res["time_left"] = f"{int(remaining // 60)}m"
                    else: res["time_left"] = "..."
                self.cache = res
                self.last_update = time.time()
                return res
            return self.cache
        except: return self.cache

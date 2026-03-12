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
        now = time.time()
        if self.cache and now - self.last_update < 2:
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
        except Exception as e:
            print(f"Erro SystemService: {e}")
        
        self.last_update = now
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
        now = time.time()
        # Se falhou ou teve erro, espera pelo menos 60 segundos antes de tentar de novo
        # Se teve sucesso, espera 10 minutos
        cooldown = 600 if self.cache else 60
        if now - self.last_update < cooldown:
            return self.cache

        self.last_update = now # Marca o tempo ANTES da chamada para evitar loops se demorar

        if not self.api_key:
            return None
        
        try:
            link = f'https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.long}&appid={self.api_key}&lang=pt_br&units=metric'
            response = requests.get(link, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            self.cache = {
                "temp": data['main']['temp'],
                "feels": data['main']['feels_like'],
                "humidity": data['main'].get('humidity', 0),
                "weather": data['weather'][0]['description'],
                "icon_id": data['weather'][0]['icon']
            }
            return self.cache
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
        if not self.refresh_token: return False
        url = "https://accounts.spotify.com/api/token"
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        payload = {"grant_type": "refresh_token", "refresh_token": self.refresh_token}
        headers = {"Authorization": f"Basic {auth_header}", "Content-Type": "application/x-www-form-urlencoded"}
        try:
            response = requests.post(url, data=payload, headers=headers, timeout=5)
            if response.status_code == 200:
                self.token = response.json().get('access_token')
                return True
        except: pass
        return False

    def get_playing(self):
        now = time.time()
        if now - self.last_update < 3:
            return self.cache

        self.last_update = now
        if not self.token and not self.refresh_access_token():
            return None
        
        try:
            response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", 
                                    headers={"Authorization": f"Bearer {self.token}"}, timeout=3)
            if response.status_code == 401 and self.refresh_access_token():
                return self.get_playing()

            if response.status_code == 200:
                json_resp = response.json()
                if json_resp.get('item'):
                    artists = [artist['name'] for artist in json_resp['item']['artists']]
                    self.cache = {
                        "artists": ', '.join(artists),
                        "music": json_resp['item']['name'],
                        "playing": json_resp['is_playing']
                    }
                else: self.cache = None
            else: self.cache = None
            return self.cache
        except:
            return self.cache

class PrinterService:
    def __init__(self):
        self.url = Config.PRINTER_URL
        self.last_update = 0
        self.cache = None

    def get_status(self):
        now = time.time()
        if self.cache and now - self.last_update < 2:
            return self.cache

        self.last_update = now
        if not self.url: return None
        try:
            link = f"{self.url}/printer/objects/query?print_stats&display_status&extruder&heater_bed"
            response = requests.get(link, timeout=2)
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
                return res
            return self.cache
        except: return self.cache

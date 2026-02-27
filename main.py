import time
import requests
import io
from datetime import datetime
from PIL import Image
from display_driver import DisplayDriver
from services import WeatherService, SpotifyService, PrinterService
from app_config import Config

class DashboardApp:
    def __init__(self):
        self.display = DisplayDriver()
        self.weather_service = WeatherService()
        self.spotify_service = SpotifyService()
        self.printer_service = PrinterService()
        self.last_weather_update = 0
        self.weather_data = None
        self.font_path = 'fonts/Arial.ttf'
        self.weather_icon_cache = {}

    def get_weather_icon(self, icon_id):
        # Cache na memória para não baixar o mesmo ícone toda hora
        if icon_id in self.weather_icon_cache:
            return self.weather_icon_cache[icon_id]
        
        url = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
        try:
            response = requests.get(url, timeout=5)
            img = Image.open(io.BytesIO(response.content)).convert("RGBA")
            self.weather_icon_cache[icon_id] = img
            return img
        except:
            return None

    def update_weather(self):
        if time.time() - self.last_weather_update > 600 or not self.weather_data:
            self.weather_data = self.weather_service.get_weather()
            self.last_weather_update = time.time()

    def render_clock(self):
        now = datetime.now()
        time_str = now.strftime('%H:%M')
        date_str = now.strftime('%d/%m/%Y')
        day_str = now.strftime('%A').upper()

        self.display.clear()
        
        # Topo: Dia da Semana
        self.display.draw_text_centered(day_str, 15, self.font_path, 12, fill=(255, 200, 50))
        self.display.draw_line(35)
        
        # Centro: Hora
        self.display.draw_text_centered(time_str, 50, self.font_path, 38, fill=(255, 255, 255))
        
        # Rodapé: Data com Linha
        self.display.draw_line(120)
        self.display.draw_text_centered(date_str, 130, self.font_path, 14, fill=(180, 180, 180))
        
        self.display.display()

    def render_weather(self):
        if not self.weather_data: return
        temp = self.weather_data.get('temp', 0)
        desc = self.weather_data.get('weather', 'N/A').capitalize()
        icon_id = self.weather_data.get('icon_id')
        
        color = (255, 255, 255)
        if temp < 15: color = (100, 180, 255)
        elif temp > 28: color = (255, 120, 50)

        self.display.clear()
        
        # Ícone do Clima (Dinâmico)
        if icon_id:
            icon_img = self.get_weather_icon(icon_id)
            if icon_img:
                self.display.draw_image(icon_img, (-1, 5), size=(40, 40))

        # Temperatura
        self.display.draw_text_centered(f"{int(temp)}°C", 50, self.font_path, 40, fill=color)
        
        # Descrição e Sensação
        self.display.draw_text_centered(desc, 105, self.font_path, 12, fill=(255, 255, 255))
        self.display.draw_line(125)
        self.display.draw_text_centered(f"SENS: {int(self.weather_data.get('feels', 0))}°C", 135, self.font_path, 10, fill=(150, 150, 150))
        
        self.display.display()

    def render_spotify(self, spotify):
        self.display.clear()
        
        self.display.draw_text_centered("SPOTIFY", 10, self.font_path, 12, fill=(30, 215, 96))
        
        # Música (Ainda mais truncado e fonte menor: 14)
        music_name = spotify['music'][:11] + ".." if len(spotify['music']) > 11 else spotify['music']
        self.display.draw_text_centered(music_name, 45, self.font_path, 14, fill=(255, 255, 255))
        
        # Artista (Truncado e fonte menor: 11)
        artist_name = spotify['artists'][:15] + ".." if len(spotify['artists']) > 15 else spotify['artists']
        self.display.draw_text_centered(artist_name, 72, self.font_path, 11, fill=(180, 180, 180))
        
        # Barra de Progresso
        self.display.draw_progress_bar(0.65, 110)
        
        self.display.draw_text_centered("♪ OUVINDO ♪", 135, self.font_path, 9, fill=(100, 100, 100))
        
        self.display.display()

    def render_printer(self, printer):
        self.display.clear()
        
        # Título
        self.display.draw_text_centered("K1 MAX", 15, self.font_path, 14, fill=(255, 140, 0))
        
        # Progresso %
        progress_pct = int(printer['progress'] * 100)
        self.display.draw_text_centered(f"{progress_pct}%", 50, self.font_path, 45, fill=(255, 255, 255))
        
        # Barra e Ícone (Simbolizar extrusão)
        self.display.draw_progress_bar(printer['progress'], 105, color=(255, 140, 0))
        
        self.display.draw_text_centered(f"RESTAM: {printer['time_left']}", 135, self.font_path, 14, fill=(180, 180, 180))
        
        self.display.display()

    def run(self):
        print("Iniciando Dashboard Portrait com Ícones...")
        try:
            while True:
                # Loop principal...
                for _ in range(10):
                    self.render_clock()
                    time.sleep(1)

                spotify = self.spotify_service.get_playing()
                if spotify:
                    for _ in range(10): 
                        self.render_spotify(spotify)
                        time.sleep(1)

                printer = self.printer_service.get_status()
                if printer:
                    for _ in range(10):
                        self.render_printer(printer)
                        time.sleep(1)

                self.update_weather()
                self.render_weather()
                time.sleep(5)
        except KeyboardInterrupt:
            print("\nEncerrando.")

if __name__ == "__main__":
    app = DashboardApp()
    app.run()

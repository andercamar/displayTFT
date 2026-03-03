import time
import requests
import io
from datetime import datetime
from PIL import Image
from display_driver import DisplayDriver
from services import WeatherService, SpotifyService, PrinterService, SystemService
from app_config import Config

class DashboardApp:
    def __init__(self):
        self.display = DisplayDriver()
        self.weather_service = WeatherService()
        self.spotify_service = SpotifyService()
        self.printer_service = PrinterService()
        self.system_service = SystemService()
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

    def get_icon(self, url, size=(20, 20)):
        # Cache para ícones gerais
        if url in self.weather_icon_cache:
            return self.weather_icon_cache[url]
        
        try:
            response = requests.get(url, timeout=5)
            img = Image.open(io.BytesIO(response.content)).convert("RGBA")
            if size:
                img = img.resize(size, Image.Resampling.LANCZOS)
            self.weather_icon_cache[url] = img
            return img
        except:
            return None

    def render_clock(self):
        now = datetime.now()
        time_str = now.strftime('%H:%M')
        
        days_br = ["SEGUNDA", "TERÇA", "QUARTA", "QUINTA", "SEXTA", "SÁBADO", "DOMINGO"]
        days_en = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
        
        day_idx = now.weekday()
        day_str_br = days_br[day_idx]
        day_str_en = days_en[day_idx]
        date_str = now.strftime('%d/%m/%Y')

        self.display.clear()
        
        # Topo: Dia em Português
        self.display.draw_text_centered(day_str_br, 15, self.font_path, 12, fill=(255, 200, 50))
        
        # Hora Central (Mais para o meio agora que não tem ícone no topo)
        self.display.draw_text_centered(time_str, 42, self.font_path, 40, fill=(255, 255, 255))
        
        # Dia em Inglês
        self.display.draw_text_centered(day_str_en, 88, self.font_path, 11, fill=(255, 255, 255))
        
        self.display.draw_line(108, margin=20, fill=(255, 255, 255))
        
        # Data no rodapé
        self.display.draw_text_centered(date_str, 120, self.font_path, 14, fill=(255, 255, 255))

        # Barra Pulsante
        pulse_color = (0, 255, 0) if int(now.strftime('%S')) % 2 == 0 else (0, 200, 0)
        self.display.draw_line(150, margin=45, fill=pulse_color)
        
        self.display.display()

    def render_weather(self):
        # ... (mantido igual, já tem ícone)
        if not self.weather_data: return
        temp = int(self.weather_data.get('temp', 0))
        feels = int(self.weather_data.get('feels', 0))
        humi = self.weather_data.get('humidity', 0)
        desc = self.weather_data.get('weather', 'N/A').upper()
        icon_id = self.weather_data.get('icon_id')
        
        self.display.clear((0, 0, 15))
        
        if icon_id:
            icon_img = self.get_weather_icon(icon_id)
            if icon_img:
                self.display.draw_image(icon_img, (-1, 0), size=(45, 45))

        color = (150, 220, 255) if temp < 20 else (255, 180, 50)
        self.display.draw_text_centered(f"{temp}°C", 45, self.font_path, 40, fill=color)
        
        self.display.draw_text_centered(desc, 85, self.font_path, 11, fill=(255, 255, 255))
        
        self.display.draw_line(105, margin=20, fill=(255, 255, 255))
        
        self.display.draw_text_centered(f"SENSAÇÃO: {feels}°C", 118, self.font_path, 11, fill=(255, 255, 255))
        self.display.draw_text_centered(f"UMIDADE: {humi}%", 135, self.font_path, 11, fill=(255, 255, 255))
        
        self.display.display()

    def render_spotify(self, spotify):
        self.display.clear()
        
        # Logo do Spotify no topo
        spotify_icon_url = "https://cdn-icons-png.flaticon.com/512/174/174872.png"
        icon_spot = self.get_icon(spotify_icon_url, size=(18, 18))
        if icon_spot:
            self.display.draw_image(icon_spot, (-1, 10))
            
        self.display.draw_text_centered("SPOTIFY", 32, self.font_path, 11, fill=(30, 255, 120))
        self.display.draw_line(45, margin=30, fill=(30, 255, 120))
        
        music_name = spotify['music']
        if len(music_name) > 16: music_name = music_name[:14] + ".."
        self.display.draw_text_centered(music_name.upper(), 65, self.font_path, 14, fill=(255, 255, 255))
        
        artist_name = spotify['artists']
        if len(artist_name) > 22: artist_name = artist_name[:20] + ".."
        self.display.draw_text_centered(artist_name, 90, self.font_path, 12, fill=(255, 255, 255))
        
        self.display.draw_progress_bar(0.65, 120, height=3, color=(30, 255, 120))
        
        status_text = "REPRODUZINDO" if spotify.get('playing') else "PAUSADO"
        self.display.draw_text_centered(status_text, 140, self.font_path, 10, fill=(255, 255, 255))
        
        self.display.display()

    def render_printer(self, printer):
        self.display.clear()
        
        # Cabeçalho
        self.display.draw_text_centered("K1 MAX", 10, self.font_path, 16, fill=(255, 140, 0))
        self.display.draw_line(30)

        state = printer.get('state', 'Unknown').upper()
        
        if state in ["PRINTING", "PAUSED"]:
            # --- TELA DE IMPRESSÃO ---
            progress_pct = int(printer['progress'] * 100)
            self.display.draw_text_centered(f"{progress_pct}%", 45, self.font_path, 44, fill=(255, 255, 255))
            
            # Barra de Progresso
            self.display.draw_progress_bar(printer['progress'], 105, color=(255, 140, 0))
            
            # Tempo restante ou Status
            info_text = f"RESTAM: {printer.get('time_left', '...')}"
            self.display.draw_text_centered(info_text, 125, self.font_path, 13, fill=(255, 255, 255))
        else:
            # --- TELA IDLE (CRIATIVA) ---
            # Status Principal
            status_color = (0, 255, 100) if state == "STANDBY" else (255, 200, 0)
            self.display.draw_text_centered(state, 45, self.font_path, 24, fill=status_color)
            
            # Temperaturas com pequenos separadores
            self.display.draw_text_centered("TEMPERATURAS", 85, self.font_path, 11, fill=(255, 255, 255))
            
            # Bico (Extruder)
            temp_ext = int(printer.get('temp_extruder', 0))
            self.display.draw_text_centered(f"BICO: {temp_ext}°C", 105, self.font_path, 16, fill=(255, 100, 50))
            
            # Mesa (Bed)
            temp_bed = int(printer.get('temp_bed', 0))
            self.display.draw_text_centered(f"MESA: {temp_bed}°C", 130, self.font_path, 16, fill=(50, 150, 255))

        self.display.display()

    def render_system(self):
        stats = self.system_service.get_stats()
        if not stats: return
        
        self.display.clear((20, 20, 20)) # Fundo grafite escuro
        
        # Título
        self.display.draw_text_centered("RASPBERRY PI", 10, self.font_path, 13, fill=(255, 50, 80))
        self.display.draw_line(28, margin=15, fill=(255, 50, 80))
        
        # Temperatura CPU (Destaque Central)
        temp = stats['temp']
        temp_color = (100, 255, 100) if temp < 55 else (255, 180, 0)
        if temp > 70: temp_color = (255, 0, 0)
        
        self.display.draw_text_centered(f"{int(temp)}°C", 45, self.font_path, 42, fill=temp_color)
        self.display.draw_text_centered("CPU TEMP", 85, self.font_path, 12, fill=(255, 255, 255))
        
        # Uso de RAM
        ram_pct = stats['ram_usage']
        self.display.draw_text_centered(f"RAM: {int(ram_pct)}%", 108, self.font_path, 12, fill=(255, 255, 255))
        self.display.draw_progress_bar(ram_pct/100, 122, height=4, color=(50, 180, 255))
        
        # Carga do Sistema
        self.display.draw_text_centered(f"LOAD: {int(stats['cpu'])}%", 138, self.font_path, 11, fill=(255, 255, 255))
        
        self.display.display()

    def run(self):
        print("Iniciando Dashboard Portrait com Monitoramento de Sistema...")
        try:
            while True:
                # 1. Relógio (10 segundos)
                for _ in range(10):
                    self.render_clock()
                    time.sleep(1)

                # 2. Spotify (se estiver tocando)
                spotify = self.spotify_service.get_playing()
                if spotify:
                    for _ in range(10): 
                        self.render_spotify(spotify)
                        time.sleep(1)

                # 3. Impressora (Sempre exibe o status atual)
                printer = self.printer_service.get_status()
                if printer:
                    for _ in range(10):
                        self.render_printer(printer)
                        time.sleep(1)

                # 4. Monitor de Sistema (Raspberry Pi)
                for _ in range(5):
                    self.render_system()
                    time.sleep(1)

                # 5. Clima (5 segundos)
                self.update_weather()
                self.render_weather()
                time.sleep(5)
        except KeyboardInterrupt:
            print("\nEncerrando.")

if __name__ == "__main__":
    app = DashboardApp()
    app.run()

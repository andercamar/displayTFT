import time
from datetime import datetime
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
        self.font_path = 'fonts/Arial.ttf' # O driver cuidará se não existir

    def update_weather(self):
        # Atualiza o clima apenas a cada 10 minutos para economizar API
        if time.time() - self.last_weather_update > 600 or not self.weather_data:
            print("Atualizando dados do clima...")
            self.weather_data = self.weather_service.get_weather()
            self.last_weather_update = time.time()

    def render_clock(self):
        now = datetime.now()
        time_str = now.strftime('%H:%M')
        date_str = now.strftime('%d %b %Y') # 26 Fev 2026
        day_str = now.strftime('%A').capitalize() # Quinta-feira

        self.display.clear()
        
        # Hora Grande e Centralizada
        self.display.draw_text_centered(time_str, 30, self.font_path, 45, fill=(255, 255, 255))
        
        # Data logo abaixo
        self.display.draw_text_centered(date_str, 85, self.font_path, 16, fill=(200, 200, 200))
        
        # Dia da Semana (Rodapé)
        self.display.draw_text_centered(day_str, 110, self.font_path, 14, fill=(150, 150, 150))
        
        self.display.display()

    def render_weather(self):
        if not self.weather_data:
            return
            
        temp = self.weather_data.get('temp', 0)
        desc = self.weather_data.get('weather', 'N/A').capitalize()
        
        # Cor dinâmica baseada na temperatura
        color = (255, 255, 255) # Branco padrão
        if temp < 15: color = (100, 150, 255) # Azul para frio
        elif temp > 28: color = (255, 150, 50) # Laranja para calor

        self.display.clear()
        
        # Título da Tela
        self.display.draw_text_centered("Clima", 15, self.font_path, 12, fill=(180, 180, 180))
        
        # Temperatura Gigante
        self.display.draw_text_centered(f"{int(temp)}°C", 40, self.font_path, 50, fill=color)
        
        # Descrição logo abaixo
        self.display.draw_text_centered(desc, 100, self.font_path, 16, fill=(255, 255, 255))
        
        self.display.display()

    def render_spotify(self, spotify):
        self.display.clear()
        
        # Ícone "Spotify" ou Barra no Topo
        self.display.draw_text_centered("Tocando agora", 15, self.font_path, 12, fill=(29, 185, 84))
        
        # Nome da música (Centralizado)
        self.display.draw_text_centered(spotify['music'], 50, self.font_path, 18, fill=(255, 255, 255))
        
        # Artista (Menor)
        self.display.draw_text_centered(spotify['artists'], 85, self.font_path, 14, fill=(180, 180, 180))
        
        # Simular Barra de Progresso
        self.display.draw_progress_bar(0.65, 140) 
        
        self.display.display()

    def render_printer(self, printer):
        self.display.clear()
        
        # Título da Tela
        self.display.draw_text_centered("Impressora 3D", 15, self.font_path, 12, fill=(255, 165, 0)) # Laranja
        
        # Progresso Grande
        progress_pct = int(printer['progress'] * 100)
        self.display.draw_text_centered(f"{progress_pct}%", 40, self.font_path, 40, fill=(255, 255, 255))
        
        # Tempo Restante
        self.display.draw_text_centered(f"Faltam: {printer['time_left']}", 90, self.font_path, 16, fill=(180, 180, 180))
        
        # Barra de Progresso (Laranja)
        self.display.draw_progress_bar(printer['progress'], 140, color=(255, 140, 0))
        
        self.display.display()

    def run(self):
        print("Iniciando Dashboard com Impressora 3D...")
        try:
            while True:
                # 1. Relógio (10s)
                for _ in range(10):
                    self.render_clock()
                    time.sleep(1)

                # 2. Spotify (Prioridade se tocando)
                spotify = self.spotify_service.get_playing()
                if spotify:
                    for _ in range(10): 
                        self.render_spotify(spotify)
                        time.sleep(1)

                # 3. Impressora 3D (Se estiver ativa)
                printer = self.printer_service.get_status()
                if printer:
                    for _ in range(10):
                        self.render_printer(printer)
                        time.sleep(1)

                # 4. Clima (5s)
                self.update_weather()
                self.render_weather()
                time.sleep(5)

        except KeyboardInterrupt:
            print("\nEncerrando aplicação.")

if __name__ == "__main__":
    app = DashboardApp()
    app.run()

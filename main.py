import time
import os
import threading
from datetime import datetime
from app_config import Config
from display_driver import DisplayDriver
from services import WeatherService, SpotifyService, PrinterService, SystemService
from page_manager import PageManager
from pages.clock import ClockPage
from pages.weather import WeatherPage
from pages.spotify import SpotifyPage
from pages.printer import PrinterPage
from pages.system import SystemPage
from pages.status_bar import StatusBar

class DashboardApp:
    def __init__(self):
        self.display = DisplayDriver()
        
        # Inicializa Serviços
        self.weather_service = WeatherService()
        self.spotify_service = SpotifyService()
        self.printer_service = PrinterService()
        self.system_service = SystemService()
        
        # Barra de Status Global
        self.status_bar = StatusBar(self.display, self.system_service, self.printer_service)
        
        # Inicializa as Páginas (Plugins)
        self.pages = [
            ClockPage(self.display),
            SpotifyPage(self.display, self.spotify_service),
            PrinterPage(self.display, self.printer_service),
            SystemPage(self.display, self.system_service),
            WeatherPage(self.display, self.weather_service)
        ]
        
        # Gerenciador de Páginas
        self.manager = PageManager(self.pages, self.display)
        self.running = True

    def background_task(self):
        """Thread que busca dados das APIs em segundo plano sem travar a interface."""
        print("Thread de dados iniciada.")
        while self.running:
            try:
                # Atualiza todos os serviços (que já têm throttling interno)
                # O manager.update() vai chamar o update() de cada página
                for page in self.pages:
                    page.update()
                self.status_bar.update()
            except Exception as e:
                print(f"Erro na thread de dados: {e}")
            
            # Espera 2 segundos antes da próxima rodada de rede
            time.sleep(2)

    def run(self):
        print("Iniciando Dashboard Multithread (Liso FPS)...")
        
        # Inicia a busca de dados em paralelo
        bg_thread = threading.Thread(target=self.background_task, daemon=True)
        bg_thread.start()

        try:
            while True:
                # O loop principal agora SÓ DESENHA
                self.display.clear()

                # 1. Gerencia trocas de página
                self.manager.update()
                
                # 2. Renderiza a página atual diretamente (transição removida para nitidez)
                current_page = self.manager.get_current_page()
                if current_page:
                    current_page.render()
                
                # 3. Renderiza a Barra de Status
                self.status_bar.render()
                
                # 4. Modo Noturno Automático (Apenas visual)
                final_frame = self.display.buffer

                def get_day_minutes(hh_mm_str):
                    h, m = map(int, hh_mm_str.split(':'))
                    return h * 60 + m
                
                now = datetime.now()
                now_min = now.hour * 60 + now.minute
                start_min = get_day_minutes(Config.NIGHT_MODE_START)
                end_min = get_day_minutes(Config.NIGHT_MODE_END)

                in_night_window = False
                if start_min > end_min: # Janela cruza meia-noite
                    in_night_window = now_min >= start_min or now_min < end_min
                else: # Janela no mesmo dia
                    in_night_window = start_min <= now_min < end_min
                
                if in_night_window:
                    final_frame = self.display.apply_night_mode(dim_factor=Config.NIGHT_MODE_DIM, red_tint=Config.NIGHT_MODE_RED_TINT)

                # 5. Envia para o display
                if self.display.debug:
                    if not os.path.exists("debug_frames"):
                        os.makedirs("debug_frames")
                    final_frame.save("debug_frames/current_frame.png")
                else:
                    self.display.disp.image(final_frame)
                
                # Loop cravado em 1 segundo (1 FPS) para máxima nitidez e economia de energia
                time.sleep(1.0)
                
        except KeyboardInterrupt:
            self.running = False
            print("\nEncerrando dashboard.")

if __name__ == "__main__":
    app = DashboardApp()
    app.run()

import time
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
        
        # Gerenciador de Páginas (Passando display para gerenciar transições)
        self.manager = PageManager(self.pages, self.display)

    def run(self):
        print("Iniciando Dashboard com Transições Suaves...")
        try:
            while True:
                # 1. Atualiza dados e gerencia trocas de página/transições
                self.manager.update()
                self.status_bar.update()
                
                # 2. Renderiza a página atual (apenas se não estiver no meio de uma transição)
                # O PageManager já cuida da renderização durante o Fade
                if not self.manager.is_transitioning:
                    current_page = self.manager.get_current_page()
                    if current_page:
                        current_page.render()
                
                # 3. Sobrepõe a Barra de Status em cada frame
                # A Barra de Status não participa do Fade para ficar sempre visível
                self.status_bar.render()
                
                # 4. Modo Noturno Automático
                # Converter horários HH:MM para minutos totais do dia para precisão
                def get_day_minutes(hh_mm_str):
                    h, m = map(int, hh_mm_str.split(':'))
                    return h * 60 + m
                
                now = datetime.now()
                now_min = now.hour * 60 + now.minute
                start_min = get_day_minutes(Config.NIGHT_MODE_START)
                end_min = get_day_minutes(Config.NIGHT_MODE_END)

                in_night_window = False
                if start_min > end_min: # Janela cruza meia-noite (ex: 19:45 até 06:00)
                    in_night_window = now_min >= start_min or now_min < end_min
                else: # Janela no mesmo dia
                    in_night_window = start_min <= now_min < end_min
                
                if in_night_window:
                    self.display.apply_night_mode(dim_factor=Config.NIGHT_MODE_DIM, red_tint=Config.NIGHT_MODE_RED_TINT)

                # Envia o frame final para o hardware/simulador
                self.display.display()
                
                # Controle de FPS: 
                # Se estiver transicionando, dorme menos para o fade ser fluido
                if self.manager.is_transitioning:
                    time.sleep(0.05) # ~20 FPS durante o fade
                else:
                    time.sleep(1) # 1 FPS normal para economizar CPU
                
        except KeyboardInterrupt:
            print("\nEncerrando dashboard.")

if __name__ == "__main__":
    app = DashboardApp()
    app.run()

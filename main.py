import time
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
        self.manager = PageManager(self.pages)

    def run(self):
        print("Iniciando Dashboard com Arquitetura Modular e Status Bar...")
        try:
            while True:
                # 1. Atualiza dados (background)
                self.manager.update()
                self.status_bar.update()
                
                # 2. Renderiza a página atual
                current_page = self.manager.get_current_page()
                if current_page:
                    current_page.render()
                
                # 3. Sobrepõe a Barra de Status em cada frame
                self.status_bar.render()
                
                # Envia o frame final para o hardware/simulador
                self.display.display()
                
                # Controle de FPS
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nEncerrando dashboard.")

if __name__ == "__main__":
    app = DashboardApp()
    app.run()

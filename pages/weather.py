import time
from pages.base import BasePage, ResourceCache

class WeatherPage(BasePage):
    def __init__(self, display, weather_service, font_path='fonts/FSEX300.ttf'):
        super().__init__(display, font_path)
        self.weather_service = weather_service
        self.weather_data = None
        self.last_update = 0

    def update(self):
        # Atualiza a cada 10 minutos
        if time.time() - self.last_update > 600 or not self.weather_data:
            try:
                self.weather_data = self.weather_service.get_weather()
                self.last_update = time.time()
            except Exception as e:
                print(f"Erro ao atualizar clima: {e}")
                self.weather_data = None

    def render(self):
        if not self.weather_data:
            self.display.clear()
            self.display.draw_text_centered("CLIMA INDISPONÍVEL", 70, self.font_path, 14)
            return

        temp = int(self.weather_data.get('temp', 0))
        feels = int(self.weather_data.get('feels', 0))
        humi = self.weather_data.get('humidity', 0)
        desc = self.weather_data.get('weather', 'N/A').upper()
        icon_id = self.weather_data.get('icon_id')
        
        self.display.clear((0, 0, 15))
        
        if icon_id:
            url = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
            icon_img = ResourceCache.get_icon(url, size=(42, 42))
            if icon_img:
                self.display.draw_image(icon_img, (-1, 16))

        color = (150, 220, 255) if temp < 20 else (255, 180, 50)
        self.display.draw_text_centered(f"{temp}°C", 50, self.font_path, 48, fill=color)
        
        self.display.draw_text_centered(desc, 90, self.font_path, 14, fill=(255, 255, 255))
        
        self.display.draw_line(106, margin=20, fill=(255, 255, 255))
        
        self.display.draw_text_centered(f"SENSAÇÃO: {feels}°C", 115, self.font_path, 14, fill=(255, 255, 255))
        self.display.draw_text_centered(f"UMIDADE: {humi}%", 132, self.font_path, 14, fill=(255, 255, 255))

    def get_duration(self):
        return 5

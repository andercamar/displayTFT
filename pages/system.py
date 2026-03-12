from pages.base import BasePage

class SystemPage(BasePage):
    def __init__(self, display, system_service, font_path='fonts/FSEX300.ttf'):
        super().__init__(display, font_path)
        self.system_service = system_service
        self.stats = None

    def update(self):
        try:
            self.stats = self.system_service.get_stats()
        except Exception as e:
            print(f"Erro Sistema: {e}")
            self.stats = None

    def render(self):
        if not self.stats: return
        
        self.display.clear((20, 20, 20))
        
        self.display.draw_text_centered("RASPBERRY PI", 18, self.font_path, 14, fill=(255, 50, 80))
        self.display.draw_line(35, margin=15, fill=(255, 50, 80))

        temp = self.stats['temp']
        temp_color = (100, 255, 100) if temp < 55 else (255, 180, 0)
        if temp > 70: temp_color = (255, 0, 0)

        self.display.draw_text_centered(f"{int(temp)}°C", 50, self.font_path, 48, fill=temp_color)
        self.display.draw_text_centered("CPU TEMP", 95, self.font_path, 14, fill=(255, 255, 255))

        ram_pct = self.stats['ram_usage']
        self.display.draw_text_centered(f"RAM: {int(ram_pct)}%", 115, self.font_path, 14, fill=(255, 255, 255))
        self.display.draw_progress_bar(ram_pct/100, 130, height=4, color=(50, 180, 255))

        self.display.draw_text_centered(f"LOAD: {int(self.stats['cpu'])}%", 142, self.font_path, 14, fill=(255, 255, 255))



    def get_duration(self):
        return 5

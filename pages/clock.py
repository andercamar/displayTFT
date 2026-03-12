from datetime import datetime
from pages.base import BasePage

class ClockPage(BasePage):
    def __init__(self, display, font_path='fonts/FSEX300.ttf'):
        super().__init__(display, font_path)
        self.pulse_state = True

    def render(self):
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
        self.display.draw_text_centered(day_str_br, 18, self.font_path, 16, fill=(255, 200, 50))
        
        # Hora Central (Mais compacta)
        self.display.draw_text_centered(time_str, 38, self.font_path, 48, fill=(255, 255, 255))
        
        # Dia em Inglês
        self.display.draw_text_centered(day_str_en, 88, self.font_path, 14, fill=(255, 255, 255))
        
        self.display.draw_line(108, margin=20, fill=(255, 255, 255))
        
        # Data
        self.display.draw_text_centered(date_str, 118, self.font_path, 18, fill=(255, 255, 255))

        # Barra Pulsante (Pisca entre Verde e Preto)
        pulse_color = (0, 255, 0) if self.pulse_state else (0, 0, 0)
        self.display.draw_line(145, margin=45, fill=pulse_color)
        self.pulse_state = not self.pulse_state

    def get_duration(self):
        return 10

from pages.base import BasePage

class PrinterPage(BasePage):
    def __init__(self, display, printer_service, font_path='fonts/FSEX300.ttf'):
        super().__init__(display, font_path)
        self.printer_service = printer_service
        self.printer_data = None

    def update(self):
        try:
            self.printer_data = self.printer_service.get_status()
        except Exception as e:
            print(f"Erro Impressora: {e}")
            self.printer_data = None

    def should_show(self):
        return self.printer_data is not None

    def render(self):
        if not self.printer_data: return
        
        self.display.clear()
        
        # Cabeçalho
        self.display.draw_text_centered("K1 MAX", 18, self.font_path, 14, fill=(255, 140, 0))
        self.display.draw_line(35)

        state = self.printer_data.get('state', 'Unknown').upper()
        
        if state in ["PRINTING", "PAUSED"]:
            progress_pct = int(self.printer_data['progress'] * 100)
            self.display.draw_text_centered(f"{progress_pct}%", 50, self.font_path, 48, fill=(255, 255, 255))
            self.display.draw_progress_bar(self.printer_data['progress'], 105, color=(255, 140, 0))
            info_text = f"RESTAM: {self.printer_data.get('time_left', '...')}"
            self.display.draw_text_centered(info_text, 125, self.font_path, 16, fill=(255, 255, 255))
        else:
            status_color = (0, 255, 100) if state == "STANDBY" else (255, 200, 0)
            self.display.draw_text_centered(state, 50, self.font_path, 28, fill=status_color)
            self.display.draw_text_centered("TEMPERATURAS", 85, self.font_path, 14, fill=(255, 255, 255))
            
            temp_ext = int(self.printer_data.get('temp_extruder', 0))
            self.display.draw_text_centered(f"BICO: {temp_ext}°C", 105, self.font_path, 18, fill=(255, 100, 50))
            
            temp_bed = int(self.printer_data.get('temp_bed', 0))
            self.display.draw_text_centered(f"MESA: {temp_bed}°C", 130, self.font_path, 18, fill=(50, 150, 255))

    def get_duration(self):
        return 10

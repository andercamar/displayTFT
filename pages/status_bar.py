class StatusBar:
    def __init__(self, display, system_service, printer_service, font_path='fonts/FSEX300.ttf'):
        self.display = display
        self.system_service = system_service
        self.printer_service = printer_service
        self.font_path = font_path
        self.stats = None
        self.printer_status = None

    def update(self):
        try:
            self.stats = self.system_service.get_stats()
            self.printer_status = self.printer_service.get_status()
        except:
            pass

    def render(self):
        if not self.stats: return
        
        # Fundo da Barra de Status
        self.display.draw_rectangle([0, 0, self.display.width, 15], fill=(20, 20, 20))
        
        # IP no canto esquerdo
        ip_text = self.stats.get('ip', '0.0.0.0')
        self.display.draw_text_absolute(ip_text, (4, 2), self.font_path, 10, fill=(180, 180, 180))
        
        # CPU Temp no meio (com cor dinâmica)
        temp = self.stats.get('temp', 0)
        t_color = (100, 255, 100) if temp < 55 else (255, 150, 0)
        self.display.draw_text_absolute(f"{int(temp)}°C", (74, 2), self.font_path, 10, fill=t_color)
        
        # Status da Impressora (Círculo colorido)
        p_color = (100, 100, 100) # Cinza (Desconectado)
        if self.printer_status:
            state = self.printer_status.get('state', '').lower()
            if state == 'printing':
                p_color = (255, 140, 0) # Laranja
            elif state in ['standby', 'ready', 'complete']:
                p_color = (0, 255, 120) # Verde Água
            else:
                p_color = (255, 50, 50) # Vermelho
        
        self.display.draw_circle((120, 7), 3, fill=p_color)

        # Linha separadora
        self.display.draw_line(15, margin=0, fill=(60, 60, 60))

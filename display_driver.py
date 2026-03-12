import os
from PIL import Image, ImageDraw, ImageFont
from app_config import Config

class DisplayDriver:
    def __init__(self, debug=Config.DEBUG_MODE):
        self.debug = debug
        self.width = 128
        self.height = 160
        self.buffer = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        self.disp = None
        
        if not self.debug:
            try:
                import board
                import busio
                import digitalio
                from adafruit_rgb_display import st7735
                
                # Configuração moderna via Blinka (CircuitPython para Linux)
                spi = board.SPI()
                
                # Pinos configurados no app_config.py
                cs_pin = digitalio.DigitalInOut(board.CE0)
                dc_pin = digitalio.DigitalInOut(getattr(board, f"D{Config.TFT_DC}"))
                reset_pin = digitalio.DigitalInOut(getattr(board, f"D{Config.TFT_RST}"))

                # Inicializa o display ST7735R
                self.disp = st7735.ST7735R(
                    spi, 
                    rotation=0, 
                    cs=cs_pin, 
                    dc=dc_pin, 
                    rst=reset_pin, 
                    baudrate=Config.TFT_SPEED_HZ,
                    width=128,
                    height=160
                )
                print(f"Hardware Display (ST7735R) inicializado: {self.width}x{self.height}")
            except Exception as e:
                print(f"Erro ao inicializar hardware: {e}")
                print("Ativando modo DEBUG/Simulador.")
                self.debug = True
        
        if self.debug:
            print("Rodando em modo Simulador (os frames serão salvos em debug_frames/).")

    def clear(self, color=(0, 0, 0)):
        self.buffer = Image.new('RGB', (self.width, self.height), color)

    def display(self):
        if self.debug:
            if not os.path.exists("debug_frames"):
                os.makedirs("debug_frames")
            self.buffer.save("debug_frames/current_frame.png")
        else:
            # Envia o buffer Pillow diretamente para o display
            self.disp.image(self.buffer)

    def apply_night_mode(self, dim_factor=0.5, red_tint=True):
        """Aplica filtro noturno no buffer e RETORNA a imagem processada sem alterar o original."""
        if dim_factor >= 1.0 and not red_tint:
            return self.buffer

        # Se red_tint for True, reduz menos agressivamente os canais Verde e Azul
        r_mult = dim_factor
        g_mult = dim_factor * 0.8 if red_tint else dim_factor
        b_mult = dim_factor * 0.7 if red_tint else dim_factor
        
        matrix = (
            r_mult, 0, 0, 0,
            0, g_mult, 0, 0,
            0, 0, b_mult, 0
        )
        # Retorna uma cópia processada, mantendo self.buffer intacto
        return self.buffer.convert("RGB", matrix)

    def _get_font(self, font_path, font_size):
        """Tenta carregar a fonte solicitada ou busca uma alternativa no sistema."""
        try:
            # Prioriza fontes em negrito do sistema Raspberry Pi OS
            system_fonts = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            ]
            
            # Se um caminho específico for passado e existir, usa ele
            if font_path and os.path.exists(font_path):
                return ImageFont.truetype(font_path, font_size)
            
            for sf in system_fonts:
                if os.path.exists(sf):
                    return ImageFont.truetype(sf, font_size)
            
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()

    def draw_text_centered(self, text, y_pos, font_path, font_size, fill=(255, 255, 255), rotation=0):
        font = self._get_font(font_path, font_size)
        draw = ImageDraw.Draw(self.buffer)
        
        # Cálculo de centralização compatível com Pillow moderno
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        x_pos = (self.width - w) // 2
        
        # Se houver rotação (para layouts horizontais/verticais específicos)
        if rotation != 0:
            text_img = Image.new('RGBA', (w + 10, bbox[3] - bbox[1] + 10), (0, 0, 0, 0))
            t_draw = ImageDraw.Draw(text_img)
            t_draw.text((0, 0), text, font=font, fill=fill)
            rotated = text_img.rotate(rotation, expand=True)
            self.buffer.paste(rotated, (x_pos, y_pos), rotated)
        else:
            draw.text((x_pos, y_pos), text, font=font, fill=fill)

    def draw_text_absolute(self, text, position, font_path, font_size, fill=(255, 255, 255)):
        font = self._get_font(font_path, font_size)
        draw = ImageDraw.Draw(self.buffer)
        draw.text(position, text, font=font, fill=fill)

    def draw_rectangle(self, coords, fill=None, outline=None):
        draw = ImageDraw.Draw(self.buffer)
        draw.rectangle(coords, fill=fill, outline=outline)

    def draw_circle(self, center, radius, fill=None, outline=None):
        draw = ImageDraw.Draw(self.buffer)
        x, y = center
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=fill, outline=outline)

    def draw_line(self, y_pos, margin=10, fill=(255, 255, 255)):
        draw = ImageDraw.Draw(self.buffer)
        draw.line((margin, y_pos, self.width - margin, y_pos), fill=fill)

    def draw_image(self, image_input, position, size=None):
        try:
            if isinstance(image_input, str):
                img = Image.open(image_input).convert("RGBA")
            else:
                img = image_input.convert("RGBA")
            
            if size:
                img = img.resize(size, Image.Resampling.LANCZOS)
            
            x, y = position
            if x == -1: # Centralizar
                x = (self.width - img.width) // 2
            
            self.buffer.paste(img, (x, y), img)
        except Exception as e:
            print(f"Erro ao desenhar imagem: {e}")

    def draw_progress_bar(self, progress, y_pos, height=4, color=(29, 185, 84)):
        progress = max(0, min(1, progress))
        draw = ImageDraw.Draw(self.buffer)
        bar_width = self.width - 20
        fill_width = int(bar_width * progress)
        
        # Fundo da barra
        draw.rectangle([10, y_pos, self.width-10, y_pos+height], fill=(100, 100, 100))
        # Progresso
        if fill_width > 0:
            draw.rectangle([10, y_pos, 10+fill_width, y_pos+height], fill=color)

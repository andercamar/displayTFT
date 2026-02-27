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
                import ST7735 as TFT
                import Adafruit_GPIO.SPI as SPI
                
                self.disp = TFT.ST7735(
                    Config.TFT_DC,
                    rst=Config.TFT_RST,
                    spi=SPI.SpiDev(
                        Config.TFT_SPI_PORT,
                        Config.TFT_SPI_DEVICE,
                        max_speed_hz=Config.TFT_SPEED_HZ
                    )
                )
                self.disp.begin()
                print("Hardware Display inicializado.")
            except ImportError:
                print("Bibliotecas de hardware não encontradas. Ativando modo DEBUG.")
                self.debug = True
        
        if self.debug:
            print("Rodando em modo Simulador (Debug).")

    def clear(self, color=(0, 0, 0)):
        self.buffer = Image.new('RGB', (self.width, self.height), color)

    def display(self):
        if self.debug:
            # Em modo debug, vamos salvar a imagem ou tentar abrir
            if not os.path.exists("debug_frames"):
                os.makedirs("debug_frames")
            self.buffer.save("debug_frames/current_frame.png")
            # print("Frame salvo em debug_frames/current_frame.png")
        else:
            self.disp.display(self.buffer)

    def draw_text_centered(self, text, y_pos, font_path, font_size, fill=(255, 255, 255), rotation=0):
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()

        # Criar imagem temporária para o texto
        # Usamos um tamanho maior para garantir que o texto caiba antes da rotação
        text_img_temp = Image.new('RGBA', (self.width * 2, self.height), (0, 0, 0, 0))
        draw_temp = ImageDraw.Draw(text_img_temp)
        bbox = draw_temp.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

        text_img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)
        text_draw.text((0, 0), text, font=font, fill=fill)
        
        rotated = text_img.rotate(rotation, expand=1)
        rw, rh = rotated.size
        
        # Centraliza horizontalmente no buffer
        x_pos = (self.width - rw) // 2
        self.buffer.paste(rotated, (x_pos, y_pos), rotated)

    def draw_line(self, y_pos, margin=10, fill=(100, 100, 100)):
        draw = ImageDraw.Draw(self.buffer)
        draw.line((margin, y_pos, self.width - margin, y_pos), fill=fill)

    def draw_image(self, image_input, position, size=None):
        """
        image_input: Pode ser um caminho (str) ou um objeto Image da PIL.
        position: (x, y)
        size: (w, h) opcional para redimensionar.
        """
        try:
            if isinstance(image_input, str):
                img = Image.open(image_input).convert("RGBA")
            else:
                img = image_input.convert("RGBA")
            
            if size:
                img = img.resize(size, Image.Resampling.LANCZOS)
            
            # Se for centralizar horizontalmente (passando x como -1)
            x, y = position
            if x == -1:
                x = (self.width - img.width) // 2
            
            self.buffer.paste(img, (x, y), img)
        except Exception as e:
            print(f"Erro ao desenhar imagem: {e}")

    def draw_progress_bar(self, progress, y_pos, height=4, color=(29, 185, 84)):
        # progress: 0.0 a 1.0
        draw = ImageDraw.Draw(self.buffer)
        width = int((self.width - 20) * progress)
        # Desenha o fundo da barra
        draw.rectangle([10, y_pos, self.width-10, y_pos+height], fill=(50, 50, 50))
        # Desenha o progresso
        draw.rectangle([10, y_pos, 10+width, y_pos+height], fill=color)

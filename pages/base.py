import requests
import io
from PIL import Image

class ResourceCache:
    """Cache centralizado para ícones e imagens para evitar downloads repetidos."""
    _cache = {}

    @classmethod
    def get_icon(cls, url, size=(20, 20)):
        if url in cls._cache:
            return cls._cache[url]
        
        try:
            response = requests.get(url, timeout=5)
            img = Image.open(io.BytesIO(response.content)).convert("RGBA")
            if size:
                img = img.resize(size, Image.Resampling.LANCZOS)
            cls._cache[url] = img
            return img
        except Exception as e:
            print(f"Erro ao carregar ícone {url}: {e}")
            return None

class BasePage:
    """Classe base para todas as telas do dashboard."""
    def __init__(self, display, font_path='fonts/FSEX300.ttf'):
        self.display = display
        self.font_path = font_path
        self.name = self.__class__.__name__

    def update(self):
        """Atualiza os dados da página (ex: chamada de API)."""
        pass

    def render(self):
        """Desenha a página no buffer do display."""
        pass

    def should_show(self):
        """Retorna True se a página deve ser exibida no loop atual."""
        return True

    def get_duration(self):
        """Retorna quanto tempo (em segundos) a página deve ficar visível."""
        return 10

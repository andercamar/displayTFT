import time
from PIL import Image

class PageManager:
    def __init__(self, pages, display):
        self.pages = pages
        self.display = display
        self.current_index = 0
        self.last_switch_time = time.time()
        
        # Estados de transição
        self.is_transitioning = False
        self.transition_start_time = 0
        self.transition_duration = 0.8 # Um pouco mais rápido para fluidez
        self.next_index = 0

    def get_current_page(self):
        if not self.pages: return None
        return self.pages[self.current_index]

    def next_page(self):
        """Prepara o início da transição."""
        if self.is_transitioning: return

        # Encontra próxima página válida
        next_idx = (self.current_index + 1) % len(self.pages)
        start_index = next_idx
        while not self.pages[next_idx].should_show():
            next_idx = (next_idx + 1) % len(self.pages)
            if next_idx == start_index: break
        
        if next_idx == self.current_index:
            self.last_switch_time = time.time()
            return

        self.old_buffer = self.display.buffer.copy()
        self.next_index = next_idx
        self.is_transitioning = True
        self.transition_start_time = time.time()

    def update(self):
        """Apenas gerencia a lógica de tempo e transição de buffers."""
        current_page = self.get_current_page()
        if not current_page: return

        # Troca de página se o tempo acabou
        if not self.is_transitioning:
            if time.time() - self.last_switch_time > current_page.get_duration():
                self.next_page()
        
        # Gerencia o efeito de Fade
        if self.is_transitioning:
            elapsed = time.time() - self.transition_start_time
            progress = elapsed / self.transition_duration
            
            if progress >= 1.0:
                self.is_transitioning = False
                self.current_index = self.next_index
                self.last_switch_time = time.time()
            else:
                # Renderiza a página ATUAL
                self.pages[self.current_index].render()
                old_buffer = self.display.buffer.copy()
                
                # Renderiza a PRÓXIMA página
                self.display.clear()
                self.pages[self.next_index].render()
                new_buffer = self.display.buffer.copy()
                
                # Mistura
                self.display.buffer = Image.blend(old_buffer, new_buffer, progress)

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
        self.transition_duration = 1.0 # Em segundos
        self.old_buffer = None
        self.next_index = 0

    def get_current_page(self):
        if not self.pages: return None
        return self.pages[self.current_index]

    def next_page(self):
        """Prepara o início da transição para a próxima página."""
        if self.is_transitioning: return

        # Encontra a próxima página válida
        next_idx = (self.current_index + 1) % len(self.pages)
        start_index = next_idx
        while not self.pages[next_idx].should_show():
            next_idx = (next_idx + 1) % len(self.pages)
            if next_idx == start_index: break
        
        # Se a próxima página for a mesma que a atual, não faz transição
        if next_idx == self.current_index:
            self.last_switch_time = time.time()
            return

        # Salva o buffer atual como 'antigo'
        self.old_buffer = self.display.buffer.copy()
        self.next_index = next_idx
            
        # Inicia a transição
        self.is_transitioning = True
        self.transition_start_time = time.time()

    def update(self):
        """Orquestra as transições e atualizações de dados."""
        # 1. Atualiza dados de todas as páginas em background
        for page in self.pages:
            page.update()

        current_page = self.get_current_page()
        if not current_page: return

        # 2. Verifica se é hora de trocar (se não estiver em transição)
        if not self.is_transitioning:
            if time.time() - self.last_switch_time > current_page.get_duration():
                self.next_page()
        
        # 3. Gerencia o efeito de Transição (Fade)
        if self.is_transitioning:
            elapsed = time.time() - self.transition_start_time
            progress = elapsed / self.transition_duration
            
            if progress >= 1.0:
                # Transição Finalizada
                self.is_transitioning = False
                self.current_index = self.next_index
                self.last_switch_time = time.time()
                self.old_buffer = None
            else:
                # Renderiza a NOVA página no buffer principal para capturar o frame
                self.pages[self.next_index].render()
                new_buffer = self.display.buffer.copy()
                
                # Mistura os buffers (Pillow blend)
                # progress=0 -> 100% old_buffer
                # progress=1 -> 100% new_buffer
                blended = Image.blend(self.old_buffer, new_buffer, progress)
                self.display.buffer = blended

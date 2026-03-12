import time

class PageManager:
    def __init__(self, pages, display):
        self.pages = pages
        self.display = display
        self.current_index = 0
        self.last_switch_time = time.time()
        self.is_transitioning = False # Mantido apenas para compatibilidade de interface

    def get_current_page(self):
        if not self.pages: return None
        return self.pages[self.current_index]

    def next_page(self):
        """Troca instantaneamente para a próxima página válida."""
        next_idx = (self.current_index + 1) % len(self.pages)
        start_index = next_idx
        while not self.pages[next_idx].should_show():
            next_idx = (next_idx + 1) % len(self.pages)
            if next_idx == start_index: break
        
        self.current_index = next_idx
        self.last_switch_time = time.time()

    def update(self):
        """Gerencia apenas a troca de páginas por tempo."""
        current_page = self.get_current_page()
        if not current_page: return

        # Troca de página se o tempo acabou
        if time.time() - self.last_switch_time > current_page.get_duration():
            self.next_page()
            print(f"Página alterada para: {self.get_current_page().name}")

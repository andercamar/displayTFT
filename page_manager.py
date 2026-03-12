import time

class PageManager:
    def __init__(self, pages):
        self.pages = pages
        self.current_index = 0
        self.last_switch_time = 0

    def get_current_page(self):
        """Retorna a página que deve ser exibida no momento."""
        # Se a lista estiver vazia, retorna None
        if not self.pages:
            return None
            
        page = self.pages[self.current_index]
        
        # Verifica se a página atual deve ser exibida
        # Se não, pula para a próxima
        if not page.should_show():
            self.next_page()
            return self.get_current_page()
            
        return page

    def next_page(self):
        """Avança para a próxima página válida."""
        self.current_index = (self.current_index + 1) % len(self.pages)
        self.last_switch_time = time.time()
        
        # Evita loop infinito se nenhuma página puder ser mostrada
        start_index = self.current_index
        while not self.pages[self.current_index].should_show():
            self.current_index = (self.current_index + 1) % len(self.pages)
            if self.current_index == start_index:
                break

    def update(self):
        """Verifica se é hora de trocar de página."""
        current_page = self.get_current_page()
        if not current_page:
            return

        # Verifica o tempo de exibição da página atual
        if time.time() - self.last_switch_time > current_page.get_duration():
            self.next_page()
            print(f"Trocando para a página: {self.get_current_page().name}")
        
        # Atualiza os dados de todas as páginas (background)
        # Nota: Você pode otimizar para atualizar apenas a atual, 
        # mas algumas precisam atualizar em background (como clima)
        for page in self.pages:
            page.update()

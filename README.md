# 📟 Smart IoT Dashboard (ST7735)

Um dashboard modular e elegante para displays TFT ST7735 (128x160), projetado para rodar em Raspberry Pi. Monitore seu tempo, clima, música e impressões 3D em um único lugar.

## ✨ Funcionalidades

- 🕒 **Relógio Inteligente**: Hora, data e dia da semana com fontes grandes para fácil leitura.
- 🌤️ **Clima Dinâmico**: Integração com OpenWeather. As cores do display mudam conforme a temperatura (Azul para frio, Laranja para calor).
- 🎵 **Spotify Sync**: Exibe a música e o artista que você está ouvindo no momento, com barra de progresso em tempo real.
- 🖨️ **3D Printer Monitor**: Suporte nativo para **Klipper/Moonraker** (testado na **Creality K1 Max**). Mostra progresso (%) e tempo restante estimado.
- 🖥️ **Modo Simulador**: Desenvolva no seu PC sem hardware! O sistema detecta a ausência do display e salva "screenshots" do que seria exibido em uma pasta de debug.

## 🚀 Estrutura do Projeto

O código foi refatorado seguindo as melhores práticas de engenharia de software:

- `main.py`: Coordena o loop principal e a lógica de UI.
- `display_driver.py`: Abstração do hardware (TFT vs Simulador).
- `services.py`: Integrações de API (Weather, Spotify, Moonraker).
- `app_config.py`: Gestão centralizada de configurações e variáveis de ambiente.

## 🛠️ Instalação

1. Clone o repositório:
   ```bash
   git clone <seu-repositorio>
   cd displayTFT
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas chaves de API e IPs
   ```

## ⚙️ Configuração (.env)

| Variável | Descrição |
|----------|-----------|
| `OPENWEATHER_API_KEY` | Sua chave da API OpenWeather |
| `LAT` / `LONG` | Suas coordenadas para o clima |
| `SPOTIFY_TOKEN` | Token de acesso da API do Spotify |
| `PRINTER_URL` | IP da sua impressora K1 Max (ex: http://192.168.1.50) |
| `DEBUG_MODE` | Defina como `True` para testar no PC |

## 🧪 Testando sem Hardware

Se você estiver no Windows, Linux (Desktop) ou Mac, defina `DEBUG_MODE=True` no `.env`. O script irá criar uma pasta chamada `debug_frames/` e atualizará o arquivo `current_frame.png` a cada segundo. Basta deixar essa imagem aberta no seu visualizador de fotos para ver o dashboard em tempo real!

---
*Projeto original modernizado e expandido.*

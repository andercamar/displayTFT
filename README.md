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

2. Crie e ative um ambiente virtual (Obrigatório em Linux modernos):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
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

### 🔑 Como Obter as Chaves

#### 1. OpenWeather (Clima)
1. Acesse [OpenWeatherMap](https://home.openweathermap.org/api_keys).
2. Crie uma conta gratuita.
3. Vá em "API Keys" e gere uma nova chave. (Pode levar alguns minutos para ativar).
4. Para **LAT** e **LONG**, abra o Google Maps, clique no seu local e copie as coordenadas da URL ou do rodapé.

#### 2. Spotify (Automação 24h)
O dashboard renova o acesso automaticamente sem precisar de intervenção manual.

1. Acesse o [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. Crie um "App" (ex: MyDashboard).
3. Clique em **"Edit Settings"** e adicione em "Redirect URIs": `http://localhost:8888/callback`. **Salve**.
4. Copie o `Client ID` e o `Client Secret` para o seu `.env`.
5. Execute o script utilitário no seu PC:
   ```bash
   python get_refresh_token.py
   ```
6. Siga as instruções no terminal para gerar o seu `SPOTIFY_REFRESH_TOKEN` e cole no `.env`.

#### 3. Creality K1 Max (Impressora 3D)
1. **IP**: No painel da impressora, vá em Configurações > Rede e anote o IP.
2. **API Key**: Se você usa o Moonraker (Fluidd/Mainsail), geralmente **não é necessário** chave para rede local. Basta preencher o `PRINTER_URL` com `http://SEU_IP`.
3. Certifique-se de que a impressora está com o "Root" ativo e o script de melhorias instalado (como o do Guilouz) para liberar o acesso total à API.

## 🧪 Testando sem Hardware

Se você estiver no Windows, Linux (Desktop) ou Mac, defina `DEBUG_MODE=True` no `.env`. O script irá criar uma pasta chamada `debug_frames/` e atualizará o arquivo `current_frame.png` a cada segundo. Basta deixar essa imagem aberta no seu visualizador de fotos para ver o dashboard em tempo real!

---
*Projeto original modernizado e expandido.*

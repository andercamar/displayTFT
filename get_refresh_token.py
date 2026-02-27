import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

# Instruções:
# 1. Vá em https://developer.spotify.com/dashboard/applications
# 2. Selecione seu App e clique em "Edit Settings"
# 3. Adicione http://localhost:8888/callback em "Redirect URIs" e salve.

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "user-read-currently-playing user-read-playback-state"

def get_auth_url():
    auth_url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}"
    print(f"""
1. Acesse este link no navegador:
{auth_url}""")

def get_tokens(code):
    url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    response = requests.post(url, data=payload, headers=headers)
    return response.json()

if __name__ == "__main__":
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Erro: Preencha SPOTIFY_CLIENT_ID e SPOTIFY_CLIENT_SECRET no seu .env primeiro!")
    else:
        get_auth_url()
        code = input("""
2. Depois de autorizar, você será redirecionado para uma página (que pode dar erro, não importa).
Cole aqui o valor do parâmetro 'code=' da URL da barra de endereços: """)
        
        tokens = get_tokens(code)
        if 'refresh_token' in tokens:
            print("""
✅ SUCESSO!""")
            print(f"Cole esta linha no seu arquivo .env: ")
            print(f"SPOTIFY_REFRESH_TOKEN={tokens['refresh_token']}")
        else:
            print(f"""
❌ ERRO ao obter tokens: {tokens}""")

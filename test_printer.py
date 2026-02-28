
import requests
import json
from app_config import Config
from services import PrinterService

def test_connection():
    print(f"--- Testando Conexão com Impressora ---")
    print(f"URL Configurada: {Config.PRINTER_URL}")
    
    # Teste 1: Ping Simples
    try:
        print("""
1. Tentando ping no endpoint do Moonraker...""")
        response = requests.get(f"{Config.PRINTER_URL}/printer/info", timeout=5)
        if response.status_code == 200:
            print("✅ Conexão básica estabelecida!")
            print(f"Informações da Impressora: {json.dumps(response.json()['result'], indent=2)}")
        else:
            print(f"❌ Erro: Status Code {response.status_code}")
    except Exception as e:
        print(f"❌ Falha na conexão básica: {e}")

    # Teste 2: Usando o PrinterService (Lógica do App)
    print("""
2. Testando lógica do PrinterService.get_status()...""")
    service = PrinterService()
    status = service.get_status()
    
    if status:
        print("✅ Dados processados com sucesso!")
        print(f"Estado: {status['state']}")
        print(f"Progresso: {status['progress']*100:.2f}%")
        print(f"Tempo Restante: {status['time_left']}")
    else:
        print("⚠️ A impressora está online, mas parece estar em Standby (não está imprimindo).")
        print("O método get_status() retorna None quando não há impressão ativa.")

if __name__ == "__main__":
    test_connection()

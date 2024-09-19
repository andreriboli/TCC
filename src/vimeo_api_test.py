import requests
from config import Config

# Inicializar a configuração
config = Config()

# URL do endpoint
url = f"{config.get_vimeo_config()['url']}/me"

# Cabeçalhos da requisição, incluindo o Bearer Token
headers = {
    "Authorization": f"Bearer {config.get_vimeo_config()['token']}"
}

# Fazendo a requisição GET para a API do Vimeo
response = requests.get(url, headers=headers, verify=False)

# Verificando o status da resposta
if response.status_code == 200:
    print("Sucesso! Dados recebidos:")
    print(response.json())
else:
    print(f"Falha na requisição. Status code: {response.status_code}")
    print(response.text)

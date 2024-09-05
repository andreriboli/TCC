import requests
from config import Config

def coletar_todos_os_cursos(config):
    url = f"{config.MOODLE_URL}wstoken={config.MOODLE_TOKEN}&wsfunction=core_course_get_courses&moodlewsrestformat=json"
    
    print(f"URL para coletar todos os cursos: {url}")  # Log da URL
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta um erro se o status não for 200 OK
        print(f"Status Code: {response.status_code}")  # Log do status da resposta
        
        cursos = response.json()
        print(f"Resposta da API: {cursos}")  # Log do conteúdo da resposta
        
        return cursos

    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP ao fazer a solicitação à API do Moodle: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Erro ao fazer a solicitação à API do Moodle: {req_err}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

    return None

def coletar_usuarios_do_curso(config, curso_id):
    url = f"{config.MOODLE_URL}wstoken={config.MOODLE_TOKEN}&wsfunction=core_enrol_get_enrolled_users&moodlewsrestformat=json&courseid={curso_id}"
    
    print(f"URL para coletar usuários do curso {curso_id}: {url}")  # Log da URL
    response = requests.get(url)
    
    if response.status_code == 200:
        try:
            usuarios = response.json()
            return usuarios
        except ValueError:
            print("Erro ao converter resposta da API para JSON")
    else:
        print(f"Erro na API do Moodle: {response.json().get('message', 'Erro desconhecido')}")
    
    return []

def buscar_curso_por_id(config, id_curso):
    url = f"{config.MOODLE_URL}wstoken={config.MOODLE_TOKEN}&wsfunction=core_course_get_courses&moodlewsrestformat=json&options[ids][0]={id_curso}"
    
    print(f"URL para buscar curso por ID {id_curso}: {url}")  # Log da URL
    response = requests.get(url)
    
    if response.status_code == 200:
        try:
            cursos = response.json()
            if cursos:
                return cursos[0]  # Retorna o primeiro curso encontrado
            else:
                print(f"Curso com ID {id_curso} não encontrado.")
                return None
        except ValueError:
            print("Erro ao converter resposta da API para JSON")
    else:
        print(f"Erro na API do Moodle: {response.json().get('message', 'Erro desconhecido')}")
    
    return None

def processar_dados_usuario(dados_usuario):
    # Processar e extrair as informações necessárias do JSON de resposta
    cursos_detalhes = []
    for curso in dados_usuario.get('cursos', []):
        curso_detalhe = {
            'id_curso': curso.get('id'),
            'curso': curso.get('fullname'),
            'progresso': curso.get('progress', 0),
            'completado': curso.get('completed', False),
            'data_primeiro_acesso': curso.get('startdate'),
            'data_ultimo_acesso': curso.get('lastaccess'),
            'tempo_medio_conclusao': curso.get('tempo_medio_conclusao', None),
            'arquivos': curso.get('overviewfiles', [])
        }
        cursos_detalhes.append(curso_detalhe)

    # Exibindo dados do usuário para debug
    print(f"Processando dados do usuário: {dados_usuario}")
    
    return {
        'email': dados_usuario.get('email', 'email@desconhecido.com'),
        'nome': dados_usuario.get('fullname', 'Nome Desconhecido'),
        'data_registro': dados_usuario.get('firstaccess', None),
        'ultimo_acesso': dados_usuario.get('lastaccess', None),
        'total_cursos': len(cursos_detalhes),
        'cursos_completados': sum(1 for curso in cursos_detalhes if curso['completado']),
        'media_progresso': sum(curso['progresso'] for curso in cursos_detalhes) / len(cursos_detalhes) if cursos_detalhes else 0,
        'cursos_detalhes': cursos_detalhes
    }
def coletar_cursos_usuario(user_id):
    url = f"https://e-learning-cco.unoesc.edu.br/moodle/webservice/rest/server.php"
    params = {
        'wstoken': '3a8281cc9763e6c73e3082d817d2218c',
        'wsfunction': 'core_enrol_get_users_courses',
        'moodlewsrestformat': 'json',
        'userid': user_id
    }
    response = requests.get(url, params=params)
    cursos = response.json()
    return cursos

def buscar_curso_por_id(config, id_curso):
    url = f"{config.MOODLE_URL}wstoken={config.MOODLE_TOKEN}&wsfunction=core_course_get_courses&moodlewsrestformat=json&options[ids][0]={id_curso}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        cursos = response.json()
        
        if cursos:
            return cursos[0]
        else:
            print(f"Curso com id {id_curso} não encontrado.")
            return None
            
    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP ao fazer a solicitação à API do Moodle: {http_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Erro ao fazer a solicitação à API do Moodle: {req_err}")
        return None
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return None

import requests
from config import Config

def coletar_todos_os_cursos(config):
    url = f"{config.MOODLE_URL}wstoken={config.MOODLE_TOKEN}&wsfunction=core_course_get_courses&moodlewsrestformat=json"
    
    # print(f"URL para coletar todos os cursos: {url}")
    
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        # print(f"Status Code: {response.status_code}")

        cursos = response.json()
        return cursos

    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP ao fazer a solicitação à API do Moodle: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Erro ao fazer a solicitação à API do Moodle: {req_err}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

    return None

def coletar_detalhes_usuario_do_curso(config, curso_id, moodle_id):
    url = f"{config.MOODLE_URL}wstoken={config.MOODLE_TOKEN}&wsfunction=core_enrol_get_users_courses&moodlewsrestformat=json&userid={moodle_id}"
    
    # print(f"URL para coletar detalhes de inscrição do usuário {moodle_id} no curso {curso_id}: {url}")
    response = requests.get(url, verify=False)
    
    if response.status_code == 200:
        try:
            cursos = response.json()
            for curso in cursos:
                if curso['id'] == curso_id:
                    return curso
        except ValueError:
            print("Erro ao converter resposta da API para JSON")
    # else:
    #     print(f"Erro na API do Moodle: {response.json().get('message', 'Erro desconhecido')}")
    
    return None


def coletar_atividades_concluidas_do_usuario(config, course_id, user_id):
    url = f"{config.MOODLE_URL}wstoken={config.MOODLE_TOKEN}&wsfunction=core_completion_get_activities_completion_status&moodlewsrestformat=json&courseid={course_id}&userid={user_id}"
    
    # print(f"URL para coletar atividades concluídas do usuário {user_id} no curso {course_id}: {url}")
    response = requests.get(url, verify=False)
    
    if response.status_code == 200:
        try:
            atividades = response.json().get('statuses', [])
            # print(f"Atividades coletadas para o usuário {user_id} no curso {course_id}: {atividades}")
            return atividades
        except ValueError:
            print("Erro ao converter a resposta da API para JSON")
    else:
        print(f"Erro na API do Moodle: {response.json().get('message', 'Erro desconhecido')}")

    return []

def coletar_usuarios_do_curso(config, curso_id):
    url = f"{config.MOODLE_URL}wstoken={config.MOODLE_TOKEN}&wsfunction=core_enrol_get_enrolled_users&moodlewsrestformat=json&courseid={curso_id}"
    
    # print(f"URL para coletar usuários do curso {curso_id}: {url}")
    response = requests.get(url, verify=False)
    
    if response.status_code == 200:
        try:
            usuarios = response.json()
            # print (usuarios[1])
            return usuarios
        except ValueError:
            print("Erro ao converter resposta da API para JSON")
    else:
        print(f"Erro na API do Moodle: {response.json().get('message', 'Erro desconhecido')}")
    
    return []

def buscar_curso_por_id(config, id_curso):
    url = f"{config.MOODLE_URL}wstoken={config.MOODLE_TOKEN}&wsfunction=core_course_get_courses&moodlewsrestformat=json&options[ids][0]={id_curso}"
    
    # print(f"URL para buscar curso por ID {id_curso}: {url}")
    response = requests.get(url, verify=False)
    
    if response.status_code == 200:
        try:
            cursos = response.json()
            if cursos:
                return cursos[0]
            else:
                # print(f"Curso com ID {id_curso} não encontrado.")
                return None
        except ValueError:
            print("Erro ao converter resposta da API para JSON")
    else:
        print(f"Erro na API do Moodle: {response.json().get('message', 'Erro desconhecido')}")
    
    return None

def processar_dados_usuario(dados_usuario):
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

    # print(f"Processando dados do usuário: {dados_usuario}")
    
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
    response = requests.get(url, params=params, verify=False)
    cursos = response.json()
    return cursos

def buscar_curso_por_id(config, id_curso):
    url = f"{config.MOODLE_URL}wstoken={config.MOODLE_TOKEN}&wsfunction=core_course_get_courses&moodlewsrestformat=json&options[ids][0]={id_curso}"
    
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        cursos = response.json()
        
        if cursos:
            return cursos[0]
        else:
            # print(f"Curso com id {id_curso} não encontrado.")
            return None
            
    except requests.exceptions.HTTPError as http_err:
        # print(f"Erro HTTP ao fazer a solicitação à API do Moodle: {http_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        # print(f"Erro ao fazer a solicitação à API do Moodle: {req_err}")
        return None
    except Exception as e:
        # print(f"Erro inesperado: {e}")
        return None
    
def coletar_atividades_do_curso(config, curso_id):
    url = f"{config.MOODLE_URL}wstoken={config.MOODLE_TOKEN}&wsfunction=core_course_get_contents&moodlewsrestformat=json&courseid={curso_id}"

    # print(f"URL para coletar atividades do curso {curso_id}: {url}")
    response = requests.get(url, verify=False)
    
    if response.status_code == 200:
        try:
            atividades = response.json()
            return atividades
        except ValueError:
            print("Erro ao converter resposta da API para JSON")
    else:
        print(f"Erro na API do Moodle: {response.json().get('message', 'Erro desconhecido')}")
    
    return []

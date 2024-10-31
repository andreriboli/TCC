import threading
import time
from datetime import datetime, timedelta

import pandas as pd
from api import start_api
from data_collection import coletar_atividades_concluidas_do_usuario, coletar_detalhes_usuario_do_curso, coletar_todos_os_cursos, coletar_usuarios_do_curso, coletar_atividades_do_curso
from database import DatabaseOperations
from db_util import DBUtil
from config import Config
from scrap_vimeo import VimeoScraper

def executar_coleta_diaria(config, db_util):

    try:
        db_util.connect()

        database_operations = DatabaseOperations(db_util, config)

        now = datetime.now()

        cursos = coletar_todos_os_cursos(config)
        if cursos:
            inserir_categorias(cursos, database_operations)
            inserir_usuarios_e_inscricoes(cursos, database_operations, config)

    except Exception as e:
        print(f"Erro durante a coleta de dados: {e}")
    finally:
        db_util.disconnect()

def inserir_categorias(cursos, database_operations):
    for curso in cursos:
        id_categoria = curso['categoryid']
        database_operations.inserir_categoria_por_id(id_categoria)

def inserir_cursos(cursos, database_operations):
    for curso in cursos:
        database_operations.inserir_curso(curso)

def inserir_usuarios_e_inscricoes(cursos, database_operations, config):
    for curso in cursos:
        if curso['id'] == 1:
            continue

        usuarios = coletar_usuarios_do_curso(config, curso['id'])
        if usuarios:
            for usuario in usuarios:
                if usuario['id'] == 1 or usuario['username'] == 'guest':
                    continue

                moodle_id = usuario['id']

                is_teacher = False
                for role in usuario['roles']:
                    if role['shortname'] in ['editingteacher', 'teacher']:
                        is_teacher = True
                        break

                if is_teacher:
                    database_operations.inserir_professor(moodle_id, curso['id'])

                    atividades = coletar_atividades_do_curso(config, curso['id'])
                    if atividades:
                        for atividade in atividades:
                            database_operations.inserir_atividade(moodle_id, curso['id'], atividade)

                detalhes_usuario = coletar_detalhes_usuario_do_curso(config, curso['id'], moodle_id)
                
                progresso = detalhes_usuario.get('progress') if detalhes_usuario else 0
                primeiro_acesso = usuario.get('firstaccess', 0)
                ultimo_acesso = usuario.get('lastaccess', 0)

                data_primeiro_acesso = datetime.fromtimestamp(primeiro_acesso) if primeiro_acesso > 0 else None
                data_ultimo_acesso = datetime.fromtimestamp(ultimo_acesso) if ultimo_acesso > 0 else None

                tempo_medio_conclusao = None

                if data_primeiro_acesso and data_ultimo_acesso:
                    tempo_medio_conclusao = data_ultimo_acesso - data_primeiro_acesso
                else:
                    tempo_medio_conclusao = timedelta(0)

                database_operations.inserir_usuario(usuario)

                if detalhes_usuario is None:
                    continue

                database_operations.inserir_inscricao(
                    moodle_id=moodle_id,
                    curso_id=curso['id'],
                    progresso=progresso,
                    detalhes_usuario=detalhes_usuario,
                    usuario=usuario
                )

                atividades_concluidas = coletar_atividades_concluidas_do_usuario(config, curso['id'], moodle_id)
                if atividades_concluidas:
                    for atividade in atividades_concluidas:
                        database_operations.inserir_atividade_concluida(moodle_id, curso['id'], atividade)

def coleta_vimeo(config, db_util):
    
    database_operations = DatabaseOperations(db_util, config)
    file_path = r"C:\Desenvolvimento\stats_export (2).csv"
    df = pd.read_csv(file_path, skip_blank_lines=True)

    if df.iloc[-1].isnull().all() or df.iloc[-1].str.contains(r'["]').any():
        df = df[:-1]

    df.rename(columns={
        'views': 'views',
        'impressions': 'impressions',
        'finishes': 'finishes',
        'downloads': 'downloads',
        'unique_impressions': 'unique_impressions',
        'unique_viewers': 'unique_viewers',
        'mean_percent_watched': 'mean_percent_watched',
        'mean_seconds_watched': 'mean_seconds_watched',
        'total_seconds_watched': 'total_seconds_watched',
        'metadata.connections.video.uri': 'id_vimeo_video',
        'metadata.connections.video.title': 'title',
        'metadata.connections.video.created_time': 'created_time',
        'metadata.connections.video.likes': 'likes',
        'metadata.connections.video.comments': 'comments'
    }, inplace=True)

    for index, row in df.iterrows():
        database_operations.inserir_dados_vimeo(row)

    try:
        db_util.connect()
        database_operations.salvar_dados_vimeo(df)

    except Exception as e:
        print("Erro durante a inserção dos dados no banco: {e}")

    finally:
        db_util.disconnect()


def start_api_in_thread(database_operations):
    start_api(database_operations)

def start_all_threads(config):
    config = Config()

    db_util_coleta = DBUtil(config.get_db_config())
    db_util_api = DBUtil(config.get_db_config())
    db_util_vimeo = DBUtil(config.get_db_config())

    def start_api():
        database_operations_api = DatabaseOperations(db_util_api, config)
        api_thread = threading.Thread(target=start_api_in_thread, args=(database_operations_api,))
        api_thread.start()
        return api_thread

    def start_coleta_moodle():
        database_operations_coleta = DatabaseOperations(db_util_coleta, config)
        coleta_thread = threading.Thread(target=executar_coleta_diaria, args=(config, db_util_coleta))
        coleta_thread.start()
        return coleta_thread

    def start_coleta_vimeo():
        database_operations_vimeo = DatabaseOperations(db_util_vimeo, config)
        vimeo_thread = threading.Thread(target=coleta_vimeo, args=(config, db_util_vimeo))
        vimeo_thread.start()
        return vimeo_thread

    start_api()

    while True:
        target_time = datetime.now().replace(hour=00, minute=00, second=1, microsecond=0)
        
        if datetime.now() > target_time:
            target_time += timedelta(days=1)

        sleep_duration = (target_time - datetime.now()).total_seconds()
        print(f"Aguardando até o próximo horário de coleta às 19:35. Tempo restante: {sleep_duration/60:.2f} minutos.")
        time.sleep(sleep_duration)

        start_time = datetime.now()
        print(f"Início da coleta: {start_time}")

        coleta_thread = start_coleta_moodle()
        vimeo_thread = start_coleta_vimeo()

        coleta_thread.join()
        vimeo_thread.join()

        end_time = datetime.now()
        print(f"Término da coleta: {end_time}")

if __name__ == "__main__":
    config = Config()
    start_all_threads(config)
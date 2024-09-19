from datetime import datetime, timedelta
import logging
import requests
import urllib3
from db_util import DBUtil
from data_collection import coletar_cursos_usuario, buscar_curso_por_id, coletar_usuarios_do_curso
from config import Config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DatabaseOperations:
    def __init__(self, db_util, config):
        self.db_util = db_util
        self.config = config

    def inserir_usuario(self, dados_usuario):
        query = """
        INSERT INTO usuarios (
            moodle_id, username, nome
        ) VALUES (
            %s, %s, %s
        )
        ON CONFLICT (moodle_id) DO UPDATE
        SET 
            username = EXCLUDED.username,
            nome = EXCLUDED.nome;
        """
        
        params = (
            dados_usuario['id'],  # moodle_id
            dados_usuario['username'],  # username
            dados_usuario['fullname']  # nome (antigo fullname)
        )
        
        print(f"Parâmetros fornecidos para inserção de usuário: {params}")
        self.db_util.execute_query(query, params)

    def inserir_curso(self, curso):
        try:
            # Exibindo o curso para verificar a estrutura antes de tentar acessar 'categoryid'
            print(f"Curso retornado da API: {curso}")

            # Obter a categoria do curso
            id_categoria = curso.get('categoryid')  # Corrigido para 'categoryid'

            if id_categoria is None:
                print(f"Categoria não encontrada para o curso com ID {curso['id']}. Pulando inserção.")
                logging.error(f"Categoria não encontrada para o curso com ID {curso['id']}.")
                return  # Pular a inserção deste curso
            
            # Verificar se o curso já existe no banco
            if not self.curso_existe(curso['id']):
                print(f"Curso com ID {curso['id']} não encontrado no banco. Inserindo agora.")
                
                # Inserir a categoria, se necessário
                id_categoria = self.inserir_categoria_por_id(id_categoria)

                # Inserir o curso no banco de dados
                query = """
                INSERT INTO cursos (id_curso, nome_curso, id_categoria, data_inicio, data_fim)
                VALUES (%s, %s, %s, to_timestamp(%s), to_timestamp(%s))
                ON CONFLICT (id_curso) DO UPDATE
                SET id_categoria = EXCLUDED.id_categoria,
                    data_inicio = EXCLUDED.data_inicio,
                    data_fim = EXCLUDED.data_fim;
                """
                
                params = (
                    curso['id'],  # id_curso
                    curso['fullname'],  # nome_curso
                    id_categoria,  # id_categoria
                    curso.get('startdate', 0),  # data_inicio
                    curso.get('enddate', 0)  # data_fim
                )

                print(f"Parâmetros fornecidos para inserção de curso: {params}")
                with self.db_util.conn.cursor() as cursor:
                    cursor.execute(query, params)
                self.db_util.conn.commit()  # Confirmar a transação

                print(f"Curso com ID {curso['id']} inserido com sucesso.")

            else:
                print(f"Curso com ID {curso['id']} já existe no banco.")

            # **Mesmo que o curso já exista, continuamos a processar os usuários e inscrições**
            print(f"Iniciando a inserção de usuários e inscrições para o curso {curso['fullname']}")
            
            config = Config()
            # Certifique-se de que está passando o curso['id'] corretamente para coletar os usuários
            usuarios = coletar_usuarios_do_curso(config, curso['id'])  # Passando o curso['id'] como argumento

            if usuarios:
                for usuario in usuarios:
                    self.inserir_usuario(usuario)
                    logging.info(f"Usuário {usuario['fullname']} inserido para o curso {curso['fullname']}.")
                    self.inserir_inscricao(usuario['id'], curso)
                    logging.info(f"Inscrição do usuário {usuario['fullname']} inserida no curso {curso['fullname']}.")
            else:
                logging.warning(f"Nenhum usuário encontrado para o curso {curso['fullname']}.")

        except Exception as e:
            print(f"Erro ao inserir curso com ID {curso['id']}: {e}")
            logging.error(f"Erro ao inserir curso com ID {curso['id']}: {e}")

    def inserir_inscricao(self, moodle_id, curso_id, progresso, detalhes_usuario):
        try:
            # Verificar se o curso foi completado
            completado = detalhes_usuario.get('completed', False)
            tempo_medio_conclusao = None
            primeiro_acesso = detalhes_usuario.get('startdate', 0)
            ultimo_acesso = detalhes_usuario.get('enddate', 0)

            if completado:
                startdate = detalhes_usuario.get('startdate', 0)
                enddate = detalhes_usuario.get('enddate', 0)

                if enddate != 0:
                    print(enddate)

                if enddate == 0:
                    ultimo_acesso = detalhes_usuario.get('lastaccess', 0)

                if startdate > 0 and enddate > 0:
                    tempo_medio_conclusao = enddate - startdate
                    tempo_medio_conclusao = timedelta(seconds=tempo_medio_conclusao)


            if primeiro_acesso != 0:
                primeiro_acesso = datetime.fromtimestamp(primeiro_acesso)
            else:
                primeiro_acesso = None

            if ultimo_acesso != 0:
                ultimo_acesso = datetime.fromtimestamp(ultimo_acesso)
            else:
                ultimo_acesso = None

            query = """
            INSERT INTO inscricoes (id_usuario, id_curso, progresso, completado, data_primeiro_acesso, data_ultimo_acesso, tempo_medio_conclusao)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id_usuario, id_curso) DO UPDATE
            SET progresso = EXCLUDED.progresso,
                completado = EXCLUDED.completado,
                data_primeiro_acesso = EXCLUDED.data_primeiro_acesso,
                data_ultimo_acesso = EXCLUDED.data_ultimo_acesso,
                tempo_medio_conclusao = EXCLUDED.tempo_medio_conclusao;
            """
            params = (
                moodle_id,
                curso_id,
                progresso,
                completado,
                primeiro_acesso,
                ultimo_acesso,
                tempo_medio_conclusao
            )

            print(f"Parâmetros fornecidos para inserção de inscrição: {params}")
            self.db_util.execute_query(query, params)

        except Exception as e:
            print(f"Erro ao inserir inscrição: {e}")
            logging.error(f"Erro ao inserir inscrição: {e}")

    def inserir_dados_usuario(self, dados_usuarios):
        for dados_usuario in dados_usuarios:
            self.inserir_usuario(dados_usuario)

            user_id = dados_usuario['id']
            cursos = coletar_cursos_usuario(user_id)

            for curso in cursos:
                self.inserir_curso(curso)
                self.inserir_inscricao(dados_usuario['id'], curso)

    def inserir_categoria_por_id(self, id_categoria):
        try:
            query = "SELECT id_categoria FROM categorias WHERE id_categoria = %s;"
            with self.db_util.conn.cursor() as cursor:
                cursor.execute(query, (id_categoria,))
                result = cursor.fetchone()

            if result:
                return result[0]
            else:
                print(f"Categoria com ID {id_categoria} não encontrada no banco. Buscando na API do Moodle.")

                url = f"{self.config.MOODLE_URL}wstoken={self.config.MOODLE_TOKEN}&wsfunction=core_course_get_categories&moodlewsrestformat=json&criteria[0][key]=id&criteria[0][value]={id_categoria}"

                response = requests.get(url, verify=False)
                response.raise_for_status() 

                categorias = response.json()
                if categorias:
                    nome_categoria = categorias[0].get('name', f"Categoria {id_categoria}")

                    insert_query = """
                        INSERT INTO categorias (id_categoria, nome_categoria)
                        VALUES (%s, %s)
                        ON CONFLICT (id_categoria) DO NOTHING
                        RETURNING id_categoria;
                    """
                    with self.db_util.conn.cursor() as cursor:
                        cursor.execute(insert_query, (id_categoria, nome_categoria))
                        result = cursor.fetchone()

                    if result:
                        self.db_util.conn.commit()
                        print(f"Categoria com ID {id_categoria} inserida com sucesso.")
                        return result[0]
                    else:
                        print(f"Falha ao inserir a nova categoria com ID {id_categoria}")
                        return None
                else:
                    print(f"Categoria com ID {id_categoria} não encontrada na API.")
                    logging.error(f"Categoria com ID {id_categoria} não encontrada na API.")
                    return None

        except requests.exceptions.HTTPError as http_err:
            print(f"Erro HTTP ao fazer a solicitação à API do Moodle: {http_err}")
            logging.error(f"Erro HTTP ao fazer a solicitação à API do Moodle para a categoria {id_categoria}: {http_err}")
            return None
        except requests.exceptions.RequestException as req_err:
            print(f"Erro ao fazer a solicitação à API do Moodle: {req_err}")
            logging.error(f"Erro ao fazer a solicitação à API do Moodle para a categoria {id_categoria}: {req_err}")
            return None
        except Exception as e:
            print(f"Erro inesperado ao buscar ou inserir a categoria: {e}")
            logging.error(f"Erro inesperado ao buscar ou inserir a categoria {id_categoria}: {e}")
        return None

    
    def coletar_curso_por_id(self, curso_id):
        url = f"{self.config.MOODLE_URL}"
        params = {
            'wstoken': self.config.MOODLE_TOKEN,
            'wsfunction': 'core_course_get_courses',
            'moodlewsrestformat': 'json',
            'options[ids][0]': curso_id
        }
        
        response = requests.get(url, params=params, verify=False)

        if response.status_code == 200:
            cursos = response.json()
            if cursos:
                return cursos[0]
            else:
                print(f"Curso com id {curso_id} não encontrado na resposta.")
                return None
        else:
            print(f"Erro ao consultar a API do Moodle. Status code: {response.status_code}")
            return None

    def curso_existe(self, id_curso):
        query = "SELECT 1 FROM cursos WHERE id_curso = %s;"
        
        try:
            with self.db_util.conn.cursor() as cursor:
                cursor.execute(query, (id_curso,))
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            print(f"Erro ao verificar a existência do curso: {e}")
            return False


    def inserir_dados_vimeo(self, views, impressions, finishes, downloads, unique_impressions,
                            unique_viewers, mean_percent_watched, mean_seconds_watched,
                            total_seconds_watched, video_uri, video_title, video_created_time,
                            likes, comments):
        try:
            query = """
            INSERT INTO vimeo_videos (
                views, impressions, finishes, downloads, unique_impressions, unique_viewers,
                mean_percent_watched, mean_seconds_watched, total_seconds_watched,
                id_vimeo_video, video_title, video_created_time, likes, comments
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, to_timestamp(%s, 'YYYY-MM-DD"T"HH24:MI:SS"Z"'), %s, %s)
            ON CONFLICT (id_vimeo_video) DO UPDATE
            SET 
                views = EXCLUDED.views,
                impressions = EXCLUDED.impressions,
                finishes = EXCLUDED.finishes,
                downloads = EXCLUDED.downloads,
                unique_impressions = EXCLUDED.unique_impressions,
                unique_viewers = EXCLUDED.unique_viewers,
                mean_percent_watched = EXCLUDED.mean_percent_watched,
                mean_seconds_watched = EXCLUDED.mean_seconds_watched,
                total_seconds_watched = EXCLUDED.total_seconds_watched,
                video_title = EXCLUDED.video_title,
                video_created_time = EXCLUDED.video_created_time,
                likes = EXCLUDED.likes,
                comments = EXCLUDED.comments;
            """
            params = (
                views, impressions, finishes, downloads, unique_impressions,
                unique_viewers, mean_percent_watched, mean_seconds_watched,
                total_seconds_watched, video_uri, video_title, video_created_time,
                likes, comments
            )
            print(f"Parâmetros fornecidos para inserção de dados Vimeo: {params}")
            self.db_util.execute_query(query, params)
            self.db_util.conn.commit()  # Confirmar a transação

        except Exception as e:
            print(f"Erro ao inserir dados do Vimeo: {e}")
            logging.error(f"Erro ao inserir dados do Vimeo: {e}")

    def salvar_dados_vimeo(self, df):
        try:
            logging.info("Conectado ao banco de dados com sucesso.")
            
            # Iterar sobre as linhas do dataframe e inserir no banco de dados
            for index, row in df.iterrows():
                self.inserir_dados_vimeo(
                    row['views'], row['impressions'], row['finishes'], row['downloads'],
                    row['unique_impressions'], row['unique_viewers'], row['mean_percent_watched'],
                    row['mean_seconds_watched'], row['total_seconds_watched'], row['metadata.connections.video.uri'],
                    row['metadata.connections.video.title'], row['metadata.connections.video.created_time'],
                    row['metadata.connections.video.likes'], row['metadata.connections.video.comments']
                )
            logging.info("Dados do Vimeo inseridos no banco de dados.")
        except Exception as e:
            logging.error(f"Erro ao salvar os dados do Vimeo: {e}")
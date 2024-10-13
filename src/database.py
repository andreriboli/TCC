from datetime import datetime, timedelta
import logging
import pandas as pd
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
            moodle_id, username, nome, firstaccess, lastaccess
        ) VALUES (
            %s, %s, %s, %s, %s
        )
        ON CONFLICT (moodle_id) DO UPDATE
        SET 
            lastaccess = EXCLUDED.lastaccess
        WHERE usuarios.lastaccess IS DISTINCT FROM EXCLUDED.lastaccess;
        """
        
        firstaccess = dados_usuario.get('firstaccess', 0)
        lastaccess = dados_usuario.get('lastaccess', 0)
        
        if firstaccess != 0:
            firstaccess = datetime.fromtimestamp(firstaccess)
        else:
            firstaccess = None

        if lastaccess != 0:
            lastaccess = datetime.fromtimestamp(lastaccess)
        else:
            lastaccess = None

        params = (
            dados_usuario['id'],
            dados_usuario['username'],
            dados_usuario['fullname'],
            firstaccess,
            lastaccess
        )
        
        print(f"Parâmetros fornecidos para inserção de usuário: {params}")
        self.db_util.execute_query(query, params)


    def inserir_curso(self, curso):
        try:
            id_categoria = curso.get('categoryid')
            
            if id_categoria is None:
                return
            
            if not self.curso_existe(curso['id']):
                id_categoria = self.inserir_categoria_por_id(id_categoria)


                query = """
                INSERT INTO cursos (id_curso, nome_curso, id_categoria, data_inicio, data_fim)
                VALUES (%s, %s, %s, to_timestamp(%s), to_timestamp(%s))
                ON CONFLICT (id_curso) DO UPDATE
                SET id_categoria = EXCLUDED.id_categoria,
                    data_inicio = EXCLUDED.data_inicio,
                    data_fim = EXCLUDED.data_fim;
                """
                
                params = (
                    curso['id'],
                    curso['fullname'],
                    id_categoria,
                    curso.get('startdate', 0),
                    curso.get('enddate', 0)
                )

                with self.db_util.conn.cursor() as cursor:
                    cursor.execute(query, params)
                self.db_util.conn.commit()
        except Exception as e:
            logging.error(f"Erro ao inserir curso com ID {curso['id']}: {e}")

    def top_cursos_mais_acessados_semana(self):
        query = """
        SELECT 
            c.id_curso,
            LEFT(UPPER(c.nome_curso), 15) AS nome_curso,
            COUNT(i.id_usuario) AS total_acessos
        FROM 
            cursos c
        INNER JOIN inscricoes i ON c.id_curso = i.id_curso
        WHERE 
            i.data_ultimo_acesso BETWEEN NOW() - INTERVAL '14 days' AND NOW()
        GROUP BY 
            c.id_curso, c.nome_curso
        ORDER BY 
            total_acessos DESC
        LIMIT 10;
        """
        
        try:
            with self.db_util.conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
        except Exception as e:
            print(f"Erro ao obter os cursos mais acessados da semana: {e}")
            return None

    def inserir_inscricao(self, moodle_id, curso_id, progresso, detalhes_usuario, usuario):
        try:
            
            if moodle_id == 274 :
                print("teste")
            completado = detalhes_usuario.get('completed', False)
            tempo_medio_conclusao = None
            primeiro_acesso = detalhes_usuario.get('startdate', 0)
            ultimo_acesso = detalhes_usuario.get('lastaccess', 0)

            if completado:
                startdate = detalhes_usuario.get('startdate', 0)
                enddate = detalhes_usuario.get('enddate', 0)

                if enddate == 0:
                    ultimo_acesso = detalhes_usuario.get('lastaccess', 0)

                if startdate > 0 and enddate > 0:
                    tempo_medio_conclusao = enddate - startdate
                    tempo_medio_conclusao = timedelta(seconds=tempo_medio_conclusao)


            if primeiro_acesso != 0:
                primeiro_acesso = datetime.fromtimestamp(primeiro_acesso)
            else:
                primeiro_acesso = None

            if ultimo_acesso != 0 and ultimo_acesso is not None:
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

    def inserir_categoria_por_id(self, id_categoria):
        try:
            query = "SELECT id_categoria FROM categorias WHERE id_categoria = %s;"
            with self.db_util.conn.cursor() as cursor:
                cursor.execute(query, (id_categoria,))
                result = cursor.fetchone()

            if result:
                return result[0]
            else:
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
                        return result[0]
                    else:
                        return None
                else:
                    return None

        except requests.exceptions.HTTPError as http_err:
            return None
        except requests.exceptions.RequestException as req_err:
            return None
        except Exception as e:
            logging.error(f"Erro inesperado ao buscar ou inserir a categoria {id_categoria}: {e}")
        return None
    
    def distribuicao_cursos_ativos(self):
        query = """
        SELECT 
            c.id_curso,
            LEFT(UPPER(c.nome_curso), 18) AS nome_curso,
            COUNT(i.id_usuario) AS total_alunos
        FROM 
            cursos c
        INNER JOIN 
            inscricoes i ON c.id_curso = i.id_curso
        GROUP BY 
            c.id_curso, c.nome_curso
        ORDER BY 
            total_alunos DESC
        LIMIT 10;
        """
        
        try:
            with self.db_util.conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()

                cursos_ativos = []
                for row in result:
                    curso = {
                        "id_curso": row[0],
                        "nome_curso": row[1],
                        "total_alunos": row[2]
                    }
                    cursos_ativos.append(curso)

                return cursos_ativos
        except Exception as e:
            print(f"Erro ao obter a distribuição de alunos por curso: {e}")
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
                return None
        else:
            return None

    def curso_existe(self, id_curso):
        query = "SELECT 1 FROM cursos WHERE id_curso = %s;"
        
        try:
            with self.db_util.conn.cursor() as cursor:
                cursor.execute(query, (id_curso,))
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            return False
        
    def ultimos_usuarios_logados(self, start_date, end_date):
        query = """
            WITH date_series AS (
                SELECT generate_series(
                    TO_DATE(%s, 'YYYY-MM-DD'),
                    TO_DATE(%s, 'YYYY-MM-DD'),
                    '1 day'::interval
                )::date AS data_login
            )
            SELECT
                date_series.data_login,
                COALESCE(COUNT(u.id_usuario), 0) AS quantidade_usuarios
            FROM
                date_series
            LEFT JOIN usuarios u ON TO_CHAR(u.lastaccess, 'YYYY-MM-DD') = TO_CHAR(date_series.data_login, 'YYYY-MM-DD')
            AND u.lastaccess BETWEEN TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS')
            AND TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS')
            GROUP BY
                date_series.data_login
            ORDER BY
                date_series.data_login;
        """
        
        try:
            with self.db_util.conn.cursor() as cursor:
                cursor.execute(query, (start_date, end_date, start_date + ' 00:00:00', end_date + ' 23:59:59'))
                result = cursor.fetchall()
                return result
        except Exception as e:
            print(f"Erro ao obter os últimos usuários logados: {e}")
            return None
        
    def distribuicao_cursos_ativos_by_category(self, end_date):
        query = """
        SELECT 
            c2.id_categoria,
            c2.nome_categoria,
            COUNT(i.id_usuario) AS total_usuarios
        FROM 
            cursos c
        INNER JOIN inscricoes i ON c.id_curso = i.id_curso
        INNER JOIN categorias c2 ON c2.id_categoria = c.id_categoria
        WHERE 
            i.data_primeiro_acesso < %s
        GROUP BY 
            c2.id_categoria,
            c2.nome_categoria
        ORDER BY 
            total_usuarios DESC;
        """
        
        try:
            with self.db_util.conn.cursor() as cursor:
                cursor.execute(query, (end_date,))
                result = cursor.fetchall()
                return result
        except Exception as e:
            print(f"Erro ao obter as categorias: {e}")
            return None

    def inserir_dados_vimeo(self, data_row):
        try:
            query = """
            INSERT INTO video_analytics (
                id_vimeo_video, title, created_time, views, impressions, finishes, downloads, 
                unique_impressions, unique_viewers, mean_percent_watched, mean_seconds_watched, 
                total_seconds_watched, likes, comments
            ) VALUES (
                %s, %s, to_timestamp(%s, 'YYYY-MM-DD"T"HH24:MI:SS'), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (id) DO UPDATE
            SET views = EXCLUDED.views,
                impressions = EXCLUDED.impressions,
                finishes = EXCLUDED.finishes,
                downloads = EXCLUDED.downloads,
                unique_impressions = EXCLUDED.unique_impressions,
                unique_viewers = EXCLUDED.unique_viewers,
                mean_percent_watched = EXCLUDED.mean_percent_watched,
                mean_seconds_watched = EXCLUDED.mean_seconds_watched,
                total_seconds_watched = EXCLUDED.total_seconds_watched,
                likes = EXCLUDED.likes,
                comments = EXCLUDED.comments;
            """

            id_vimeo_video = data_row['id_vimeo_video'].split('/')[-1]
            params = (
                id_vimeo_video,
                data_row['title'],
                data_row['created_time'].split("+")[0],
                data_row['views'] if not pd.isna(data_row['views']) else 0,
                data_row['impressions'] if not pd.isna(data_row['impressions']) else 0,
                data_row['finishes'] if not pd.isna(data_row['finishes']) else 0,
                data_row['downloads'] if not pd.isna(data_row['downloads']) else 0,
                data_row['unique_impressions'] if not pd.isna(data_row['unique_impressions']) else 0,
                data_row['unique_viewers'] if not pd.isna(data_row['unique_viewers']) else 0,
                data_row['mean_percent_watched'] if not pd.isna(data_row['mean_percent_watched']) else 0,
                data_row['mean_seconds_watched'] if not pd.isna(data_row['mean_seconds_watched']) else 0,
                data_row['total_seconds_watched'] if not pd.isna(data_row['total_seconds_watched']) else 0,
                data_row['likes'] if not pd.isna(data_row['likes']) else 0,
                data_row['comments'] if not pd.isna(data_row['comments']) else 0
            )
            
            self.db_util.execute_query(query, params)

        except Exception as e:
            print(f"Erro ao inserir dados do Vimeo: {e}")


    def salvar_dados_vimeo(self, df): 
        db_util = DBUtil(
            dbname=self.config.DB_NAME,
            user=self.config.DB_USER,
            password=self.config.DB_PASSWORD,
            host=self.config.DB_HOST,
            port=self.config.DB_PORT
        )
    
        try:
            db_util.connect()
            
            for index, row in df.iterrows():
                if pd.isna(row['metadata.connections.video.uri']) or row['metadata.connections.video.uri'].strip() == "":
                    continue

                self.inserir_dados_vimeo(
                    row['views'], row['impressions'], row['finishes'], row['downloads'],
                    row['unique_impressions'], row['unique_viewers'], row['mean_percent_watched'],
                    row['mean_seconds_watched'], row['total_seconds_watched'], 
                    row['metadata.connections.video.uri'], row['metadata.connections.video.title'],
                    row['metadata.connections.video.created_time'], row['metadata.connections.video.likes'],
                    row['metadata.connections.video.comments']
                )
            logging.info("Dados do Vimeo inseridos no banco de dados.")
        except Exception as e:
            logging.error(f"Erro ao salvar os dados do Vimeo: {e}")
        finally:
            db_util.disconnect()
            logging.info("Desconectado do banco de dados.")

    def inserir_atividade_concluida(self, moodle_id, curso_id, atividade):
        try:
            query = """
            INSERT INTO atividades (id_usuario, id_curso, cmid, completado, data_conclusao)
            VALUES (%s, %s, %s, %s, to_timestamp(%s))
            ON CONFLICT (id_usuario, id_curso, cmid) DO UPDATE
            SET completado = EXCLUDED.completado,
                data_conclusao = EXCLUDED.data_conclusao;
            """
            params = (
                moodle_id,
                curso_id,
                atividade['cmid'],
                atividade['state'] == 1,
                atividade.get('timecompleted', 0) if atividade.get('timecompleted') else None
            )

            print(f"Parâmetros fornecidos para inserção de atividade concluída: {params}")
            self.db_util.execute_query(query, params)

        except Exception as e:
            print(f"Erro ao inserir atividade concluída: {e}")
            logging.error(f"Erro ao inserir atividade concluída: {e}")

    def inserir_professor(self, id_usuario, id_curso):
        query = """
            INSERT INTO professor (id_usuario, id_curso)
            VALUES (%s, %s)
            ON CONFLICT (id_usuario, id_curso) DO NOTHING;
        """
        
        params = (id_usuario, id_curso)
        
        try:
            with self.db_util.conn.cursor() as cursor:
                cursor.execute(query, params)
                self.db_util.conn.commit()
        except Exception as e:
            print(f"Erro ao inserir professor: {e}")

    def top_professores(self):
        query = """
        SELECT 
            u.nome AS professor_nome,
            COUNT(p.id_curso) AS numero_de_cursos
        FROM 
            professor p
        JOIN 
            usuarios u ON p.id_usuario = u.moodle_id
        GROUP BY 
            u.nome
        ORDER BY 
            numero_de_cursos DESC;
        """
        try:
            with self.db_util.conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
        except Exception as e:
            print(f"Erro ao obter os professores com mais cursos: {e}")
            return None
        
    def cursos_com_menos_inscricoes(database_operations):
        query = """
        SELECT 
            LEFT(UPPER(c.nome_curso), 15) AS nome_curso,
            COUNT(i.id_usuario) AS numero_de_inscricoes
        FROM 
            cursos c
        LEFT JOIN 
            inscricoes i ON c.id_curso = i.id_curso
        WHERE 
            c.id_curso != 1
        GROUP BY 
            c.nome_curso
        ORDER BY 
            numero_de_inscricoes ASC
        LIMIT 10;
        """
        
        try:
            with database_operations.db_util.conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
        except Exception as e:
            print(f"Erro ao obter cursos com menos inscrições: {e}")
            return None

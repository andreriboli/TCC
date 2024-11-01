from datetime import datetime, timedelta
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
            self.db_util.conn.rollback()

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
            self.db_util.conn.rollback()
            return None

    def inserir_inscricao(self, moodle_id, curso_id, progresso, detalhes_usuario, usuario):
        try:
            
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
            self.db_util.conn.rollback()

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
            self.db_util.conn.rollback()
        return None
    
    def distribuicao_cursos_ativos(self):
        query = """
            WITH total_geral AS (
                SELECT COUNT(i.id_usuario) AS total_usuarios
                FROM inscricoes i
            )
            SELECT 
                c.id_curso,
                LEFT(UPPER(c.nome_curso), 18) AS nome_curso,
                COUNT(i.id_usuario) AS total_alunos,
                ROUND((COUNT(i.id_usuario)::decimal / (SELECT total_usuarios FROM total_geral)) * 100, 2) AS percentual
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
                        "total_alunos": row[2],
                        "percentual": row[3]
                    }
                    cursos_ativos.append(curso)

                return cursos_ativos
        except Exception as e:
            self.db_util.conn.rollback()
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
            self.db_util.conn.rollback()
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
            self.db_util.conn.rollback()
            return None
        
    def distribuicao_cursos_ativos_by_category(self, end_date):
        query = """
        WITH total_users AS (
            SELECT 
                COUNT(i.id_usuario) AS total_geral
            FROM 
                cursos c
            INNER JOIN inscricoes i ON c.id_curso = i.id_curso
            WHERE 
                i.data_primeiro_acesso < %s
        )
        SELECT 
            c2.id_categoria,
            c2.nome_categoria,
            COUNT(i.id_usuario) AS total_usuarios,
            ROUND((COUNT(i.id_usuario)::decimal / (SELECT total_geral FROM total_users)) * 100, 2) AS percentual
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
                cursor.execute(query, (end_date, end_date))
                result = cursor.fetchall()
                return result
        except Exception as e:
            self.db_util.conn.rollback()
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
            ON CONFLICT (id_vimeo_video) DO UPDATE
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
            self.db_util.conn.rollback()


    def salvar_dados_vimeo(self, df): 
        config = Config()

        db_util = DBUtil(config.get_db_config())
    
        try:
            db_util.connect()
            
            for index, row in df.iterrows():
                if pd.isna(row['id_vimeo_video']) or row['id_vimeo_video'].strip() == "":
                    continue

                self.inserir_dados_vimeo(row)
        except Exception as e:
            self.db_util.conn.rollback()
        finally:
            db_util.disconnect()

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

            self.db_util.execute_query(query, params)

        except Exception as e:
            self.db_util.conn.rollback()

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
            self.db_util.conn.rollback()

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
            self.db_util.conn.rollback()
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
            return None
        
    def get_alunos_menos_engajados(self, start_date: str, end_date: str):
        query = """
        SELECT 
            LEFT(UPPER(u.nome), 15) AS nome_aluno,
            COUNT(i.id_usuario) AS total_logins
        FROM 
            usuarios u
        JOIN 
            inscricoes i ON u.moodle_id = i.id_usuario
        WHERE 
            i.data_ultimo_acesso BETWEEN %s AND %s
        GROUP BY 
            u.nome
        ORDER BY 
            total_logins ASC
        LIMIT 10;
        """
        try:
            with self.db_util.conn.cursor() as cursor:
                cursor.execute(query, (start_date, end_date))
                result = cursor.fetchall()
                return result
        except Exception as e:
            self.db_util.conn.rollback()
            return None

    def get_alunos_mais_engajados(self, start_date: str, end_date: str):
        query = """
        SELECT 
            LEFT(UPPER(u.nome), 15) AS nome_aluno,
            COUNT(i.id_usuario) AS total_logins
        FROM 
            usuarios u
        JOIN 
            inscricoes i ON u.moodle_id = i.id_usuario
        WHERE 
            i.data_ultimo_acesso BETWEEN %s AND %s
        GROUP BY 
            u.nome
        ORDER BY 
            total_logins DESC
        LIMIT 10;
        """
        try:
            with self.db_util.conn.cursor() as cursor:
                cursor.execute(query, (start_date, end_date))
                result = cursor.fetchall()
                return result
        except Exception as e:
            self.db_util.conn.rollback()
            return None
        
    def get_cursos_por_semestre(self):
        query = """
            SELECT
                CONCAT(EXTRACT(YEAR FROM c.data_inicio), ' - ', 
                    CASE
                        WHEN EXTRACT(MONTH FROM c.data_inicio) <= 6 THEN '1'
                        ELSE '2'
                    END) AS ano_semestre,
                COUNT(*) AS total_cursos
            FROM
                cursos c
            WHERE EXTRACT(YEAR FROM c.data_inicio) > 1970
            GROUP BY
                EXTRACT(YEAR FROM c.data_inicio),
                CASE
                    WHEN EXTRACT(MONTH FROM c.data_inicio) <= 6 THEN '1'
                    ELSE '2'
                END
            ORDER BY
                EXTRACT(YEAR FROM c.data_inicio), ano_semestre;
        """

        try:
            with self.db_util.conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
        except Exception as e:
            self.db_util.conn.rollback()
            return None

    def get_inscricoes_sem_certificado(self):
        query = """
            SELECT 
                COUNT(I.ID_CURSO) AS TOTAL_INSCRICOES_SEM_CERTIFICADO,
                LEFT(UPPER(c.nome_curso), 15) AS nome_curso
            FROM 
                USUARIOS U
            INNER JOIN INSCRICOES I ON U.MOODLE_ID = I.ID_USUARIO
            INNER JOIN CURSOS C ON C.ID_CURSO = I.ID_CURSO
            WHERE 
                I.PROGRESSO = 100
                AND I.COMPLETADO = FALSE
            GROUP BY
                I.ID_CURSO,
                C.NOME_CURSO
            ORDER BY 
                TOTAL_INSCRICOES_SEM_CERTIFICADO DESC;
        """

        try:
            with self.db_util.conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
        except Exception as e:
            self.db_util.conn.rollback()
            return None
    
    def inserir_atividade(self, professor_id, curso_id, atividade):
        query = """
            INSERT INTO atividades_professor 
                (professor_id, curso_id, nome_atividade, descricao, data_criacao)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """
        
        try:
            nome_atividade = atividade.get('name')
            descricao = atividade.get('intro')
            data_criacao = atividade.get('timecreated', None)
            
            if data_criacao:
                data_criacao = datetime.fromtimestamp(data_criacao)
            else:
                data_criacao = None
            
            with self.db_util.conn.cursor() as cursor:
                cursor.execute(query, (professor_id, curso_id, nome_atividade, descricao, data_criacao))
                self.db_util.conn.commit()
                
        except Exception as e:
            print(f"Erro ao inserir atividade: {e}")

    def get_professor_mais_engajado(self):
        query = """
            SELECT 
                LEFT((u.nome),15) AS professor_nome,
                COUNT(DISTINCT p.id_curso) AS numero_de_cursos,
                COUNT(a.id_atividade_professor) AS total_atividades,
                COUNT(a.id_atividade_professor) / COUNT(DISTINCT p.id_curso) AS engajamento_por_curso
            FROM 
                professor p
            JOIN 
                usuarios u ON p.id_usuario = u.moodle_id
            JOIN 
                atividades_professor a ON p.id_curso = a.curso_id
            GROUP BY 
                u.nome
            ORDER BY 
                total_atividades DESC;
        """

        try:
            with self.db_util.conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
        except Exception as e:
            self.db_util.conn.rollback()
            return None
        
    def get_videos_mais_engajado(self):
        query = """
            SELECT 
                title AS video_title,
                views,
                unique_viewers,
                (unique_viewers::decimal / views) * 100 AS unique_viewers_percentage
            FROM 
                video_analytics
            WHERE 
                views > 10
            ORDER BY 
                unique_viewers_percentage DESC;
        """

        try:
            with self.db_util.conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
        except Exception as e:
            self.db_util.conn.rollback()
            return None
        

    def get_videos_melhor_conclusao(self):
        query = """
            SELECT
                title AS video_title,
                views,
                finishes,
                (finishes::decimal / views) * 100 AS completion_rate
            FROM
                video_analytics
            WHERE
                views > 5
            ORDER BY
                completion_rate DESC
            LIMIT 10;
        """

        try:
            with self.db_util.conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
        except Exception as e:
            self.db_util.conn.rollback()
            return None
        
    def get_alunos_com_mais_atividades(self):
        query = """
            SELECT 
                usuarios.moodle_id,
                usuarios.nome,
                LEFT((usuarios.nome), 15) AS usuarios,
                COUNT(*) AS total_atividades_concluidas
            FROM 
                inscricoes
            inner join usuarios on usuarios.moodle_id = inscricoes.id_usuario
            GROUP BY 
                usuarios.moodle_id,
                usuarios.nome
            ORDER BY 
                total_atividades_concluidas DESC
            LIMIT 10;
        """

        try:
            with self.db_util.conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
        except Exception as e:
            self.db_util.conn.rollback()
            return None


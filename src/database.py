import requests
from db_util import DBUtil
from data_collection import coletar_cursos_usuario, buscar_curso_por_id
from config import Config

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
        id_categoria = self.inserir_categoria_por_id(curso['category'])
        
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
        self.db_util.execute_query(query, params)

    def inserir_inscricao(self, moodle_id, curso):
        try:
            # Verificar se o curso existe no banco de dados
            if not self.curso_existe(curso['id']):
                print(f"Curso com ID {curso['id']} não encontrado no banco de dados. Buscando na API do Moodle.")
                # Buscar o curso pelo ID via API do Moodle
                curso_detalhes = buscar_curso_por_id(self, curso['id'])  # Função importada de data_collection
                
                # Debug: Verifique o conteúdo de curso_detalhes
                print(f"Detalhes do curso obtidos da API: {curso_detalhes}")
                
                if curso_detalhes:
                    try:
                        # Tentar acessar a chave 'category' e inserir o curso
                        self.inserir_curso(curso_detalhes)
                    except KeyError as e:
                        print(f"Erro ao acessar a chave {e} em curso_detalhes: {curso_detalhes}")
                        return
                else:
                    print(f"Falha ao buscar o curso com ID {curso['id']}. Não será possível inserir a inscrição.")
                    return  # Retornar sem tentar inserir a inscrição

            # Se o curso existir ou após inseri-lo, tente inserir a inscrição
            query = """
            INSERT INTO inscricoes (id_usuario, id_curso, progresso, completado, data_primeiro_acesso, data_ultimo_acesso, tempo_medio_conclusao)
            VALUES (%s, %s, %s, %s, to_timestamp(%s), to_timestamp(%s), %s)
            ON CONFLICT (id_usuario, id_curso) DO UPDATE
            SET progresso = EXCLUDED.progresso,
                completado = EXCLUDED.completado,
                data_primeiro_acesso = EXCLUDED.data_primeiro_acesso,
                data_ultimo_acesso = EXCLUDED.data_ultimo_acesso,
                tempo_medio_conclusao = EXCLUDED.tempo_medio_conclusao;
            """
            params = (
                moodle_id,
                curso['id'],
                curso.get('progress', 0),
                curso.get('completed', False),
                curso.get('startdate', 0),
                curso.get('lastaccess', 0),
                None
            )
        
            print(f"Parâmetros fornecidos para inserção de inscrição: {params}")
            self.db_util.execute_query(query, params)
        
        except Exception as e:
            print(f"Erro ao inserir inscrição: {e}")

    def inserir_dados_usuario(self, dados_usuarios):
        for dados_usuario in dados_usuarios:
            self.inserir_usuario(dados_usuario)

            # Coletar cursos para o usuário específico
            user_id = dados_usuario['id']
            cursos = coletar_cursos_usuario(user_id)

            # Inserir cursos e inscrições
            for curso in cursos:
                self.inserir_curso(curso)
                self.inserir_inscricao(dados_usuario['id'], curso)

    def inserir_categoria_por_id(self, id_categoria):
    # Construir a URL da API do Moodle para buscar a categoria pelo ID
        url = f"{self.config.MOODLE_URL}wstoken={self.config.MOODLE_TOKEN}&wsfunction=core_course_get_categories&moodlewsrestformat=json&criteria[0][key]=id&criteria[0][value]={id_categoria}"
        
        try:
            # Fazer a requisição à API do Moodle
            response = requests.get(url)
            response.raise_for_status()  # Lança uma exceção se o status for 4xx ou 5xx
            
            categorias = response.json()
            if categorias:
                # Obter o nome da categoria a partir da resposta da API
                nome_categoria = categorias[0].get('name', f"Categoria {id_categoria}")
                
                # Verificar se a categoria já existe no banco de dados
                query = "SELECT id_categoria FROM categorias WHERE id_categoria = %s;"
                with self.db_util.conn.cursor() as cursor:
                    cursor.execute(query, (id_categoria,))
                    result = cursor.fetchone()

                    # Se a categoria não existir, inseri-la
                    if result is None:
                        insert_query = """
                            INSERT INTO categorias (id_categoria, nome_categoria)
                            VALUES (%s, %s)
                            ON CONFLICT (id_categoria) DO NOTHING
                            RETURNING id_categoria;
                        """
                        cursor.execute(insert_query, (id_categoria, nome_categoria))
                        result = cursor.fetchone()

                # Retornar o ID da categoria
                if result:
                    return result[0]  # Retorna o ID da categoria inserida ou encontrada
                else:
                    print(f"Falha ao inserir ou recuperar a categoria {id_categoria}")
                    return None
            else:
                print(f"Não foi possível encontrar a categoria com id {id_categoria}")
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


    def coletar_curso_por_id(self, curso_id):
        url = f"{self.config.MOODLE_URL}"
        params = {
            'wstoken': self.config.MOODLE_TOKEN,
            'wsfunction': 'core_course_get_courses',
            'moodlewsrestformat': 'json',
            'options[ids][0]': curso_id
        }
        
        response = requests.get(url, params=params)
        
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

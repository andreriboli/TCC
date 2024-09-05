from src.db_util import DBUtil

class ExampleTable:
    def __init__(self, db_util):
        self.db_util = db_util

    def create_table(self):
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS example_table (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            descricao TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        '''
        self.db_util.execute_query(create_table_query)
        print("Tabela 'example_table' criada com sucesso.")

    def insert_data(self, nome, descricao):
        insert_query = '''
        INSERT INTO example_table (nome, descricao)
        VALUES (%s, %s);
        '''
        self.db_util.execute_query(insert_query, (nome, descricao))
        print("Dados inseridos com sucesso na tabela 'example_table'.")

    def fetch_data(self, nome):
        select_query = '''
        SELECT * FROM example_table WHERE nome = %s;
        '''
        cursor = self.db_util.execute_query(select_query, (nome,))
        return cursor.fetchall()

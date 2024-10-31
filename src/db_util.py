import psycopg2

class DBUtil:
    def __init__(self, db_config):
        self.dbname = db_config['dbname']
        self.user = db_config['user']
        self.password = db_config['password']
        self.host = db_config['host']
        self.port = db_config['port']
        self.conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )

    def connect(self):
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )

    def disconnect(self):
        if self.conn and not self.conn.closed:
            self.conn.close()

    def execute_query(self, query, params=None):
        try:
            # Garante que a conexão está aberta antes de executar a query
            self.connect()
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                self.conn.commit()
                return cursor
        except psycopg2.InterfaceError as e:
            print(f"Erro de interface com o banco de dados: {e}")
            self.disconnect()  # Fecha a conexão se houver um problema de interface
            raise
        except Exception as e:
            self.conn.rollback()
            print(f"Erro ao executar a query: {e}")
            raise
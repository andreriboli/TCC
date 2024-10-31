import psycopg2

class DBUtil:
    def __init__(self, dbname, user, password, host, port):
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)

    def connect(self):
        if self.conn.closed:
            self.conn = psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host, port=self.port)

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                self.conn.commit()
                return cursor 
        except Exception as e:
            self.conn.rollback()
            # print(f"Erro ao executar a consulta: {e}")
            return None
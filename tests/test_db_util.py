import psycopg2


DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "root"
DB_HOST = "localhost"
DB_PORT = "5432"

def connect_and_test():
    try:
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

        cursor = connection.cursor()
        
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("Você está conectado ao - ", record, "\n")
    
    except Exception as error:
        print("Erro ao conectar ao PostgreSQL:", error)
    
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Conexão com PostgreSQL fechada.")

connect_and_test()

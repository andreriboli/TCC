class Config:
    def __init__(self):
        self.DB_NAME = "postgres"
        self.DB_USER = "postgres"
        self.DB_PASSWORD = "root"
        self.DB_HOST = "localhost"
        self.DB_PORT = "5432"

        self.MOODLE_URL = "https://e-learning-cco.unoesc.edu.br/moodle/webservice/rest/server.php?"
        self.MOODLE_TOKEN = "3a8281cc9763e6c73e3082d817d2218c"

        self.VIMEO_API_URL = "https://api.vimeo.com"
        self.VIMEO_TOKEN = "a9a4ca8237856e61e2425e5846cad690"

        self.DOWNLOAD_DIR = "C:\Desenvolvimento"

        self._validate_config()

    def _validate_config(self):
        if not all([self.DB_NAME, self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_PORT]):
            raise ValueError("Configurações do banco de dados estão incompletas.")
        if not self.MOODLE_TOKEN:
            raise ValueError("Token do Moodle não está configurado.")
        if not self.VIMEO_TOKEN:
            raise ValueError("Token do Vimeo não está configurado.")

    def get_db_config(self):
        return {
            'dbname': self.DB_NAME,
            'user': self.DB_USER,
            'password': self.DB_PASSWORD,
            'host': self.DB_HOST,
            'port': self.DB_PORT
        }

    def get_moodle_config(self):
        return {
            'url': self.MOODLE_URL,
            'token': self.MOODLE_TOKEN
        }

    def get_vimeo_config(self):
        return {
            'url': self.VIMEO_API_URL,
            'token': self.VIMEO_TOKEN
        }

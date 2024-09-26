import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

class VimeoScraper:
    def __init__(self, email, password, download_dir):
        self.email = email
        self.password = password
        self.download_dir = download_dir
        self.driver = self.inicializar_driver()

    def inicializar_driver(self):
        chrome_options = Options()
        # Use um perfil temporário do Chrome
        chrome_options.add_argument("--incognito")  # Modo anônimo

        # Configurações de download
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })

        # Configurações para remover detecção de automação
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Inicializa o Chrome com as opções
        driver = webdriver.Chrome(options=chrome_options)

        # Remove a propriedade 'webdriver'
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
            })
            """
        })

        return driver



    def login(self):
        try:
            self.driver.get("https://vimeo.com/log_in")
            
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "email_login"))
            )
            
            email_input = self.driver.find_element(By.ID, "email_login")
            email_input.send_keys(self.email)
            
            password_input = self.driver.find_element(By.ID, "password_login")
            password_input.send_keys(self.password)
            
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            if len(buttons) >= 4:
                buttons[3].click()
            
            WebDriverWait(self.driver, 30).until(
                EC.url_changes("https://vimeo.com/log_in")
            )
            print("Login bem-sucedido")
            
        except Exception as e:
            print(f"Erro ao fazer login: {e}")

    def obter_link_csv(self):
        try:
            self.driver.get("https://vimeo.com/analytics/video")
            
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(5) 
            
            csv_link = self.driver.find_element(By.CSS_SELECTOR, "#__next > div.naniiu-0.hidfuh > div.css-1tl0aqy > div.css-1t2az4r > div > div.sc-5z31bk-0.bwvIAq > div.mcrvh1-0.kMSZnu > div.css-qkv6yk > div.n2q0v9-4.dGlonL > a")
            
            if csv_link:
                csv_url = csv_link.get_attribute("href")
                print(f"Link de download do CSV encontrado: {csv_url}")
                return csv_url
            else:
                print("Link de download do CSV não encontrado.")
                return None
        except Exception as e:
            print(f"Erro ao tentar obter o link de download do CSV: {e}")
            return None

    def download_csv_directly(self, csv_url, download_dir):
        try:
            response = requests.get(csv_url)
            
            if response.status_code == 200:
                file_path = f"{download_dir}/vimeo_analytics.csv"
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                print(f"Download completo. Arquivo salvo em: {file_path}")
                return file_path
            else:
                print(f"Erro ao baixar o CSV. Código de status: {response.status_code}")
                return None
        except Exception as e:
            print(f"Erro ao tentar baixar o CSV: {e}")
        return None

    def fechar(self):
        self.driver.quit()


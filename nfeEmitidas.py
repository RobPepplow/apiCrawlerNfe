from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json
import time
import re
import os

# Configurar o local de download
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-extensions")
options.add_argument("--proxy-server='direct://'")
options.add_argument("--proxy-bypass-list=*")
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-default-apps")
options.add_argument("--enable-features=NetworkServiceInProcess")
options.add_argument("--disable-features=NetworkService")

# Define o diretório de download
base_directory = os.path.dirname(os.path.abspath(__file__))
download_directory = os.path.join(base_directory, "downloadsNfe")

# Define as opções de download
prefs = {
    "download.default_directory": download_directory,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}

# Adiciona as preferências ao objeto de opções do Chrome
options.add_experimental_option("prefs", prefs)

service = Service(ChromeDriverManager().install())

def crawlerAgendarEmitidas(
    userNfeReceitaPr: str,
    passwordNfeReceitaPr: str,
    documentNumber: str,
    documentNumberOffice: str,
    initialDate: str,
    endDate: str,
    escritorioId: str,
    empresaId: str,
    razaoSocial: str
) -> dict:

    initialHour = '000000'
    endHour = '235959'
    cnpjFormatado = re.sub(r'^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$', r'\1.\2.\3/\4-\5', documentNumber)
    initialDateFormatted = re.sub(r'(\d{2})(\d{2})(\d{4})', r'\1/\2/\3', initialDate)
    endDateFormatted = re.sub(r'(\d{2})(\d{2})(\d{4})', r'\1/\2/\3', endDate)
    url = 'https://www.dfeportal.fazenda.pr.gov.br/dfe-portal/manterDownloadDFe.do?action=iniciar'

    page = webdriver.Chrome(service=service, options=options)
    page.maximize_window()
    page.get(url)

    page.find_element(By.ID, 'cpfusuario').send_keys(userNfeReceitaPr)
    page.find_element(By.CSS_SELECTOR,
        'body > div.content > form.login-form.text-center > div:nth-child(3) > div > input').send_keys(
            passwordNfeReceitaPr)
    page.find_element(By.CSS_SELECTOR,
        'body > div.content > form.login-form.text-center > div.form-actions > button').click()

    time.sleep(1)

    page.find_element(By.CSS_SELECTOR, '#ext-gen1112').click()

    documentNumber_input = page.find_element(By.CSS_SELECTOR, '#ext-gen1081')
    documentNumber_input.send_keys(cnpjFormatado)
    time.sleep(1)
    documentNumber_input.send_keys(Keys.TAB)

    time.sleep(2)

    page.find_element(By.CSS_SELECTOR, "#ext-gen1030").send_keys(initialDateFormatted)
    page.find_element(By.CSS_SELECTOR, "#ext-gen1030").send_keys(Keys.TAB)
    page.find_element(By.CSS_SELECTOR, "#ext-gen1022").send_keys(initialHour)
    page.find_element(By.CSS_SELECTOR, "#ext-gen1022").send_keys(Keys.TAB)
    page.find_element(By.CSS_SELECTOR, "#ext-gen1032").send_keys(endDateFormatted)
    page.find_element(By.CSS_SELECTOR, "#ext-gen1032").send_keys(Keys.TAB)
    page.find_element(By.CSS_SELECTOR, "#ext-gen1023").send_keys(endHour)
    time.sleep(1)

    page.find_element(By.CSS_SELECTOR, "#ucs20_BtnAgendar").click()
    time.sleep(2)

    elemento = None
    try:
        elemento = page.find_element(By.CSS_SELECTOR, "#messagebox-1001")
    except:
        pass

    if elemento:
        page.quit()
        print("Este pedido de download DF-e já foi solicitado.")
        return {"Mensagem": "Este pedido de download DF-e já foi solicitado."}
    else:
        confere = f"{initialDate} 00:00:00 a {endDate} 23:59:59"

        tabela_selector = "table.x-grid-table.x-grid-table-resizer"
        linhas_selector = f"{tabela_selector} tbody tr:not(:first-child)"
        linhas = page.find_elements(By.CSS_SELECTOR, linhas_selector)

        resultados = []

        for linha in linhas:
            celulas_selector = "td"
            celulas = linha.find_elements(By.CSS_SELECTOR, celulas_selector)

            objeto_linha = {}

            time.sleep(1)

            for i, celula in enumerate(celulas, start=1):
                texto_celula = celula.text.strip()
                objeto_linha[f"coluna{i}"] = texto_celula

            resultados.append(objeto_linha)

            if objeto_linha["coluna3"] == confere and objeto_linha["coluna4"] == "Emitidas":
                
                status = objeto_linha["coluna10"].split('.')[0].strip()
                splitDate = initialDate.split('/')
                formattedDate = splitDate[1] + '/' + splitDate[2]

                resultado_encontrado = {
                    "filterDate": objeto_linha["coluna3"],
                    "countInvoices": 'Não tem',
                    "documentNumber": documentNumber,
                    "docType": objeto_linha["coluna4"],
                    "description": status,
                    "escritorioId": escritorioId,
                    "empresaId": empresaId,
                    "requestNumber": objeto_linha["coluna1"],
                    "documentNumberOffice": documentNumberOffice,
                    "processDate": objeto_linha["coluna9"],
                    "requestDate": objeto_linha["coluna8"],
                    "referenceDate": formattedDate,
                    "razaoSocial": razaoSocial,
                    "urlFile": 'Não tem',
                    "msg": f"Agendamento Emitidas Cnpj: {documentNumber}, Realizado Com Sucesso",
                }

                print("Resultado encontrado:")
                print(json.dumps(resultado_encontrado, indent=2, ensure_ascii=False).encode('utf-8').decode('utf-8'))                
                page.quit()
                return resultado_encontrado
                
    page.quit()
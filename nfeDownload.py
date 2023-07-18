from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import re
import time
import os

from copyFolder import copyFolder
from uploadFile import UploadFileNfe

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

def crawlerUpdate(
        id: str,
        userNfeReceitaPr: str,
        passwordNfeReceitaPr: str,
        documentNumber: str,
        documentNumberOffice: str,
        escritorioId: str,
        empresaId: str,
        razaoSocial: str,
        requestNumber: str,
        referenceDate: str,
) -> dict:
    cnpjFormatado = re.sub(r'^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$', r'\1.\2.\3/\4-\5', documentNumber)
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

    documentNumber_input = page.find_element(By.CSS_SELECTOR, '#ext-gen1081')
    documentNumber_input.send_keys(cnpjFormatado)
    time.sleep(1)
    documentNumber_input.send_keys(Keys.TAB)

    time.sleep(5)

    tabela_selector = "table.x-grid-table.x-grid-table-resizer"
    linhas_selector = f"{tabela_selector} tbody tr:not(:first-child)"
    linhas = page.find_elements(By.CSS_SELECTOR, linhas_selector)

    resultados = []

    for linha in linhas:
        celulas_selector = "td"
        celulas = linha.find_elements(By.CSS_SELECTOR, celulas_selector)
        target_imgs = linha.find_elements(By.CSS_SELECTOR,
                                          "img.x-action-col-icon.x-action-col-1.x-grid-center-icon")
        if target_imgs:
            target_img = target_imgs[0]
            actions = ActionChains(page)
            actions.move_to_element(target_img).click().perform()

        objeto_linha = {}

        time.sleep(1)

        for i, celula in enumerate(celulas, start=1):
            texto_celula = celula.text.strip()
            objeto_linha[f"coluna{i}"] = texto_celula

        resultados.append(objeto_linha)

        if objeto_linha["coluna1"] == requestNumber:

            if objeto_linha["coluna10"] == "Solicitação processada. Clique na imagem para realizar o download.":
                docType = objeto_linha["coluna4"]
                
                status = objeto_linha["coluna10"].split('.')[0].strip()
                matches = re.findall(r'\d{2}/\d{2}/\d{4}', objeto_linha["coluna3"])
                date1 = matches[0].replace('/', '-')
                date2 = matches[1].replace('/', '-')
                period = f"{date1}_a_{date2}"

                newFolderName = f"DowloadsNfes-{documentNumber}.zip";
                fileName = newFolderName
                copyFolder(newFolderName, requestNumber)

                
                referenceDateStorage = referenceDate.replace('/', '-')


                upload_file_instance = UploadFileNfe.get_instance()
                upload_file_instance.execute(
                    documentNumberOffice,
                    documentNumber,
                    referenceDateStorage,
                    period,
                    docType,
                    fileName
                )

                resultado_encontrado = {
                    "filterDate": objeto_linha["coluna3"],
                    "countInvoices": objeto_linha["coluna11"],
                    "documentNumber": documentNumber,
                    "docType": docType,
                    "description": status,
                    "escritorioId": escritorioId,
                    "empresaId": empresaId,
                    "requestNumber": requestNumber,
                    "documentNumberOffice": documentNumberOffice,
                    "processDate": objeto_linha["coluna9"],
                    "requestDate": objeto_linha["coluna8"],
                    "referenceDate": referenceDate,
                    "id": id,
                    "razaoSocial": razaoSocial,
                    "urlFile": f"https://storage.cloud.google.com/othree-notas/NFe/PR/{documentNumberOffice}/{documentNumber}/{referenceDateStorage}/{period}/{docType}/{fileName}"
                }
                page.quit()
                return resultado_encontrado
            elif objeto_linha["coluna10"] == "Solicitação expirada.":
                resultado_encontrado = {
                    "filterDate": objeto_linha["coluna3"],
                    "countInvoices": objeto_linha["coluna11"],
                    "documentNumber": documentNumber,
                    "docType": objeto_linha["coluna4"],
                    "description": objeto_linha["coluna10"],
                    "escritorioId": escritorioId,
                    "empresaId": empresaId,
                    "requestNumber": requestNumber,
                    "documentNumberOffice": documentNumberOffice,
                    "processDate": objeto_linha["coluna9"],
                    "requestDate": objeto_linha["coluna8"],
                    "referenceDate": referenceDate,
                    "id": id,
                    "razaoSocial": razaoSocial,
                    "urlFile": 'Não tem',
                    "msg": 'Prazo da Solicitação Expirou.'
                }
                page.quit()
                return resultado_encontrado
            elif objeto_linha["coluna10"] == "Não foram encontrados documentos para esta solicitação.":
                resultado_encontrado = {
                    "filterDate": objeto_linha["coluna3"],
                    "countInvoices": objeto_linha["coluna11"],
                    "documentNumber": documentNumber,
                    "docType": objeto_linha["coluna4"],
                    "description": objeto_linha["coluna10"],
                    "escritorioId": escritorioId,
                    "empresaId": empresaId,
                    "requestNumber": requestNumber,
                    "documentNumberOffice": documentNumberOffice,
                    "processDate": objeto_linha["coluna9"],
                    "requestDate": objeto_linha["coluna8"],
                    "referenceDate": referenceDate,
                    "id": id,
                    "razaoSocial": razaoSocial,
                    "urlFile": 'Não tem',
                    "msg": 'Não foram encontrados documentos para esta solicitação.',
                }
                page.quit()
                return resultado_encontrado
            elif objeto_linha["coluna10"] == "Solictação cancelada.":
                resultado_encontrado = {
                    "filterDate": objeto_linha["coluna3"],
                    "countInvoices": objeto_linha["coluna11"],
                    "documentNumber": documentNumber,
                    "docType": objeto_linha["coluna4"],
                    "description": objeto_linha["coluna10"],
                    "escritorioId": escritorioId,
                    "empresaId": empresaId,
                    "requestNumber": requestNumber,
                    "documentNumberOffice": documentNumberOffice,
                    "processDate": objeto_linha["coluna9"],
                    "requestDate": objeto_linha["coluna8"],
                    "referenceDate": referenceDate,
                    "id": id,
                    "razaoSocial": razaoSocial,
                    "urlFile": 'Não tem',
                    "msg": 'Solicitação Cancelada',
                }
                page.quit()
                return resultado_encontrado
            else:
                resultado_encontrado = {
                  "Mensagem": 'Solicitação já foi agendada e está em análise',
                }
                page.quit()
                return resultado_encontrado
            page.quit()

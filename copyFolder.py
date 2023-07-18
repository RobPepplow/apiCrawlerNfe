import os
import shutil

def clearFolder(folder_path):
    # Obtém a lista de arquivos no diretório
    files = os.listdir(folder_path)

    # Remove cada arquivo individualmente
    for file in files:
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    print(f"Conteúdo removido da pasta {folder_path} com sucesso!")

def copyFolder(newFolderName, requestNumber):
    source_file = f'downloadsNfe/DownloadDFe_{requestNumber}.zip'
    destination_file = f'zip/{newFolderName}'

    # Limpa o conteúdo da pasta "zip"
    clearFolder('zip')
    

    if not os.path.exists('zip'):
        os.makedirs('zip')
    try:
       # Copia o arquivo para a pasta de destino com novo nome
        shutil.copy2(source_file, destination_file)
        print("Arquivo copiado com sucesso!")
    except FileNotFoundError:
        print("Nenhum arquivo correspondente encontrado na pasta de downloads.")

    # Limpa o conteúdo da pasta "DownloadsNfe"
    clearFolder('DownloadsNfe')
    

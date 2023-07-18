from flask import Flask, request, jsonify
from flask_cors import CORS
from nfeDownload import crawlerUpdate
from nfeEmitidas import crawlerAgendarEmitidas
from nfeDestinadas import crawlerAgendarDestinadas

app = Flask(__name__)
CORS(app)

@app.route('/')
def resposta():
    return "A Api de Nfe - Paraná esta no Ar"

@app.route('/api/crawler/nfe/download', methods=['POST'])
def update():
    data = request.get_json()

    id = data['id']
    userNfeReceitaPr = data['userNfeReceitaPr']
    passwordNfeReceitaPr = data['passwordNfeReceitaPr']
    documentNumber = data['documentNumber']
    documentNumberOffice = data['documentNumberOffice']
    escritorioId = data['escritorioId']
    empresaId = data['empresaId']
    razaoSocial = data['razaoSocial']
    requestNumber = data['requestNumber']
    referenceDate = data['referenceDate']

    dados = crawlerUpdate(
        id=id,
        userNfeReceitaPr=userNfeReceitaPr,
        passwordNfeReceitaPr=passwordNfeReceitaPr,
        documentNumber=documentNumber,
        documentNumberOffice=documentNumberOffice,
        escritorioId=escritorioId,
        empresaId=empresaId,
        razaoSocial=razaoSocial,
        requestNumber=requestNumber,
        referenceDate=referenceDate,
    )

    if dados:
        return jsonify(dados)
    else:
        return 'Nenhum resultado encontrado.'

@app.route('/api/crawler/nfe/emitidas', methods=['POST'])
def Emitidas():
    data = request.get_json()

    userNfeReceitaPr = data['userNfeReceitaPr']
    passwordNfeReceitaPr = data['passwordNfeReceitaPr']
    documentNumber = data['documentNumber']
    documentNumberOffice = data['documentNumberOffice']
    escritorioId = data['escritorioId']
    empresaId = data['empresaId']
    razaoSocial = data['razaoSocial']
    initialDate = data['initialDate']
    endDate = data['endDate']

    dados = crawlerAgendarEmitidas(
        userNfeReceitaPr=userNfeReceitaPr,
        passwordNfeReceitaPr=passwordNfeReceitaPr,
        documentNumber=documentNumber,
        documentNumberOffice=documentNumberOffice,
        escritorioId=escritorioId,
        empresaId=empresaId,
        razaoSocial=razaoSocial,
        initialDate=initialDate,
        endDate=endDate,
    )

    if dados:
        return jsonify(dados)
    else:
        return 'Não Foi Possivel Agendar Emitidas.'

@app.route('/api/crawler/nfe/destinadas', methods=['POST'])
def Destinadas():
    data = request.get_json()

    userNfeReceitaPr = data['userNfeReceitaPr']
    passwordNfeReceitaPr = data['passwordNfeReceitaPr']
    documentNumber = data['documentNumber']
    documentNumberOffice = data['documentNumberOffice']
    escritorioId = data['escritorioId']
    empresaId = data['empresaId']
    razaoSocial = data['razaoSocial']
    initialDate = data['initialDate']
    endDate = data['endDate']

    dados = crawlerAgendarDestinadas(
        userNfeReceitaPr=userNfeReceitaPr,
        passwordNfeReceitaPr=passwordNfeReceitaPr,
        documentNumber=documentNumber,
        documentNumberOffice=documentNumberOffice,
        escritorioId=escritorioId,
        empresaId=empresaId,
        razaoSocial=razaoSocial,
        initialDate=initialDate,
        endDate=endDate,
    )

    if dados:
        return jsonify(dados)
    else:
        return 'Não Foi Possivel Agendar Destinadas.'

if __name__ == "__main__":
    app.run()

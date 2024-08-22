import requests
import json
import pandas as pd
from datetime import datetime, timedelta

#tentar usar a biblioteca datetime para conseguir resultados melhores e mais afunilados

url = ["https://api-publica.datajud.cnj.jus.br/api_publica_tjac/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjal/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjam/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjap/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjba/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjce/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjdft/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjes/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjgo/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjma/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjmg/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjms/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjmt/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjpa/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjpb/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjpe/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjpi/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjpr/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjrj/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjrn/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjro/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjrr/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjrs/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjsc/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjse/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjsp/_search", "https://api-publica.datajud.cnj.jus.br/api_publica_tjto/_search"]

now = datetime.now()
today = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
twentyEightDaysAgo = (now - timedelta(days=28)).strftime("%Y-%m-%dT%H:%M:%S.000Z")

dataMatchRangeMax = today

dataMatchRangeMin = twentyEightDaysAgo

#Criando o dicionário vazio para receber as informações do JSON e criar o CSV
response = {
    'classe': [],
    'numeroProcesso': [],
    'tribunal': [],
    'datahoraultimaatualizacao': [],
    'dataajuizamento': [],
}

def fetch_url(url):    
    payload = json.dumps({
        "size": 500,
        "query": {
            "bool": {
                "must": [
                    {"match": {"classe.codigo": 129}},
                    {"range": {"dataAjuizamento": {"gte": dataMatchRangeMin, "lte": dataMatchRangeMax}}},
                ]
            }
        }
    }
    )

    #Substituir <API Key> pela Chave Pública
    headers = {
    'Authorization': 'ApiKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==',
    'Content-Type': 'application/json'
    }

    responsebrute = requests.request("POST", url, headers=headers, data=payload)

    #Dando append aos dicionários vindo do JSON responsebrute
    for i in range(len(responsebrute.json()['hits']['hits'])):
        response['classe'].append(responsebrute.json()['hits']['hits'][i]['_source']['classe']['nome'])
        response['numeroProcesso'].append("'" + responsebrute.json()['hits']['hits'][i]['_source']['numeroProcesso'] + "'")
        response['tribunal'].append(responsebrute.json()['hits']['hits'][i]['_source']['tribunal'])
        response['datahoraultimaatualizacao'].append(responsebrute.json()['hits']['hits'][i]['_source']['dataHoraUltimaAtualizacao'])
        response['dataajuizamento'].append(responsebrute.json()['hits']['hits'][i]['_source']['dataAjuizamento'])

for i in range(len(url)):
    fetch_url(url[i])

#Criando o arquivo JSON a partir do dicionário
with open('jsonfile.json', 'w', encoding='utf-8') as f:
    json.dump(response, f, ensure_ascii=False, indent=4)

print("criado arquivo json")

#tentando transformar em CSV

df = pd.read_json('jsonfile.json')

#criando o arquivo CSV usando a biblioteca pandas e definindo as colunas e separador
df.to_csv('csvfile.csv', encoding='utf-8', columns=['classe', 'numeroProcesso', 'tribunal', 'datahoraultimaatualizacao', 'dataajuizamento'], sep=';', index=False)

import requests
import json
import pandas as pd
from datetime import datetime
import os
import customtkinter as ctk
from tkcalendar import DateEntry
import glob
import threading
import openpyxl

# Variáveis Globais
classecodigo = None
nomedoarquivo = None
TJ = None
datainicial = None
datafinal = None
sheet_name = None  # Variable to hold the selected Excel sheet

# Funções
def tags():
    return [
        "TJAC", "TJAL", "TJAM", "TJAP", "TJBA", "TJCE", "TJDF", "TJES", "TJGO",
        "TJMA", "TJMG", "TJMS", "TJMT", "TJPA", "TJPB", "TJPE", "TJPI", "TJPR",
        "TJRJ", "TJRN", "TJRO", "TJRR", "TJSC", "TJSE", "TJSP", "TJTO", "Todos"
    ]

def classe_codes():
    return {
        "Recuperação Extrajudicial": 128,
        "Recuperação Judicial": 129
    }

def get_excel_sheets():
    """Return a list of all Excel files in the current directory plus 'No Sheet' option."""
    sheets = [f for f in glob.glob("*.xlsx")]
    sheets.append("No Sheet")  
    return sheets

def requisicao():
    global nomedoarquivo, TJ, classecodigo, datainicial, datafinal, sheet_name

    urlList = {
            "TJAC": "https://api-publica.datajud.cnj.jus.br/api_publica_tjac/_search",
            "TJAL": "https://api-publica.datajud.cnj.jus.br/api_publica_tjal/_search",
            "TJAM": "https://api-publica.datajud.cnj.jus.br/api_publica_tjam/_search",
            "TJAP": "https://api-publica.datajud.cnj.jus.br/api_publica_tjap/_search",
            "TJBA": "https://api-publica.datajud.cnj.jus.br/api_publica_tjba/_search",
            "TJCE": "https://api-publica.datajud.cnj.jus.br/api_publica_tjce/_search",
            "TJDF": "https://api-publica.datajud.cnj.jus.br/api_publica_tjdft/_search",
            "TJES": "https://api-publica.datajud.cnj.jus.br/api_publica_tjes/_search",
            "TJGO": "https://api-publica.datajud.cnj.jus.br/api_publica_tjgo/_search",
            "TJMA": "https://api-publica.datajud.cnj.jus.br/api_publica_tjma/_search",
            "TJMG": "https://api-publica.datajud.cnj.jus.br/api_publica_tjmg/_search",
            "TJMS": "https://api-publica.datajud.cnj.jus.br/api_publica_tjms/_search",
            "TJMT": "https://api-publica.datajud.cnj.jus.br/api_publica_tjmt/_search",
            "TJPA": "https://api-publica.datajud.cnj.jus.br/api_publica_tjpa/_search",
            "TJPB": "https://api-publica.datajud.cnj.jus.br/api_publica_tjpb/_search",
            "TJPE": "https://api-publica.datajud.cnj.jus.br/api_publica_tjpe/_search",
            "TJPI": "https://api-publica.datajud.cnj.jus.br/api_publica_tjpi/_search",
            "TJPR": "https://api-publica.datajud.cnj.jus.br/api_publica_tjpr/_search",
            "TJRJ": "https://api-publica.datajud.cnj.jus.br/api_publica_tjrj/_search",
            "TJRN": "https://api-publica.datajud.cnj.jus.br/api_publica_tjrn/_search",
            "TJRO": "https://api-publica.datajud.cnj.jus.br/api_publica_tjro/_search",
            "TJRR": "https://api-publica.datajud.cnj.jus.br/api_publica_tjrr/_search",
            "TJSC": "https://api-publica.datajud.cnj.jus.br/api_publica_tjsc/_search",
            "TJSE": "https://api-publica.datajud.cnj.jus.br/api_publica_tjse/_search",
            "TJSP": "https://api-publica.datajud.cnj.jus.br/api_publica_tjsp/_search",
            "TJTO": "https://api-publica.datajud.cnj.jus.br/api_publica_tjto/_search",
        }

    dataMatchRangeMax = datafinal
    dataMatchRangeMin = datainicial

    response = {
        'classe': [], 'numeroProcesso': [], 'tribunal': [], 'datahoraultimaatualizacao': [],
        'dataajuizamento': [], 'movimentosorgaoJulgadornomeOrgao': [], 'movimentosorgaoJulgadornomecodigo': []
    }

    def fetch_url(url):    
        payload = json.dumps({
            "size": 1000,
            "query": {
                "bool": {
                    "must": [
                        {"match": {"classe.codigo": classecodigo}},
                        {"range": {"dataajuizamento": {"gte": dataMatchRangeMin, "lte": dataMatchRangeMax}}},
                    ]
                }
            }
        })

        headers = {
            'Authorization': 'ApiKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==',
            'Content-Type': 'application/json'
        }

        try:
            responsebrute = requests.request("POST", url, headers=headers, data=payload)
            data = responsebrute.json()['hits']['hits']

            for item in data:
                source = item['_source']
                response['classe'].append(source['classe']['nome'])
                response['numeroProcesso'].append("'" + source['numeroProcesso'] + "'")
                response['tribunal'].append(source['tribunal'])
                response['datahoraultimaatualizacao'].append(source['dataHoraUltimaAtualizacao'])
                response['dataajuizamento'].append(source['dataAjuizamento'])
                response['movimentosorgaoJulgadornomeOrgao'].append(source['orgaoJulgador']['nome'])
                response['movimentosorgaoJulgadornomecodigo'].append(source['orgaoJulgador']['codigo'])
        except Exception as e:
            print(f"Error fetching data from {url}: {e}")

    # Fetch data for the selected TJ or all TJs
    if TJ == "Todos":
        status_label.configure(text="Seu arquivo está sendo gerado...")
        for url in urlList.values():
            fetch_url(url)
    else:
        fetch_url(urlList[TJ])

    # Save fetched data to Excel
    save_to_excel(response)

def refresh_sheet_list():
    """Refresh the list of Excel sheets in the combobox."""
    combobox_sheet.configure(values=get_excel_sheets())

def save_to_excel(response):
    """Save the fetched data to an Excel file and refresh sheet list."""
    fetched_df = pd.DataFrame(response)

    if sheet_name != "No Sheet":
        existing_df = pd.read_excel(sheet_name)

        # Compare fetched data with existing data
        new_rows_df = fetched_df[~fetched_df['numeroProcesso'].isin(existing_df['numeroProcesso'])]

        if not new_rows_df.empty:
            new_filename = nomedoarquivo + '_novos_processos.xlsx'
            new_rows_df.to_excel(new_filename, index=False)
            status_label.configure(text=f"Novas linhas encontradas!\nArquivo salvo como: {new_filename}")
        else:
            status_label.configure(text="Nenhuma nova linha encontrada.")
    else:
        new_filename = nomedoarquivo + '.xlsx'
        fetched_df.to_excel(new_filename, index=False)
        status_label.configure(text="Arquivo Gerado com Sucesso!")

    # Refresh the list of available sheets after saving the file
    refresh_sheet_list()

def iniciar_requisicao():
    global nomedoarquivo, TJ, classecodigo, datainicial, datafinal, sheet_name

    nomedoarquivo = entry_nome_arquivo.get()
    TJ = combobox_TJ.get()
    classecodigo = classe_codes()[combobox_classe.get()]
    datainicial = entry_data_inicial.get_date().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    datafinal = entry_data_final.get_date().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    sheet_name = combobox_sheet.get()

    status_label.configure(text="Seu arquivo está sendo gerado...")

    # Run the requisicao function in a separate thread
    threading.Thread(target=requisicao).start()

def criar_interface():
    global entry_nome_arquivo, combobox_TJ, combobox_classe, entry_data_inicial, entry_data_final, status_label, combobox_sheet

    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    janela = ctk.CTk()
    janela.title("Consulta de Processos")
    janela.geometry("615x762")

    label_arquivo = ctk.CTkLabel(janela, text="Nome do Arquivo:")
    label_arquivo.pack(pady=10)
    entry_nome_arquivo = ctk.CTkEntry(janela)
    entry_nome_arquivo.pack(pady=10)

    label_TJ = ctk.CTkLabel(janela, text="Selecione o TJ:")
    label_TJ.pack(pady=10)
    combobox_TJ = ctk.CTkComboBox(janela, values=tags())
    combobox_TJ.pack(pady=10)

    label_classe = ctk.CTkLabel(janela, text="Selecione a Classe:")
    label_classe.pack(pady=10)
    combobox_classe = ctk.CTkComboBox(janela, values=list(classe_codes().keys()))
    combobox_classe.pack(pady=10)

    label_data_inicial = ctk.CTkLabel(janela, text="Data Inicial (dd/mm/aaaa):")
    label_data_inicial.pack(pady=10)
    entry_data_inicial = DateEntry(janela, date_pattern='dd/mm/yyyy')
    entry_data_inicial.pack(pady=10)

    label_data_final = ctk.CTkLabel(janela, text="Data Final (dd/mm/aaaa):")
    label_data_final.pack(pady=10)
    entry_data_final = DateEntry(janela, date_pattern='dd/mm/yyyy')
    entry_data_final.pack(pady=10)

    label_sheet = ctk.CTkLabel(janela, text="Selecione a Planilha Existente:")
    label_sheet.pack(pady=10)
    combobox_sheet = ctk.CTkComboBox(janela, values=get_excel_sheets())
    combobox_sheet.pack(pady=10)

    botao_iniciar = ctk.CTkButton(janela, text="Iniciar Requisição", command=iniciar_requisicao)
    botao_iniciar.pack(pady=20)

    status_label = ctk.CTkLabel(janela, text="")
    status_label.pack(pady=20)

    janela.mainloop()

if __name__ == "__main__":
    criar_interface()


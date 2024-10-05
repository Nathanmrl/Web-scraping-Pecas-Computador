from selenium import webdriver
from bs4 import BeautifulSoup
import mysql.connector
import re

# Conexão com o banco de dados
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="comp"
)

def extrair_atributos_placa_mae(nome_placa_mae):
    # Padronizando o nome da placa-mãe
    nome_placa_mae = nome_placa_mae.lower().replace('-', ' ').replace(',', '')

    # Definindo padrões para extrair os atributos
    padrao_qtd_slots_memoria = r'(\d+)x[\s-]*dimms?'
    padrao_qtd_slots_pci = r'(\d+)x[\s-]*pc[i-e][\s-]*e?[\s-]*x?[\s-]*\d'
    padrao_chipset = r'(?:intel|amd)[\s-]*(\w+(?:\s*\w+)*)'
    padrao_formato = r'(atx|matx|micro[\s-]*atx|mini[\s-]*itx)'
    padrao_soquete = r'(lga|am|fm)?\d{3,4}'

    # Procurando por padrões no nome da placa-mãe
    match_qtd_slots_memoria = re.search(padrao_qtd_slots_memoria, nome_placa_mae)
    match_qtd_slots_pci = re.search(padrao_qtd_slots_pci, nome_placa_mae)
    match_chipset = re.search(padrao_chipset, nome_placa_mae)
    match_formato = re.search(padrao_formato, nome_placa_mae)
    match_soquete = re.search(padrao_soquete, nome_placa_mae)

    # Extraindo os atributos
    qtd_slots_memoria = int(match_qtd_slots_memoria.group(1)) if match_qtd_slots_memoria else 0
    qtd_slots_pci = int(match_qtd_slots_pci.group(1)) if match_qtd_slots_pci else 0
    chipset = match_chipset.group(1).capitalize() if match_chipset else ''
    formato = match_formato.group(1).upper() if match_formato else ''
    soquete = match_soquete.group() if match_soquete else ''

    return qtd_slots_memoria, qtd_slots_pci, chipset, formato, soquete

# Conectando com o site 
driver = webdriver.Chrome()
driver.get("https://www.kabum.com.br/hardware/placas-mae")

html = driver.page_source
site = BeautifulSoup(html, 'html.parser')

# Pegando os valores
imagens_placa_mae = site.find_all("img", class_="imageCard" )

precos_placa_mae = site.find_all("span", class_="sc-b1f5eb03-2")

nomes_placas_mae = site.find_all("span", class_="sc-d79c9c3f-0")

links_processador = site.find_all("a", class_="sc-9d1f1537-10 kueyFw productLink")


precos_limpos = []
Nomes_placa_mae = []
Precos_placa_mae = []
urls_imagens = []
Links_processador = []
Links_Limpos = []


# Adicionando à lista 
for span in nomes_placas_mae:
    Nomes_placa_mae.append(span.text.strip())

for span in precos_placa_mae:
    Precos_placa_mae.append(span.text.strip())

for link in links_processador:
    Links_processador.append(link['href'])

# Extrair URLs das imagens e adicionar à lista
for img in imagens_placa_mae:
    src_attr = img.get("src")
    if src_attr:
        urls_imagens.append(src_attr)

# Fecha a página 
driver.quit()


# Limpa o preço
def limpar_e_converter(valor_str):
    valor_str = ''.join(caracter for caracter in valor_str if caracter.isdigit() or caracter == ',').replace(',', '.')
    return float(valor_str)

for valor in Precos_placa_mae:
    preco_convertido = limpar_e_converter(valor)
    precos_limpos.append(preco_convertido)

# Adiciona "https://www.kabum.com.br" ao início de cada link
for link in Links_processador:
    Links_Limpos.append(f"https://www.kabum.com.br{link}")



print(Nomes_placa_mae)
print("---------")
print(precos_limpos)
print("---------")
print(urls_imagens)
print("---------")
print(Links_Limpos)


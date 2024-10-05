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

def extrair_atributos_processador(nome_processador):
    # Padronizando o nome do processador
    nome_processador = nome_processador.lower().replace('-', ' ').replace(',', '')

    # Definindo padrões para extrair os atributos
    padrao_marca = r'(amd|intel)' 
    padrao_cores_threads = r'(\d+)(?:[\s-]*core)(?:s)?(?:[\s-]+(\d+)(?:[\s-]*thread)(?:s)?)?'
    padrao_frequencia = r'(\d+(?:\.\d+)?)ghz(?:[\s-]*\(?(?:base|turbo)?(?:clock)?\)?(?:[\s-]*(\d+(?:\.\d+)?)ghz)?)?'
    padrao_cache = r'(\d+mb)(?:[\s-]*cache)?'
    padrao_soquete = r'(lga|am|fm)?\d{3,4}'
    
    # Procurando por padrões no nome do processador
    match_marca = re.search(padrao_marca, nome_processador)
    match_cores_threads = re.search(padrao_cores_threads, nome_processador)
    match_frequencia = re.search(padrao_frequencia, nome_processador)
    match_cache = re.search(padrao_cache, nome_processador)
    match_soquete = re.search(padrao_soquete, nome_processador)

    # Extraindo os atributos
    marca = match_marca.group(1).capitalize() if match_marca else ''
    num_cores = int(match_cores_threads.group(1)) if match_cores_threads and match_cores_threads.group(1) else 0
    num_threads = int(match_cores_threads.group(2)) if match_cores_threads and match_cores_threads.group(2) else 0
    frequencia_base = float(match_frequencia.group(1)) if match_frequencia and match_frequencia.group(1) else 0.0
    frequencia_turbo = float(match_frequencia.group(2)) if match_frequencia and match_frequencia.group(2) else None
    cache = int(match_cache.group(1).replace('mb', '')) if match_cache else 0
    soquete = match_soquete.group() if match_soquete else ''

    return marca, num_cores, num_threads, frequencia_base, frequencia_turbo, cache, soquete


# Conectando-se ao site
driver = webdriver.Chrome()
driver.get("https://www.kabum.com.br/hardware/processadores")

# Obtendo o código-fonte da página
html = driver.page_source
site = BeautifulSoup(html, 'html.parser')

# Pegando os valores
imagens_processador = site.find_all("img", class_="imageCard")
precos_processador = site.find_all("span", class_="sc-b1f5eb03-2")
nomes_processador = site.find_all("span", class_="sc-d79c9c3f-0")
links_processador = site.find_all("a", class_="sc-9d1f1537-10 kueyFw productLink")

# Inicializando a lista para armazenar URLs das imagens
Precos_processador = []
Nomes_processador = []
urls_imagens = []
precos_limpos = []
Links_processador = []
Links_Limpos = []

# Adicionando à lista 
for span in nomes_processador:
    Nomes_processador.append(span.text.strip())

for span in precos_processador:
    Precos_processador.append(span.text.strip())

for link in links_processador:
    Links_processador.append(link['href'])

# Extrair URLs das imagens e adicionar à lista
for img in imagens_processador:
    src_attr = img.get("src")
    if src_attr:
        urls_imagens.append(src_attr)

# Fechando o navegador
driver.quit()

# Limpa o preço
def limpar_e_converter(valor_str):
    valor_str = ''.join(caracter for caracter in valor_str if caracter.isdigit() or caracter == ',').replace(',', '.')
    return float(valor_str)

for valor in Precos_processador:
    preco_convertido = limpar_e_converter(valor)
    precos_limpos.append(preco_convertido)

# Exibindo os links dos processadores

# Adiciona "https://www.submarino.com.br/" ao início de cada link
for link in Links_processador:
    Links_Limpos.append(f"https://www.kabum.com.br{link}")



# Integração com o banco de dados
cursor = mydb.cursor()

# Inserindo os produtos e detalhes do processador no banco de dados
for nome, preco, imagem_url, link in zip(Nomes_processador, precos_limpos, urls_imagens, Links_Limpos):
    # Usando a função extrair_atributos_processador para dividir o nome do processador em outros atributos
    marca, num_cores, num_threads, frequencia_base, frequencia_turbo, cache, soquete = extrair_atributos_processador(nome)
    
    # Inserindo o produto na tabela 'produto'
    cursor.execute("INSERT INTO produto (Nome, Marca, Preco, Site, Imagem, Data, Link) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                   (nome, marca, preco, 'Kabum', imagem_url, '2024-06-11', link))
    mydb.commit()

    # Obtendo o ID do produto recém-inserido
    idProduto = cursor.lastrowid

    # Inserindo os detalhes do processador na tabela 'processador' e vinculando-o ao produto
    cursor.execute("INSERT INTO processador (Produto_idProduto, Qtd_Nucleos, Qtd_Threads, Clock_Base, Clock_Turbo, Cache, Soquete) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                   (idProduto, num_cores, num_threads, frequencia_base, frequencia_turbo, cache, soquete))
    mydb.commit()

cursor.close()
mydb.close()
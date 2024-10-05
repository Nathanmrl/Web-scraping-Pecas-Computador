import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time

# Conexão com o banco de dados
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="comp"
)

cursor = mydb.cursor()

# Selecionar produtos onde o Site não é 'Kabum'
cursor.execute("SELECT idProduto, Nome FROM produto WHERE Site != 'Kabum'")
produtos = cursor.fetchall()

cursor.close()

def cortar_nome(nome):
    # Função para cortar o nome imediatamente após encontrar '00', '0 ', '-', ou 'm'
    for i, char in enumerate(nome):
        if char == '-' or char == ',':
            return nome[:i+1]
    
    return nome 

if not produtos:
    print("Nenhum produto encontrado com o Site diferente de 'Kabum'")
else:
    # Iniciar o navegador
    driver = webdriver.Chrome()

    # Função para limpar e converter o preço
    def limpar_e_converter(valor_str):
        valor_str = ''.join(caracter for caracter in valor_str if caracter.isdigit() or caracter == ',').replace(',', '.')
        return float(valor_str)

    for produto in produtos:
        id_produto, nome_produto = produto
        nome_produto_cortado = cortar_nome(nome_produto)  # Cortando o nome do produto
        
        driver.get("https://www.kabum.com.br/busca/")
        search_box = driver.find_element(By.ID, "input-busca")
        search_box.send_keys(nome_produto_cortado)
        search_box.send_keys(Keys.RETURN)
        
        # Esperar o carregamento da página
        time.sleep(4)

        # Obter o código-fonte da página e analisar com BeautifulSoup
        html = driver.page_source
        site = BeautifulSoup(html, 'html.parser')

        # Extrair os primeiros três itens encontrados
        imagens_processador = site.find_all("img", class_="imageCard")
        precos_processador = site.find_all("span", class_="sc-b1f5eb03-2")
        nomes_processador = site.find_all("span", class_="sc-d79c9c3f-0")
        links_processador = site.find_all("a", class_="sc-9d1f1537-10 kueyFw productLink")

        # Inicializando as listas para armazenar as informações
        Precos_processador = []
        Nomes_processador = []
        urls_imagens = []
        precos_limpos = []
        Links_processador = []
        Links_Limpos = []

        # Adicionando os nomes à lista 
        for span in nomes_processador:
            Nomes_processador.append(span.text.strip())

        # Adicionando os preços à lista 
        for span in precos_processador:
            Precos_processador.append(span.text.strip())

        # Adicionando os links à lista
        for link in links_processador:
            Links_processador.append(link['href'])

        # Extrair URLs das imagens e adicionar à lista
        for img in imagens_processador:
            src_attr = img.get("src")
            if src_attr:
                urls_imagens.append(src_attr)

        # Limpar e converter os preços
        for valor in Precos_processador:
            preco_convertido = limpar_e_converter(valor)
            precos_limpos.append(preco_convertido)

        # Adicionar "https://www.kabum.com.br" ao início de cada link
        for link in Links_processador:
            Links_Limpos.append(f"https://www.kabum.com.br{link}")

        # Exibindo as informações
        print(f"Produto: {nome_produto}")
        print(f"Nome cortado: {nome_produto_cortado}")
        for i in range(len(Nomes_processador)):
            print(f"Nome: {Nomes_processador[i]}")
            print(f"Preço: {precos_limpos[i]}")
            print(f"Imagem: {urls_imagens[i]}")
            print(f"Link: {Links_Limpos[i]}")
            print('----')

    # Fechar o navegador
    driver.quit()

mydb.close()

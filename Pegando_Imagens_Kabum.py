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

# Selecionar produtos onde o Site é 'Kabum' e a Imagem é NULL
cursor.execute("SELECT idProduto, Nome FROM produto WHERE Site = 'Kabum' AND Imagem = 'null'")
produtos = cursor.fetchall()

cursor.close()

if not produtos:
    print("Nenhum produto encontrado com o Site 'Kabum' e Imagem NULL.")
else:
    # Iniciar o navegador
    driver = webdriver.Chrome()

    for produto in produtos:
        id_produto, nome_produto = produto
        
        driver.get("https://www.kabum.com.br/busca/")
        search_box = driver.find_element(By.ID, "input-busca")
        search_box.send_keys(nome_produto)
        search_box.send_keys(Keys.RETURN)
        
        # Esperar o carregamento da página
        time.sleep(3)

        # Obter o código-fonte da página e analisar com BeautifulSoup
        html = driver.page_source
        site = BeautifulSoup(html, 'html.parser')

        # Procurar pela imagem do produto
        imagens = site.find_all("img", class_="imageCard")

        if imagens:
            imagem_url = imagens[0]['src']  # Pegando a primeira imagem encontrada

            # Atualizar o banco de dados com a URL da imagem
            cursor = mydb.cursor()
            cursor.execute("UPDATE produto SET Imagem = %s WHERE idProduto = %s", (imagem_url, id_produto))
            mydb.commit()
            cursor.close()

            print(f"Imagem atualizada para o produto: {nome_produto}")
        else:
            print(f"Imagem não encontrada para o produto: {nome_produto}")

    # Fechar o navegador
    driver.quit()

mydb.close()

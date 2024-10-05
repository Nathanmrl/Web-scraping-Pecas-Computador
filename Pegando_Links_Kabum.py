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

# Selecionar produtos onde o Site é 'Kabum' e a Imagem é 'null'
cursor.execute("SELECT idProduto, Nome FROM produto WHERE Site = 'Kabum' AND Link is NULL or Link = 'null'")
produtos = cursor.fetchall()

cursor.close()

if not produtos:
    print("Nenhum produto encontrado com o Site 'Kabum' e Imagem NULL.")
else:
    # Iniciar o navegador
    driver = webdriver.Chrome()

    try:
        for produto in produtos:
            id_produto, nome_produto = produto
            try:
            
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
                
                # Procurar pelo link do produto
                links_processador = site.find_all("a", class_="sc-9d1f1537-10 kueyFw productLink")

                # Inicializar variáveis para armazenar a imagem e o link
                link_url = None

                

                # Obter a URL do primeiro link encontrado
                if links_processador:
                    link_url = f"https://www.kabum.com.br{links_processador[0]['href']}"

                # Atualizar o banco de dados com a URL da imagem e do link, se encontrados
                if link_url:
                    cursor = mydb.cursor()
                    cursor.execute("UPDATE produto SET Link = %s WHERE idProduto = %s", (link_url, id_produto))
                    mydb.commit()
                    cursor.close()
                    print(f"Imagem e link atualizados para o produto: {nome_produto}")
            
                else:
                    print(f"Imagem e link não encontrados para o produto: {nome_produto}")

            except Exception as e:
                # Atualizar o banco de dados com 'NULL' em caso de erro
                cursor = mydb.cursor()
                cursor.execute("UPDATE produto SET Link = %s WHERE idProduto = %s", ('NULL', id_produto))
                mydb.commit()
                cursor.close()
                print(f"Erro ao processar o produto {nome_produto}: {e}")
                print(f"Imagem atualizada como NULL para o produto: {nome_produto}")

    finally:
        # Fechar o navegador
        driver.quit()

# Fechar cursor e conexão com o banco de dados
cursor.close()
mydb.close()

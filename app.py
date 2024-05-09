from flask import Flask
import psycopg2
import requests
from datetime import datetime


dbname = 'TCC'
user = 'postgres'
password = '1234'
host = 'localhost'

base_url = "https://viacep.com.br/ws/"

try:
    conn = psycopg2.connect(dbname=dbname, user=user,
                            password=password, host=host)
    print("Conexão bem-sucedida!")
except psycopg2.Error as e:
    print("Erro ao conectar:", e)

server = Flask(__name__)

@server.get('/cep')
def get_ceps():
  
    # Formata a data e hora no formato desejado
    inicio =datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(inicio)
    cur = conn.cursor()
    cur.execute("SELECT * FROM cep")
    results = cur.fetchall()

    for row in results:
        id,cep = row
        url = f'{base_url}{cep}/json'
        print(url)
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            print(data)

            # Extrai os valores do JSON
            logradouro = data.get('logradouro', '')
            bairro = data.get('bairro', '')
            localidade = data.get('localidade', '')
            uf = data.get('uf', '')
            ibge = data.get('ibge', '')
            gia = data.get('gia', '')
            ddd = data.get('ddd', '')
            siafi = data.get('siafi', '')

            cur.execute("INSERT INTO endereco (cep, logradouro, bairro, localidade, uf, ibge, gia, ddd, siafi) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (cep, logradouro, bairro, localidade, uf, ibge, gia, ddd, siafi))
            
            conn.commit()
            
    fim = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(fim)
    cur.close()

    return {
        'inicioRotina': inicio,
        'finalRotina': fim
    }



server.run(debug=True)
conn.close()

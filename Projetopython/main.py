from flask import Flask
import fdb

app = Flask(__name__)
app.config.from_pyfile('config.py')

host = app.config['DB_HOST']
database = app.config['DB_NAME']
user = app.config['DB_USER']
password = app.config['DB_PASSWORD']

try:
    con = fdb.connect(host=host, database=database, user=user, password=password) # conn = conexão
    print("Conexão estabelecida com sucesso!")
except Exception as e:
    print(f"Erro! {e}")

from view import *  #importa tudo do file view

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) #porta 5000 é a porta-padrão

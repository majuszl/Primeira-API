from flask import Flask, jsonify
from main import app, con

@app.route('/livro', methods=['GET'])
def livro(): # nome da rota
    cur = con.cursor() # abre o cursor para executar a instrução SQL
    cur.execute("SELECT id_livro, titulo, autor, ano_publicacao FROM livro")
    livros = cur.fetchall() # percorrendo, cria uma lista dentro da lista de campos, fazendo com que cada livro com suas informções represente um item da lista
    livros_dic = []# tranformando em dicionário
    for livro in livros:
        livros_dic.append({
            'id_livro': livro[0],
            'titulo': livro[1],
            'autor': livro[2],
            'ano_publicacao': livro[3]
        })
        return jsonify(mensagem='Lista de Livros', livros=livros_dic) # transformando em JSON

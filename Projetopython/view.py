from flask import Flask, jsonify, request
from main import app, con

@app.route('/livros', methods=['GET'])
def livro(): # nome da rota
    cur = con.cursor() # abre o cursor para executar a instrução SQL
    cur.execute("SELECT id_livro, titulo, autor, ano_publicacao FROM livros")
    livros = cur.fetchall() # percorrendo, cria uma lista dentro da lista de campos, fazendo com que cada livro com suas informções represente um item da lista
    livros_dic = []# tranformando em dicionário
    for livro in livros:
        livros_dic.append({
            'id_livro': livro[0],
            'titulo': livro[1],
            'autor': livro[2],
            'ano_publicacao': livro[3],
        })
    return jsonify(mensagem='Lista de Livros', livros=livros_dic) # transformando em JSON

@app.route('/livros', methods=['POST'])
def livro_post():
    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')
    ano_publicacao = data.get('ano_publicacao')

    cursor = con.cursor() # abrindo cursor

    cursor.execute("SELECT 1 FROM livros WHERE titulo = ?", (titulo, )) # 1 comprova a existência de algo, se não existir, retorna nulo

    if cursor.fetchone(): # se retornou um único registro (fetchone)
        return jsonify("Livro já cadastrado") # eu retorno que o livro já existe na tabela

    cursor.execute("INSERT INTO livros(titulo, autor, ano_publicacao) VALUES (?, ?, ?)", (titulo, autor, ano_publicacao))

    con.commit() # comitando o banco
    cursor.close() # fechando o cursor

    return jsonify({
        'message': "Livro cadastrado com sucesso!",
        'livro': {
            'titulo': titulo,
            'autor': autor,
            'ano_publicacao': ano_publicacao
        }
    })


@app.route('/livro/<int:id>', methods=['PUT']) # método PUT edita
def livro_put(id):
        cursor = con.cursor()
        cursor.execute("SELECT id_livro, titulo, autor, ano_publicacao FROM livros WHERE id_livro = ?", (id, ))
        livro_data = cursor.fetchone()

        if not livro_data:
            cursor.close()
            return jsonify({"error": "O livro não foi encontrado... ):"}),404

        data = request.get_json()
        titulo = data.get('titulo')
        autor = data.get('autor')
        ano_publicacao = data.get('ano_publicacao')

        cursor.execute("UPDATE livros SET titulo = ?, autor = ?, ano_publicacao = ? WHERE id_livro = ?",
                       (titulo, autor, ano_publicacao, id))

        con.commit()
        cursor.close()

        return jsonify({
        'message': "Livro atualizado com sucesso!",
        'livro': {
            'id_livro': id,
            'titulo': titulo,
            'autor': autor,
            'ano_publicacao': ano_publicacao
            }
        })

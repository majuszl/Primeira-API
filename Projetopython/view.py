import re
from flask import Flask, jsonify, request, redirect, url_for, session
from main import app, con
from flask_bcrypt import generate_password_hash, check_password_hash

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

@app.route('/livros/<int:id>', methods=['DELETE'])
def deletar_livro(id):
    cursor = con.cursor() #abrindo o cursor

    #para verificar se o livro existe
    cursor.execute("SELECT 1 FROM livros WHERE id_livro = ?", (id,))
    if not cursor.fetchone(): #se não
        cursor.close() #fecha o cursor
        return jsonify({"error": "Livro não encontrado"}), 404 #A função jsonify converte objetos Python em strings JSON

    # para excluir o livro
    cursor.execute("DELETE FROM livros WHERE id_livro = ?", (id,))
    con.commit()
    cursor.close() #fecha o cursor

    return jsonify({ #retorne em JSON
        'message': "Livro excluído com sucesso!",
        'id_livro': id
    })

@app.route('/usuario', methods=['GET'])
def usuario():
    cur = con.cursor()  # abre o cursor para executar a instrução SQL
    cur.execute("SELECT id_usuario, nome, e_mail, senha FROM usuario")
    usuarios = cur.fetchall()  # percorrendo, cria uma lista dentro da lista de campos, fazendo com que cada livro com suas informções represente um item da lista
    usuarios_dic = []  # tranformando em dicionário
    for usuario in usuarios:
        usuarios_dic.append({
            'id_usuario': usuario[0],
            'nome': usuario[1],
            'e_mail': usuario[2],
            'senha': usuario[3],
        })
    return jsonify(mensagem='Lista de usuários', usuarios=usuarios_dic)  # transformando em JSON
def validar_senha(senha):
    padrao = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%¨&*])(?=.*\d).{8,}$'

    # verificando
    if re.fullmatch(padrao, senha):
        return True
    else:
        return False

@app.route('/adiciona_usuario', methods=['POST'])
def adiciona_usuario():
    data = request.get_json()
    nome = data.get('nome')
    e_mail = data.get('e_mail')
    senha = data.get('senha')

    if not validar_senha(senha):
        return jsonify ({
            'message': "A sua senha precisa ter pelo menos 8 caracteres, uma letra maiúscula, uma minúscula, um número e um caractere especial."
        })

    cursor = con.cursor()

    cursor.execute('SELECT FIRST 1 id_usuario FROM usuario WHERE e_mail = ?', (e_mail,))
    if cursor.fetchone():
            return jsonify ({
                'message': "Este e-mail já está sendo usado!"
            })

    senha = generate_password_hash(senha).decode('utf-8')

    cursor.execute("INSERT INTO usuario (nome, e_mail, senha) VALUES (?, ?, ?)", (nome, e_mail, senha))
    con.commit()
    cursor.close()

    return jsonify ({
        'message': "Usuário adicionado com sucesso!",
        'cadastro': {
            'nome': nome,
            'e_mail': e_mail,
            'senha': senha
        }
    })


@app.route('/editar_usuario/<int:id>', methods=['PUT'])
def editar_usuario(id):
    cursor = con.cursor()
    cursor.execute("SELECT id_usuario, nome, e_mail, senha FROM usuario WHERE id_usuario = ?", (id,))
    usuarios_data = cursor.fetchone()

    if not usuarios_data:
        cursor.close()
        return jsonify({"error": "O usuário não foi encontrado... ):"}), 404

    data = request.get_json()
    nome = data.get('nome')
    e_mail = data.get('e_mail')
    senha = data.get('senha')

    cursor.execute("UPDATE usuario SET nome = ?, e_mail = ?, autor = ? WHERE id_usuario = ?",
                   (nome, e_mail, senha, id))

    con.commit()
    cursor.close()

    return jsonify({
        'message': "Usuário atualizado com sucesso!",
        'Usuarios': {
            'id_usuario': id,
            'nome': nome,
            'e_mail': e_mail,
            'senha': senha
        }
    })
@app.route('/login', methods=['GET', 'POST'])
def login():
    data = request.get_json()
    e_mail = data.get('e_mail')
    senha = data.get('senha')

    cursor = con.cursor()
    cursor.execute("SELECT senha FROM usuario WHERE e_mail = ?", (e_mail,))
    senha_banco = cursor.fetchone()

    if not senha_banco:
        cursor.close()
        return jsonify({'message': "Login não encontrado..."})

    senha_hash = senha_banco[0]

    if check_password_hash(senha_hash, senha):
        return jsonify({ 'message': " Login feito com sucesso! (;"}), 200
    else:
        return jsonify ({ "error": "Usuário ou senha incorretos!"}), 401

@app.route('/deletar_usuario/<int:id>', methods=['DELETE'])
def deletar_usuario(id):
    cursor = con.cursor() #abrindo o cursor

    #para verificar se o livro existe
    cursor.execute("SELECT 1 FROM usuario WHERE id_usuario = ?", (id,))
    if not cursor.fetchone(): #se não
        cursor.close() #fecha o cursor
        return jsonify({"error": "Usuário não encontrado"}), 404 #A função jsonify converte objetos Python em strings JSON

    # para excluir o livro
    cursor.execute("DELETE FROM usuario WHERE id_usuario = ?", (id,))
    con.commit()
    cursor.close() #fecha o cursor

    return jsonify({ #retorne em JSON
        'message': "User excluído com sucesso!",
        'id_livro': id
    })






import re
from flask import Flask, jsonify, request, redirect, url_for, session, send_file
from main import app, con
from flask_bcrypt import generate_password_hash, check_password_hash
from fpdf import FPDF
import os

import jwt
app.config.from_pyfile('config.py')

senha_secreta = app.config['SECRET_KEY']

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def generated_token(user_id):
    payload = {'id_usuario': user_id}
    token = jwt.encode(payload, senha_secreta, algorithm='HS256')
    return token

def remover_bearer(token):
    if token.startwith('Bearer '):
        return token[len('Bearer '):]
    else:
        return token

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
    token = request.headers.get('Authorization')
    if not token:
       return jsonify({'mensagem': 'Token de autenticação necessário'}), 401

    token = remover_bearer(token)
    try:
        payload = jwt.decode(token, senha_secreta, algorithms=['HS256'])
        id_usuario = payload['id_usuario']
    except jwt.ExpiredSignatureError:
        return jsonify({'mensagem': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'mensagem': 'Token Inválido'}), 401

    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')
    ano_publicacao = data.get('ano_publicacao')

    cursor = con.cursor() # abrindo cursor

    cursor.execute("SELECT 1 FROM livros WHERE titulo = ?", (titulo, )) # 1 comprova a existência de algo, se não existir, retorna nulo

    if cursor.fetchone(): # se retornou um único registro (fetchone)
        return jsonify("Livro já cadastrado"), 400 # eu retorno que o livro já existe na tabela

    cursor.execute("INSERT INTO livros (titulo, autor, ano_publicacao) VALUES (?, ?, ?)", (titulo, autor, ano_publicacao))

    con.commit() # comitando o banco
    cursor.close() # fechando o cursor

    return jsonify({
        'message': "Livro cadastrado com sucesso!",
        'livro': {
            'titulo': titulo,
            'autor': autor,
            'ano_publicacao': ano_publicacao
        }
    }), 201

# IMAGEM
imagem = request.files.get('imagem')  # Arquivo enviado

# Insere o novo livro e retorna o ID gerado
cursor.execute(
    "INSERT INTO livros (TITULO, AUTOR, ANO_PUBLICACAO) VALUES (?, ?, ?) RETURNING ID_livro", (titulo, autor, ano_publicacao))
livro_id = cursor.fetchone()[0]
con.commit()

if imagem:
  nome_imagem = f"{livro_id}.jpeg"
  pasta_destino = os.path.join(app.config['UPLOAD_FOLDER'], "Livros")
  os.makedirs(pasta_destino, exist_ok=True)
  imagem_path = os.path.join(pasta_destino, nome_imagem)
  imagem.save(imagem_path)





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

# GERAR RELATÓRIO EM PDF -----------------------
@app.route('/livros/relatorio', methods=['GET'])
def gerar_relatorio():
    cursor = con.cursor()
    cursor.execute("SELECT id_livro, titulo, autor, ano_publicacao FROM livros")
    livros = cursor.fetchall()
    cursor.close()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Relatorio de Livros", ln=True, align='C')

    pdf.ln(5)  # Espaço entre o título e a linha
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())  # Linha abaixo do título
    pdf.ln(5)  # Espaço após a linha

    pdf.set_font("Arial", size=12)
    for livro in livros:
        pdf.cell(200, 10, f"ID: {livro[0]} - {livro[1]} - {livro[2]} - {livro[3]}", ln=True)

    contador_livros = len(livros)
    pdf.ln(10)  # Espaço antes do contador
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, f"Total de livros cadastrados: {contador_livros}", ln=True, align='C')

    pdf_path = "relatorio_livros.pdf"
    pdf.output(pdf_path)
    return send_file(pdf_path, as_attachment=True, mimetype='application/pdf')

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

    cursor.execute("SELECT senha, id_usuario FROM usuario WHERE e_mail = ?", (e_mail,))
    resultado = cursor.fetchone()
    cursor.close()

    if not resultado:
        return jsonify({'message': "Usuário não encontrado..."}), 404
    senha_hash = resultado[0]
    id_usuario = resultado[1]

    if check_password_hash(senha_hash, senha):
        token = generated_token(id_usuario)
        return jsonify({ 'message': "Login feito com sucesso! (;", 'token': token}), 200

    return jsonify({ "error": "E-mail ou senha incorretos!"}), 401

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










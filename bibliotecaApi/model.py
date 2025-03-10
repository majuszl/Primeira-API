import fdb

class Livros: #classe tem a primeira letra maiúscula
    def __int__(self, id_livro, titulo, autor, ano_publicacao): # "self" é ele mesmo
        self.id_livro = id_livro
        self.titulo = titulo
        self.autor = autor
        self.ano_publicacao = ano_publicacao

class Usuario:
    def __int__(self, id_usuario, nome, e_mail, senha): # "self" é ele mesmo
        self.id_usuario = id_usuario
        self.nome = nome
        self.e_mail = e_mail
        self.senha = senha

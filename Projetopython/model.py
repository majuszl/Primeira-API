import fdb

class Livros: #classe tem a primeira letra maiúscula
    def __int__(self, id_livro, titulo, autor, ano_publicacao): # "self" é ele mesmo
        self.id_livro = id_livro
        self.titulo = titulo
        self.autor = autor
        self.ano_publicacao = ano_publicacao

from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import declarative_base

# Conexão com o BD
db = create_engine("sqlite:///banco.db")

# Base do BD
Base = declarative_base()

# Criando tabelas do BD

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String, nullable=False)
    email = Column("email", String, nullable=False, unique=True)
    senha = Column("senha", String, nullable=False)
    perfil = Column("perfil", String,default="CLIENTE")
    ativo = Column("ativo", Integer, nullable=False, default=1)

    def __init__(self, nome, email, senha, perfil="CLIENTE", ativo=1):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.perfil = perfil
        self.ativo = ativo

class Pedido(Base):
    __tablename__ = "pedidos"
  
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    usuario = Column("usuario", ForeignKey("usuarios.id"), nullable=False)
    produto = Column("produto", ForeignKey("produtos.id"), nullable=False)
    quantidade = Column("quantidade", Integer, nullable=False)
    valor_total = Column("total", Float, nullable=False)
    status = Column("status", String, nullable=False,default="AGUARDANDO PAGAMENTO")
    canal = Column("canal", String, nullable=False)
    data = Column("data", String)

    def __init__(self, usuario, produto, quantidade, valor_total, data, canal, status="AGUARDANDO_PAGAMENTO"):
        self.usuario = usuario
        self.produto = produto
        self.quantidade = quantidade
        self.valor_total = valor_total
        self.canal = canal
        self.status = status
        self.data = data

class Produto(Base):
    __tablename__ = "produtos"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String, nullable=False)
    descricao = Column("descricao", String)
    preco = Column("preco", Float)
    estoque = Column("estoque", Integer, nullable=False, default=0)
    ativo = Column("ativo", Integer, nullable=False, default=1) 

    def __init__(self, nome, descricao, preco, estoque, ativo=1):
        self.nome = nome
        self.descricao = descricao
        self.preco = preco
        self.estoque = estoque
        self.ativo = ativo



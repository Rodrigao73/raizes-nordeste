from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import declarative_base

# Conexão com o BD
db = create_engine("sqlite:///banco.db")

# Base do BD
Base = declarative_base()

# Criando tabelas do BD

class Filial(Base):
    __tablename__ = "filiais"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String, nullable=False)
    cidade = Column("cidade", String, nullable=False)
    estado = Column("estado", String, nullable=False)
    ativa = Column("ativa", Integer, nullable=False, default=1) 

    def __init__(self, nome, cidade, estado, ativa=1):
        self.nome = nome
        self.cidade = cidade
        self.estado = estado
        self.ativa = ativa

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String, nullable=False)
    email = Column("email", String, nullable=False, unique=True)
    senha = Column("senha", String, nullable=False)
    perfil = Column("perfil", String,default="CLIENTE")
    filial = Column("filial_id", Integer, ForeignKey("filiais.id"),nullable=True)
    ativo = Column("ativo", Integer, nullable=False, default=1)

    def __init__(self, nome, email, senha, perfil="CLIENTE", filial_id=None, ativo=1):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.perfil = perfil
        self.filial = filial_id
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
    filial = Column("filial_id", Integer, ForeignKey("filiais.id"),nullable=False)
    data = Column("data", String)

    def __init__(self, usuario, produto, quantidade, valor_total, data, canal, filial_id, status="AGUARDANDO_PAGAMENTO"):
        self.usuario = usuario
        self.produto = produto
        self.quantidade = quantidade
        self.valor_total = valor_total
        self.canal = canal
        self.filial = filial_id
        self.status = status
        self.data = data

class Produto(Base):
    __tablename__ = "produtos"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String, nullable=False)
    descricao = Column("descricao", String)
    preco = Column("preco", Float)
    estoque = Column("estoque", Integer, nullable=False, default=0)
    filial = Column("filial_id", Integer, ForeignKey("filiais.id"),nullable=False)
    ativo = Column("ativo", Integer, nullable=False, default=1) 

    def __init__(self, nome, descricao, preco, estoque, filial_id, ativo=1):
        self.nome = nome
        self.descricao = descricao
        self.preco = preco
        self.estoque = estoque
        self.filial = filial_id
        self.ativo = ativo

class Fidelizacao(Base):
    __tablename__ = "fidelizacao"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    usuario_id = Column("usuario_id", Integer, ForeignKey("usuarios.id"), nullable=False)
    pontos_acumulados = Column("pontos_acumulados", Integer, nullable=False, default=0)
    pontos_trocados = Column("pontos_trocados", Integer, nullable=False, default=0)
    aprovacao = Column("aprovacao", Integer, nullable=False, default=0)
    data_adesao = Column("data_adesao", String, nullable=True)

    def __init__(self, usuario_id, aprovacao=0):
        self.usuario_id = usuario_id
        self.pontos_acumulados = 0
        self.pontos_trocados = 0
        self.aprovacao = aprovacao
        self.data_adesao = None
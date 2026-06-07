from pydantic import BaseModel
from typing import Optional

# Criando as classes

class UsuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str
    perfil: Optional[str] = "CLIENTE"

    class Config:
        from_attributes = True

class PedidoSchema(BaseModel):
    produto: int
    quantidade: int
    canal: str
  
    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email: str
    senha: str

    class Config:
        from_attributes = True

class ProdutoSchema(BaseModel):
    nome: str
    descricao: str
    preco: float
    estoque: int

    class Config:
        from_attributes = True

class AtualizarPedidoSchema(BaseModel):
    quantidade: int
    operacao: str

    class Config:
        from_attributes = True

class RealizarPagamento(BaseModel):
    id: int
    forma_pagamento: str

    class Config:
        from_attributes = True

class AtualizarStatusSchema(BaseModel):
    status: str

    class Config:
        from_attributes = True

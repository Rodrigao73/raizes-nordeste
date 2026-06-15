from pydantic import BaseModel, Field
from typing import Optional

# Criando as classes

class UsuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str
    perfil: Optional[str] = "CLIENTE"
    filial_id: Optional[int] = None

    class Config:
        from_attributes = True

class PedidoSchema(BaseModel):
    produto: int
    quantidade: int
    canal: str
    filial_id: int
    usar_pontos: Optional[int] = Field (
        default=0,
        ge=0,
        description="Quantidade de pontos para usar como desconto"
    )
  
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
    preco: float = Field(
        gt=0,
        description="O preço deve ser maior que zero"
    )
    estoque: int = Field(
        gt=0,
        description="O estoque deve ser maior que zero"
    )
 
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

class FilialSchema(BaseModel):
    nome: str
    cidade: str
    estado: str

    class Config:
        from_attributes = True

class AderirFidelizacaoSchema(BaseModel):
    aprovacao: bool

    class Config:
        from_attributes = True
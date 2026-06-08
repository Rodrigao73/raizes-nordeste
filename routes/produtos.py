from fastapi import APIRouter, Depends, HTTPException
from dependencies import pegar_sessao, exigir_perfil, verificar_token
from schemas import ProdutoSchema, AtualizarPedidoSchema
from models import Produto
from sqlalchemy.orm import Session
from constants import OPERACOES

produtos_router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"],
    dependencies=[Depends(verificar_token)]
)

# Cadastrar produto

@produtos_router.post(
    "/cadastrar-produto",
    status_code=201,
    description= "Para o usuário realizar o cadastro de um produto",
    dependencies=[Depends(exigir_perfil(["ADMIN"]))]
)
async def cadastrar_produto(
    produto_schema: ProdutoSchema,
    session: Session = Depends(pegar_sessao)
):

    existe = session.query(Produto).filter(
        Produto.nome == produto_schema.nome
    ).first()

    if existe:
        raise HTTPException(
            status_code=409,
            detail="Produto já cadastrado"
        )

    novo_produto = Produto(
        produto_schema.nome,
        produto_schema.descricao,
        produto_schema.preco,
        produto_schema.estoque
    )

    session.add(novo_produto)
    session.commit()
    session.refresh(novo_produto)

    return {
        "mensagem": f"O produto {produto_schema.nome} foi cadastrado com sucesso",
        "id": novo_produto.id
    }
    
# Listar produtos ativos

@produtos_router.get("/listar-produtos",
    description= "Para o usuário realizar a busca dos produtos ativos"
)
async def listar_produtos(session: Session = Depends(pegar_sessao)):

    resultado = session.query(Produto).filter(Produto.ativo == 1).all()

    produtos = []
    for p in resultado:
        produtos.append({
            "id": p.id,
            "nome": p.nome,
            "descricao": p.descricao,
            "preco": p.preco,
            "estoque": p.estoque
        })

    return produtos

# Atualizar estoque

@produtos_router.patch(
    "/{produto_id}/estoque",
    description="NA OPERAÇÃO USE ENTRADA PARA ADICIONAR MAIS PRODUTOS E AJUSTE PARA DIMINUIR",
    dependencies=[Depends(exigir_perfil(["ADMIN"]))]
)
async def atualizar_estoque(
    produto_id: int,
    dados: AtualizarPedidoSchema,
    session: Session = Depends(pegar_sessao)
):

    produto = session.query(Produto).filter(
        Produto.id == produto_id
    ).first()

    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )

    if dados.operacao not in OPERACOES:
        raise HTTPException(
            status_code=422,
            detail=f"Operação inválida. Use: {OPERACOES}"
        )
    if dados.operacao == "ENTRADA":
        novo_estoque = produto.estoque + dados.quantidade
    else:
        novo_estoque = dados.quantidade

    if novo_estoque < 0:
        raise HTTPException(
            status_code=409,
            detail=f"Estoque insuficiente. Disponível: {produto.estoque}"
        )

    produto.estoque = novo_estoque
    session.commit()

    return {
        "mensagem": "Estoque atualizado",
        "estoque_atual": novo_estoque
    }

# Inativar produto

@produtos_router.patch(
    "/{produto_id}/inativar",
    description= "Para o usuário realizar a inativação de um produto",
    dependencies=[Depends(exigir_perfil(["ADMIN"]))]
)
async def inativar_produto(
    produto_id: int,
    session: Session = Depends(pegar_sessao)
):

    produto = session.query(Produto).filter(
        Produto.id == produto_id
    ).first()

    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )

    if produto.ativo == 0:
        raise HTTPException(
            status_code=409,
            detail="Produto já está inativo"
        )

    produto.ativo = 0
    session.commit()

    return {
        "mensagem":f"O Produto: {produto.nome} foi inativado com sucesso"
    }
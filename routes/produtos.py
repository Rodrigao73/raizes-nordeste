from fastapi import APIRouter, Depends, HTTPException, Query
from dependencies import pegar_sessao, exigir_perfil, verificar_token, verificar_filial
from schemas import ProdutoSchema, AtualizarPedidoSchema, FilialSchema
from models import Produto, Usuario, Filial
from sqlalchemy.orm import Session
from constants import OPERACOES

produtos_router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"],
    dependencies=[Depends(verificar_token)]
)

produtos_publico_router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"]
)

# Cadastrar produto

@produtos_router.post(
    "/cadastrar-produto",
    status_code=201,
    description= "Para o ADMIN realizar o cadastro de um produto",
    dependencies=[Depends(exigir_perfil(["ADMIN"]))]
)
async def cadastrar_produto(
    produto_schema: ProdutoSchema,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)
):

    if not usuario.filial:
        raise HTTPException(
            status_code=403,
            detail="O usuário não está vinculado a nenhuma filial"
        )

    existe = session.query(Produto).filter(
        Produto.nome == produto_schema.nome,
        Produto.filial == usuario.filial
    ).first()

    if existe:
        raise HTTPException(
            status_code=409,
            detail="Produto já cadastrado nessa filial"
        )

    novo_produto = Produto(
        produto_schema.nome,
        produto_schema.descricao,
        produto_schema.preco,
        produto_schema.estoque,
        usuario.filial
    )

    session.add(novo_produto)
    session.commit()
    session.refresh(novo_produto)

    return {
        "mensagem": f"O produto {produto_schema.nome} foi cadastrado com sucesso",
        "id": novo_produto.id,
        "filial_id": novo_produto.filial
    }
    
# Listar produtos por filial

@produtos_publico_router.get(
    "/listar-produtos",
    dependencies=[],
    description= "Para o usuário realizar a busca dos produtos ativos."
)
async def listar_produtos(
    filial_id: int = Query(description="ID da filial"),
    session: Session = Depends(pegar_sessao)
):

    resultado = session.query(Produto).filter(
        Produto.filial == filial_id,
        Produto.ativo == 1).all()

    produtos = []
    
    for p in resultado:
        produtos.append({
            "id": p.id,
            "nome": p.nome,
            "descricao": p.descricao,
            "preco": p.preco,
            "estoque": p.estoque,
            "filial_id": p.filial
        })

    return produtos

# Atualizar estoque

@produtos_router.patch(
    "/{produto_id}/estoque",
    description=" Para o GERENTE e o ADMIN realizar o ajuste de estoque. Na operação use ENTRADA para adicionar mais produtos e AJUSTE para diminuir.",
    dependencies=[Depends(exigir_perfil(["ADMIN","GERENTE"]))]
)
async def atualizar_estoque(
    produto_id: int,
    dados: AtualizarPedidoSchema,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)
):

    produto = session.query(Produto).filter(
        Produto.id == produto_id
    ).first()

    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )

    verificar_filial(usuario, produto.filial)

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
    description= "Para o ADMIN realizar a inativação de um produto",
    dependencies=[Depends(exigir_perfil(["ADMIN"]))]
)
async def inativar_produto(
    produto_id: int,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)
):

    produto = session.query(Produto).filter(
        Produto.id == produto_id
    ).first()

    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )

    verificar_filial(usuario, produto.filial)

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
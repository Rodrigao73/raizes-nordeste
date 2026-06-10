from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token, exigir_perfil
from schemas import PedidoSchema, AtualizarStatusSchema
from models import Pedido, Usuario, Produto
from datetime import datetime
from constants import STATUS, CANAIS

pedidos_router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"],
    dependencies=[Depends(verificar_token)]
)

# Criar pedido

@pedidos_router.post("/criar-pedido", 
    status_code=201,
    dependencies=[Depends(exigir_perfil(["CLIENTE"]))],
    description="OS CANAIS VÁLIDOS SÃO: APP, TOTEM, BALCAO, PICKUP E WEB."
)
async def criar_pedido(
    pedido_schema: PedidoSchema,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)
):

    if pedido_schema.canal not in CANAIS:
        raise HTTPException(
            status_code=422,
            detail=f"Canal inválido. Use: {CANAIS}"
        )

    produto = session.query(Produto).filter(
        Produto.id == pedido_schema.produto,
        Produto.ativo == 1
    ).first()

    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )

    if produto.estoque < pedido_schema.quantidade:
        raise HTTPException(
            status_code=409,
            detail=f"Estoque insuficiente. Disponível: {produto.estoque}"
        )

    valor_total = produto.preco * pedido_schema.quantidade

    novo_pedido = Pedido(
        usuario=usuario.id,
        produto=pedido_schema.produto,
        quantidade=pedido_schema.quantidade,
        valor_total=valor_total,
        canal=pedido_schema.canal,
        status="AGUARDANDO_PAGAMENTO",
        data=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    produto.estoque -= pedido_schema.quantidade

    session.add(novo_pedido)
    session.commit()
    session.refresh(novo_pedido)
    
    return {
        "id_pedido": novo_pedido.id,
        "canal": novo_pedido.canal,
        "valor_total": novo_pedido.valor_total,
        "status": novo_pedido.status,
        "mensagem": "Pedido criado com sucesso"
    }


# Listar pedidos com filtros

@pedidos_router.get("/listar-pedidos",
    description= "Para o usuário realizar os filtros de busca",
    dependencies=[Depends(exigir_perfil(["ADMIN", "GERENTE", "CLIENTE","COZINHA"]))]
)
async def listar_pedidos(
    id_pedido: int = Query(default=None, description="Filtrar por ID do pedido"),
    id_usuario: int = Query(default=None, description="Filtrar por ID do usuário"),
    canal: str = Query(default=None, description="Filtrar por canal"),
    status: str = Query(default=None, description="Filtrar por status"),
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)
):
    query = session.query(Pedido)

    if usuario.perfil == "CLIENTE":
        query = query.filter(Pedido.usuario == usuario.id)
    else:
        if id_usuario:
            query = query.filter(Pedido.usuario == id_usuario)

    if id_pedido:
        query = query.filter(Pedido.id == id_pedido)

    if canal:
        if canal not in CANAIS:
            raise HTTPException(
                status_code=422,
                detail=f"Canal inválido. Use: {CANAIS}"
            )
        query = query.filter(Pedido.canal == canal)

    if status:
        if status not in STATUS:
            raise HTTPException(
                status_code=422,
                detail=f"Status inválido. Use: {STATUS}"
            )
        query = query.filter(Pedido.status == status)

    resultado = query.all()

    pedidos = []
    for p in resultado:
        pedidos.append({
            "id": p.id,
            "usuario_id": p.usuario,
            "produto_id": p.produto,
            "quantidade": p.quantidade,
            "valor_total": p.valor_total,
            "status": p.status,
            "canal": p.canal,
            "data": p.data
        })

    return pedidos

# Atualizar status do pedido

@pedidos_router.patch("/{id_pedido}/status",
    description= "OS STATUS PERMITIDOS SÃO: AGUARDANDO_PAGAMENTO, EM_PREPARACAO, PRONTO, ENTREGUE E CANCELADO.",
    dependencies=[Depends(exigir_perfil(["ADMIN", "GERENTE", "CLIENTE", "COZINHA"]))]
)
async def atualizar_status(
    id_pedido: int,
    dados: AtualizarStatusSchema,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)
):

    if dados.status not in STATUS:
        raise HTTPException(
            status_code=422,
            detail=f"Status inválido. Use: {STATUS}"
        )

    pedido = session.query(Pedido).filter(
        Pedido.id == id_pedido
    ).first()

    if not pedido:
        raise HTTPException(
            status_code=404,
            detail="Pedido não encontrado"
        )

    if usuario.perfil == "CLIENTE":
        if pedido.usuario != usuario.id:
            raise HTTPException(
                status_code=403,
                detail="Você não tem permissão para alterar esse pedido"
            )
        if dados.status != "CANCELADO":
            raise HTTPException(
                status_code=403,
                detail="Cliente só pode cancelar pedidos"
            )

    status_anterior = pedido.status
    pedido.status = dados.status

    if dados.status == "CANCELADO" and status_anterior != "CANCELADO":
        produto = session.query(Produto).filter(
            Produto.id == pedido.produto
        ).first()

        if produto:
            produto.estoque += pedido.quantidade

    session.commit()

    return {
        "id_pedido": id_pedido,
        "status_anterior": status_anterior,
        "status_atual": pedido.status,
        "mensagem": "Status atualizado com sucesso"
    }
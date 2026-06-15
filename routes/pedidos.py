from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token, exigir_perfil, verificar_filial
from schemas import PedidoSchema, AtualizarStatusSchema
from models import Pedido, Usuario, Produto, Filial, Fidelizacao
from datetime import datetime
from constants import STATUS, CANAIS

pedidos_router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"],
    dependencies=[Depends(verificar_token)]
)

# Criar pedido
@pedidos_router.post(
    "/criar-pedido",
    status_code=201,
    dependencies=[Depends(exigir_perfil(["CLIENTE"]))],
    description="Para o CLIENTE realizar os seus pedidos. Os canais válidos são: APP, TOTEM, BALCAO, PICKUP e WEB."
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

    filial = session.query(Filial).filter(
        Filial.id == pedido_schema.filial_id,
        Filial.ativa == 1
    ).first()

    if not filial:
        raise HTTPException(
            status_code=404,
            detail="Filial inativa ou não encontrada"
        )

    produto = session.query(Produto).filter(
        Produto.id == pedido_schema.produto,
        Produto.filial == pedido_schema.filial_id,
        Produto.ativo == 1
    ).first()

    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado nessa filial"
        )

    if produto.estoque < pedido_schema.quantidade:
        raise HTTPException(
            status_code=409,
            detail=f"Estoque insuficiente. Disponível: {produto.estoque}"
        )

    valor_total = round(produto.preco * pedido_schema.quantidade, 2)

    if pedido_schema.usar_pontos and pedido_schema.usar_pontos > 0:
        fidelizacao = session.query(Fidelizacao).filter(
            Fidelizacao.usuario_id == usuario.id,
            Fidelizacao.aprovacao == 1
        ).first()

        if not fidelizacao:
            raise HTTPException(
                status_code=409,
                detail="Você ainda não está cadastrado no programa de fidelidade"
            )

        pontos_disponiveis = (
            fidelizacao.pontos_acumulados - fidelizacao.pontos_trocados
        )

        if pedido_schema.usar_pontos > pontos_disponiveis:
            raise HTTPException(
                status_code=409,
                detail=f"A quantidade de pontos é insuficiente. Disponível: {pontos_disponiveis}"
            )

        desconto = round(pedido_schema.usar_pontos * 0.05, 2)

        desconto = min(desconto, valor_total)

        valor_total = round(valor_total - desconto, 2)

        fidelizacao.pontos_trocados += pedido_schema.usar_pontos

    novo_pedido = Pedido(
        usuario=usuario.id,
        produto=pedido_schema.produto,
        quantidade=pedido_schema.quantidade,
        valor_total=valor_total,
        canal=pedido_schema.canal,
        filial_id=pedido_schema.filial_id,
        status="AGUARDANDO_PAGAMENTO",
        data=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    produto.estoque -= pedido_schema.quantidade

    session.add(novo_pedido)
    session.commit()
    session.refresh(novo_pedido)

    return {
        "id_pedido": novo_pedido.id,
        "filial": filial.nome,
        "canal": novo_pedido.canal,
        "valor_total": novo_pedido.valor_total,
        "desconto_aplicado": round(pedido_schema.usar_pontos * 0.05, 2) if pedido_schema.usar_pontos else 0,
        "status": novo_pedido.status,
        "mensagem": "Pedido criado com sucesso"
    }


# Listar pedidos

@pedidos_router.get(
    "/listar-pedidos",
    description="Para o usuário realizar os filtros dos pedidos.",
    dependencies=[Depends(exigir_perfil(["ADMIN", "GERENTE", "CLIENTE", "COZINHA", "SUPER_ADMIN"]))]
)
async def listar_pedidos(
    filial_id: int = Query(default=None, description="Filtrar por filial"),
    id_pedido: int = Query(default=None, description="Filtrar por ID do pedido"),
    canal: str = Query(default=None, description="Filtrar por canal"),
    status: str = Query(default=None, description="Filtrar por status"),
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)
):
    query = session.query(Pedido)

    if usuario.perfil == "SUPER_ADMIN":
        resultado = session.query(Usuario).all()
    if usuario.perfil == "CLIENTE":
        query = query.filter(Pedido.usuario == usuario.id)
        if id_pedido:
            query = query.filter(Pedido.id == id_pedido)

    elif usuario.perfil in ["ADMIN", "GERENTE", "COZINHA"]:
        query = query.filter(Pedido.filial == usuario.filial)
        if filial_id and filial_id != usuario.filial:
            raise HTTPException(
                status_code=403,
                detail="Você só tem acesso aos pedidos da sua filial"
            )
        if id_pedido:
            query = query.filter(Pedido.id == id_pedido)

    else:
        if filial_id:
            query = query.filter(Pedido.filial == filial_id)
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
            "filial_id": p.filial,
            "data": p.data
        })

    return pedidos


# Atualizar status do pedido

@pedidos_router.patch(
    "/{id_pedido}/status",
    description="Para atualizar o status do pedido. Os status permitidos são: AGUARDANDO_PAGAMENTO, EM_PREPARACAO, PRONTO, ENTREGUE E CANCELADO.",
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

    if usuario.perfil in ["ADMIN", "GERENTE", "COZINHA"]:
        verificar_filial(usuario, pedido.filial)

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
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import verificar_token, pegar_sessao, exigir_perfil
from schemas import RealizarPagamento
from models import Usuario, Pedido
from constants import FORMAS_PAGAMENTO
import random

pagamentos_router = APIRouter(
    prefix="/pagamentos",
    tags=["Pagamentos"]
)

# Para realizar o pagamento

@pagamentos_router.post("/realizar-pagamento",
    summary="Realizar Pagamento",
    dependencies=[Depends(exigir_perfil(["CLIENTE"]))],
    description="Para o CLIENTE realizar o pagamento do pedido. As formas de pagamento aceitas são: PIX, CARTAO_CREDITO, CARTAO_DEBITO, E DINHEIRO."
)
async def realizar_pagamento(
    dados: RealizarPagamento,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(exigir_perfil(["CLIENTE"]))
):
    
    if dados.forma_pagamento not in FORMAS_PAGAMENTO:
         raise HTTPException(
            status_code=422,
            detail=f"Forma inválida. Use: {FORMAS_PAGAMENTO}"
        )

    pedido = session.query(Pedido).filter(Pedido.id==dados.id).first()

    if not pedido:
        raise HTTPException(
            status_code=404,
            detail= "Pedido não encontrado",
        )
        
    if usuario.perfil == "CLIENTE" and pedido.usuario != usuario.id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para pagar esse pedido"
        )

    if pedido.status != "AGUARDANDO_PAGAMENTO":
        raise HTTPException(
            status_code=409,
            detail=f"O Pedido não pode ser pago. Status atual: {pedido.status}"
        )

    aprovado = random.random() > 0.25

    if aprovado:
        novo_status = "EM_PREPARACAO"
        resultado = "APROVADO"

    else:
        novo_status = "CANCELADO"
        resultado = "RECUSADO"

    pedido.status= novo_status

    session.commit()

    return {
        "id_pedido": pedido.id,
        "canal_pedido": pedido.canal,
        "forma_pagamento": dados.forma_pagamento,
        "valor_total": pedido.valor_total,
        "status_pagamento": resultado,
        "status_pedido": novo_status,
        "mensagem": (
            "Pagamento aprovado! Pedido em preparação."
            if aprovado else
            "Pagamento recusado. Tente novamente."
        )
    }


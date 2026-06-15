from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token, exigir_perfil
from schemas import AderirFidelizacaoSchema
from models import Fidelizacao, Usuario
from datetime import datetime

fidelizacao_router = APIRouter(
    prefix="/fidelizacao",
    tags=["Fidelização"],
    dependencies=[Depends(verificar_token)]
)

# Adesão ao programa de fidelização

@fidelizacao_router.post(
    "/aderir",
    status_code=201,
    dependencies=[Depends(exigir_perfil(["CLIENTE"]))],
    description="O cliente aprova e adere ao programa de fidelização"
)
async def aderir_fidelizacao(
    dados: AderirFidelizacaoSchema,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)
):

    ja_aderiu = session.query(Fidelizacao).filter(
        Fidelizacao.usuario_id == usuario.id
    ).first()

    if ja_aderiu:
        raise HTTPException(
            status_code=409,
            detail="Você já está cadastrado no programa de fidelização"
        )

    if not dados.aprovacao:
        raise HTTPException(
            status_code=422,
            detail="É necessário aprovar o uso dos seus dados para aderir ao programa"
        )

    novo_cadastro = Fidelizacao(
        usuario_id=usuario.id,
        aprovacao=1
    )

    novo_cadastro.data_adesao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    session.add(novo_cadastro)
    session.commit()
    session.refresh(novo_cadastro)

    return {
        "mensagem": "Adesão ao programa de fidelização realizada com sucesso",
        "usuario_id": usuario.id,
        "pontos_acumulados": novo_cadastro.pontos_acumulados,
        "data_adesao": novo_cadastro.data_adesao
    }


# Consultar saldo de pontos

@fidelizacao_router.get(
    "/saldo",
    dependencies=[Depends(exigir_perfil(["CLIENTE"]))],
    description="Consulta o saldo de pontos do cliente"
)
async def consultar_saldo(
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)
):
    fidelizacao = session.query(Fidelizacao).filter(
        Fidelizacao.usuario_id == usuario.id
    ).first()

    if not fidelizacao:
        raise HTTPException(
            status_code=404,
            detail="Você não está cadastrado no programa de fidelização"
        )

    pontos_disponiveis = (
        fidelizacao.pontos_acumulados - fidelizacao.pontos_trocados
    )

    return {
        "usuario_id": usuario.id,
        "pontos_acumulados": fidelizacao.pontos_acumulados,
        "pontos_trocados": fidelizacao.pontos_trocados,
        "pontos_disponiveis": pontos_disponiveis,
        "data_adesao": fidelizacao.data_adesao
    }
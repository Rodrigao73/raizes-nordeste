from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, exigir_perfil
from schemas import FilialSchema
from models import Filial

filiais_router = APIRouter(
    prefix="/filiais",
    tags=["Filiais"]
)

# Cadastros de filiais

@filiais_router.post(
    "/cadastrar-filial",
    status_code=201,
    description="Para o SUPER_ADMIN realizar o cadastro de uma nova filial.",
    dependencies=[Depends(exigir_perfil(["SUPER_ADMIN"]))]
)
async def cadastrar_filial(
    dados: FilialSchema,
    session: Session = Depends(pegar_sessao)
):
    existe = session.query(Filial).filter(
        Filial.nome == dados.nome,
        Filial.cidade == dados.cidade
    ).first()

    if existe:
            raise HTTPException(
                status_code=409,
                detail="Já existe uma filial com o mesmo nome cadastrada nessa cidade"
            )

    nova_filial = Filial(
            dados.nome,
            dados.cidade,
            dados.estado
        )

    session.add(nova_filial)
    session.commit()
    session.refresh(nova_filial)

    return {
        "mensagem": f"A filial {dados.nome} - {dados.cidade} foi cadastrada com sucesso"
    }

# Listar filiais

@filiais_router.get(
    "/listar-filiais",
    description="Para os usuários listarem as filiais ativas."
)
async def listar_filiais(session: Session = Depends(pegar_sessao)):

    resultado = session.query(Filial).filter(Filial.ativa == 1).all()

    filiais = []

    for f in resultado:
        filiais.append({
            "id": f.id,
            "nome": f.nome,
            "cidade": f.cidade,
            "estado": f.estado
        })

    return filiais

# Inativar Filial

@filiais_router.patch(
    "/{filial_id}/inativar",
    description="Para o SUPER_ADMIN inativar uma filial.",
    dependencies=[Depends(exigir_perfil(["SUPER_ADMIN"]))]
)
async def inativar_filial(
    filial_id: int,
    session: Session = Depends(pegar_sessao)
):
    filial = session.query(Filial).filter(
        Filial.id == filial_id
    ).first()

    if not filial:
        raise HTTPException(
            status_code=404,
            detail="A filial não foi encontrada"
        )

    if filial.ativa == 0:
        raise HTTPException(
            status_code=409,
            detail="A filial já está inativa"
        )
    
    filial.ativa = 0
    session.commit()

    return {
        "mensagem": f" A filial {filial.nome} - {filial.cidade} foi inativada com sucesso"
    }


    
from fastapi import APIRouter, Depends, HTTPException
from models import Usuario
from dependencies import pegar_sessao, exigir_perfil, verificar_filial, verificar_token
from config import bcrypt_context
from schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session
from routes.login import criar_token, autenticar_usuario

usuarios_router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)

# Cadastrar usuário

@usuarios_router.post(
    "/criar-conta",
    description="Para realizar o cadastro de um novo usuário. Os perfis podem ser: SUPER_ADMIN, ADMIN, GERENTE, CLIENTE E COZINHA.",
    status_code=201
)
async def criar_conta(
    usuario_schema: UsuarioSchema,
    session: Session = Depends(pegar_sessao)
):
    existe = session.query(Usuario).filter(
        Usuario.email == usuario_schema.email
    ).first()

    if existe:
        raise HTTPException(
            status_code=409,
            detail="Já existe um usuário com esse e-mail"
        )

    senha_criptografada = bcrypt_context.hash(usuario_schema.senha)

    if usuario_schema.perfil != "SUPER_ADMIN" and not usuario_schema.filial_id:
        raise HTTPException(
            status_code=422,
            detail="Apenas o usuário SUPER_ADMIN pode ser cadastrado sem filial, por favor vincular uma filial no seu usuário."
        )

    novo_usuario = Usuario(
    usuario_schema.nome,
    usuario_schema.email,
    senha_criptografada,
    usuario_schema.perfil,
    usuario_schema.filial_id
    )

    session.add(novo_usuario)
    session.commit()
    session.refresh(novo_usuario)

    return {
        "mensagem": f"Usuário {usuario_schema.email} cadastrado com sucesso",
        "id": novo_usuario.id,
        "perfil": novo_usuario.perfil
    }

# Listar usuários

@usuarios_router.get(
    "/listar-usuarios",
    description="Para listar os usuários cadastrados.",
    dependencies=[Depends(exigir_perfil(["ADMIN","GERENTE","SUPER_ADMIN"]))]
)
async def listar_usuarios(
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)
):

    if usuario.perfil == "SUPER_ADMIN":
        resultado = session.query(Usuario).all()
    else:
        resultado = session.query(Usuario).filter(
            Usuario.filial == usuario.filial
        ).all()

    usuarios = [
        {
            "id": u.id,
            "nome": u.nome,
            "email": u.email,
            "perfil": u.perfil,
            "ativo": u.ativo
        }
        for u in resultado
    ]

    return usuarios

# Inativar usuário

@usuarios_router.patch(
    "/{usuario_id}/inativar",
    description="Para realizar a inativação de um usuário. Apenas ADMIN e SUPER_ADMIN tem essa permissão.",
    dependencies=[Depends(exigir_perfil(["ADMIN", "SUPER_ADMIN"]))]
)
async def inativar_usuario(
    usuario_id: int,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)
):
    alvo = session.query(Usuario).filter(
        Usuario.id == usuario_id
    ).first()

    if not alvo:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    if usuario.perfil != "SUPER_ADMIN":
        verificar_filial(usuario, alvo.filial)

    if alvo.ativo == 0:
        raise HTTPException(
            status_code=409,
            detail="Usuário já está inativo"
        )

    usuario.ativo = 0
    session.commit()

    return {
        "mensagem": f"O usuário: {alvo.email} foi inativado com sucesso"
    }
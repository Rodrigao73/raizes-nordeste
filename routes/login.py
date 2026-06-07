from fastapi import APIRouter, Depends, HTTPException
from schemas import LoginSchema
from dependencies import pegar_sessao
from config import bcrypt_context, ALGORITHM, ACESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from models import Usuario
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta, timezone

login_router = APIRouter(
    prefix="/login",
    tags=["Login"]
)

# Criação do token

def criar_token(usuario: Usuario) -> str:
    data_expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=ACESS_TOKEN_EXPIRE_MINUTES
    )
    dados = {
        "sub": str(usuario.id),
        "perfil": usuario.perfil,
        "exp": data_expiracao
    }
    token = jwt.encode(dados, SECRET_KEY, algorithm=ALGORITHM)
    return token

# Valida a senha

def autenticar_usuario(email: str, senha: str, session: Session):
    usuario = session.query(Usuario).filter(
        Usuario.email == email
    ).first()

    if not usuario:
        return None

    if not bcrypt_context.verify(senha, usuario.senha):
        return None

    return usuario

# Login

@login_router.post("/",
    summary="Login",
    description="usuário administrador: admin@admin.com / senha: admin"    
)
async def login(
    dados: LoginSchema,
    session: Session = Depends(pegar_sessao)
):
    usuario = autenticar_usuario(dados.email, dados.senha, session)

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha inválidos"
        )

    token = criar_token(usuario)

    return {
        "access_token": token,
        "token_type": "Bearer",
        "perfil": usuario.perfil
    }
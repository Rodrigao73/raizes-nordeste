from fastapi import Depends, HTTPException
from config import SECRET_KEY, ALGORITHM, oauth_schema
from models import db
from sqlalchemy.orm import sessionmaker, Session
from models import Usuario
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Abertura e fechamento correto do BD 

def pegar_sessao():

    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
        
    finally:
        session.close()

# Validação do token

def verificar_token (
    credenciais: HTTPAuthorizationCredentials = Depends(oauth_schema), 
    session: Session = Depends(pegar_sessao)
    ):

    try:
        dic = jwt.decode(
        credenciais.credentials, 
        SECRET_KEY, 
        algorithms=[ALGORITHM]
        )

        id_usuario = int(dic.get("sub"))

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Acesso negado, por favor verifique a validade do token"
        )
    usuario = session.query(Usuario).filter(Usuario.id==id_usuario).first()

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Acesso inválido"
        )
        
    return usuario

# Autorização de perfil

def exigir_perfil(perfis_autorizados: list):
    def verificar(usuario: Usuario = Depends(verificar_token)):
        
        if usuario.perfil not in perfis_autorizados:
            raise HTTPException(
                status_code=403,
                detail="Você não tem permissão para esta ação"
            )
        
        return usuario
        
    return verificar

# Verifica se usuário tem acesso à filial

def verificar_filial(usuario: Usuario, filial_id: int):
    if usuario.perfil == "SUPER_ADMIN":
        return True
    if usuario.filial != filial_id:
        raise HTTPException(
            status_code=403,
            detail="Você só tem acesso aos dados da sua filial"
        )
    return True
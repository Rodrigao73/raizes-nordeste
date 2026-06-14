from fastapi import FastAPI
from models import Base,db

app = FastAPI(
    title="Sistema de Pedidos - Raizes do Nordeste",
    description="""

## API de gerenciamento de pedidos

Projeto acadêmico da disciplina de **Desenvolvimento Back-End**

    version="1.0.0",
    contact={
        "name": "Rodrigo Oliveira",
        "e-mail": "4826339@alunouninter.com",
        "RU": "4826339"
    }
    
""")

Base.metadata.create_all(bind=db)

from routes.pagamentos import pagamentos_router
from routes.pedidos import pedidos_router
from routes.produtos import produtos_router, produtos_publico_router
from routes.usuarios import usuarios_router
from routes.login import login_router
from routes.filiais import filiais_router

@app.get(
    "/",
    tags=["Sistema"],
    summary="Página Inicial",
    description="Verificar funcionamento da API"
)

async def home():

    return {
        "mensagem": "API funcionando com sucesso"
    }

app.include_router(usuarios_router)
app.include_router(login_router)
app.include_router(produtos_router)
app.include_router(pedidos_router)
app.include_router(pagamentos_router)
app.include_router(produtos_publico_router)
app.include_router(filiais_router)

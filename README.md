# Raizes do Nordeste

A API foi constuida usando: Python 3.13, FastAPI, SQLAlchemy, JWT (python-jose), Bcrypt (passlib), Pydantic Uvicorn, SQLAlchemy e SQLite como banco de dados.

**Aluno:** Rodrigo Oliveira  
**RU:** 4826339  
**Trilha:** Back-end

A API simula a funcionalidade de uma plataforma de rede de lanchonetes Raízes do Nordeste com objetivo de promover a culinária nordestina.

---

## Índice

- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Instruções para uso](#instruções-para-uso)
- [API Endpoints](#api-endpoints)
- [Fluxo principal](#fluxo-principal)
- [Autenticação](#autenticação)
- [Coleção Postman](#coleção-postman)

---

## Requisitos

- Python 3.10 ou superior
- pip

---

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/Rodrigao73/raizes-nordeste.git
cd raizes-nordeste
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv venv

# Windows

venv\Scripts\activate

# Linux/Mac

source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install fastapi uvicorn sqlalchemy python-jose passlib bcrypt python-dotenv pydantic
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

SECRET_KEY=sua_chave_secreta_aqui
ALGORITHM=HS256
ACESS_TOKEN_EXPIRE_MINUTES=60

---

## Instruções para uso

### 1. Inicie a API

```bash
uvicorn main:app --reload
```

### 2. Acesse a documentação

Abra no navegador: http://localhost:8000/docs

---

## API Endpoints

**GET PÁGINA INICIAL**

GET / - É a página inicial do sistema.

```json
[
    {
        "mensagem": "API funcionando com sucesso"
    }
]
```

---

**GET USUÁRIOS**

GET /usuarios/listar-usuarios - Utilizado para administradores listarem as contas de todos os usuários.

```json
[
    {
        "id": 1,
        "nome": "Pedro",
        "email": "pedro@example.com",
        "perfil": "CLIENTE",
        "ativo": "0"
    },
    {
        "id": 2,
        "nome": "Carlos",
        "email": "Carlos@example.com",
        "perfil": "ADMIN",
        "ativo": "0"
    }
]
```

**POST USUÁRIOS**

POST /usuarios/criar-conta - Utilizado para criar as contas de usuários.

```json
[
    {
        "nome": "Lucas",
        "email": "Lucas@example.com",
	"senha": "123"
        "perfil": "CLIENTE"
    }
]
```

**PATCH USUÁRIOS**

PATCH /usuarios/{usuario_id}/inativar - Utilizado para administradores inativarem usuários.

``` json
{
  "mensagem": "O usuário: xxx@gmail.com foi inativado com sucesso"
}

```

**POST LOGIN**

POST /login/ - Utilizado para o usuário logar na sua conta

```json
[
    {
        "email": "Anna@example.com",
	"senha": "456"
    }
]
```

**GET PRODUTOS**

GET /produtos/listar-produtos - Utilizado para os usuários visualizarem o que tem disponível no estoque.

```json
[
  {
    "id": 1,
    "nome": "Cuscuz",
    "descricao": "Com ovo e manteiga",
    "preco": 10,
    "estoque": 30
  },
  {
    "id": 2,
    "nome": "Tapioca",
    "descricao": "Com queijo",
    "preco": 5,
    "estoque": 10
  }
]
```

**POST PRODUTOS**

POST /produtos/cadastrar-produto - Para os administradores cadastrarem novos produtos no sistema.

```json
[
  {
  "nome": "Pão",
  "descricao": "Com queijo e ovo",
  "preco": 5,
  "estoque":20
  }
]
```

**PATCH PRODUTOS**

PATCH /produtos/{produto_id}/estoque - Para os gerentes e administradores atualizarem o estoque de forma manual.

```json
[
  {	
  "mensagem": "Estoque atualizado",
  "estoque_atual": 10
  }
]
```

PATCH /produtos/{produto_id}/inativar - Para os administradores inativarem produtos que não serão mais utilizados.

``` json
{
  "mensagem": "O produto: Tapioca foi inativado com sucesso"
}
```

**GET PEDIDOS**

GET /pedidos/listar-pedidos - Utilizado para administradores listarem todos os pedidos e os usuários apenas os seus pedidos.

```json
[
  {
    "id": 1,
    "usuario_id": 1,
    "produto_id": 1,
    "quantidade": 2,
    "valor_total": 25.80,
    "status": "AGUARDANDO_PAGAMENTO",
    "canal": "APP",
    "data": "2026-06-06 18:21:00"
  }
]
```

**POST PEDIDOS**

POST /pedidos/criar-pedido - Utilizado para criar os pedidos no sistema.

```json
[
  {
    "id": 1,
    "usuario_id": 1,
    "produto_id": 1,
    "quantidade": 1,
    "valor_total": 70,
    "status": "ENTREGUE",
    "canal": "APP",
    "data": "2026-06-06 18:21:00"
  }
]
```

**PATCH PEDIDOS**

PATCH /pedidos/{id_pedido}/status - Utilizado para administradores, usuários, gerentes e a a equipe da cozinha para alterar o status do pedido.

```json
[
  {
  "id_pedido": 5,
  "status_anterior": "PRONTO",
  "status_atual": "ENTREGUE",
  "mensagem": "Status atualizado com sucesso"
  }
]
```

**POST PAGAMENTOS**

POST /pagamentos/realizar-pagamento - Utilizado para realizar os pagamentos.

```json
[
  {
  "id_pedido": 7,
  "canal_pedido": "PICKUP",
  "forma_pagamento": "PIX",
  "valor_total": 20,
  "status_pagamento": "APROVADO",
  "status_pedido": "EM_PREPARACAO",
  "mensagem": "Pagamento aprovado! Pedido em preparação."
  }
]
```
---

## Fluxo principal

1. Cadastre um usuário em `POST /usuarios/criar-conta`
2. Faça login em `POST /usuarios/login`
3. Copie o token e clique em **Authorize** no Swagger
4. Crie um pedido em `POST /pedidos/`
5. Realize o pagamento em `POST /pagamentos/realizar-pagamento/`
6. Acompanhe o status em `GET /pedidos/`

---

## Autenticação

A API utiliza o FastAPI Secutiry para controle de autenticação. Os seguintes perfis estão disponíveis:

```bash
CLIENTE - Criar pedido, listar próprios pedidos, realizar pagamento, cancelar próprio pedido 
ADMIN - Acesso total — cadastrar produtos, listar usuários, atualizar estoque, gerenciar pedidos 
GERENTE - Atualizar estoque e status de pedidos 
COZINHA - Atualizar status de pedidos 
```

---

## Coleção Postman

O arquivo `colecao_postman.json` está na raiz do repositório com os cenários de teste organizados.
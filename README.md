# RAÍZES DO NORDESTE

A API foi constuida usando: Python 3.13, FastAPI, JWT (python-jose), Bcrypt (passlib), Pydantic, Uvicorn, SQLAlchemy e SQLite como banco de dados.

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
ACCESS_TOKEN_EXPIRE_MINUTES=60  

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
        "ativo": "1"
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
	    "senha": "123",
        "perfil": "CLIENTE",
        "filial_id": 0
    }
]
```

**PATCH USUÁRIOS**

PATCH /usuarios/{usuario_id}/inativar - Utilizado para administradores inativarem usuários.

``` json
[
    {
        "mensagem": "O usuário: rodrigo@gmail.com foi inativado com sucesso"
    }
]

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

GET /produtos/listar-produtos - Utilizado para A visualização do que tem disponível no estoque.

```json
[
    {
        "id": 1,
        "nome": "Cuscuz",
        "descricao": "Com ovo e manteiga",
        "preco": 10,
        "estoque": 30,
        "filial_id": 1
    },
    {
        "id": 2,
        "nome": "Tapioca",
        "descricao": "Com queijo",
        "preco": 5,
        "estoque": 10,
        "filial_id": 2
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
[
    {
        "mensagem": "O produto: Tapioca foi inativado com sucesso"
    }
]
```

**GET PEDIDOS**

GET /pedidos/listar-pedidos - Utilizado para administradores listarem todos os pedidos e os usuários apenas os seus pedidos.

```json
[
    {
        "id": 1,
        "usuario_id": 5,
        "produto_id": 1,
        "quantidade": 1,
        "valor_total": 30.99,
        "status": "ENTREGUE",
        "canal": "APP",
        "filial_id": 1,
        "data": "2026-06-13 13:35:22"
    },
    {
        "id": 2,
        "usuario_id": 5,
        "produto_id": 1,
        "quantidade": 1,
        "valor_total": 30.99,
        "status": "EM_PREPARACAO",
        "canal": "APP",
        "filial_id": 1,
        "data": "2026-06-13 13:35:33"
    }
]
```

**POST PEDIDOS**

POST /pedidos/criar-pedido - Utilizado para os clientes criarem os pedidos no sistema.

```json
[
    {
        "produto": 4,
        "quantidade": 2,
        "canal": "APP",
        "filial_id": 1
    }
]
```

**PATCH PEDIDOS**

PATCH /pedidos/{id_pedido}/status - Utilizado para administradores, clientes, gerentes e a equipe da cozinha para alterar o status do pedido.

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

POST /pagamentos/realizar-pagamento - Utilizado para os clintes realizarem os pagamentos.

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

**GET FIDELIZACAO**

GET /fidelizacao/saldo - Para o cliente consultar seus pontos.

```json
[
    {
        "usuario_id": 4,
        "pontos_acumulados": 154,
        "pontos_trocados": 125,
        "pontos_disponiveis": 29,
        "data_adesao": "2026-06-14 20:47:57"
    }
]
```

**POST FIDELIZACAO**

POST /fidelizacao/aderir - Para o cliente aderir ao programa de fidelização.

```json
[
    {
        "aprovacao": true    
    }
]
```

**GET FILIAIS**

GET /filiais/listar-filiais - Lista todas as filiais ativas.

```json
[
    {
        "id": 1,
        "nome": "Raizes do Nordeste",
        "cidade": "Salvador",
        "estado": "BA"
  },
  {
        "id": 2,
        "nome": "Raizes do Nordeste",
        "cidade": "Recife",
        "estado": "PE"
  }
]
```

**POST FILIAIS**

POST /filiais/cadastrar-filial - Para o SUPER_ADMIN cadastrar novas filiais.

```json
[
    {
        "nome": "Raizes do Nordeste",
        "cidade": "Salvador",
        "estado": "BA"
    }
]
```

**PATCH FILIAIS**

PATCH /filiais/{filial_id}/inativar - Para o SUPER_ADMIN cadastrar novas filiais.

```json
[
    {
    "mensagem": " A filial Raizes do Nordeste - PE foi inativada com sucesso"
    }
]
```
---

## Fluxo principal

1. Cadastre um SUPER_ADMIN em `POST /usuarios/criar-conta` (Não é necessário informar filial)
2. Faça login com SUPER_ADMIN em `POST /login`
3. Copie o token e clique em **Authorize** no Swagger
4. Cadastre as filiais em `POST /filiais/cadastrar-filial`
5. Cadastre um ADMIN vinculado a uma filial em `POST /usuarios/criar-conta`
6. Faça login com ADMIN e cadastre produtos da filial em `POST /produtos/cadastrar-produto`
7. Cadastre um CLIENTE em `POST /usuarios/criar-conta`
8. Faça login com CLIENTE
9. Adira ao programa de fidelização em `POST /fidelizacao/aderir`
10. Liste produtos da filial em `GET /produtos/listar-produtos?filial_id=1`
11. Crie um pedido em `POST /pedidos/criar-pedido`
12. Realize o pagamento em `POST /pagamentos/realizar-pagamento/`
13. Consulte pontos acumulados em `GET /fidelizacao/saldo`
14. Acompanhe o status em `GET /pedidos/listar-pedidos`
15. No próximo pedido, informe `usar_pontos` para aplicar desconto

---

## Autenticação

A API utiliza o FastAPI Security para controle de autenticação. Os seguintes perfis estão disponíveis:

```bash
SUPER_ADMIN - Acesso total à rede — cadastrar filiais, gerenciar todos os usuários e visualizar dados de todas as filiais.
CLIENTE - Criar pedido, listar próprios pedidos, realizar pagamento e cancelar próprio pedido.
ADMIN - Gerencia sua filial — cadastrar produtos, listar usuários, atualizar estoque e gerenciar pedidos.
GERENTE - Listar usuários e pedidos, atualizar estoque e status de pedidos da sua filial. 
COZINHA - Atualizar status de pedidos e listar pedidos da sua filial. 
```

---

## Coleção Postman

O arquivo `colecao_postman.json` está na raiz do repositório com os cenários de teste organizados.
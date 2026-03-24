# Teste-de-software

## Estrutura do projeto

```text
Códigos/
|-- app/
|   |-- controllers/
|   |-- models/
|   |-- routes/
|   |-- static/
|   |-- templates/
|   `-- views/
`-- database/
```

## Tecnologias

- Python 3.12
- Flask
- PyMySQL
- MySQL 8.4
- Docker e Docker Compose

## Requisitos

- Docker
- Docker Compose

## Como executar

1. Entre na pasta [`Códigos`](/home/roberto/Documents/GitHub/Teste-de-software/Códigos).
2. Execute:

```bash
docker compose up --build
```

3. Acesse a aplicação em `http://localhost:5000`.
4. O MySQL ficará disponível na porta `3306`.

## Containers

- `app`: container da aplicação Flask
- `db`: container do MySQL

## Banco de dados

O banco é criado a partir de [schema.sql](/home/roberto/Documents/GitHub/Teste-de-software/Códigos/database/schema.sql).

## Configuração

As configurações da aplicação ficam em [config.py](/home/roberto/Documents/GitHub/Teste-de-software/Códigos/config.py) e são lidas de variáveis de ambiente:

- `SECRET_KEY`
- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`

No ambiente Docker, essas variáveis são definidas em [docker-compose.yml](/home/roberto/Documents/GitHub/Teste-de-software/Códigos/docker-compose.yml).

## Arquitetura

- `app/controllers`: controla o fluxo das requisições e integra as camadas da aplicação
- `app/models`: concentra regras de negócio e acesso aos dados
- `app/routes`: organiza e registra as rotas da aplicação
- `app/views`: centraliza a renderização das respostas
- `app/templates`: armazena os templates HTML
- `app/static`: guarda arquivos estáticos como CSS, JavaScript e imagens
- `database`: reúne scripts e artefatos relacionados ao banco de dados

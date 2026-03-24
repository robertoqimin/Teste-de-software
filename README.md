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
|   |-- views/
|   |-- __init__.py
|   `-- database.py
|-- database/
|   `-- schema.sql
|-- .env.example
|-- .dockerignore
|-- Dockerfile
|-- app.py
|-- config.py
|-- docker-compose.yml
`-- requirements.txt
```

## Tecnologias

- Python 3.12
- Flask
- PyMySQL
- MySQL 8.4
- Docker e Docker Compose

## Como executar

1. Entre na pasta [`Códigos`](/home/roberto/Documents/GitHub/Teste-de-software/Códigos).
2. Execute:

```bash
docker compose up --build
```

3. Acesse a aplicacao em `http://localhost:5000`.
4. O MySQL ficara disponivel na porta `3306`.

## Containers

- `app`: container da aplicacao Flask
- `db`: container do MySQL

O arquivo [docker-compose.yml](/home/roberto/Documents/GitHub/Teste-de-software/Códigos/docker-compose.yml) publica:

- `5000:5000` para a aplicacao
- `3306:3306` para o MySQL

Por isso a aplicacao pode abrir em:

- `http://localhost:5000`
- `http://127.0.0.1:5000`
- `http://SEU_IP_LOCAL:5000`

## Banco de dados

O banco e criado a partir de [schema.sql](/home/roberto/Documents/GitHub/Teste-de-software/Códigos/database/schema.sql), que define:

- banco `app_web`
- tabela `users`

Campos da tabela `users`:

- `id`
- `name`
- `email`
- `password_hash`
- `created_at`

Importante: a senha do usuario nao e armazenada em texto puro. A aplicacao salva apenas `password_hash`.

## Configuracao

As configuracoes da aplicacao ficam em [config.py](/home/roberto/Documents/GitHub/Teste-de-software/Códigos/config.py) e sao lidas de variaveis de ambiente:

- `SECRET_KEY`
- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`

No ambiente Docker, essas variaveis sao definidas em [docker-compose.yml](/home/roberto/Documents/GitHub/Teste-de-software/Códigos/docker-compose.yml).

## Arquitetura

- [app.py](/home/roberto/Documents/GitHub/Teste-de-software/Códigos/app.py): ponto de entrada da aplicacao
- [app/__init__.py](/home/roberto/Documents/GitHub/Teste-de-software/Códigos/app/__init__.py): cria a app Flask e registra as rotas
- [app/routes/__init__.py](/home/roberto/Documents/GitHub/Teste-de-software/Códigos/app/routes/__init__.py): registro das rotas
- [app/controllers/home_controller.py](/home/roberto/Documents/GitHub/Teste-de-software/Códigos/app/controllers/home_controller.py): fluxo da rota principal
- [app/models/site_model.py](/home/roberto/Documents/GitHub/Teste-de-software/Códigos/app/models/site_model.py): dados de texto da pagina
- [app/models/user_model.py](/home/roberto/Documents/GitHub/Teste-de-software/Códigos/app/models/user_model.py): operacoes na tabela `users`
- [app/views/home_view.py](/home/roberto/Documents/GitHub/Teste-de-software/Códigos/app/views/home_view.py): renderizacao do template
- [app/templates/index.html](/home/roberto/Documents/GitHub/Teste-de-software/Códigos/app/templates/index.html): interface HTML
- [app/database.py](/home/roberto/Documents/GitHub/Teste-de-software/Códigos/app/database.py): conexao com o MySQL

## Fluxo da aplicacao

1. O usuario acessa `/`
2. O controller renderiza o formulario
3. O usuario envia `nome`, `email` e `senha`
4. O controller valida os campos
5. A senha e convertida em hash
6. O model salva o usuario no MySQL
7. A pagina retorna com mensagem de sucesso ou erro

## Persistencia dos dados

O MySQL usa um volume Docker, entao os dados continuam salvos mesmo apos reiniciar os containers.

Se voce ja cadastrou usuarios antes, eles podem continuar existindo na base em novas execucoes do projeto.

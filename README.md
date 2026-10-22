# Sistema de Gestão da Secretaria Escolar DF

O Sistema de Gestão da Secretaria Escolar DF é uma plataforma digital desenvolvida para apoiar as atividades administrativas de instituições de ensino, centralizando e organizando informações acadêmicas e administrativas.

O frontend é uma SPA (Single Page Application) com componentes React e navegação pelo React Router. O backend Flask fornece APIs JSON, autenticação e acesso ao banco MySQL. O Vite compila o frontend, e o próprio Flask entrega os arquivos gerados ao navegador.

## Estrutura do projeto

```text
Códigos/
|-- app/
|   |-- controllers/
|   |-- models/
|   |-- routes/
|   |-- static/
|   |   `-- dist/           # gerado pelo Vite
|   |-- templates/
|   |   `-- partials/
|   `-- frontend.py
|-- frontend/
|   |-- src/
|   |   |-- components/    # navegação, sessão, abas e formulários
|   |   |-- pages/         # 13 telas em JSX
|   |   `-- styles/
|   `-- tests/            # testes Playwright
|-- tests/                # servidor isolado para testes
|-- app.py
|-- config.py
|-- docker-compose.yml
|-- Dockerfile
`-- requirements.txt
```

## Tecnologias

### Frontend

| Tecnologia | Versão principal | Uso no projeto |
| --- | --- | --- |
| React e React DOM | 18.3 | Renderização das 13 telas em componentes JSX e gerenciamento de estado. |
| React Router DOM | 7 | Navegação SPA, rotas por perfil e compatibilidade com URLs antigas. |
| JavaScript e JSX | — | Componentes, formulários, filtros e interações da interface. |
| HTML5 e CSS3 | — | Documento de entrada e estilos das telas. |
| Tailwind CSS | 3.4 | Classes utilitárias compiladas localmente. |
| Vite | 7 | Build de produção, recompilação em modo watch e manifesto dos assets. |
| PostCSS e Autoprefixer | 8 e 10 | Processamento do CSS no build. |
| Node.js e npm | Node 22 na imagem Docker | Instalação das dependências e execução do build do frontend. |
| Fetch API e FormData | APIs do navegador | Comunicação com o Flask e envio de formulários e arquivos sem recarregar a página. |

React e Tailwind são instalados pelo npm e incluídos no build. As telas não
carregam essas bibliotecas por CDN. As versões resolvidas das dependências
JavaScript ficam registradas em `frontend/package-lock.json`.

### Backend e banco de dados

| Tecnologia | Versão/configuração | Uso no projeto |
| --- | --- | --- |
| Python | 3.12 na imagem Docker | Execução do backend. |
| Flask | 3.1.0 | APIs JSON, sessões, permissões, uploads e entrega da SPA. |
| Jinja2 | Dependência do Flask | Inclusão dos assets no HTML de entrada; as telas são renderizadas pelo React. |
| SQLAlchemy | 2.0.44 | Mapeamento dos modelos e acesso ao banco via ORM. |
| PyMySQL | 1.1.2 | Conexão do backend com o MySQL. |
| MySQL | 8.4 | Persistência dos dados acadêmicos e administrativos. |
| python-dotenv | 1.0.1 | Leitura das variáveis do arquivo `.env`. |
| cryptography | >=42 e <46 | Suporte criptográfico utilizado pelas dependências de conexão ao banco. |

A SPA utiliza o cookie de sessão do Flask na mesma origem. As APIs verificam
as permissões de administrador, professor e aluno no servidor.

### Infraestrutura e testes

| Tecnologia | Uso no projeto |
| --- | --- |
| Docker | Build em duas etapas: Node compila o frontend e Python executa o Flask. |
| Docker Compose | Inicialização dos serviços `app` e `db`, rede e volumes persistentes. |
| Playwright Test | Testes de ponta a ponta da SPA em navegador. |
| SQLite | Banco temporário e isolado nos testes, sem acessar o MySQL da instalação. |

## Requisitos

- Docker
- Docker Compose

Para executar pelos containers, não é necessário instalar Node.js ou Python no
host: o Dockerfile prepara ambos os ambientes. Para desenvolvimento e testes
fora do Docker, instale Python com as dependências de `Códigos/requirements.txt`
e Node.js 22.12+ (ou 20.19+) com npm.

## Como executar

1. Entre na pasta `Códigos`:

```bash
cd Códigos
```

2. Crie o arquivo de ambiente a partir do exemplo:

```bash
cp .env.example .env
```

3. Edite o `.env` e defina valores seguros para:
- `SECRET_KEY`
- `DB_PASSWORD`
- `MYSQL_ROOT_PASSWORD`

4. Suba os serviços:

```bash
docker compose up -d --build
```

5. Verifique se os containers estão rodando:

```bash
docker compose ps
```

6. Execute o seed para criar o usuário administrador inicial:

```bash
docker compose exec app python -m app.seed
```

7. Acesse a aplicação em `http://localhost:5000`.
8. O MySQL ficará disponível na porta `3306`.

Credenciais padrão geradas pelo script de seed (recomenda-se alterar para maior segurança):
- Email: `admin@admin.com`
- Senha: `123`

## Containers

- `app`: container da aplicação Flask
- `db`: container do MySQL

## Banco de dados

As tabelas são criadas automaticamente pelo ORM (SQLAlchemy) na inicialização da aplicação.

Importante:
- As variáveis `MYSQL_*` e criação de usuário/banco são aplicadas na primeira inicialização do volume do MySQL.
- Se você trocar senha no `.env` depois disso, será necessário recriar o volume:

```bash
docker compose down -v
docker compose up -d --build
```

## Configuração

As configurações da aplicação ficam em `config.py` e são lidas de variáveis de ambiente:

- `SECRET_KEY`
- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`
- `MYSQL_ROOT_PASSWORD` (usada pelo container do MySQL)

No ambiente Docker, as variáveis são lidas do arquivo `.env` via `docker-compose.yml`.

## Arquitetura

- `frontend/src/App.jsx`: rotas da SPA e compatibilidade com URLs antigas.
- `frontend/src/pages`: 13 telas renderizadas em componentes React, sem HTML injetado.
- `frontend/src/components`: sessão, proteção por perfil, navegação, abas, formulários e carregamento de dados.
- `frontend/src/styles`: estilos das telas; Tailwind é compilado no build.
- `app/routes/api_routes.py`: consultas e operações administrativas em JSON.
- `app/routes`: também mantém autenticação, uploads e downloads protegidos.
- `app/controllers` e `app/models`: regras de negócio e acesso ao banco.
- `app/templates/spa.html`: documento de entrada único, contendo apenas a raiz React e os assets.
- `app/frontend.py`: resolve os arquivos versionados pelo manifesto do Vite.
- `app/static/dist`: build gerado, servido pelo próprio Flask.

A navegação interna usa o histórico do navegador sem recarregar o documento.
O Flask entrega o mesmo documento nas URLs das telas, permitindo abrir links
diretos e atualizar a página. URLs antigas são encaminhadas para as rotas atuais
pelo React Router. As APIs validam a sessão e o perfil no servidor; não dependem
da proteção visual do React. Sessão e dados privados usam `Cache-Control: no-store`.

Os formulários enviam `FormData` por `fetch`, incluindo arquivos. Erros de
validação são exibidos no próprio formulário e, após sucesso, os dados da tela
são consultados novamente. Não é necessário armazenar JWT no navegador: a SPA
usa o cookie de sessão do Flask na mesma origem.

Principais endpoints:

| Endpoint | Operação |
| --- | --- |
| `POST /login` | Autenticação |
| `GET /api/session`, `POST /api/logout` | Sessão |
| `GET /api/admin/dashboard`, `GET /api/admin/banco-de-dados` | Resumos e registros |
| `GET/POST /api/admin/disciplinas`, `/api/admin/turmas`, `/api/admin/comunicados` | Gestão acadêmica |
| `POST /api/cadastro/aluno`, `/api/cadastro/professor` | Cadastros com foto |
| `GET /api/admin/alunos/:id`, `/api/admin/professores/:id` | Detalhes |
| `POST /api/admin/alunos/:id/editar`, `/api/admin/professores/:id/editar` | Edição |
| `POST /api/admin/alunos/:id/documentos/solicitar`, `/api/admin/professores/:id/documentos/solicitar` | Solicitações |
| `GET /api/aluno`, `GET /api/aluno/disciplinas/:id`, `GET /api/professor` | Portais |
| `POST /api/professor/notas/salvar`, `/api/professor/atividades/lancar` | Notas e atividades |
| `POST /api/aluno/documentos/upload`, `/api/professor/documentos/upload` | Documentos solicitados |
| `POST /api/arquivos/upload`, `/api/professores/:id/arquivos/upload` | Arquivos enviados pela secretaria |

## Comandos úteis

Ver containers:

```bash
docker compose ps
```

Ver logs da aplicação:

```bash
docker compose logs -f app
```

Executar seed:

```bash
docker compose exec app python -m app.seed
```

Parar os containers:

```bash
docker compose down
```

## Desenvolvimento do frontend

Requer Node.js 22.12+ (ou 20.19+) e npm. Na pasta `Códigos/frontend`:

```bash
npm ci
npm run build
```

Os comandos disponíveis em `frontend/package.json` são:

| Comando | Função |
| --- | --- |
| `npm ci` | Instala as dependências nas versões do lockfile. |
| `npm run build` | Gera os arquivos de produção em `app/static/dist`. |
| `npm run dev` | Observa alterações e recompila os arquivos servidos pelo Flask. |
| `npm run test:e2e` | Executa os testes Playwright com servidor e banco isolados. |

Para recompilar ao alterar os componentes ou estilos:

```bash
npm run dev
```

Execute o Flask separadamente e acesse a porta 5000. O comando `dev` observa
os arquivos e grava o build servido pelo Flask; não usa um servidor na porta 5173.
Atualize o navegador após a recompilação para carregar o novo bundle.

O Docker executa o build automaticamente em uma etapa Node e copia os assets
para a imagem Python. O serviço `app` usa os arquivos da imagem; após alterações,
execute `docker compose up -d --build`. O volume de uploads permanece persistente.

Todas as telas são renderizadas no navegador pelo React. O Jinja é usado apenas
para inserir os arquivos do build no documento de entrada, sem renderizar dados
acadêmicos ou conteúdo das telas.

## Arquivos gerados e versionamento

Edite os componentes e estilos em `Códigos/frontend/src`. O comando de build
produz JavaScript e CSS com nomes versionados e o arquivo
`app/static/dist/.vite/manifest.json`. O Flask consulta esse manifesto para
carregar os assets corretos por meio de `templates/partials/frontend_assets.html`.

Devem ser versionados os fontes do frontend e backend, os templates de entrada,
as configurações do Vite, Tailwind e PostCSS, `package.json`, `package-lock.json`,
os testes e os arquivos de configuração do Docker.

`node_modules/`, `app/static/dist/`, relatórios de testes e `.env` ficam fora do
Git, conforme o `.gitignore`. O Docker gera o build durante a criação da imagem.

## Testes da SPA

Instale as dependências Python em um ambiente virtual e as dependências npm.
Depois, na pasta `Códigos/frontend`:

```bash
npm run build
npx playwright install chromium
npm run test:e2e
```

Os testes iniciam um Flask na porta 5051 com banco SQLite e uploads temporários,
sem acessar o MySQL ou os uploads da instalação. Cobrem login, navegação sem
recarregar, cadastros, filtros, edição, documentos, atividades, notas, permissões,
sessão expirada, URLs antigas e atualização direta de uma rota.

Para usar um Python de ambiente virtual ou um Chrome já instalado:

```bash
SPA_TEST_PYTHON=/caminho/venv/bin/python PLAYWRIGHT_CHROMIUM_EXECUTABLE=/usr/bin/google-chrome npm run test:e2e
```

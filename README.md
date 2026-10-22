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
|   |   |-- pages/         # 15 telas em JSX
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
| React e React DOM | 18.3 | Renderização das 15 telas em componentes JSX e gerenciamento de estado. |
| React Router DOM | 7 | Navegação SPA, rotas por perfil e compatibilidade com URLs antigas. |
| JavaScript e JSX | — | Componentes, formulários, filtros e interações da interface. |
| HTML5 e CSS3 | — | Documento de entrada e estilos das telas. |
| Tailwind CSS | 3.4 | Classes utilitárias compiladas localmente. |
| Vite | 7 | Build de produção, recompilação em modo watch e manifesto dos assets. |
| PostCSS e Autoprefixer | 8 e 10 | Processamento do CSS no build. |
| Node.js e npm | Node 22 na imagem Docker | Instalação das dependências e execução do build do frontend. |
| Fetch API e FormData | APIs do navegador | Comunicação com o Flask e envio de formulários e arquivos sem recarregar a página. |

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
as permissões de administrador, secretaria escolar, professor e aluno no servidor.

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

6. Execute a seed para criar o administrador inicial:

```bash
docker compose exec app python -m app.seed
```

7. Acesse a aplicação em `http://localhost:5000`.
8. O MySQL ficará disponível na porta `3306`.

A seed padrão cria `gestor@escola.com` com o perfil **Administrador**.
Defina uma senha de pelo menos oito caracteres quando o comando solicitar.
Não há senha padrão. A conta acessa `/gestao`.

## Perfis e administração geral

| Perfil | Responsabilidade | Tela inicial |
| --- | --- | --- |
| Secretaria Escolar (`secretaria`) | Cadastros de alunos/professores, turmas, disciplinas, comunicados e documentos. | `/admin/dashboard` |
| Administrador (`admin`) | Gestão geral de contas, permissões, auditoria, configurações, relatórios e backup do banco. | `/gestao` |
| Professor (`professor`) | Publicar atividades e conteúdos, lançar notas e consultar entregas e comunicados. | `/professor` |
| Aluno (`aluno`) | Consultar disciplinas, horários, notas e comunicados; enviar atividades e documentos solicitados. | `/aluno` |

Na primeira inicialização desta versão, as contas antigas `ADMIN`/`admin`
são convertidas para `secretaria`, preservando e-mail, senha e vínculos.
A migração fica registrada em `configuracoes` e não converte administradores
criados posteriormente. As URLs antigas `/admin/...` continuam atendendo à
secretaria para preservar links existentes.

Na pasta `Códigos`, criar o administrador padrão:

```bash
docker compose exec app python -m app.seed
```

O comando solicita uma senha de pelo menos oito caracteres, sem exibi-la.
O seed preserva usuários existentes e não altera contas com e-mail já cadastrado.
Entre com a nova conta para acessar `/gestao`. Para criar outra conta administrativa,
usar `--admin --email outro.gestor@escola.com`.

Para criar uma conta da secretaria explicitamente:

```bash
docker compose exec app python -m app.seed --secretaria --email secretaria@escola.com
```

A seed solicita a senha da nova conta. Contas anteriores, incluindo
`admin@admin.com`, não são renomeadas nem têm seu perfil alterado.


O administrador pode:

- Criar contas de secretaria e outros administradores, editar seus perfis e e-mails.
- Bloquear/desbloquear contas, redefinir senhas, exigir troca no próximo acesso e encerrar sessões ao salvar uma conta.
- Liberar/revogar permissões de cadastro, gestão acadêmica, documentos e comunicados da secretaria. As permissões controlam operações de escrita, inclusive pelas URLs antigas; a consulta às telas da secretaria permanece disponível.
- Consultar totais de alunos, professores, turmas, contas bloqueadas e documentos pendentes.
- Consultar os últimos 100 eventos de auditoria, incluindo tentativas de login e alterações em contas, permissões, cadastros e notas. Alterações de cadastros, notas e configurações registram valores anteriores e novos; senhas e tokens não são registrados.
- Definir parâmetros acadêmicos: ano letivo, quantidade de períodos, média de referência e prazo de notas. O prazo bloqueia lançamentos após a data configurada, no horário de São Paulo. Ano, períodos e média são referências institucionais; não modificam retroativamente turmas ou o modelo atual de notas.
- Exportar relatórios CSV de contas e dados acadêmicos.
- Exportar e restaurar backup JSON do banco, com confirmação e senha atual. A restauração aceita até 32 MB, exige um administrador ativo no backup, substitui os dados em uma transação e revoga as sessões anteriores.

O backup inclui hashes de senhas e deve ser guardado com acesso restrito.
Arquivos enviados não fazem parte do backup JSON: copie também o volume de uploads.
A restauração não altera esse volume. O sistema continua atendendo uma única
instituição; não há isolamento de dados entre várias escolas nesta versão.

As permissões e o estado da conta são conferidos no servidor em cada requisição.
O administrador não pode bloquear nem alterar o próprio perfil pelo formulário
de contas; para trocar a própria senha, use o link no cabeçalho do painel.

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
- `frontend/src/pages`: 15 telas renderizadas em componentes React, sem HTML injetado.
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
| `GET /api/admin/dashboard`, `GET /api/admin/banco-de-dados` | Resumos e dados para cadastros |
| `GET /api/admin/registros` | Consultar registros com paginação, busca, filtro por tipo e exportação |
| `GET /api/gestao/painel` | Consultar contas paginadas, resumo, configurações e auditoria |
| `GET/POST /api/admin/disciplinas`, `/api/admin/turmas`, `/api/admin/comunicados` | Gestão acadêmica |
| `POST /api/cadastro/aluno`, `/api/cadastro/professor` | Cadastros com foto |
| `GET /api/admin/alunos/:id`, `/api/admin/professores/:id` | Detalhes |
| `POST /api/admin/alunos/:id/editar`, `/api/admin/professores/:id/editar` | Edição |
| `POST /api/admin/alunos/:id/documentos/solicitar`, `/api/admin/professores/:id/documentos/solicitar` | Solicitações |
| `GET /api/aluno`, `GET /api/aluno/disciplinas/:id`, `GET /api/professor` | Portais |
| `POST /api/professor/notas/salvar` | Lançar notas |
| `POST /api/professor/atividades/lancar` | Publicar atividades ou conteúdos pelo campo `tipo` |
| `POST /api/aluno/atividades/:id/enviar` | Enviar resposta de uma atividade da própria turma |
| `GET /api/aluno/comunicados`, `GET /api/professor/comunicados` | Consultar avisos por perfil com carregamento progressivo |
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
sessão expirada, URLs antigas e atualização direta de uma rota. Também cobrem
paginação e filtros, comunicados por perfil, espaçamento dos botões, lançamento
de notas em janela, publicação de conteúdos e entrega de atividades.

Para usar um Python de ambiente virtual ou um Chrome já instalado:

```bash
SPA_TEST_PYTHON=/caminho/venv/bin/python PLAYWRIGHT_CHROMIUM_EXECUTABLE=/usr/bin/google-chrome npm run test:e2e
```

### Testes da administração geral

Com as dependências Python instaladas, execute a partir da raiz:

```bash
python Códigos/tests/test_governanca.py
```

Esses testes usam SQLite temporário e cobrem migração única, seed sem exclusões,
separação de perfis, permissões, bloqueio/revogação de sessões, troca obrigatória
de senha, prazo de notas, auditoria, restauração com rollback, paginação e
autorização dos envios e downloads de atividades.
A suíte Playwright inclui o fluxo do novo administrador e o primeiro acesso
de uma conta de secretaria com senha temporária.

## População com dados fictícios

Na pasta `Códigos`, com os containers atualizados:

```bash
docker compose exec -T app python -m app.seed_demo
```

A carga adiciona 800 alunos e 200 professores (proporção 80:20), preservando
contas e registros existentes. Também cria 20 turmas, 10 disciplinas, vínculos
acadêmicos, 8.000 notas, 400 atividades, 1.000 documentos, 1.000 solicitações,
12 comunicados e registros de configuração/auditoria. Os 1.400 arquivos TXT
fictícios ficam no volume de uploads e podem ser baixados pelo sistema.

Os e-mails seguem os padrões `aluno0001@demo.invalid` e
`professor0001@demo.invalid`. A senha aleatória compartilhada pelas contas
fictícias é exibida somente na primeira execução. Nomes, CPFs e documentos são
sintéticos e servem exclusivamente para demonstração.

O marcador `carga_demo_v1` impede duplicação em novas execuções. A proporção
80:20 refere-se às pessoas adicionadas; eventuais alunos/professores já
existentes são mantidos. Configurações acadêmicas existentes são preservadas.
Em caso de falha, a transação é revertida e os arquivos recém-criados são removidos.

Validação isolada da carga:

```bash
python Códigos/tests/test_seed_demo.py
```

## Cronograma semanal por turma

Na secretaria, abra **Turmas**, clique na turma desejada e selecione a aba
**Disciplinas e cronograma**. Essa aba mostra somente a grade semanal. Clique
em **Gerenciar disciplinas e horários** para abrir os formulários em outra janela:

1. Selecione a disciplina; a turma já vem definida pela janela aberta.
2. Informe os horários de início e fim e marque os dias de segunda a sábado.
3. Clique em **Associar disciplina e salvar horários**.

O sistema cria o vínculo da disciplina com a turma caso ainda não exista.
Uma disciplina pode ter vários intervalos na semana. A edição permite ajustar
um lançamento por vez; a remoção de um horário preserva o vínculo da disciplina.
Intervalos inválidos e sobreposições na mesma turma são rejeitados. Esta
validação não verifica conflitos de disponibilidade de professores entre turmas.

Os horários ficam na tabela `horarios`, vinculados a `turmas_disciplinas`.
As operações exigem o perfil secretaria e a permissão de gestão acadêmica,
e ficam registradas na auditoria.

O aluno visualiza os horários de suas próprias turmas em **Disciplinas**, numa
grade semanal com navegação para os detalhes de cada disciplina. Disciplinas
sem horário definido continuam disponíveis abaixo da grade. A coluna do dia
atual recebe destaque; em telas menores a grade tem rolagem horizontal.

Para acrescentar horários fictícios às turmas já criadas pela carga demo:

```bash
docker compose exec -T app python -m app.seed_horarios_demo
```

O comando somente atende às turmas `DEMO-T...` da carga fictícia e não altera
uma turma que já tenha horários. Os horários fictícios aparecem identificados
como demonstração e podem ser editados pela secretaria. Novas execuções da
carga completa `app.seed_demo` também preenchem a grade de demonstração.

### Janelas de gerenciamento de turmas

A página Turmas exibe a lista de turmas e o botão **Nova turma**, que abre o
cadastro em uma janela centralizada. Ao clicar no nome de uma turma, uma nova
janela reúne as abas **Alunos**, **Professores** e **Disciplinas e cronograma**.
Os botões de associação ficam dentro dessas abas; alunos e professores já
vinculados não são oferecidos novamente. A lista é atualizada após salvar.
As consultas retornam todos os vínculos, inclusive nas turmas da carga demo.

## Interface e navegação

- Manter a navegação lateral e o padrão visual azul nas páginas internas.
- Centralizar e limitar a área principal, com painéis, listas e tabelas com rolagem própria.
- Abrir ações de cadastro, edição, associação, publicação e envio em janelas centralizadas.
- Preservar os layouts próprios de login e troca de senha, com formulários centralizados.
- Padronizar botões de ação com gradiente ciano/azul, altura mínima de 44 px, fonte de 14 px e raio de 12 px, sem faixa lateral de cor diferente.
- Separar grupos de ações com 12 px; usar 16 px entre **Solicitar documento** e **Enviar arquivo** nos detalhes de alunos e professores.
- Permitir fechar janelas pelo botão de fechar ou Escape, bloqueando o fechamento durante o envio.
- Exibir erros e confirmações no formulário e atualizar a consulta após salvar.

### Secretaria escolar

- Listar disciplinas cadastradas e abrir **Nova disciplina** em janela flutuante.
- Abrir os professores associados ao selecionar uma disciplina e oferecer a associação dentro dessa janela.
- Listar turmas e abrir cadastro, detalhes e associações em janelas, conforme o contexto.
- Exibir a grade em **Disciplinas e cronograma** e abrir **Gerenciar disciplinas e horários** para associar disciplinas e configurar os dias e intervalos.
- Consultar e cadastrar alunos e professores por listas com busca e formulários em janela.
- Redirecionar **Ver detalhes** do painel geral e do banco de dados diretamente ao cadastro completo do aluno ou professor.
- Editar dados, solicitar documentos, enviar arquivos e baixar documentos nas páginas de detalhes.

### Paginação e comunicados da secretaria

- Paginar no servidor os usuários em **Banco de Dados** e em **Contas**, na gestão administrativa.
- Carregar 20 registros por padrão e permitir selecionar 10, 20, 50 ou 100 por página.
- Aplicar busca e filtros à base completa e retornar à primeira página ao alterar os critérios.
- Preservar o CSV da secretaria com todos os resultados do filtro, independentemente da página atual.
- Exibir os comunicados completos na página principal, com total, rolagem própria e paginação no servidor.
- Posicionar **Novo comunicado** à direita do cabeçalho e abrir o formulário em janela flutuante.
- Retornar à primeira página após publicar um comunicado.

### Portal do professor

- Consultar turmas e abrir seus detalhes em janela flutuante.
- Organizar as publicações da turma nas abas **Atividades** e **Conteúdos**, dentro do mesmo painel.
- Abrir **Lançar atividade** em janela para informar disciplina, título, descrição, prazo opcional e anexo opcional.
- Abrir **Publicar conteúdo** em janela para compartilhar materiais de estudo, sem prazo de entrega.
- Manter as publicações existentes como atividades.
- Retirar a lista de alunos e o lançamento de notas dos detalhes da turma.
- Preservar a aba **Notas**, mostrar o histórico na página e abrir o lançamento pelo botão **Lançar notas** em janela flutuante.
- Consultar documentos próprios e entregas dos alunos em **Documentos → Arquivos e entregas**, com identificação do aluno e download.

### Portal do aluno

- Consultar a grade semanal das próprias turmas e abrir os detalhes de cada disciplina.
- Retirar a seção de professores da página da disciplina.
- Reunir **Atividades** e **Conteúdos** em abas no mesmo painel, seguindo o estilo do portal do professor.
- Permitir baixar anexos das duas categorias e enviar respostas apenas para atividades.
- Abrir **Enviar atividade** em janela para anexar a resposta.
- Exibir confirmação, data, histórico e download das próprias entregas; permitir novos envios sem apagar os anteriores.
- Vincular cada entrega à atividade, ao aluno, à disciplina e ao professor responsável.
- Validar a turma e a disciplina no servidor antes de aceitar uma entrega e impedir acesso aos arquivos de outro aluno.
- Manter o envio de documentos solicitados pela secretaria em janela flutuante.

### Comunicados nos portais acadêmicos

- Disponibilizar a consulta pelo botão **Comunicados** no menu lateral de alunos e professores.
- Carregar no máximo 3 recados inicialmente e até 5 adicionais por clique em **Carregar mais**.
- Acumular os recados dentro de uma área com rolagem própria e ocultar o botão ao chegar ao fim.
- Mostrar avisos gerais e os destinados ao perfil autenticado; impedir a consulta pelo endpoint do outro perfil.
- Manter a publicação e a gestão dos comunicados na secretaria escolar.

## Alterações de persistência

- Registrar governança nas tabelas de configurações e auditoria e nas propriedades de acesso das contas.
- Persistir o cronograma na tabela `horarios`, vinculada às associações entre turmas e disciplinas.
- Distinguir atividades de conteúdos pelo campo `atividades.tipo`, com valor inicial `atividade` para os registros existentes.
- Vincular entregas pelo campo opcional `documentos.atividade_id`, preservando os demais usos dos documentos.
- Aplicar a criação de tabelas e os ajustes de colunas durante a inicialização, preservando os dados existentes.
- Manter os arquivos enviados no volume persistente de uploads e controlar seus downloads por perfil e vínculo.

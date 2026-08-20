# Sincronizar o projeto entre dois computadores (trabalho e casa)

## Ideia geral

O **GitHub** vira o "ponto de encontro" entre os dois computadores. Cada
máquina tem uma cópia completa do repositório; você manda suas mudanças pra
lá (`push`) e traz as mudanças que fez na outra máquina de volta (`pull`).

```
Notebook empresa  ──push/pull──▶  GitHub (2 repos: público + privado)  ◀──push/pull──  PC de casa
```

**Importante:** o repositório principal do código é **público** — só
**código e documentação** vão nele, é assim de propósito (ver
`05-git-e-seguranca.md`). Segredos (`.env`, credenciais do Google) e dados
reais (banco `.db`, planilhas geradas) **nunca vão nesse repositório**.

Os segredos sincronizam por um **segundo repositório, esse sim privado**:
[`diadepipocagourmetboot-wpp---secrets`](https://github.com/maryasanchess/diadepipocagourmetboot-wpp---secrets)
— ver a seção específica mais abaixo.

## Os dois repositórios já existem

Não precisa criar nada — os dois já estão no ar:

| Repositório | Visibilidade | O que tem |
|---|---|---|
| [`diadepipocagourmetboot-wpp`](https://github.com/maryasanchess/diadepipocagourmetboot-wpp) | 🌐 Público | Todo o código e a documentação — o que pode ser visto por qualquer pessoa |
| [`diadepipocagourmetboot-wpp---secrets`](https://github.com/maryasanchess/diadepipocagourmetboot-wpp---secrets) | 🔒 Privado | `.env` e `backend/credentials/google_credentials.json` reais — só você tem acesso |

## Passo 1 — Clonar os dois repositórios na máquina nova

```bash
git clone https://github.com/maryasanchess/diadepipocagourmetboot-wpp.git
git clone https://github.com/maryasanchess/diadepipocagourmetboot-wpp---secrets.git
```

Na primeira vez, o GitHub vai pedir autenticação (não aceita mais senha
comum por linha de comando):
- **Token de acesso pessoal (HTTPS)** — mais simples pra começar: GitHub → Settings → Developer settings → Personal access tokens → gerar um token e usar no lugar da senha quando pedir.
- **Chave SSH** — mais robusto a longo prazo, mas exige gerar uma chave em cada máquina e cadastrar no GitHub.

## Passo 2 — Copiar os segredos pro lugar certo

```bash
cp diadepipocagourmetboot-wpp---secrets/.env diadepipocagourmetboot-wpp/.env
cp diadepipocagourmetboot-wpp---secrets/backend/credentials/google_credentials.json diadepipocagourmetboot-wpp/backend/credentials/google_credentials.json
```

Pronto — o projeto do código já reconhece esses arquivos automaticamente
(estão no `.gitignore` de lá, então nunca vão ser commitados por engano
no repositório público).

## Quando um segredo mudar (token, chave Pix, etc.)

Atualize o `.env` dentro da pasta `diadepipocagourmetboot-wpp---secrets`
(não na pasta do código) e sincronize só esse repositório:

```bash
cd diadepipocagourmetboot-wpp---secrets
git add .env
git commit -m "Atualizar token do WhatsApp"
git push
```

Na outra máquina, `git pull` nesse repositório e repete o `cp` do Passo 2.

O banco de dados (`pipoca.db`) **não precisa** existir nas duas máquinas —
ele só importa na máquina que estiver rodando o bot de verdade (o VPS,
quando chegarmos lá). Nas máquinas de desenvolvimento, cada uma cria seu
próprio banco de teste vazio automaticamente.

## Rotina do dia a dia (para não perder trabalho nem gerar conflito)

**Sempre que for começar a mexer no projeto**, em qualquer máquina:
```bash
git pull
```
Isso traz qualquer mudança feita na outra máquina antes de você começar.

**Sempre que terminar uma parte do trabalho**, na mesma máquina:
```bash
git add <arquivos que mudaram>
git commit -m "descrição do que mudou"
git push
```

Regra prática: **não deixe trabalho não commitado indo de uma máquina pra
outra sem passar pelo GitHub** — se você mexeu no notebook da empresa e não
deu `push`, essa mudança não existe pra o PC de casa ainda.

### Se aparecer conflito
Só acontece se você editar o **mesmo trecho do mesmo arquivo** nas duas
máquinas sem sincronizar entre as edições. O Git avisa exatamente onde está
o conflito quando você faz `git pull`; me chama nesse momento que eu te
ajudo a resolver — não é destrutivo, só precisa decidir qual versão
manter.

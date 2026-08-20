# Sincronizar o projeto entre dois computadores (trabalho e casa)

## Ideia geral

O **GitHub** vira o "ponto de encontro" entre os dois computadores. Cada
máquina tem uma cópia completa do repositório; você manda suas mudanças pra
lá (`push`) e traz as mudanças que fez na outra máquina de volta (`pull`).

```
Notebook empresa  ──push/pull──▶  GitHub (repo público)  ◀──push/pull──  PC de casa
```

**Importante:** este repositório é **público** — só **código e
documentação** vão nele, é assim de propósito (ver
`05-git-e-seguranca.md`). Segredos (`.env`, credenciais do Google) e dados
reais (banco `.db`, planilhas geradas) **nunca vão nesse repositório**, em
nenhuma hipótese, e precisam ser configurados manualmente em cada máquina
(veja a seção específica mais abaixo).

## Passo 1 — Clonar o repositório na máquina nova

```bash
git clone https://github.com/maryasanchess/diadepipocagourmetboot-wpp.git
```

Na primeira vez, o GitHub vai pedir autenticação (não aceita mais senha
comum por linha de comando):
- **Token de acesso pessoal (HTTPS)** — mais simples pra começar: GitHub → Settings → Developer settings → Personal access tokens → gerar um token e usar no lugar da senha quando pedir.
- **Chave SSH** — mais robusto a longo prazo, mas exige gerar uma chave em cada máquina e cadastrar no GitHub.

## Passo 2 — Configurar os segredos em CADA máquina (fora do Git)

Como `.env` e as credenciais do Google não vão pelo GitHub, você precisa
recriá-los manualmente em cada computador:

1. Copie `.env.example` para `.env` na raiz do projeto, em cada máquina.
2. Preencha os valores reais (token da Meta, ID do calendário, número admin etc.) — os mesmos valores nos dois computadores, já que é o mesmo bot.
3. Coloque o arquivo `google_credentials.json` dentro de `backend/credentials/` em cada máquina.

**Como levar esses valores de um computador para o outro com segurança:**
não mande por e-mail/WhatsApp/print em texto puro. Opções melhores:
- Um gerenciador de senhas (ex: Bitwarden, 1Password) guardando os valores como "nota segura" — você acessa de qualquer dispositivo logado.
- Copiar o arquivo `.env` e `google_credentials.json` por um pen drive, apagando do pen drive depois.

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

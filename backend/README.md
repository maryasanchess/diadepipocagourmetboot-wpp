# Backend do PipocaBot

## Rodando localmente (Windows / PowerShell)

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copie o `.env.example` da raiz do projeto para `.env` (também na raiz) e
preencha os valores conforme for configurando cada serviço (ver
`docs/04-guia-de-inicio.md`).

Suba o servidor:

```powershell
uvicorn app.main:app --reload --port 8000
```

Teste no navegador: [http://localhost:8000](http://localhost:8000) deve
responder `{"status": "PipocaBot rodando"}`.

## Testar a conversa sem precisar do WhatsApp

Não precisa de conta Meta nem de nada configurado — dá pra "conversar" com o
bot direto no terminal:

```powershell
cd backend
.venv\Scripts\Activate.ps1
python chat_local.py
```

Digite as mensagens como se você fosse o cliente e vê a resposta do bot na
hora. `/novo` simula um cliente diferente (do zero); `/admin` simula o
número admin configurado no `.env` (pra testar o comando `relatorio`);
`/sair` encerra.

## Rodando os testes automatizados

```powershell
cd backend
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest tests/ -v
```

18 testes cobrindo o fluxo de pedido completo, múltiplos sabores,
cancelamento, antecedência mínima, comandos admin e o relatório mensal.
Cada bug real encontrado em teste manual (ver
`docs/08-registro-de-testes.md`) virou um teste automatizado aqui, pra
nunca mais precisar redescobrir o mesmo problema. Rodam em banco SQLite
em memória — não tocam no banco de desenvolvimento nem geram arquivos
reais.

## O que já existe
- `GET /webhook` — verificação exigida pela Meta ao cadastrar a URL
- `POST /webhook` — recebe mensagens do WhatsApp e conduz a conversa completa de pedido
- **Fluxo de pedido completo** (`app/conversation.py`): cardápio → sabor → tamanho → quantidade → repetir para mais itens → entrega/retirada → endereço → data/horário → resumo com chave Pix → confirmação → pedido salvo no banco
- Cliente pode escolher **mais de um sabor numa mensagem só** (ex: "Nutella e Torta de Limão") — o bot pergunta tamanho e quantidade de cada um em sequência
- Reconhecimento de sabor **ignora acentos** (ex: "limao" reconhece "Limão") — achado em teste real, ver `docs/08-registro-de-testes.md`
- Cliente pode digitar `cancelar` a qualquer momento (cancela o pedido em andamento, ou o último pedido já confirmado, se ainda estiver em status que permite)
- **Cardápio lido direto da Google Sheet** (`app/cardapio.py`) — a loja edita sabores/tamanhos/preços/disponibilidade na planilha, sem precisar de mim. Cache de `CARDAPIO_CACHE_MINUTOS` (`.env`) pra não bater na API a cada mensagem; se a planilha falhar, usa o último cardápio válido em cache e, na pior hipótese, um cardápio fixo de último recurso — a conversa nunca quebra por causa disso
- **Antecedência mínima de 24h** (`app/agendamento.py`) — a loja trabalha por encomenda, então o bot exige pelo menos `ANTECEDENCIA_MINIMA_HORAS` (`.env`) entre o pedido e a entrega/retirada. Entende `hoje`, `amanhã` e datas explícitas (`25/12`) sempre com horário, com ou sem "h"/":" (`15h`, `15h30`, `20`) — parser feito à mão de propósito, não usa lib de NLP de datas (ver `docs/01-visao-geral.md`)
- **Evento criado automaticamente no Google Agenda** (`app/agenda_service.py`) ao confirmar um pedido — data/horário, itens e endereço (se entrega). Se a Agenda não estiver configurada ou a chamada falhar, o pedido continua sendo salvo normalmente (não trava a conversa)
- Banco SQLite criado automaticamente em `data/pipoca.db` na primeira execução
- Checagem de horário de atendimento (8h–21h, configurável no `.env`)
- **Taxa de entrega pronta pra ligar** — `TAXA_ENTREGA_FIXA` (`.env`) fica em branco até a loja decidir a regra ("a confirmar com a loja" no resumo); preenchendo um valor fixo, passa a aparecer automaticamente no resumo e no total, sem precisar de código novo
- **Relatório mensal real** (`app/relatorio.py`) — checagem de número admin (`ADMIN_PHONE_NUMBER` no `.env`, aceita mais de um separado por vírgula) com os comandos `relatorio` (mês atual) e `relatorio mes passado`. Gera um `.xlsx` com quantidade e faturamento por sabor/tamanho, salvo em `backend/relatorios/` (nunca commitado — dados reais de venda), e **manda o arquivo direto pelo WhatsApp** como anexo (`app/whatsapp.py: enviar_documento`)
- `app/dispatcher.py` decide se uma mensagem é comando admin ou pedido normal — usado tanto pelo webhook quanto pelo `chat_local.py`, pra não duplicar essa lógica
- `app/respostas.py` (`RespostaBot`) separa texto de anexo na resposta — só o webhook de verdade faz a chamada de envio pelo WhatsApp; o resto do código (incluindo os testes) nunca bate na API real

## Próximos passos (ver docs/04-guia-de-inicio.md)
- Definir a chave Pix real da loja no `.env`
- Completar a Verificação da Empresa na Meta (bloqueando o envio de mensagens agora — erro 130497)
- Testar o webhook publicamente com um túnel temporário (ex: ngrok) durante o desenvolvimento
- Deploy no VPS

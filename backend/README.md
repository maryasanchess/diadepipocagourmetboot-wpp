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

## O que já existe
- `GET /webhook` — verificação exigida pela Meta ao cadastrar a URL
- `POST /webhook` — recebe mensagens do WhatsApp e conduz a conversa completa de pedido
- **Fluxo de pedido completo** (`app/conversation.py`): cardápio → sabor → tamanho → quantidade → repetir para mais itens → entrega/retirada → endereço → data/horário → resumo com chave Pix → confirmação → pedido salvo no banco
- Cliente pode digitar `cancelar` a qualquer momento (cancela o pedido em andamento, ou o último pedido já confirmado, se ainda estiver em status que permite)
- Cardápio em `app/cardapio.py` — **preços fictícios por enquanto** (a loja ainda não definiu os valores reais; quando a Google Sheet do cardápio existir, só esse arquivo muda)
- Banco SQLite criado automaticamente em `data/pipoca.db` na primeira execução
- Checagem de horário de atendimento (8h–21h, configurável no `.env`)
- Checagem de número admin (`ADMIN_PHONE_NUMBER` no `.env`) com comando `relatorio` (ainda um placeholder)

## Próximos passos (ver docs/04-guia-de-inicio.md)
- Testar o webhook publicamente com um túnel temporário (ex: ngrok) durante o desenvolvimento
- Trocar os preços fictícios pelos preços reais da loja
- Ler o cardápio da Google Sheet (em vez do placeholder em `app/cardapio.py`)
- Criar evento no Google Agenda ao confirmar pedido
- Gerar a planilha mensal sob o comando `relatorio`

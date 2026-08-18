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
- `POST /webhook` — recebe mensagens do WhatsApp e responde com uma mensagem fixa de boas-vindas (fluxo completo de pedido ainda não implementado)
- Banco SQLite criado automaticamente em `data/pipoca.db` na primeira execução
- Checagem de horário de atendimento (8h–21h, configurável no `.env`)
- Checagem de número admin (`ADMIN_PHONE_NUMBER` no `.env`) com comando `relatorio` (ainda um placeholder)

## Próximos passos (ver docs/04-guia-de-inicio.md)
- Testar o webhook publicamente com um túnel temporário (ex: ngrok) durante o desenvolvimento
- Implementar o fluxo real de pedido (cardápio → tamanho → quantidade → entrega → pagamento)
- Ler o cardápio da Google Sheet
- Criar evento no Google Agenda ao confirmar pedido
- Gerar a planilha mensal sob o comando `relatorio`

# Arquitetura

## Diagrama (visão simples)

```
Cliente (WhatsApp)
      │
      ▼
WhatsApp Cloud API (Meta) ── webhook (HTTPS) ──▶ Backend (FastAPI, no VPS)
      ▲                                                 │
      │ resposta via API                                ├──▶ Banco de dados (SQLite)
      └─────────────────────────────────────────────────┤        guarda pedidos, clientes, estado da conversa
                                                          │
                                                          ├──▶ Google Sheets API (cardápio)
                                                          │        loja edita sabores/tamanhos/preços direto na planilha
                                                          │
                                                          ├──▶ Google Calendar API
                                                          │        cria evento de previsão de entrega
                                                          │
                                                          └──▶ Gerador de planilha (openpyxl/pandas)
                                                                   roda mensalmente (ou sob comando) → .xlsx
```

## Componentes

### 1. Webhook (recebe mensagens)
Endpoint HTTPS (`POST /webhook`) que a Meta chama toda vez que o cliente manda
uma mensagem. Precisa responder rápido (Meta espera resposta em poucos
segundos) — por isso o processamento pesado deve ser assíncrono.

Também precisa de um endpoint `GET /webhook` para a verificação inicial que a
Meta exige ao cadastrar a URL (challenge/response com o `WHATSAPP_VERIFY_TOKEN`).

### 2. Motor de conversa (state machine)
Cada número de telefone tem um "estado" de conversa (ex: `aguardando_sabor`,
`aguardando_tamanho`, `aguardando_confirmacao`). O backend decide a próxima
pergunta com base no estado atual + na mensagem recebida. Esse estado fica
salvo no banco (não em memória), para sobreviver a reinícios do servidor.

### 3. Banco de dados
SQLite para começar — é um único arquivo, fácil de fazer backup, e dá conta
tranquilamente do volume de uma loja pequena/média. Tabelas principais:
- `clientes` (telefone, nome)
- `pedidos` (cliente, itens, endereço/retirada, data de entrega, status)
- `itens_pedido` (pedido, sabor, tamanho, quantidade, preço)
- `estado_conversa` (telefone, etapa_atual, dados_temporarios)

Se o volume crescer muito (centenas de pedidos simultâneos, múltiplos
atendentes), migra-se para PostgreSQL sem mudar o resto da arquitetura.

### 4. Cardápio administrável (Google Sheets)
Sabores, tamanhos, preços e disponibilidade **não ficam fixos no código** —
ficam numa Google Sheet que a própria loja edita. O backend lê essa planilha
via Google Sheets API (mesma conta de serviço usada no Calendar) e mantém um
cache curto em memória/banco para não bater na API a cada mensagem recebida.
Se a leitura falhar (API fora do ar, planilha mal preenchida), o bot usa o
último cardápio válido em cache em vez de quebrar a conversa.

### 5. Integração com Google Agenda
Ao confirmar um pedido, o backend chama a Google Calendar API e cria um
evento com: data/hora de entrega prevista, nome do cliente, itens
resumidos, endereço (se entrega). Usa uma **conta de serviço** do Google
Cloud com acesso de "editor" a um calendário específico (não a agenda
pessoal de ninguém).

### 6. Gerador de planilha mensal
Um script/rotina que consulta o banco (`pedidos` + `itens_pedido`) filtrando
por mês, agrupa por sabor + tamanho, e gera um `.xlsx`. Pode ser disparado:
- manualmente (comando no terminal do VPS),
- por um agendador (cron) rodando todo dia 1º,
- ou por um comando especial que a própria loja manda no WhatsApp (ex: dono manda "relatório" e o bot responde com o arquivo) — desde que o número da loja seja identificado como "admin".

### 7. Hospedagem (VPS)
O backend fica rodando continuamente num VPS com:
- Python + FastAPI atrás de um servidor ASGI (uvicorn/gunicorn)
- Um proxy reverso (nginx ou Caddy) cuidando do HTTPS (certificado via Let's Encrypt) — a Meta **exige** que o webhook seja HTTPS
- Um domínio ou subdomínio apontando para o VPS (necessário para o certificado HTTPS)

## Por que essa arquitetura e não outra
- Simples o suficiente para uma pessoa manter sozinha.
- Sem dependências pagas além do que já está listado em `03-custos.md`.
- Cada peça (webhook, banco, calendário, planilha) é independente — dá para testar uma de cada vez.

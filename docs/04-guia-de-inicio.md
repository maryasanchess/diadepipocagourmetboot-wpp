# Guia de início — do zero ao primeiro deploy

Ordem recomendada. Cada etapa vira um commit/checkpoint no projeto.

## Etapa 0 — Onde programar
Você não precisa de nenhuma ferramenta paga para programar:
- **Editor de código:** VS Code (gratuito) — é o mais usado para Python/FastAPI, tem extensão oficial de Python.
- **Python:** instalar Python 3.11+ no seu computador (mesmo ambiente que você já usa no projeto GLPI).
- Vamos programar e testar o bot **localmente no seu PC** primeiro, e só depois publicar no VPS.

## Etapa 1 — Conta WhatsApp Business (Meta)
1. Criar/usar uma conta em [business.facebook.com](https://business.facebook.com) (Meta Business Suite).
2. Dentro do Meta Business, acessar "WhatsApp" → criar um app de desenvolvedor em [developers.facebook.com](https://developers.facebook.com).
3. Associar o app ao WhatsApp Business Platform (Cloud API).
4. Anotar: `Phone Number ID`, `WhatsApp Business Account ID`, e gerar um `Token de acesso temporário` (depois trocamos por um permanente).
5. Confirmar a página de preços atual da Cloud API (ver `03-custos.md`).

> Vamos fazer essa etapa juntos quando você estiver pronto — eu te explico cada tela.

## Etapa 2 — Google Cloud (para Calendar e Sheets) ✅ concluída
1. ✅ Criar um projeto gratuito no [Google Cloud Console](https://console.cloud.google.com). Projeto: `diadepipoca-bot`.
2. ✅ Ativar a "Google Calendar API" **e** a "Google Sheets API" (mesmo projeto).
3. ✅ Criar uma **conta de serviço** e baixar o arquivo de credenciais JSON. Conta de serviço: `diadepipocas-agenda-planilha@diadepipoca-bot.iam.gserviceaccount.com` (arquivo salvo localmente em `backend/credentials/google_credentials.json`, protegido pelo `.gitignore` — nunca é commitado).
4. ✅ Google Agenda "Pedidos Diadê Pipocas" compartilhada com a conta de serviço (permissão de editor). ID salvo em `.env` (local, nunca commitado).
5. ✅ Planilha "Cardápio Diadê Pipocas" criada, preenchida com os 18 itens do cardápio, formatada e compartilhada com a conta de serviço. ID salvo em `.env`.

## Etapa 3 — Esqueleto do backend (local)
1. Criar ambiente virtual Python (`python -m venv .venv`) dentro de `backend/`.
2. Instalar FastAPI + uvicorn.
3. Criar os dois endpoints do webhook (`GET` de verificação, `POST` de recebimento).
4. Testar localmente expondo a porta com uma ferramenta de túnel temporária (ex: ngrok) só durante o desenvolvimento, para a Meta conseguir alcançar seu PC.

## Etapa 4 — Fluxo de conversa ✅ concluída
State machine completa (`01-visao-geral.md`), com o cardápio lido **direto
da Google Sheet** (`backend/app/cardapio.py`, com cache e fallback se a
planilha falhar) em vez de preços fixos no código.

## Etapa 5 — Persistência (banco de dados)
Modelar as tabelas de `02-arquitetura.md`, salvar pedidos reais de teste.

## Etapa 6 — Integração com Google Agenda ✅ concluída
Ao confirmar um pedido, o backend cria automaticamente o evento na Agenda
(`backend/app/agenda_service.py`), com data/horário, itens e endereço (se
entrega). Testado com um pedido real de ponta a ponta — evento conferido
direto na API e removido depois por ser só teste.

## Etapa 7 — Geração da planilha mensal ✅ concluída (falta só o envio pelo WhatsApp)
`backend/app/relatorio.py` lê o banco e gera o `.xlsx` agrupado por
sabor/tamanho, com faturamento e total de pedidos. Acionado pelos comandos
admin `relatorio` (mês atual) e `relatorio mes passado`. O arquivo fica
salvo em `backend/relatorios/` — enviar automaticamente pelo WhatsApp
depende da Cloud API estar configurada de verdade.

## Etapa 8 — Deploy no VPS
1. Escolher provedor (ver `03-custos.md`).
2. Configurar domínio/subdomínio + HTTPS (Let's Encrypt).
3. Subir o backend com um processo supervisionado (ex: `systemd` ou Docker) para reiniciar sozinho se cair.
4. Atualizar a URL do webhook na Meta para apontar pro VPS.

## Etapa 9 — Testes com pedido real controlado
Fazer um pedido de teste de ponta a ponta com um número seu, conferir se o
evento apareceu certo no Google Agenda e se o pedido ficou salvo certo no
banco.

---

**Próxima ação sugerida:** você me passa o cardápio real (sabores, tamanhos,
preços, se tem entrega/retirada, forma de pagamento aceita) e a gente já
fecha o `01-visao-geral.md` com as respostas, aí partimos pra Etapa 1.

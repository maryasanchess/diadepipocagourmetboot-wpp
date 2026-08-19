# Guia de início — do zero ao primeiro deploy

Ordem recomendada. Cada etapa vira um commit/checkpoint no projeto.

## Etapa 0 — Onde programar
Você não precisa de nenhuma ferramenta paga para programar:
- **Editor de código:** VS Code (gratuito) — é o mais usado para Python/FastAPI, tem extensão oficial de Python.
- **Python:** instalar Python 3.11+ no seu computador (mesmo ambiente que você já usa no projeto GLPI).
- Vamos programar e testar o bot **localmente no seu PC** primeiro, e só depois publicar no VPS.

## Etapa 1 — Conta WhatsApp Business (Meta)
1. ✅ Criar conta pessoal + portfólio empresarial em [business.facebook.com](https://business.facebook.com) — "Diadê Pipocas Gourmet".
2. ✅ Superada a restrição inicial da conta (bloqueio de "conta muito nova" e depois uma restrição de publicidade/automação — resolvida via pedido de análise em 19/08/2026).
3. ✅ Criar o app de desenvolvedor em [developers.facebook.com](https://developers.facebook.com) ("Diadê Pipocas Gourmet Bot"), associado ao portfólio "Diadê Pipocas Gourmet".
4. ✅ Adicionar o produto **WhatsApp** ao app e reivindicar o número de teste.
5. ✅ `Phone Number ID`, `WhatsApp Business Account ID` e `Token de acesso temporário` salvos no `.env` local.
6. ✅ Webhook configurado e verificado (ver nota abaixo sobre o túnel de teste).
7. ✅ Campo `messages` assinado, e app inscrito na conta do WhatsApp Business (`subscribed_apps` — ver nota abaixo).
8. 🚧 **Bloqueado:** mensagens de teste falham com o erro 130497 ("Business account is restricted from messaging users in this country"). Provável causa: falta completar a **Etapa 3. Verificação da empresa** dentro do fluxo da Meta (pode exigir CNPJ). Em investigação.
9. ⬜ Confirmar a página de preços atual da Cloud API (ver `03-custos.md`).

> Feita junto, tela por tela, mas **sem automação de navegador** — a Meta
> restringiu a conta uma vez suspeitando de automação, então essa etapa
> daqui pra frente é sempre a própria loja clicando/digitando.

### Nota — testando o webhook localmente com ngrok
Enquanto o backend não está no VPS (Etapa 8), usamos o **ngrok** (instalado
localmente) pra criar uma URL pública temporária que aponta pro backend
rodando no PC, só durante os testes. Essa URL muda toda vez que o ngrok é
reiniciado — **não é a URL definitiva**, então não adianta anotar em lugar
nenhum permanente. Quando o backend for pro VPS, trocamos pela URL real do
domínio na configuração do webhook.

Achado real durante o teste: mensagens de texto livre só são entregues
depois que o cliente manda a primeira mensagem pro número (abre a "janela
de 24h"); mandar via **webhook.site** pra depurar não funcionou porque ele
não responde ao desafio de verificação do jeito que a Meta exige — por
isso trocamos pro nosso próprio backend via túnel ngrok.

Outro achado: verificar o webhook e assinar `messages` não é suficiente —
a conta do WhatsApp Business precisa estar **inscrita no app**
(`subscribed_apps`). Sem isso, os eventos vão pro app de demonstração
padrão da Meta, não pro nosso. Ver `docs/08-registro-de-testes.md` (Teste
3) para o diagnóstico completo, incluindo como usamos o próprio ngrok
(`http://127.0.0.1:4040`) pra inspecionar o conteúdo das requisições e
achar o erro 130497 escondido no status de entrega.

**Diadê Pipocas Gourmet tem CNPJ**, então a Etapa 3 (Verificação da
empresa) pode seguir o caminho normal, sem precisar de alternativa pra
negócio informal.

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
1. ✅ Escolher provedor (ver `03-custos.md`) — decidido: **Hostinger**.
2. ⬜ Criar a conta e contratar o plano de VPS.
3. ⬜ Configurar domínio/subdomínio + HTTPS (Let's Encrypt).
4. ⬜ Subir o backend com um processo supervisionado (ex: `systemd` ou Docker) para reiniciar sozinho se cair.
5. ⬜ Atualizar a URL do webhook na Meta para apontar pro VPS.

## Etapa 9 — Testes com pedido real controlado
Fazer um pedido de teste de ponta a ponta com um número seu, conferir se o
evento apareceu certo no Google Agenda e se o pedido ficou salvo certo no
banco.

---

**Próxima ação sugerida:** você me passa o cardápio real (sabores, tamanhos,
preços, se tem entrega/retirada, forma de pagamento aceita) e a gente já
fecha o `01-visao-geral.md` com as respostas, aí partimos pra Etapa 1.

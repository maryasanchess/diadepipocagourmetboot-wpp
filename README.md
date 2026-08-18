# PipocaBot — Atendimento de pedidos via WhatsApp

Bot de WhatsApp para uma loja de pipocas gourmet. O cliente faz o pedido inteiro
conversando com o bot; a loja só precisa olhar o calendário (Google Agenda) para
ver as entregas previstas, e consultar uma planilha mensal para saber quantidades
vendidas por sabor/tamanho.

> Projeto em construção. A documentação em `docs/` está sendo escrita junto com o
> desenvolvimento — cada etapa concluída é registrada lá.

## Como o sistema funciona (visão geral)

1. Cliente manda mensagem no WhatsApp da loja.
2. A Meta (WhatsApp Cloud API) entrega essa mensagem para o nosso backend via *webhook*.
3. O backend conduz uma conversa guiada (sabor, tamanho, quantidade, endereço/data de entrega, pagamento) e salva o pedido em um banco de dados local.
4. Ao fechar o pedido, o backend cria automaticamente um evento no Google Agenda com a previsão de entrega.
5. Mensalmente (ou sob demanda), o backend gera uma planilha `.xlsx` com o total de pedidos por sabor/tamanho.

## Documentação

- [docs/01-visao-geral.md](docs/01-visao-geral.md) — escopo e fluxo de conversa do bot
- [docs/02-arquitetura.md](docs/02-arquitetura.md) — como as peças se conectam
- [docs/03-custos.md](docs/03-custos.md) — tudo que tem custo mensal ou único
- [docs/04-guia-de-inicio.md](docs/04-guia-de-inicio.md) — passo a passo para sair do zero até o primeiro deploy
- [docs/05-git-e-seguranca.md](docs/05-git-e-seguranca.md) — o que pode ir pro Git e o que nunca pode

## Stack escolhida

- **Backend:** Python + FastAPI
- **WhatsApp:** WhatsApp Cloud API (oficial, Meta)
- **Calendário:** Google Calendar API
- **Planilhas:** openpyxl / pandas
- **Banco de dados:** SQLite (início) — pode migrar para PostgreSQL se o volume crescer
- **Hospedagem:** VPS (a definir provedor em `docs/03-custos.md`)

## Status atual

- [x] Estrutura do projeto e documentação inicial
- [ ] Conta Meta Business + WhatsApp Cloud API configurada
- [ ] Webhook recebendo mensagens
- [ ] Fluxo de conversa (cardápio → pedido → confirmação)
- [ ] Integração com Google Agenda
- [ ] Geração de planilha mensal
- [ ] Deploy no VPS

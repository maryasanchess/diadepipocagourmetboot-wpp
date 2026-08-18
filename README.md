<div align="center">

# 🍿 PipocaBot

**Atendimento automático de pedidos via WhatsApp para uma loja de pipocas gourmet**

![status](https://img.shields.io/badge/status-em%20desenvolvimento-C87F0A)
![python](https://img.shields.io/badge/backend-Python%20%2B%20FastAPI-3776AB)
![whatsapp](https://img.shields.io/badge/whatsapp-Cloud%20API-25D366)
![privado](https://img.shields.io/badge/repo-privado-6B3F1D)

</div>

---

## 📋 Sobre o projeto

O cliente faz o pedido inteiro conversando com o bot no WhatsApp — escolhe
sabor, tamanho, quantidade, entrega ou retirada, e forma de pagamento — sem
que ninguém da loja precise responder mensagem manualmente.

A loja só interage com dois lugares:

| Onde | Para quê |
|---|---|
| 📅 **Google Agenda** | Ver as entregas previstas do dia/semana |
| 📊 **Planilha mensal** | Ver quantidade vendida por sabor e tamanho |

> Projeto em construção. A documentação em [`docs/`](docs/) é escrita junto
> com o desenvolvimento — cada decisão e cada etapa concluída fica
> registrada lá.

## 🔄 Como funciona

```
Cliente (WhatsApp)
      │  manda mensagem
      ▼
WhatsApp Cloud API (Meta)
      │  webhook
      ▼
Backend (FastAPI)  ──▶  Cardápio (Google Sheet, editado pela loja)
      │
      ├──▶  Banco de dados — salva o pedido
      ├──▶  Google Agenda — cria evento de previsão de entrega
      └──▶  Planilha mensal — relatório de vendas por sabor/tamanho
```

1. Cliente manda mensagem no WhatsApp da loja.
2. A Meta (WhatsApp Cloud API) entrega essa mensagem ao backend via *webhook*.
3. O backend conduz a conversa (sabor → tamanho → quantidade → entrega/retirada → pagamento), consultando o cardápio atualizado numa Google Sheet.
4. Ao fechar o pedido, cria automaticamente um evento no Google Agenda com a previsão de entrega.
5. Mensalmente (ou sob comando do número admin), gera uma planilha `.xlsx` com o total vendido por sabor/tamanho.

## 📚 Documentação

| Documento | Conteúdo |
|---|---|
| [`docs/01-visao-geral.md`](docs/01-visao-geral.md) | Escopo, cardápio, regras de negócio e fluxo de conversa |
| [`docs/02-arquitetura.md`](docs/02-arquitetura.md) | Como as peças se conectam |
| [`docs/03-custos.md`](docs/03-custos.md) | Tudo que tem custo mensal ou único |
| [`docs/04-guia-de-inicio.md`](docs/04-guia-de-inicio.md) | Passo a passo do zero até o primeiro deploy |
| [`docs/05-git-e-seguranca.md`](docs/05-git-e-seguranca.md) | O que pode ir pro Git e o que nunca pode |
| [`docs/06-sincronizar-dois-computadores.md`](docs/06-sincronizar-dois-computadores.md) | Trabalhar do notebook da empresa e de casa sem perder nada |
| [`Resumo-Projeto-PipocaBot.docx`](Resumo-Projeto-PipocaBot.docx) | Resumo não técnico, em Word, para compartilhar |

## 🛠️ Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python + FastAPI |
| WhatsApp | WhatsApp Cloud API (oficial, Meta) |
| Calendário | Google Calendar API |
| Cardápio | Google Sheets API (editável pela loja) |
| Planilhas de relatório | openpyxl / pandas |
| Banco de dados | SQLite (início) → PostgreSQL se o volume crescer |
| Hospedagem | VPS (provedor a definir, ver `docs/03-custos.md`) |

## ✅ Status atual

- [x] Estrutura do projeto e documentação inicial
- [x] Esqueleto do backend rodando localmente (webhook, banco, horário de atendimento, checagem de admin)
- [x] Repositório salvo com segurança no GitHub (privado)
- [ ] Conta Meta Business + WhatsApp Cloud API configurada
- [ ] Webhook testado recebendo mensagens reais (via túnel/deploy)
- [ ] Cardápio lido da Google Sheet
- [ ] Fluxo de conversa completo (cardápio → tamanho → quantidade → entrega → pagamento → confirmação)
- [ ] Cancelamento/alteração de pedido pelo bot
- [ ] Integração com Google Agenda
- [ ] Geração de planilha mensal (comando admin `relatorio`)
- [ ] Deploy no VPS

---

<div align="center">
<sub>Projeto privado — loja de pipocas gourmet. Não contém dados reais de clientes ou credenciais (ver <a href="docs/05-git-e-seguranca.md">docs/05-git-e-seguranca.md</a>).</sub>
</div>

<div align="center">

# 🍿 PipocaBot

**Atendimento automático de pedidos via WhatsApp para a Diadê Pipocas Gourmet**

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
| [`docs/07-como-testar-e-consultar.md`](docs/07-como-testar-e-consultar.md) | Como ver o código, ler a documentação e testar o bot no dia a dia |
| [`docs/08-registro-de-testes.md`](docs/08-registro-de-testes.md) | Histórico de testes reais: o que foi testado, bugs encontrados e corrigidos |
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

## 🗂️ Estrutura do projeto

```
PipocaBot_WhatsApp/
├── README.md                        este arquivo
├── .env.example                     modelo de configuração (o .env real nunca é commitado)
├── docs/                            documentação completa, um tema por arquivo
├── Resumo-Projeto-PipocaBot.docx    resumo não técnico do projeto
└── backend/
    ├── app/
    │   ├── main.py                  app FastAPI
    │   ├── webhook.py               endpoints que recebem o WhatsApp
    │   ├── conversation.py          fluxo de pedido (a "inteligência" do bot)
    │   ├── cardapio.py              sabores/tamanhos/preços (fictícios por enquanto)
    │   ├── models.py                tabelas do banco de dados
    │   └── ...
    ├── chat_local.py                testa o bot no terminal, sem WhatsApp
    ├── data/                        banco SQLite local (gitignored)
    └── credentials/                 credenciais do Google (gitignored)
```

## ✅ Status atual

- [x] Estrutura do projeto e documentação inicial
- [x] Repositório salvo com segurança no GitHub (privado)
- [x] Esqueleto do backend rodando localmente (webhook, banco, horário de atendimento, checagem de admin)
- [x] Fluxo de conversa completo (cardápio → tamanho → quantidade → entrega → pagamento → confirmação), testado de ponta a ponta com preços reais
- [x] Cancelamento de pedido pelo bot (em andamento ou já confirmado)
- [x] Antecedência mínima de 24h para pedidos (loja trabalha por encomenda)
- [x] Chat de terminal para testar sem depender do WhatsApp (`chat_local.py`)
- [x] Preços reais definidos pela loja (fixos no código por enquanto, ver `docs/01-visao-geral.md`)
- [ ] Cardápio lido da Google Sheet (hoje os preços estão fixos em `backend/app/cardapio.py`)
- [ ] Conta Meta Business + WhatsApp Cloud API configurada
- [ ] Webhook testado recebendo mensagens reais (via túnel/deploy)
- [ ] Integração com Google Agenda
- [ ] Geração de planilha mensal (comando admin `relatorio`)
- [ ] Deploy no VPS

---

<div align="center">
<sub>Projeto privado — Diadê Pipocas Gourmet. Não contém dados reais de clientes ou credenciais (ver <a href="docs/05-git-e-seguranca.md">docs/05-git-e-seguranca.md</a>).</sub>
</div>

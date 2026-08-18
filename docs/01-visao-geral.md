# Visão geral do produto

## Objetivo

Automatizar 100% do atendimento de pedidos da loja de pipocas gourmet pelo
WhatsApp, sem que ninguém da loja precise responder mensagens manualmente. A
equipe da loja só interage com dois lugares:

1. **Google Agenda** — cada pedido fechado vira um evento com a previsão de entrega.
2. **Planilha mensal** — relatório `.xlsx` com quantidade vendida por sabor e tamanho.

## Quem usa o quê

| Papel | O que faz | Onde |
|---|---|---|
| Cliente | Faz o pedido inteiro conversando com o bot | WhatsApp |
| Loja | Vê as entregas do dia/semana | Google Agenda |
| Loja | Vê quanto vendeu de cada sabor/tamanho no mês | Planilha `.xlsx` |
| Loja (opcional) | Aciona geração da planilha por comando ou recebe automaticamente todo mês | WhatsApp ou e-mail |

## Fluxo de conversa (rascunho — vamos refinar juntos)

1. **Saudação** — cliente manda "oi"/qualquer mensagem → bot se apresenta e mostra o cardápio (sabores + tamanhos + preços).
2. **Escolha do sabor** — bot lista opções, cliente escolhe (texto livre ou botões de lista da Cloud API).
3. **Escolha do tamanho** — P / M / G, com preço de cada um.
4. **Quantidade** — quantas unidades desse sabor/tamanho.
5. **Mais alguma coisa?** — permite adicionar outro sabor ao mesmo pedido, repetindo passos 2–4.
6. **Entrega ou retirada** — pergunta endereço (se entrega) ou confirma retirada na loja.
7. **Data/horário desejado** — cliente informa quando quer receber; bot valida contra horários que a loja aceita (a definir).
8. **Forma de pagamento** — Pix, cartão, dinheiro (a definir quais a loja aceita via bot; pagamento em si pode continuar sendo tratado fora do bot, ex: chave Pix enviada como texto).
9. **Resumo e confirmação** — bot mostra o pedido completo e pede confirmação final.
10. **Fechamento** — bot salva o pedido, cria o evento no Google Agenda, envia mensagem de confirmação ao cliente com o número do pedido.

### Perguntas para decidirmos juntos antes de programar o fluxo
- Quais sabores e tamanhos existem hoje, e os preços de cada combinação?
- A loja faz entrega, retirada, ou os dois? Tem taxa de entrega / raio de entrega?
- Existe prazo mínimo de antecedência para o pedido (ex: "pedidos só para o dia seguinte")?
- Como funciona o pagamento hoje (Pix manual, link de pagamento, na entrega)?
- O cliente pode cancelar ou alterar um pedido pelo próprio bot?
- Precisa ter um horário de atendimento (ex: bot só aceita pedido das 9h às 20h) ou funciona 24h?

## Fora de escopo (por enquanto)
- Atendimento humano assumindo a conversa (pode ser adicionado depois com "handoff").
- Pagamento integrado (gateway de pagamento dentro do bot).
- Múltiplas lojas/filiais.

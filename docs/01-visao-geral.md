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

## Cardápio (confirmado)

Sabores disponíveis:

| Sabor |
|---|
| 🍫 Nutella |
| 🥛 Ninho |
| 🧀 Doritos |
| 🍫 Kinder Bueno |
| 🍓 Frutas Vermelhas |
| 🍋 Torta de Limão |

Tamanhos disponíveis (mesmo conjunto para todos os sabores): **50g, 80g,
100g, 150g**.

### Cardápio administrável pela própria loja (decisão de arquitetura)

Os preços ainda não estão definidos, e a loja quer poder **cadastrar e
atualizar sabores/tamanhos/preços sozinha, sem depender de mudança de
código**. Decisão: o cardápio vai morar numa **Google Sheet** (planilha do
Google, não arquivo local), no formato:

| sabor | tamanho_g | preco | disponivel |
|---|---|---|---|
| Nutella | 50 | 12.00 | sim |
| Nutella | 80 | 18.00 | sim |
| ... | ... | ... | ... |

- A loja edita essa planilha direto (inclusive pelo celular, app do Google Sheets).
- O bot lê os preços/disponibilidade dessa planilha (com um cache curto, ex: 5–10 minutos, para não consultar a API do Google a cada mensagem).
- Usa a mesma conta de serviço do Google que já vamos criar para o Calendar — só precisamos ativar também a **Google Sheets API** no mesmo projeto (ver `04-guia-de-inicio.md`).
- Coluna `disponivel` permite a loja "pausar" um sabor/tamanho (ex: acabou o estoque) sem apagar a linha.

> **Pendente:** você define os preços e me avisa quando quiser que eu monte o modelo real da planilha (posso criar um exemplo pronto para você preencher).

## Entrega e retirada (confirmado)
- A loja faz **os dois**: entrega e retirada no local.
- Tem **taxa de entrega**, mas a regra ainda está em definição — combinamos esperar. Até lá, o bot pergunta o endereço normalmente e registra a taxa como **"a confirmar"** no pedido; a loja informa o valor manualmente ao cliente por fora do bot. Quando a regra existir (fixo, por bairro, por km), plugamos no fluxo sem precisar redesenhar o resto.

## Prazo de antecedência (confirmado)
**Sem trava no MVP** — o bot aceita pedido para qualquer horário/data que o
cliente escolher. Se na prática isso gerar problema (pedido de última hora
inviável), adicionamos uma regra depois com base em casos reais.

## Pagamento (confirmado)
- Só **Pix**, "de qualquer forma" — ou seja, o bot não precisa validar tipo de chave nem gerar cobrança automática por enquanto. Ele informa a chave Pix da loja (ou manda um texto/QR fixo) e o cliente paga por fora do bot. Confirmação de pagamento pode ficar manual (loja confere o Pix recebido) neste primeiro momento.

### Ainda em aberto
- Preços de cada sabor+tamanho na planilha do cardápio
- Regra e valor da taxa de entrega
- Se o cliente pode cancelar/alterar pedido pelo próprio bot
- Horário de atendimento do bot (24h ou dentro de uma janela, ex: 9h–20h)

## Fora de escopo (por enquanto)
- Atendimento humano assumindo a conversa (pode ser adicionado depois com "handoff").
- Pagamento integrado (gateway de pagamento dentro do bot).
- Múltiplas lojas/filiais.

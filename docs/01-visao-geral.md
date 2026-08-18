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

> **Pendente:** tamanhos (ex: P/M/G ou pacote único?) e preço de cada
> combinação sabor+tamanho. Sem isso o bot não consegue montar o orçamento
> do pedido — é o próximo dado que preciso de você.

## Entrega e retirada (confirmado)
- A loja faz **os dois**: entrega e retirada no local.
- Tem **taxa de entrega**, mas o valor/regra (fixo? por bairro? por distância/raio em km?) ainda **não foi definido**. Até decidirmos, o bot pode perguntar o endereço e a loja calcula a taxa manualmente por enquanto (fica registrado como "a confirmar" no pedido) — ou definimos um valor fixo simples para começar (ex: "R$5 para entrega, retirada grátis") e refinamos depois.

## Prazo de antecedência — explicando a pergunta
Isso é sobre se o bot deve **aceitar pedido para "agora/hoje"** ou só para
datas futuras. Exemplos do que essa regra evita:
- Cliente pede às 22h pedindo entrega em 20 minutos, mas a loja já fechou ou não dá tempo de preparar.
- Cliente pede 50 unidades para "daqui a 1 hora", impossível de produzir a tempo.

Com uma regra de antecedência (ex: "pedidos feitos até as 18h são para o dia
seguinte" ou "mínimo de 2h de antecedência"), o bot já filtra isso na
conversa e nem deixa o cliente escolher um horário inviável.

> **Pendente:** você decide se quer essa trava e qual seria (ex: sem trava
> nenhuma / mínimo de X horas / só para o dia seguinte). Podemos começar
> **sem trava nenhuma** no MVP e adicionar depois se virar problema na
> prática — costuma ser mais fácil ajustar depois de ver pedidos reais.

## Pagamento (confirmado)
- Só **Pix**, "de qualquer forma" — ou seja, o bot não precisa validar tipo de chave nem gerar cobrança automática por enquanto. Ele informa a chave Pix da loja (ou manda um texto/QR fixo) e o cliente paga por fora do bot. Confirmação de pagamento pode ficar manual (loja confere o Pix recebido) neste primeiro momento.

### Ainda em aberto
- Tamanhos e preços de cada sabor (bloqueia o próximo passo)
- Regra e valor da taxa de entrega
- Se o cliente pode cancelar/alterar pedido pelo próprio bot
- Horário de atendimento do bot (24h ou dentro de uma janela, ex: 9h–20h)

## Fora de escopo (por enquanto)
- Atendimento humano assumindo a conversa (pode ser adicionado depois com "handoff").
- Pagamento integrado (gateway de pagamento dentro do bot).
- Múltiplas lojas/filiais.

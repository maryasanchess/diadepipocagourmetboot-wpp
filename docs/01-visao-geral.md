# Visão geral do produto

## Objetivo

Automatizar 100% do atendimento de pedidos da **Diadê Pipocas Gourmet** pelo
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

## Fluxo de conversa (implementado e testado — ver `docs/08-registro-de-testes.md`)

1. **Saudação** — cliente manda "oi"/qualquer mensagem → bot se apresenta e mostra o cardápio (sabores).
2. **Escolha do sabor** — bot lista opções numeradas; cliente escolhe pelo número, pelo nome (com ou sem acento), ou **mais de um de uma vez** (ex: "Nutella e Torta de Limão").
3. **Escolha do tamanho** — 80g / 100g / 150g, com preço de cada um (50g é brinde, não aparece aqui).
4. **Quantidade** — quantas unidades desse sabor/tamanho. Se o cliente escolheu vários sabores no passo 2, o bot repete os passos 3–4 pra cada um automaticamente, sem precisar confirmar entre eles.
5. **Mais alguma coisa?** — só aparece depois que a fila de sabores escolhidos termina; permite adicionar mais sabores, repetindo os passos 2–4.
6. **Entrega ou retirada** — lista numerada (1. Entrega / 2. Retirada); pergunta endereço se for entrega.
7. **Data/horário desejado** — cliente informa quando quer receber; bot exige pelo menos 24h de antecedência (loja trabalha por encomenda) e reformula o pedido se a data não for entendida ou for muito próxima.
8. **Forma de pagamento** — só Pix; bot informa a chave da loja no resumo do pedido.
9. **Resumo e confirmação** — bot mostra o pedido completo (itens, total, entrega/retirada, data/horário, chave Pix) e pede confirmação final.
10. **Fechamento** — bot salva o pedido no banco com a data/horário validada e cria automaticamente o evento no Google Agenda com a previsão de entrega.

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

### Tamanhos e preços (confirmado, valor inicial)

| Tamanho | Preço | Observação |
|---|---|---|
| 50g | — | **Não é vendido.** É um brinde dado sob encomenda, a critério da loja — não faz parte do fluxo de compra do bot por enquanto. |
| 80g | R$ 12,00 | Mesmo preço para todos os sabores |
| 100g | R$ 18,00 | **Kinder Bueno: R$ 22,00** |
| 150g | R$ 25,00 | Mesmo preço para todos os sabores, incluindo Kinder Bueno |

Esses valores estão fixos em `backend/app/cardapio.py` só para colocar o
bot pra funcionar. A loja pode mudar qualquer preço a qualquer momento me
avisando — e quando a Google Sheet administrável (abaixo) estiver pronta,
a própria loja edita direto por lá, sem precisar de mim.

### Cardápio administrável pela própria loja (decisão de arquitetura)

A loja quer poder **cadastrar e atualizar sabores/tamanhos/preços
sozinha, sem depender de mudança de código**. Decisão: o cardápio vai
morar numa **Google Sheet** (planilha do Google, não arquivo local), no
formato:

| sabor | tamanho_g | preco | disponivel |
|---|---|---|---|
| Nutella | 80 | 12.00 | sim |
| Nutella | 100 | 18.00 | sim |
| Kinder Bueno | 100 | 22.00 | sim |
| ... | ... | ... | ... |

- A loja edita essa planilha direto (inclusive pelo celular, app do Google Sheets).
- O bot lê os preços/disponibilidade dessa planilha (com um cache curto, ex: 5–10 minutos, para não consultar a API do Google a cada mensagem).
- Usa a mesma conta de serviço do Google que já vamos criar para o Calendar — só precisamos ativar também a **Google Sheets API** no mesmo projeto (ver `04-guia-de-inicio.md`).
- Coluna `disponivel` permite a loja "pausar" um sabor/tamanho (ex: acabou o estoque) sem apagar a linha.

## Entrega e retirada (confirmado)
- A loja faz **os dois**: entrega e retirada no local.
- Tem **taxa de entrega**, mas a regra ainda está em definição — combinamos esperar. Até lá, o bot pergunta o endereço normalmente e registra a taxa como **"a confirmar"** no pedido; a loja informa o valor manualmente ao cliente por fora do bot. Quando a regra existir (fixo, por bairro, por km), plugamos no fluxo sem precisar redesenhar o resto.

## Prazo de antecedência (confirmado — revisado)
A loja trabalha **por encomenda**, então o bot exige **pelo menos 24h de
antecedência** entre o pedido e a data/horário de entrega ou retirada
(configurável em `ANTECEDENCIA_MINIMA_HORAS` no `.env`, caso mude no
futuro). Se o cliente pedir uma data/horário mais próximo que isso, o bot
explica a regra e pede uma data mais à frente, sem travar a conversa.

O bot entende os formatos: `hoje`, `amanhã`, uma data explícita (`25/12`
ou `25/12/2026`) — sempre junto com um horário (`15h`, `15h30` ou
`15:30`). Se não conseguir entender o texto, pede pra reformular com um
exemplo.

> Decisão técnica: testamos usar uma biblioteca de interpretação de datas
> em linguagem natural (`dateparser`) e ela deu resultado **errado** em
> casos simples durante o teste. Como essa regra afeta pedido real e,
> depois, o evento no Google Agenda, optamos por um parser simples e
> totalmente previsível (`backend/app/agendamento.py`) em vez de uma
> lib "mágica" que pode falhar sem avisar.

## Pagamento (confirmado)
- Só **Pix**, "de qualquer forma" — ou seja, o bot não precisa validar tipo de chave nem gerar cobrança automática por enquanto. Ele informa a chave Pix da loja (ou manda um texto/QR fixo) e o cliente paga por fora do bot. Confirmação de pagamento pode ficar manual (loja confere o Pix recebido) neste primeiro momento.

## Cancelar/alterar pedido (confirmado)
O cliente **pode cancelar ou alterar** um pedido pelo próprio bot — mas só
enquanto o pedido ainda estiver num estado que permita mudança (ex: ainda
não saiu para produção/entrega). Regra inicial simples: permitir
cancelamento/alteração enquanto o status do pedido for `recebido` ou
`confirmado`; depois que a loja marcar como `em preparo` ou `em entrega`, o
bot informa que não pode mais alterar sozinho e orienta a falar com a loja.
(Esse controle de status é manual por enquanto — ver "Comando de admin"
abaixo.)

## Horário de atendimento (confirmado)
O bot só aceita pedidos **das 8h às 21h**. Fora desse horário:
- o bot continua respondendo (pode tirar dúvida, mostrar cardápio),
- mas avisa que pedidos só são processados dentro do horário de atendimento e sugere o cliente confirmar dentro da janela (ou enfileira o pedido para confirmação assim que abrir, a definir qual comportamento é melhor na prática).

## Comando de admin (confirmado)
A loja terá um **número de telefone cadastrado como admin** (definido em
configuração, não em código — vai para o `.env`, nunca commitado). Só
mensagens vindas desse número específico têm acesso aos comandos
administrativos, por exemplo:
- `relatorio` → bot gera e envia a planilha do mês atual
- (futuro) `pausar <sabor>` → marca um item como indisponível sem precisar abrir a Google Sheet

Qualquer tentativa de usar um comando admin vindo de outro número é
ignorada/rejeitada — o bot trata como mensagem normal de cliente.

### Ainda em aberto
- Regra e valor da taxa de entrega
- Comportamento exato do bot fora do horário 8h–21h (só avisa, ou enfileira o pedido?)

## Fora de escopo (por enquanto)
- Atendimento humano assumindo a conversa (pode ser adicionado depois com "handoff").
- Pagamento integrado (gateway de pagamento dentro do bot).
- Múltiplas lojas/filiais.

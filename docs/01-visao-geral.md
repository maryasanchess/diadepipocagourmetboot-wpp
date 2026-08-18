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
- Preços de cada sabor+tamanho na planilha do cardápio
- Regra e valor da taxa de entrega
- Comportamento exato do bot fora do horário 8h–21h (só avisa, ou enfileira o pedido?)

## Fora de escopo (por enquanto)
- Atendimento humano assumindo a conversa (pode ser adicionado depois com "handoff").
- Pagamento integrado (gateway de pagamento dentro do bot).
- Múltiplas lojas/filiais.

# Registro de testes

Log dos testes reais feitos no bot (via `chat_local.py`) e o que cada um
encontrou. Serve como histórico — pra saber o que já foi validado e o que
foi corrigido por causa de um teste real, não só teoria.

---

## Teste 1 — 2026-08-18: pedido com 2 sabores, entrega

**Quem testou:** a loja, pelo `chat_local.py`, logo depois de ativar a
regra de antecedência mínima de 24h.

**O que foi testado:** pedido com Nutella + Torta de Limão, entrega,
confirmação.

### 🐛 Bug 1 — data/horário sem "h" não era reconhecida
Digitando `hoje as 20`, `18/08 as 16`, `19/08/2026 as 20` (número solto,
sem "h" ou ":" junto), o bot respondia sempre "Não entendi essa
data/horário" — mesmo pra formatos que deveriam ser válidos.

**Causa:** o parser (`backend/app/agendamento.py`) só reconhecia hora no
formato `15h`, `15h30` ou `15:30` — exigia "h" ou ":" grudado no número.
`as 20` (sem separador) não batia com essa regra.

**Correção:** o parser agora primeiro remove o trecho da data do texto e,
se não achar hora no formato com "h"/":", procura um número solto de 1–2
dígitos no que sobrou (ex: "20" em "hoje as 20"). Testado com todos os
formatos que falharam nesse teste — todos passaram a funcionar.

### 🐛 Bug 2 — sabor digitado sem acento não era reconhecido
Digitando `Nutella e Torta de Limao` (sem o til em "Limão"), o bot não
reconheceu **nenhum** dos dois sabores e mostrou "Não encontrei esse
sabor" — mesmo o Nutella, que estava certo.

**Causa:** a comparação de texto era sensível a acento. "limao" (sem
acento) não batia com "Limão" (com acento), e como a função de múltiplos
sabores exige que *todos* os itens do texto sejam reconhecidos, um
sabor com problema de acento invalidava a mensagem inteira.

**Correção:** a comparação agora ignora acentos dos dois lados (usando
normalização Unicode). "limao", "Limão", "LIMAO" etc. todos batem com o
mesmo item do cardápio.

### ✏️ Melhoria — pergunta de entrega/retirada confusa
A pergunta "Você quer entrega ou retirada na loja?" era só texto livre,
sem deixar claro que **as duas opções existem** (a loja achou que só
tinha entrega). Agora aparece como lista numerada, igual ao resto do
fluxo:
```
1. Entrega
2. Retirada na loja
```

### ✨ Funcionalidade nova — múltiplos sabores em uma mensagem só
A loja pediu para poder digitar `Nutella e Torta de Limão` numa mensagem
só, em vez de escolher um sabor, terminar ele, e só depois poder
escolher o próximo. Implementado: o bot reconhece 2+ sabores separados
por vírgula, "e", "+" ou "/", e vai perguntando tamanho e quantidade de
cada um em sequência, sem precisar confirmar "sim" entre eles.

### ✅ Resultado final do teste
Depois das correções, o fluxo completo (2 sabores numa mensagem, tamanho
e quantidade de cada, entrega, data/horário no formato que tinha
falhado, confirmação) rodou do início ao fim sem erro, com o pedido
salvo corretamente no banco (2 itens, total calculado certo, data/hora
prevista salva).

---

## Teste 2 — 2026-08-18: pedido completo até o fim + mensagem depois de confirmado

**Quem testou:** a loja, pelo `chat_local.py`, logo depois das correções do Teste 1.

**O que foi testado:** pedido com Doritos, retirada, confirmação — e o
que acontece se o cliente mandar mais uma mensagem depois.

### 🐛 Bug 3 — "ok" depois do pedido reabria o cardápio inteiro
Depois do bot confirmar o pedido (`Pedido #1 confirmado!...`), a loja
digitou `ok` só pra encerrar a conversa educadamente — e o bot respondeu
com a saudação completa de novo, mostrando todo o cardápio, como se
fosse um cliente novo começando um pedido.

**Causa:** qualquer mensagem recebida com a conversa no estado inicial
(`inicio`) disparava o início de um novo pedido, sem distinguir "quero
pedir algo" de uma resposta de encerramento tipo "ok"/"obrigada"/"blz".

**Correção:** mensagens curtas de agradecimento/encerramento (`ok`,
`blz`, `beleza`, `obrigado(a)`, `valeu`, `vlw`, `de nada`, 👍, 🙏)
recebidas logo após o fim de uma conversa agora recebem só um "por nada"
educado, sem reabrir o cardápio. Uma mensagem de verdade (`oi`, nome de
sabor, etc.) continua abrindo um pedido novo normalmente.

### ✅ Resultado final do teste
Fluxo completo (1 sabor, retirada, data no formato sem "h", confirmação)
rodou sem erro. Depois de confirmado, `ok` respondeu com agradecimento;
`oi` logo em seguida abriu um pedido novo corretamente.

---

## Como ler este registro no futuro
Cada teste novo que encontrar um problema real deve virar uma entrada
aqui: o que foi testado, o que quebrou, por que quebrou, e o que foi
mudado. Não precisa registrar testes que passaram sem problema — só o
que ensinou alguma coisa.

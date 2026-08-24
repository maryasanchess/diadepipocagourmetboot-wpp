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

## Teste 3 — 2026-08-19: primeira mensagem real via WhatsApp Cloud API

**Quem testou:** a loja, configurando o app de desenvolvedor na Meta pela primeira vez.

**O que foi testado:** mandar uma mensagem de teste de verdade pelo número
de teste do WhatsApp, e configurar o webhook pra receber mensagens.

### 🐛 Achado 1 — mensagem de texto livre não chega na primeira tentativa
A primeira mensagem enviada pela API (texto livre, sem template) não
chegou no WhatsApp da loja, mesmo a API retornando sucesso (200 OK com
`wamid` válido).

**Causa:** regra do WhatsApp Business Platform — uma empresa não pode
mandar mensagem de texto livre pra alguém que nunca iniciou conversa com
ela. É preciso que o cliente mande a primeira mensagem (abre a "janela de
24h") ou a empresa usa um modelo de mensagem pré-aprovado.

**Correção:** não é bug do código — é assim que a plataforma funciona.
Documentado aqui pra não gerar confusão de novo: **sempre que testar com
um número novo, mande uma mensagem desse número pro número de teste
primeiro.**

### 🐛 Achado 2 — webhook.site não serve pra validar o webhook da Meta
Tentamos usar [webhook.site](https://webhook.site) como um "espião"
temporário pra ver o que a Meta estava enviando. A verificação do webhook
falhou ("Não foi possível validar a URL de callback ou o token de
verificação").

**Causa:** a Meta exige que a URL do webhook responda ao desafio de
verificação (`GET` com `hub.challenge`) ecoando esse valor de volta como
corpo da resposta. O webhook.site é uma ferramenta de captura passiva —
ele não faz esse eco automaticamente, então a validação sempre falha
nele.

**Correção:** usamos o próprio backend do projeto (que já implementa a
verificação corretamente em `app/webhook.py`) exposto temporariamente via
**ngrok**, em vez de uma ferramenta de terceiros. Funcionou de primeira —
a Meta conseguiu validar e a requisição de verificação apareceu no log do
backend.

### 🐛 Achado 3 — app errado estava inscrito na conta do WhatsApp Business
Mesmo com o webhook verificado e o campo `messages` assinado, nenhuma
notificação chegava no backend.

**Causa:** a URL do webhook fica configurada no nível do **app**, mas cada
conta do WhatsApp Business (WABA) precisa estar "inscrita"
(`subscribed_apps`) nesse app especificamente. Consultamos
`GET /{WABA-ID}/subscribed_apps` e descobrimos que o app inscrito era o
**"WA DevX Webhook Events 1P App"** — um app de demonstração interno da
própria Meta, não o nosso "Diadê Pipocas Gourmet Bot".

**Correção:** `POST /{WABA-ID}/subscribed_apps` (autenticado com o token
do nosso app) inscreveu o app certo. Confirmado por nova consulta GET —
os dois apps (o nosso e o de demonstração) ficaram listados.

### 🐛 Achado 4 — causa real de nenhuma mensagem chegar: restrição de país
Depois de corrigir a inscrição do app, o primeiro POST de status chegou
no webhook — e revelou o motivo real de nenhuma mensagem ter sido
entregue nas últimas horas:

```
"code": 130497,
"title": "Business account is restricted from messaging users in this country."
```

**Causa provável:** a conta ainda não passou pela **Etapa 3. Verificação
da empresa** (Business Verification) da Meta. Contas não verificadas
costumam ficar bloqueadas de mandar mensagem pra alguns países,
especialmente usando o número de teste americano (+1) pra alcançar
números brasileiros.

**Status:** em investigação — próximo passo é avaliar a verificação da
empresa (pode exigir CNPJ).

### ✅ Resultado do teste até aqui
Webhook configurado, verificado e recebendo eventos reais (inclusive
status de falha, o que finalmente revelou a causa raiz da não-entrega).
Fluxo de diagnóstico ficou registrado aqui pra não repetir os mesmos
passos às cegas numa próxima vez.

---

## Teste 4 — 2026-08-24: Verificação da Empresa (Meta) — 1ª tentativa

Enviado um documento pra comprovar que o telefone da empresa pertence ao
CNPJ, como parte da Etapa 3 (Verificação da Empresa), que é o que
desbloqueia o erro 130497 do Teste 3.

### 🐛 Achado 5 — documento rejeitado: tipo não aceito
A Meta recusou o documento com a mensagem "não foi possível verificar...
usando as informações fornecidas" e apontou que o tipo de documento
enviado pra comprovar o telefone não está na lista aceita.

**Causa:** o documento enviado não é um dos tipos que a Meta aceita pra
essa comprovação específica.

**Tipos aceitos** (segundo a própria mensagem de erro), desde que
mostrem a razão social **e** o telefone juntos no mesmo documento:
- Contrato social / estatuto
- Licença ou alvará de funcionamento
- Extrato bancário ou resumo de transações
- Carta do banco
- Conta de serviço público (água, gás, luz ou telefone)

**Status:** pendente — próximo passo é reenviar com um documento de tipo
aceito (ex: conta de telefone ou extrato bancário da conta PJ) que
mostre o número exatamente como cadastrado na Meta.

---

## Como ler este registro no futuro
Cada teste novo que encontrar um problema real deve virar uma entrada
aqui: o que foi testado, o que quebrou, por que quebrou, e o que foi
mudado. Não precisa registrar testes que passaram sem problema — só o
que ensinou alguma coisa.

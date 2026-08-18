# Como consultar e testar o projeto no dia a dia

Guia rápido pra quando você quiser ver o código, ler a documentação ou
testar o bot sem precisar me perguntar toda vez.

## 1. Ver os arquivos do projeto (código e documentação)

**Sem instalar nada:** abra
[github.com/maryasanchess/diadepipocagourmetboot-wpp](https://github.com/maryasanchess/diadepipocagourmetboot-wpp)
no navegador. O GitHub renderiza os arquivos `.md` da pasta `docs/`
formatados (títulos, tabelas, listas), então dá pra ler direto de lá.

**Pra editar ou navegar mais confortável:** instale o
[VS Code](https://code.visualstudio.com/) (gratuito):
1. Instala normal (próximo, próximo, concluir)
2. Abre o VS Code → **File → Open Folder** → escolhe `C:\Users\marya.souza\Downloads\PipocaBot_WhatsApp`
3. Os arquivos `.md` podem ser vistos formatados com `Ctrl+Shift+V`

## 2. Testar o bot conversando com ele (sem WhatsApp configurado)

Ainda não existe conta Meta/WhatsApp configurada, mas dá pra testar o fluxo
de pedido completo direto no terminal:

```powershell
cd C:\Users\marya.souza\Downloads\PipocaBot_WhatsApp\backend
.venv\Scripts\Activate.ps1
python chat_local.py
```

Digite as mensagens como se você fosse o cliente (ex: `oi`, depois o nome
de um sabor, depois o tamanho, etc.) e veja a resposta do bot aparecer na
hora. Comandos especiais dentro do chat:
- `/novo` — simula um cliente diferente, do zero (novo número de telefone fictício)
- `/sair` — encerra o chat
- `cancelar` — testa o cancelamento de pedido (funciona igual vai funcionar no WhatsApp de verdade)

Isso usa os **preços fictícios** do cardápio (`backend/app/cardapio.py`) até
a loja definir os valores reais.

### Se quiser começar do zero de novo
Cada teste fica salvo no banco local (`backend/data/pipoca.db`), então se
você conversar de novo com o mesmo número, o bot lembra do que já
aconteceu antes (é assim que vai funcionar de verdade também). Se quiser
apagar tudo e testar do zero:

```powershell
del C:\Users\marya.souza\Downloads\PipocaBot_WhatsApp\backend\data\pipoca.db
```

(Esse arquivo nunca vai pro Git, então apagar ele não afeta nada do projeto salvo.)

## 3. Ver a lista do que já foi feito e o que falta

O checklist de status fica sempre atualizado no topo do
[README.md](../README.md) principal do projeto.

## 4. Onde perguntar/pedir mudança

Só voltar nessa conversa (ou abrir uma nova comigo) e pedir — eu leio os
arquivos atuais do projeto antes de mexer, então não preciso que você me
lembre o que já foi decidido.

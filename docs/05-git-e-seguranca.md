# Git e segurança — o que pode e o que não pode vazar

## Regra de ouro
O repositório Git deve conter **código e documentação**. Nunca deve conter
**segredos** (senhas, tokens, chaves) nem **dados reais de clientes/pedidos**
da loja.

## Pode ir para o Git ✅
- Código-fonte (`backend/`)
- Documentação (`docs/`, `README.md`)
- `.env.example` (modelo **sem** valores reais, só os nomes das variáveis)
- `requirements.txt` (lista de dependências)
- Scripts de configuração/deploy que não contenham senha
- Estrutura de banco de dados (schema/migrations) — sem dados

## NUNCA pode ir para o Git ❌
| O que | Por quê |
|---|---|
| `.env` (valores reais) | Contém token da Meta, credenciais do Google, chave secreta do app |
| `credentials.json` / `google_credentials.json` | Dá acesso à conta de serviço do Google Calendar |
| Arquivos `.db` / `.sqlite` | Contêm nome, telefone e pedidos reais de clientes — dado pessoal |
| Planilhas `.xlsx` geradas | Mesmo motivo — dado real de vendas e clientes |
| Logs (`*.log`, pasta `logs/`) | Podem registrar números de telefone e mensagens trocadas |
| Qualquer print/export com nome, telefone ou endereço de cliente real | Dado pessoal — vazamento pode ter implicação de LGPD |

O `.gitignore` que já criei na raiz do projeto bloqueia automaticamente todos
esses itens. Mesmo assim, **sempre rode `git status` antes de commitar** e
confira se não aparece nada da lista acima antes de dar `git add`.

## Repositório privado ou público?
**Os dois, cada um com um papel diferente:**

| Repositório | Visibilidade | O que tem |
|---|---|---|
| [`diadepipocagourmetboot-wpp`](https://github.com/maryasanchess/diadepipocagourmetboot-wpp) | 🌐 Público | Código e documentação — serve de portfólio, sem nenhum dado sensível |
| [`diadepipocagourmetboot-wpp---secrets`](https://github.com/maryasanchess/diadepipocagourmetboot-wpp---secrets) | 🔒 Privado, sempre | `.env` e credenciais reais — token, chave Pix, IDs do Google |

O código foi tornado público de propósito, depois de uma revisão
cuidadosa (histórico limpo de qualquer dado real — ver
`08-registro-de-testes.md`) — não revela preços nem lógica de negócio
sensível, só a implementação técnica. Se algum dia isso mudar (ex: lógica
de desconto proprietária for adicionada), reavalie manter público.

O repositório de segredos **nunca** pode virar público — ver
`06-sincronizar-dois-computadores.md` pra como usar ele no dia a dia.

## Se algum segredo for commitado por engano
Trocar a chave/token imediatamente (revogar o antigo na Meta/Google) — não
basta apagar do histórico do Git, porque o valor já pode ter sido exposto.
Depois, sim, limpar o histórico se o repositório for compartilhado com
alguém.

## Checklist antes de cada `git push`
- [ ] `git status` não mostra `.env`, `*.db`, `*.xlsx` reais nem `logs/`
- [ ] Nenhum token/senha aparece em texto dentro de arquivos `.py`
- [ ] Nenhum nome/telefone real de cliente aparece em arquivos de exemplo ou teste (use dados fictícios tipo "Cliente Teste", "11999999999")

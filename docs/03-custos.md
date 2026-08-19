# Custos do projeto

> Valores de mercado mudam com frequência (câmbio, promoções, mudanças de
> política da Meta). Os números abaixo são faixas aproximadas para
> planejamento — **sempre confirme o valor atual na fonte oficial antes de
> se comprometer**, especialmente a tabela de preços da Meta, que já mudou de
> modelo de cobrança mais de uma vez nos últimos anos.

## Custos únicos (configuração inicial)

| Item | Custo aproximado | Observação |
|---|---|---|
| Verificação de empresa no Meta Business | Gratuita | Pode exigir CNPJ e documentos da empresa |
| Número de telefone dedicado ao bot | R$0 (chip pré-pago) a ~R$50 | Precisa ser um número que **não** esteja em uso no WhatsApp normal/Business App |
| Domínio (ex: `.com.br`) | ~R$40/ano | Necessário para o HTTPS do webhook |

## Custos recorrentes (mensais)

| Item | Custo aproximado | Observação |
|---|---|---|
| VPS | R$0 (Oracle Cloud free tier) a ~R$30–50/mês (Hostinger, DigitalOcean, Contabo) | Recomendo começar num plano pago barato — o free tier da Oracle é ótimo mas tem processo de criação mais burocrático |
| Certificado HTTPS | Gratuito | Let's Encrypt, renovação automática |
| WhatsApp Cloud API — mensagens | Varia | A Meta cobra por "conversa" iniciada dentro de certas categorias (ex: marketing, utilidade). Conversas de **atendimento/serviço** iniciadas pelo próprio cliente costumam ter uma cota gratuita generosa — mas isso **precisa ser confirmado na Central de Preços da Meta no momento em que você for configurar**, pois já mudou de modelo antes |
| Google Calendar API | Gratuito | Dentro dos limites de uso de uma loja pequena, não tem custo |
| Backup / armazenamento extra | R$0–10/mês | Opcional, ex: backup do banco de dados em nuvem |

## Estimativa realista para começar

Para uma loja pequena testando o bot: **R$0 a ~R$60/mês**, dependendo do VPS
escolhido, mais o custo pontual do domínio (~R$40/ano). O item mais
imprevisível é a cobrança por mensagem da Cloud API — vamos configurar um
alerta de gasto na conta Meta Business assim que ativarmos, para nunca ter
surpresa na fatura.

## Coisas que NÃO temos custo nenhum
- Python, FastAPI, SQLite, openpyxl/pandas — tudo open source, gratuito.
- Git e GitHub (repositório privado é gratuito em conta pessoal/pequena equipe).
- Google Calendar API (uso dentro da cota gratuita).

## Escolha do provedor de VPS (decidido)

O VPS é onde o backend vai rodar 24 horas por dia, com um endereço fixo na
internet — sem ele, o bot só funciona enquanto o computador de alguém
estiver ligado com o script rodando, o que não serve pra atender clientes
de verdade a qualquer hora.

Comparamos:

| Provedor | Preço aproximado | Pontos fortes | Pontos fracos |
|---|---|---|---|
| **Hostinger VPS** | ~R$20–35/mês | Cobra em real, aceita Pix/boleto, suporte em português, painel simples | Menos "padrão de mercado" pra tutoriais técnicos em inglês |
| DigitalOcean | ~R$25–35/mês (cobrado em dólar) | Muito usado, documentação excelente, confiável | Cobrança em cartão internacional (dólar), sem Pix |
| Contabo | ~R$25–30/mês | Specs generosas pelo preço | Empresa alemã, suporte só em inglês, cobrança internacional |
| Oracle Cloud (Free Tier) | R$0 pra sempre | Plano gratuito real | Cadastro com fama de ser burocrático e travar contas sem motivo claro — evitado depois da restrição que pegamos na conta Meta |

**Escolhido: Hostinger.** Paga em real (Pix), suporte em português, e o bot
é leve o suficiente pra rodar bem no plano mais barato. Evitamos o Oracle
de propósito por já termos enfrentado uma trava de verificação de conta
recente (Meta), e não queremos repetir esse tipo de imprevisto logo na
etapa de hospedagem.

## Próximo passo sobre custos
Quando formos configurar a conta Meta Business (em `04-guia-de-inicio.md`),
paramos juntos na página de preços oficial da Meta para conferir os valores
atuais antes de você inserir qualquer dado de cobrança.

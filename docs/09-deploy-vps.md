# Deploy no VPS

> Este guia é o passo a passo da **Etapa 8** de `04-guia-de-inicio.md`. Os
> arquivos prontos (unidade systemd e config do nginx) estão em
> [`deploy/`](../deploy/) — foram preparados com antecedência, sem depender
> da conta do VPS existir, pra ficar só copiar e ajustar quando a hora
> chegar.

## O que já está pronto
- [`deploy/pipocabot.service`](../deploy/pipocabot.service) — unidade
  systemd que sobe o backend com `uvicorn` e reinicia sozinho se cair.
- [`deploy/nginx-pipocabot.conf`](../deploy/nginx-pipocabot.conf) — config
  do nginx que termina HTTPS e repassa pro backend, que fica ouvindo só em
  `127.0.0.1:8000` (nunca exposto direto na internet).

## O que falta (depende da conta do VPS existir)
1. ⬜ Criar a conta Hostinger e contratar o plano de VPS (ver `03-custos.md`).
2. ⬜ Apontar o domínio/subdomínio pro IP do VPS (registro DNS tipo `A`).
3. ⬜ Seguir os passos abaixo, na ordem.

## Passo a passo (a rodar no VPS, via SSH)

### 1. Criar um usuário sem privilégio de root pro bot
Rodar o backend como root é desnecessário e arriscado — se algo no código
falhar de um jeito inesperado, o processo não deveria ter poder sobre o
resto do servidor.

```bash
adduser --disabled-password --gecos "" pipocabot
```

### 2. Instalar dependências do sistema
```bash
apt update
apt install -y python3-venv python3-pip nginx certbot python3-certbot-nginx git
```

### 3. Trazer o código pro servidor
O repositório é **público** — não precisa de autenticação pra clonar.

```bash
mkdir -p /opt/pipocabot
chown pipocabot:pipocabot /opt/pipocabot
su - pipocabot
git clone https://github.com/maryasanchess/diadepipocagourmetboot-wpp.git /opt/pipocabot
```

### 4. Criar o `.env` de produção
O `.env` **nunca** vai pro repositório (ver `05-git-e-seguranca.md`) —
precisa ser criado direto no servidor, com os valores reais.

```bash
cp /opt/pipocabot/.env.example /opt/pipocabot/.env
nano /opt/pipocabot/.env
```

Coloque também o arquivo `google_credentials.json` (credencial da conta
de serviço do Google) em `/opt/pipocabot/backend/credentials/` — ele
também nunca vai pelo Git.

### 5. Criar o ambiente virtual e instalar as dependências
```bash
cd /opt/pipocabot/backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 6. Instalar e subir o serviço (como root)
```bash
exit  # sai do usuário pipocabot, volta pra root
cp /opt/pipocabot/deploy/pipocabot.service /etc/systemd/system/pipocabot.service
systemctl daemon-reload
systemctl enable --now pipocabot
systemctl status pipocabot   # confirma que está "active (running)"
```

Se algo der errado, `journalctl -u pipocabot -f` mostra os logs em tempo
real.

### 7. Configurar o nginx (proxy HTTPS)
```bash
cp /opt/pipocabot/deploy/nginx-pipocabot.conf /etc/nginx/sites-available/pipocabot
# editar e trocar SEU_DOMINIO_AQUI pelo domínio real:
nano /etc/nginx/sites-available/pipocabot
ln -s /etc/nginx/sites-available/pipocabot /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

### 8. Gerar o certificado HTTPS (gratuito, renova sozinho)
```bash
certbot --nginx -d SEU_DOMINIO_AQUI
```

### 9. Testar de fora
```bash
curl https://SEU_DOMINIO_AQUI/
# esperado: {"status": "PipocaBot rodando"}
```

### 10. Atualizar a URL do webhook na Meta
No painel do app (Meta for Developers), trocar a URL do webhook da URL
temporária do ngrok para `https://SEU_DOMINIO_AQUI/webhook`, com o mesmo
`WHATSAPP_VERIFY_TOKEN` do `.env`.

## Atualizando o código depois do primeiro deploy
```bash
su - pipocabot
cd /opt/pipocabot
git pull
cd backend
.venv/bin/pip install -r requirements.txt   # só se requirements.txt mudou
exit
systemctl restart pipocabot
```

## Firewall
Só as portas 22 (SSH), 80 e 443 precisam ficar abertas pro mundo. A porta
8000 do backend fica só em `127.0.0.1` (loopback), então nem precisa de
regra de firewall pra ela — só o nginx local consegue falar com ela.

```bash
ufw allow 22
ufw allow 80
ufw allow 443
ufw enable
```

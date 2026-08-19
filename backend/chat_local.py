"""
Chat de terminal para testar o bot localmente, sem precisar do WhatsApp.

Simula uma conversa: você digita a mensagem como se fosse o cliente, e vê a
resposta que o bot mandaria de volta. Usa o mesmo motor de conversa
(app/conversation.py) que vai rodar de verdade depois.

Uso:
    cd backend
    .venv\\Scripts\\python.exe chat_local.py

Comandos especiais durante o chat:
    /novo    -> simula um novo cliente (novo número de telefone)
    /admin   -> simula o número admin configurado no .env (pra testar 'relatorio')
    /sair    -> encerra o chat
"""

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stdin.reconfigure(encoding="utf-8", errors="replace")

from app.database import Base, SessionLocal, engine
from app import models  # noqa: F401 garante que os modelos existam
from app.admin import _numeros_admin
from app.dispatcher import processar_mensagem_recebida

Base.metadata.create_all(bind=engine)

TELEFONE_PADRAO = "5511999999999"


def main() -> None:
    telefone = TELEFONE_PADRAO
    db = SessionLocal()

    print("=" * 60)
    print("Chat local do PipocaBot (Ctrl+C ou /sair para encerrar)")
    print(f"Simulando o cliente: {telefone}")
    print("Digite /novo para simular um cliente diferente do zero.")
    print("=" * 60)

    while True:
        try:
            texto = input("\nVocê (cliente): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando.")
            break

        if not texto:
            continue
        if texto == "/sair":
            print("Encerrando.")
            break
        if texto == "/novo":
            import random

            telefone = f"55119{random.randint(10000000, 99999999)}"
            print(f"\n[Simulando novo cliente: {telefone}]")
            continue
        if texto == "/admin":
            numeros = _numeros_admin()
            if not numeros:
                print("\n[Nenhum ADMIN_PHONE_NUMBER configurado no .env]")
                continue
            telefone = next(iter(numeros))
            print(f"\n[Simulando o número admin: {telefone}]")
            continue

        resposta = processar_mensagem_recebida(db, telefone, texto)
        print(f"\nBot: {resposta}")

    db.close()


if __name__ == "__main__":
    sys.exit(main())

import json
import re
import unicodedata
from datetime import datetime

from sqlalchemy.orm import Session

from . import models
from .agendamento import antecedencia_suficiente, interpretar_data_hora
from .cardapio import sabores_disponiveis, tamanhos_disponiveis
from .config import settings
from .horario import dentro_do_horario_de_atendimento

MENSAGEM_FORA_DO_HORARIO = (
    "No momento estamos fora do horário de atendimento "
    f"({settings.horario_abertura} às {settings.horario_fechamento}). "
    "Você pode montar o pedido, mas ele só é processado dentro desse horário."
)

PEDIDO_DATA_HORA = (
    "Pode ser 'hoje', 'amanhã' ou uma data (ex: 25/12), sempre junto com o "
    "horário (ex: 'amanhã às 15h')."
)

PALAVRAS_CANCELAR = {"cancelar", "cancela", "cancelar pedido"}
PALAVRAS_SIM = {"sim", "s", "quero", "confirmar", "confirmo"}
PALAVRAS_NAO = {"não", "nao", "n"}

_SEPARADOR_MULTIPLOS_SABORES = re.compile(r"\s*(?:,| e |\+|/)\s*", re.IGNORECASE)


# ---- estado / persistência auxiliares -------------------------------------

def _carregar_dados(estado: models.EstadoConversa) -> dict:
    if not estado.dados_temporarios:
        return {}
    return json.loads(estado.dados_temporarios)


def _salvar_dados(estado: models.EstadoConversa, dados: dict) -> None:
    estado.dados_temporarios = json.dumps(dados, ensure_ascii=False)


def _ir_para(estado: models.EstadoConversa, etapa: str) -> None:
    estado.etapa_atual = etapa


def _resetar(estado: models.EstadoConversa) -> None:
    estado.etapa_atual = "inicio"
    estado.dados_temporarios = None


def _obter_ou_criar_cliente(db: Session, telefone: str) -> models.Cliente:
    cliente = db.query(models.Cliente).filter_by(telefone=telefone).first()
    if cliente is None:
        cliente = models.Cliente(telefone=telefone)
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
    return cliente


def _obter_ou_criar_estado(db: Session, telefone: str) -> models.EstadoConversa:
    estado = db.get(models.EstadoConversa, telefone)
    if estado is None:
        estado = models.EstadoConversa(telefone=telefone, etapa_atual="inicio")
        db.add(estado)
        db.commit()
        db.refresh(estado)
    return estado


# ---- formatação -------------------------------------------------------------

def _formatar_cardapio() -> str:
    return "\n".join(f"{i + 1}. {sabor}" for i, sabor in enumerate(sabores_disponiveis()))


def _formatar_tamanhos(sabor: str) -> str:
    itens = tamanhos_disponiveis(sabor)
    return "\n".join(f"{i + 1}. {item['tamanho_g']}g - R$ {item['preco']:.2f}" for i, item in enumerate(itens))


def _resumo_pedido(dados: dict) -> str:
    linhas = ["Resumo do seu pedido:"]
    total = 0.0
    for item in dados.get("itens", []):
        subtotal = item["preco"] * item["quantidade"]
        total += subtotal
        linhas.append(f"- {item['quantidade']}x {item['sabor']} {item['tamanho_g']}g - R$ {subtotal:.2f}")

    if dados.get("tipo_entrega") == "entrega":
        linhas.append(f"Entrega em: {dados.get('endereco', '(endereço não informado)')}")
        linhas.append("Taxa de entrega: a confirmar com a loja")
    else:
        linhas.append("Retirada na loja")

    if dados.get("data_hora_texto"):
        linhas.append(f"Data/horário desejado: {dados['data_hora_texto']}")

    linhas.append(f"Total dos itens: R$ {total:.2f} (+ taxa de entrega, se houver)")
    linhas.append("Pagamento: Pix")
    return "\n".join(linhas)


# ---- interpretação de respostas do cliente ----------------------------------

def _normalizar(texto: str) -> str:
    """minúsculas e sem acento, pra aceitar 'limao' como 'Limão' etc."""
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return sem_acento.strip().lower()


def _resolver_sabor(texto: str, opcoes: list[str]) -> str | None:
    texto = texto.strip()
    if texto.isdigit():
        indice = int(texto) - 1
        return opcoes[indice] if 0 <= indice < len(opcoes) else None
    texto_norm = _normalizar(texto)
    for opcao in opcoes:
        opcao_norm = _normalizar(opcao)
        if opcao_norm == texto_norm or texto_norm in opcao_norm:
            return opcao
    return None


def _resolver_multiplos_sabores(texto: str, opcoes: list[str]) -> list[str] | None:
    """Se o texto tiver 2+ sabores válidos separados por vírgula/'e'/'+'/'/',
    retorna a lista resolvida. Caso contrário (inclusive um único sabor),
    retorna None e quem chamou trata como escolha simples."""
    partes = [p for p in _SEPARADOR_MULTIPLOS_SABORES.split(texto) if p.strip()]
    if len(partes) < 2:
        return None

    resolvidos = []
    for parte in partes:
        sabor = _resolver_sabor(parte, opcoes)
        if sabor is None:
            return None
        resolvidos.append(sabor)
    return resolvidos


def _resolver_tamanho(texto: str, itens: list[dict]) -> dict | None:
    texto = texto.strip().lower().replace("g", "")
    if not texto.isdigit():
        return None
    valor = int(texto)
    if 1 <= valor <= len(itens):
        return itens[valor - 1]
    for item in itens:
        if item["tamanho_g"] == valor:
            return item
    return None


def _extrair_inteiro_positivo(texto: str) -> int | None:
    texto = texto.strip()
    if texto.isdigit() and int(texto) > 0:
        return int(texto)
    return None


# ---- etapas da conversa ------------------------------------------------------

def _iniciar_pedido(estado: models.EstadoConversa) -> str:
    _ir_para(estado, "aguardando_sabor")
    _salvar_dados(estado, {"itens": []})
    return (
        "Oi! Bem-vindo(a) à loja de pipocas gourmet \U0001f37f\n\n"
        "Temos os seguintes sabores:\n"
        f"{_formatar_cardapio()}\n\n"
        "Me diz o número ou o nome do sabor que você quer "
        "(pode escolher mais de um de uma vez, ex: 'Nutella e Torta de Limão')."
    )


def _escolher_sabor(estado: models.EstadoConversa, texto: str) -> str:
    opcoes = sabores_disponiveis()
    dados = _carregar_dados(estado)

    multiplos = _resolver_multiplos_sabores(texto, opcoes)
    if multiplos is not None:
        primeiro, *resto = multiplos
        dados["fila_sabores"] = resto
        dados["sabor_atual"] = primeiro
        _salvar_dados(estado, dados)
        _ir_para(estado, "aguardando_tamanho")
        return (
            f"Beleza, anotei {', '.join(multiplos)}. Vamos por {primeiro} primeiro, "
            f"escolhe o tamanho:\n{_formatar_tamanhos(primeiro)}"
        )

    sabor = _resolver_sabor(texto, opcoes)
    if sabor is None:
        return f"Não encontrei esse sabor. Escolhe um da lista:\n{_formatar_cardapio()}"

    dados["sabor_atual"] = sabor
    _salvar_dados(estado, dados)
    _ir_para(estado, "aguardando_tamanho")
    return f"Show, {sabor}! Agora escolhe o tamanho:\n{_formatar_tamanhos(sabor)}"


def _escolher_tamanho(estado: models.EstadoConversa, texto: str) -> str:
    dados = _carregar_dados(estado)
    sabor = dados.get("sabor_atual", "")
    itens = tamanhos_disponiveis(sabor)
    item = _resolver_tamanho(texto, itens)
    if item is None:
        return f"Não entendi o tamanho. Escolhe um da lista:\n{_formatar_tamanhos(sabor)}"

    dados["tamanho_atual"] = item["tamanho_g"]
    dados["preco_atual"] = item["preco"]
    _salvar_dados(estado, dados)
    _ir_para(estado, "aguardando_quantidade")
    return f"Quantas unidades de {sabor} {item['tamanho_g']}g você quer?"


def _escolher_quantidade(estado: models.EstadoConversa, texto: str) -> str:
    quantidade = _extrair_inteiro_positivo(texto)
    if quantidade is None:
        return "Me manda só o número de unidades (ex: 2)."

    dados = _carregar_dados(estado)
    dados.setdefault("itens", []).append(
        {
            "sabor": dados.pop("sabor_atual"),
            "tamanho_g": dados.pop("tamanho_atual"),
            "preco": dados.pop("preco_atual"),
            "quantidade": quantidade,
        }
    )

    fila = dados.get("fila_sabores") or []
    if fila:
        proximo_sabor, *resto = fila
        dados["fila_sabores"] = resto
        dados["sabor_atual"] = proximo_sabor
        _salvar_dados(estado, dados)
        _ir_para(estado, "aguardando_tamanho")
        return f"Adicionado! Agora o {proximo_sabor}, escolhe o tamanho:\n{_formatar_tamanhos(proximo_sabor)}"

    _salvar_dados(estado, dados)
    _ir_para(estado, "aguardando_mais_itens")
    return "Adicionado! Quer pedir mais algum sabor? (sim/não)"


def _perguntar_mais_itens(estado: models.EstadoConversa, texto: str) -> str:
    resposta = texto.strip().lower()
    if resposta in PALAVRAS_SIM:
        _ir_para(estado, "aguardando_sabor")
        return f"Beleza! Escolhe o próximo sabor (ou mais de um, ex: 'Nutella e Ninho'):\n{_formatar_cardapio()}"
    if resposta in PALAVRAS_NAO:
        _ir_para(estado, "aguardando_tipo_entrega")
        return "Fechado esses itens. Como você quer receber?\n1. Entrega\n2. Retirada na loja"
    return "Não entendi. Responde 'sim' ou 'não': quer pedir mais algum sabor?"


def _escolher_tipo_entrega(estado: models.EstadoConversa, texto: str) -> str:
    resposta = texto.strip().lower()
    dados = _carregar_dados(estado)
    if resposta in ("1",) or "entreg" in resposta:
        dados["tipo_entrega"] = "entrega"
        _salvar_dados(estado, dados)
        _ir_para(estado, "aguardando_endereco")
        return "Show! Me manda o endereço completo para entrega."
    if resposta in ("2",) or "retir" in resposta:
        dados["tipo_entrega"] = "retirada"
        _salvar_dados(estado, dados)
        _ir_para(estado, "aguardando_data_hora")
        return f"Combinado, retirada na loja. Pra quando você gostaria de retirar? {PEDIDO_DATA_HORA}"
    return "Não entendi. Responde com o número ou a palavra:\n1. Entrega\n2. Retirada na loja"


def _informar_endereco(estado: models.EstadoConversa, texto: str) -> str:
    dados = _carregar_dados(estado)
    dados["endereco"] = texto.strip()
    _salvar_dados(estado, dados)
    _ir_para(estado, "aguardando_data_hora")
    return f"Anotado! Pra quando você gostaria da entrega? {PEDIDO_DATA_HORA}"


def _informar_data_hora(estado: models.EstadoConversa, texto: str) -> str:
    data_hora = interpretar_data_hora(texto)
    if data_hora is None:
        return f"Não entendi essa data/horário. {PEDIDO_DATA_HORA}"

    if not antecedencia_suficiente(data_hora):
        return (
            f"A loja trabalha por encomenda e precisa de pelo menos "
            f"{settings.antecedencia_minima_horas}h de antecedência. "
            f"Escolhe uma data/horário mais à frente. {PEDIDO_DATA_HORA}"
        )

    dados = _carregar_dados(estado)
    dados["data_hora_texto"] = texto.strip()
    dados["data_hora_iso"] = data_hora.isoformat()
    _salvar_dados(estado, dados)
    _ir_para(estado, "aguardando_confirmacao_final")
    return (
        f"{_resumo_pedido(dados)}\n\n"
        f"Chave Pix da loja: {settings.pix_chave}\n"
        "Pode confirmar o pedido? (sim/não)"
    )


def _confirmar_pedido(db: Session, cliente: models.Cliente, estado: models.EstadoConversa, texto: str) -> str:
    resposta = texto.strip().lower()
    dados = _carregar_dados(estado)

    if resposta in PALAVRAS_SIM:
        pedido = _criar_pedido(db, cliente, dados)
        _resetar(estado)
        return (
            f"Pedido #{pedido.id} confirmado! Assim que o pagamento via Pix for identificado, "
            "a loja começa a preparar. Qualquer coisa, é só me chamar por aqui. \U0001f37f"
        )
    if resposta in PALAVRAS_NAO:
        _resetar(estado)
        return "Pedido cancelado. Se quiser começar de novo, é só mandar qualquer mensagem."
    return "Não entendi. Responde 'sim' pra confirmar ou 'não' pra cancelar o pedido."


def _criar_pedido(db: Session, cliente: models.Cliente, dados: dict) -> models.Pedido:
    data_hora_prevista = None
    if dados.get("data_hora_iso"):
        data_hora_prevista = datetime.fromisoformat(dados["data_hora_iso"])

    pedido = models.Pedido(
        cliente_id=cliente.id,
        tipo_entrega=dados["tipo_entrega"],
        endereco=dados.get("endereco"),
        taxa_entrega=None,
        data_hora_prevista=data_hora_prevista,
        status=models.StatusPedido.recebido,
    )
    for item in dados.get("itens", []):
        pedido.itens.append(
            models.ItemPedido(
                sabor=item["sabor"],
                tamanho_g=item["tamanho_g"],
                quantidade=item["quantidade"],
                preco_unitario=item["preco"],
            )
        )
    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    return pedido


# ---- cancelamento (fora do fluxo normal) -------------------------------------

def _tratar_cancelamento(db: Session, cliente: models.Cliente, estado: models.EstadoConversa) -> str:
    if estado.etapa_atual != "inicio":
        _resetar(estado)
        db.commit()
        return "Pedido em andamento cancelado. Se quiser começar de novo, é só mandar qualquer mensagem."

    ultimo_pedido = (
        db.query(models.Pedido)
        .filter(models.Pedido.cliente_id == cliente.id)
        .order_by(models.Pedido.id.desc())
        .first()
    )
    if ultimo_pedido is None:
        return "Você ainda não tem nenhum pedido para cancelar."
    if not ultimo_pedido.status.permite_alteracao_pelo_cliente:
        return (
            f"Seu pedido #{ultimo_pedido.id} já está em '{ultimo_pedido.status.value}' "
            "e não pode mais ser cancelado por aqui. Fala direto com a loja."
        )
    ultimo_pedido.status = models.StatusPedido.cancelado
    db.commit()
    return f"Pedido #{ultimo_pedido.id} cancelado."


# ---- ponto de entrada ---------------------------------------------------------

_ETAPAS = {
    "aguardando_sabor": _escolher_sabor,
    "aguardando_tamanho": _escolher_tamanho,
    "aguardando_quantidade": _escolher_quantidade,
    "aguardando_mais_itens": _perguntar_mais_itens,
    "aguardando_tipo_entrega": _escolher_tipo_entrega,
    "aguardando_endereco": _informar_endereco,
    "aguardando_data_hora": _informar_data_hora,
}


def processar_mensagem(db: Session, telefone: str, texto: str) -> str:
    cliente = _obter_ou_criar_cliente(db, telefone)
    estado = _obter_ou_criar_estado(db, telefone)

    if texto.strip().lower() in PALAVRAS_CANCELAR:
        return _tratar_cancelamento(db, cliente, estado)

    etapa = estado.etapa_atual
    avisar_horario = etapa == "inicio"

    if etapa == "inicio":
        resposta = _iniciar_pedido(estado)
    elif etapa == "aguardando_confirmacao_final":
        resposta = _confirmar_pedido(db, cliente, estado, texto)
    elif etapa in _ETAPAS:
        resposta = _ETAPAS[etapa](estado, texto)
    else:
        _resetar(estado)
        resposta = _iniciar_pedido(estado)

    db.commit()

    if avisar_horario and not dentro_do_horario_de_atendimento():
        resposta = f"{resposta}\n\n{MENSAGEM_FORA_DO_HORARIO}"

    return resposta

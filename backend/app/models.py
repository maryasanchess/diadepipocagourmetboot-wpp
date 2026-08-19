import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


def agora() -> datetime:
    return datetime.now(timezone.utc)


class StatusPedido(str, enum.Enum):
    recebido = "recebido"
    confirmado = "confirmado"
    em_preparo = "em_preparo"
    em_entrega = "em_entrega"
    pronto_retirada = "pronto_retirada"
    concluido = "concluido"
    cancelado = "cancelado"

    @property
    def permite_alteracao_pelo_cliente(self) -> bool:
        return self in (StatusPedido.recebido, StatusPedido.confirmado)


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True)
    telefone = Column(String, unique=True, index=True, nullable=False)
    nome = Column(String, nullable=True)
    criado_em = Column(DateTime, default=agora)

    pedidos = relationship("Pedido", back_populates="cliente")


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    tipo_entrega = Column(String, nullable=False)  # "entrega" | "retirada"
    endereco = Column(Text, nullable=True)
    taxa_entrega = Column(Float, nullable=True)  # None = "a confirmar"
    data_hora_prevista = Column(DateTime, nullable=True)
    evento_agenda_id = Column(String, nullable=True)  # ID do evento no Google Agenda, se criado
    status = Column(Enum(StatusPedido), default=StatusPedido.recebido, nullable=False)
    criado_em = Column(DateTime, default=agora)
    atualizado_em = Column(DateTime, default=agora, onupdate=agora)

    cliente = relationship("Cliente", back_populates="pedidos")
    itens = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")


class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    sabor = Column(String, nullable=False)
    tamanho_g = Column(Integer, nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Float, nullable=False)

    pedido = relationship("Pedido", back_populates="itens")


class EstadoConversa(Base):
    __tablename__ = "estado_conversa"

    telefone = Column(String, primary_key=True)
    etapa_atual = Column(String, nullable=False, default="inicio")
    dados_temporarios = Column(Text, nullable=True)  # JSON serializado
    atualizado_em = Column(DateTime, default=agora, onupdate=agora)

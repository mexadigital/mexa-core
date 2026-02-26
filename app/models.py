from enum import Enum

from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# =========================
# ENUMS
# =========================

class ModoSerie(str, Enum):
    NINGUNA = "NINGUNA"
    OPCIONAL = "OPCIONAL"
    OBLIGATORIA = "OBLIGATORIA"


# =========================
# MODELOS
# =========================

class EPP(Base):
    __tablename__ = 'epp'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)

    consumables = relationship('Consumable', back_populates='epp')


class Consumable(Base):
    __tablename__ = 'consumables'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    epp_id = Column(Integer, ForeignKey('epp.id'), nullable=False)

    # 🔥 Nuevo: control de serialización
    modo_serie = Column(SAEnum(ModoSerie), nullable=False, default=ModoSerie.NINGUNA)

    epp = relationship('EPP', back_populates='consumables')


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)

    organizations = relationship('Organization', back_populates='user')


class Organization(Base):
    __tablename__ = 'organizations'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship('User', back_populates='organizations')


class Inventory(Base):
    __tablename__ = 'inventory'

    id = Column(Integer, primary_key=True)
    item_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship('User')


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    inventory_id = Column(Integer, ForeignKey('inventory.id'), nullable=False)

    user = relationship('User')
    inventory = relationship('Inventory')

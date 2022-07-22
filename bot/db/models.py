from sqlalchemy import JSON, Column, BigInteger, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from bot.enums import ActionType, TriggerType

Base = declarative_base()


class Trigger(Base):
    __tablename__ = "triggers"

    id = Column(BigInteger, primary_key=True, auto_increment=True)
    guild_id = Column(BigInteger, nullable=False)
    type = Column(Enum(TriggerType), nullable=False)
    activation_params = Column(JSON, nullable=False)
    actions = relationship("Action", back_populates="trigger")


class Action(Base):
    __tablename__ = "actions"

    id = Column(BigInteger, primary_key=True, auto_increment=True)
    guild_id = Column(BigInteger, nullable=False)
    type = Column(Enum(ActionType), nullable=False)
    action_params = Column(JSON, nullable=False)

    trigger_id = Column(
        ForeignKey("triggers.id", ondelete="CASCADE"), nullable=False
    )
    trigger = relationship("Trigger", back_populates="actions")

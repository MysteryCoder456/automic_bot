from sqlalchemy import Column, BigInteger, Enum
from sqlalchemy.ext.declarative import declarative_base

from bot.enums import TriggerType

Base = declarative_base()


class Trigger(Base):
    __tablename__ = "triggers"

    id = Column(BigInteger, primary_key=True, auto_increment=True)
    guild_id = Column(BigInteger, nullable=False)
    type = Column(Enum(TriggerType), nullable=False)


class BaseAction:
    id = Column(BigInteger, primary_key=True, auto_increment=True)
    guild_id = Column(BigInteger, nullable=False)


class MessageSendAction(Base, BaseAction):
    __tablename__ = "message_send_actions"

    channel_id = Column(BigInteger, nullable=False)


class MessageDeleteAction(Base, BaseAction):
    __tablename__ = "message_delete_actions"

    channel_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)


# TODO: Add more action tables...

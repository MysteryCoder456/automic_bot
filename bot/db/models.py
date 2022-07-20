from sqlalchemy import JSON, Column, BigInteger, Enum, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_mixin, declared_attr, relationship

from bot.enums import TriggerType

Base = declarative_base()


class Trigger(Base):
    __tablename__ = "triggers"

    id = Column(BigInteger, primary_key=True, auto_increment=True)
    guild_id = Column(BigInteger, nullable=False)
    type = Column(Enum(TriggerType), nullable=False)
    activation_params = Column(JSON, nullable=False)


@declarative_mixin
class BaseAction:
    id = Column(BigInteger, primary_key=True, auto_increment=True)
    guild_id = Column(BigInteger, nullable=False)

    @declared_attr
    def trigger_id(self):
        return Column(
            ForeignKey("triggers.id", ondelete="CASCADE"), nullable=False
        )

    @declared_attr
    def trigger(self):
        return relationship("Trigger")


class MessageSendAction(Base, BaseAction):
    __tablename__ = "message_send_actions"

    channel_id = Column(BigInteger, nullable=False)
    message_content = Column(String, nullable=False)


class MessageDeleteAction(Base, BaseAction):
    __tablename__ = "message_delete_actions"

    channel_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)


# TODO: Add more action tables...

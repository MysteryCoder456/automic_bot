from sqlalchemy import Column, BigInteger, Enum
from sqlalchemy.ext.declarative import declarative_base

from bot.enums import TriggerType

Base = declarative_base()


class Trigger(Base):
    __tablename__ = "triggers"

    id = Column(BigInteger, primary_key=True, auto_increment=True)
    guild_id = Column(BigInteger, nullable=False)
    type = Column(Enum(TriggerType), nullable=False)

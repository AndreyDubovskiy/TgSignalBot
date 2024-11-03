from db.models.BaseModel import BaseModel
from db.models.imports import *
from datetime import datetime

class SubscribeModel(BaseModel):
    __tablename__ = 'subscribes'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer())
    symbol: Mapped[str] = mapped_column(String(255))
    timeframe: Mapped[str] = mapped_column(String(255))
    updated_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True))

    def __init__(self, user_id: int, symbol: str, timeframe: str, updated_at: datetime = datetime.now(), created_at: datetime = datetime.now()):
        self.user_id = user_id
        self.symbol = symbol
        self.timeframe = timeframe
        self.updated_at = updated_at
        self.created_at = created_at

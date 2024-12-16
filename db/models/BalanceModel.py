from db.models.BaseModel import BaseModel
from db.models.imports import *
from datetime import datetime

class BalanceModel(BaseModel):
    __tablename__ = 'balances'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    timeframe: Mapped[str] = mapped_column(String(255))
    signal_price: Mapped[float] = mapped_column(Float(), nullable=True)
    signal_type: Mapped[str] = mapped_column(String(255), nullable=True)
    updated_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True))

    def __init__(self, name: str, timeframe: str, signal_price: float = None, signal_type: str = None,  updated_at: datetime = datetime.now(), created_at: datetime = datetime.now()):
        self.name = name
        self.timeframe = timeframe
        self.signal_price = signal_price
        self.signal_type = signal_type
        self.updated_at = updated_at
        self.created_at = created_at

    def __repr__(self) -> str:
        return f'<Balance {self.name} {self.timeframe} {self.signal_price} {self.signal_type}>'

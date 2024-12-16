from db.models.BaseModel import BaseModel
from db.models.imports import *
from datetime import datetime

class UserVModel(BaseModel):
    __tablename__ = 'uservs'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_name: Mapped[str] = mapped_column(String(255))
    updated_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True))

    def __init__(self, tg_name: str, updated_at: datetime = datetime.now(), created_at: datetime = datetime.now()):
        self.tg_name = tg_name
        self.updated_at = updated_at
        self.created_at = created_at

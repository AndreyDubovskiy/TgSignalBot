from sqlalchemy import select
from sqlalchemy import delete
from typing import List, Optional
from db.controllers.TemplateController import Controller
from db.models.BalanceModel import BalanceModel
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

class BalancesController(Controller):
    async def get_all(self) -> List[BalanceModel]:
        async with self.async_session() as session:
            query = select(BalanceModel)
            result = await session.scalars(query)
            res: List[BalanceModel] = result.all()
        return res

    async def get_by(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None,
        timeframe: Optional[str] = None,
        signal_price: Optional[float] = None,
        signal_type: Optional[str] = None,
        updated_at_start = None,
        updated_at_end = None,
        created_at_start = None,
        created_at_end = None
    ) -> List[BalanceModel]:
        async with self.async_session() as session:
            query = select(BalanceModel)
            if id is not None:
                query = query.where(BalanceModel.id == id)
            if name is not None:
                query = query.where(BalanceModel.name == name)
            if timeframe is not None:
                query = query.where(BalanceModel.timeframe == timeframe)
            if signal_price is not None:
                query = query.where(BalanceModel.signal_price == signal_price)
            if signal_type is not None:
                query = query.where(BalanceModel.signal_type == signal_type)
            if updated_at_start is not None:
                query = query.where(BalanceModel.updated_at >= updated_at_start)
            if updated_at_end is not None:
                query = query.where(BalanceModel.updated_at <= updated_at_end)
            if created_at_start is not None:
                query = query.where(BalanceModel.created_at >= created_at_start)
            if created_at_end is not None:
                query = query.where(BalanceModel.created_at <= created_at_end)

            result = await session.scalars(query)
            res: List[BalanceModel] = result.all()
        return res

    async def create(
            self,
            name: str,
            timeframe: str,
            signal_price: float = None,
            signal_type: str = None,
            updated_at: datetime = datetime.now(),
            created_at: datetime = datetime.now()
    ) -> BalanceModel:
        async with self.async_session() as session:
            async with session.begin():
                tmp = BalanceModel(
                    name=name,
                    timeframe=timeframe,
                    signal_price=signal_price,
                    signal_type=signal_type,
                    updated_at=updated_at,
                    created_at=created_at
                )
                session.add(tmp)
                await session.commit()
                #await session.refresh(tmp)
        return tmp

    async def delete(self, id: int) -> Optional[BalanceModel]:
        async with self.async_session() as session:
            async with session.begin():
                query = select(BalanceModel).where(BalanceModel.id == id)
                result = await session.scalars(query)
                tmp: Optional[BalanceModel] = result.first()
                if tmp:
                    await session.delete(tmp)
                    await session.commit()
        return tmp

    async def delete_all(self):
        async with self.async_session() as session:
            async with session.begin():  # Убедитесь, что используется транзакция
                query = delete(BalanceModel)
                await session.execute(query)
            await session.commit()
from sqlalchemy import select
from typing import List, Optional
from db.controllers.TemplateController import Controller  # Используем асинхронный контроллер
from db.models.SubscribeModel import SubscribeModel
from sqlalchemy.ext.asyncio import AsyncSession

class SubscribesController(Controller):
    async def get_all(self) -> List[SubscribeModel]:
        async with self.async_session() as session:
            query = select(SubscribeModel)
            result = await session.scalars(query)
            res: List[SubscribeModel] = result.all()
        return res

    async def get_by(
        self,
        id: Optional[int] = None,
        user_id: Optional[int] = None,
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
        updated_at_start = None,
        updated_at_end = None,
        created_at_start = None,
        created_at_end = None,
        offset = None,
        limit = None
    ) -> List[SubscribeModel]:
        async with self.async_session() as session:
            query = select(SubscribeModel)
            if id is not None:
                query = query.where(SubscribeModel.id == id)
            if user_id is not None:
                query = query.where(SubscribeModel.user_id == user_id)
            if symbol is not None:
                query = query.where(SubscribeModel.symbol == symbol)
            if timeframe is not None:
                query = query.where(SubscribeModel.timeframe == timeframe)
            if updated_at_start is not None:
                query = query.where(SubscribeModel.updated_at >= updated_at_start)
            if updated_at_end is not None:
                query = query.where(SubscribeModel.updated_at <= updated_at_end)
            if created_at_start is not None:
                query = query.where(SubscribeModel.created_at >= created_at_start)
            if created_at_end is not None:
                query = query.where(SubscribeModel.created_at <= created_at_end)

            if offset is not None:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)

            result = await session.scalars(query)
            res: List[SubscribeModel] = result.all()
        return res

    async def create(
        self, user_id: int, symbol: str, timeframe: str
    ) -> SubscribeModel:
        async with self.async_session() as session:
            async with session.begin():
                tmp = SubscribeModel(
                    user_id=user_id,
                    symbol=symbol,
                    timeframe=timeframe
                )
                session.add(tmp)
                await session.commit()
                #await session.refresh(tmp)
        return tmp

    async def delete(self, id: int) -> Optional[SubscribeModel]:
        async with self.async_session() as session:
            async with session.begin():
                query = select(SubscribeModel).where(SubscribeModel.id == id)
                result = await session.scalars(query)
                tmp: Optional[SubscribeModel] = result.first()
                if tmp:
                    await session.delete(tmp)
                    await session.commit()
        return tmp

    async def delete_by_user_id(self, id: int) -> Optional[SubscribeModel]:
        async with self.async_session() as session:
            async with session.begin():
                query = select(SubscribeModel).where(SubscribeModel.user_id == id)
                result = await session.scalars(query)
                tmp: List[SubscribeModel] = result.all()
                if len(tmp) > 0:
                    for i in tmp:
                        await session.delete(i)
                    await session.commit()
        return tmp

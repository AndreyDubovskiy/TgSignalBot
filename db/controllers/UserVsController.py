from sqlalchemy import select
from typing import List, Optional
from db.controllers.TemplateController import Controller  # Используем асинхронный контроллер
from db.models.UserVModel import UserVModel
from sqlalchemy.ext.asyncio import AsyncSession

class UserVsController(Controller):
    async def get_all(self) -> List[UserVModel]:
        async with self.async_session() as session:
            query = select(UserVModel)
            result = await session.scalars(query)
            res: List[UserVModel] = result.all()
        return res

    async def get_by(
        self,
        id: Optional[int] = None,
        tg_name: Optional[str] = None,
        updated_at_start = None,
        updated_at_end = None,
        created_at_start = None,
        created_at_end = None
    ) -> List[UserVModel]:
        async with self.async_session() as session:
            query = select(UserVModel)
            if id is not None:
                query = query.where(UserVModel.id == id)
            if tg_name is not None:
                query = query.where(UserVModel.tg_name == tg_name)
            if updated_at_start is not None:
                query = query.where(UserVModel.updated_at >= updated_at_start)
            if updated_at_end is not None:
                query = query.where(UserVModel.updated_at <= updated_at_end)
            if created_at_start is not None:
                query = query.where(UserVModel.created_at >= created_at_start)
            if created_at_end is not None:
                query = query.where(UserVModel.created_at <= created_at_end)

            result = await session.scalars(query)
            res: List[UserVModel] = result.all()
        return res

    async def create(
        self, tg_name: str
    ) -> UserVModel:
        async with self.async_session() as session:
            async with session.begin():
                tmp = UserVModel(
                    tg_name=tg_name
                )
                session.add(tmp)
                await session.commit()
                #await session.refresh(tmp)
        return tmp

    async def delete(self, id: int) -> Optional[UserVModel]:
        async with self.async_session() as session:
            async with session.begin():
                query = select(UserVModel).where(UserVModel.id == id)
                result = await session.scalars(query)
                tmp: Optional[UserVModel] = result.first()
                if tmp:
                    await session.delete(tmp)
                    await session.commit()
        return tmp

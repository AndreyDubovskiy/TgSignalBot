from sqlalchemy import select
from typing import List, Optional
from db.controllers.TemplateController import Controller  # Используем асинхронный контроллер
from db.models.UserModel import UserModel
from sqlalchemy.ext.asyncio import AsyncSession

class UsersController(Controller):
    async def get_all(self) -> List[UserModel]:
        async with self.async_session() as session:
            query = select(UserModel)
            result = await session.scalars(query)
            res: List[UserModel] = result.all()
        return res

    async def get_by(
        self,
        id: Optional[int] = None,
        tg_id: Optional[str] = None,
        updated_at_start = None,
        updated_at_end = None,
        created_at_start = None,
        created_at_end = None
    ) -> List[UserModel]:
        print("Get by")
        async with self.async_session() as session:
            query = select(UserModel)
            if id is not None:
                query = query.where(UserModel.id == id)
            if tg_id is not None:
                query = query.where(UserModel.tg_id == tg_id)
            if updated_at_start is not None:
                query = query.where(UserModel.updated_at >= updated_at_start)
            if updated_at_end is not None:
                query = query.where(UserModel.updated_at <= updated_at_end)
            if created_at_start is not None:
                query = query.where(UserModel.created_at >= created_at_start)
            if created_at_end is not None:
                query = query.where(UserModel.created_at <= created_at_end)

            result = await session.scalars(query)
            res: List[UserModel] = result.all()
        return res

    async def create(
        self, tg_id: str
    ) -> UserModel:
        print("TRY create")
        async with self.async_session() as session:
            async with session.begin():
                tmp = UserModel(
                    tg_id=tg_id
                )
                session.add(tmp)
                print("good add db")
                await session.commit()
                print("commit")
                #await session.refresh(tmp)
        return tmp

    async def delete(self, id: int) -> Optional[UserModel]:
        async with self.async_session() as session:
            async with session.begin():
                query = select(UserModel).where(UserModel.id == id)
                result = await session.scalars(query)
                tmp: Optional[UserModel] = result.first()
                if tmp:
                    await session.delete(tmp)
                    await session.commit()
        return tmp

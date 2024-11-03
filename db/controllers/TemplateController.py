from sqlalchemy import select
from typing import List
import db.database as db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

class Controller:
    def __init__(self, engine=None):
        self.engine = engine or db.engine
        self.async_session = db.get_async_session()

    async def get_all(self, class_model):
        async with self.async_session() as session:
            query = select(class_model)
            result = await session.scalars(query)
            res: List[class_model] = result.all()
        return res

    async def get_by(self, class_model, id):
        async with self.async_session() as session:
            query = select(class_model).where(class_model.id == id)
            result = await session.scalars(query)
            res: List[class_model] = result.all()
        return res

    async def create(self, class_model):
        async with self.async_session() as session:
            async with session.begin():  # Транзакция
                tmp = class_model()
                session.add(tmp)
                await session.commit()  # Сохраняем изменения
                #await session.refresh(tmp)  # Обновляем объект
        return tmp

    async def delete(self, class_model, id):
        async with self.async_session() as session:
            async with session.begin():
                query = select(class_model).where(class_model.id == id)
                result = await session.scalars(query)
                tmp: class_model = result.first()
                if tmp:
                    await session.delete(tmp)
                    await session.commit()
        return tmp

    async def save(self, obj_model):
        async with self.async_session() as session:
            async with session.begin():
                session.add(obj_model)
                await session.commit()
                #await session.refresh(obj_model)
        return obj_model

    async def save_all(self, obj_models):
        async with self.async_session() as session:
            async with session.begin():
                session.add_all(obj_models)
                await session.commit()
        return obj_models

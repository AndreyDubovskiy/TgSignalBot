from sqlalchemy import select
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from db.controllers.TemplateController import Controller
from db.models.ConfigModel import ConfigModel

class ConfigsController(Controller):
    async def get_all(self) -> List[ConfigModel]:
        async with self.async_session() as session:
            query = select(ConfigModel)
            result = await session.scalars(query)
            res: List[ConfigModel] = result.all()
        return res

    async def get_by(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None,
        group: Optional[str] = None,
        value: Optional[str] = None
    ) -> List[ConfigModel]:
        async with self.async_session() as session:
            query = select(ConfigModel)
            if id is not None:
                query = query.where(ConfigModel.id == id)
            if name is not None:
                query = query.where(ConfigModel.name == name)
            if group is not None:
                query = query.where(ConfigModel.group == group)
            if value is not None:
                query = query.where(ConfigModel.value == value)
            result = await session.scalars(query)
            res: List[ConfigModel] = result.all()
        return res

    async def create(
        self,
        name: str,
        value: Optional[str] = None,
        group: Optional[str] = None,
        binary_data: Optional[bytes] = None
    ) -> ConfigModel:
        async with self.async_session() as session:
            async with session.begin():
                tmp = ConfigModel(name=name, value=value, group=group, binary_data=binary_data)
                session.add(tmp)
                await session.commit()
                #await session.refresh(tmp)
        return tmp

    async def delete(self, id: int) -> Optional[ConfigModel]:
        async with self.async_session() as session:
            async with session.begin():
                query = select(ConfigModel).where(ConfigModel.id == id)
                result = await session.scalars(query)
                tmp: Optional[ConfigModel] = result.first()
                if tmp:
                    await session.delete(tmp)
                    await session.commit()
        return tmp

    async def set_config(
        self,
        name: str,
        value: Optional[str] = None,
        group: Optional[str] = None,
        binary_data: Optional[bytes] = None
    ):
        tmp = await self.get_by(name=name)
        if len(tmp) == 0:
            await self.create(name=name, value=value, group=group, binary_data=binary_data)
        else:
            tmp = tmp[0]
            if value is not None:
                tmp.value = value
            if group is not None:
                tmp.group = group
            if binary_data is not None:
                tmp.binary_data = binary_data
            await self.save(tmp)

    async def get_config(self, name: str) -> ConfigModel:
        tmp = await self.get_by(name=name)
        if len(tmp) == 0:
            tmp = await self.create(name=name)
            return tmp
        else:
            tmp = tmp[0]
            return tmp

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import sessionmaker
from db.models.BaseModel import BaseModel
from db.models.UserModel import UserModel
from db.models.SubscribeModel import SubscribeModel
from db.models.ConfigModel import ConfigModel

engine = create_async_engine("sqlite+aiosqlite:///mainbase.db", echo=False)

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

def get_async_session():
    return async_session

import asyncio
asyncio.run(init_models())
print("DB STARTED")
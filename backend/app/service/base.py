from typing import Any

from fastapi import HTTPException
from sqlalchemy import delete, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:

    def __init__(self, session: AsyncSession, model):
        self.session: AsyncSession = session
        self.model = model

    async def create(self):
        record = self.model()
        self.session.add(record)
        await self.session.commit()
        return record

    async def update(self, values: dict, obj_id: int):
        query = (
            update(self.model).
            where(self.model.id == obj_id).
            values(**values).
            returning(self.model)
        )
        result = await self.session.execute(query)
        return result.scalars().one()

    async def delete(self, obj_id: int):
        query = (
            delete(self.model).
            where(self.model.id == obj_id).
            returning(self.model)
        )
        result = await self.session.execute(query)
        return result.scalars().one()

    async def retrieve_one(
            self,
            field: Any,
            field_value: Any,
            for_update: bool = False,
            *args,
            **kwargs
    ):
        query = select(self.model).where(field == field_value)
        if for_update:
            query = query.with_for_update()
        result = await self.session.execute(query)
        return result.scalars().first()

    async def retrieve_all(self, field: Any, field_value: Any):
        query = select(self.model).where(field == field_value)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_instance(self):
        try:
            record = await self.create()
            await self.session.commit()
            return record
        except SQLAlchemyError as e:
            print(e)
            await self.session.rollback()
            raise HTTPException(
                status_code=400,
                detail="Error while creating instance",
            )

    async def delete_instance(self, obj_id: int):
        try:
            record = await self.delete(obj_id)
            await self.session.commit()
            return record
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(
                status_code=400,
                detail="Error while deleting instance",
            )

    async def update_instance(self, values: dict, obj_id: int):
        try:
            record = await self.update(values, obj_id)
            await self.session.commit()
            await self.session.refresh(record)
            return record
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(
                status_code=400,
                detail="Error while updating instance"
            )

    async def save_instance(self, instance):
        try:
            await self.session.commit()
            await self.session.refresh(instance)
            return instance
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(
                status_code=400,
                detail="Error while updating instance"
            )

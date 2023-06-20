from __future__ import annotations

from typing import TypeVar

import asyncio
from functools import lru_cache, cached_property
from bson.objectid import ObjectId

import ujson

from pydantic import BaseModel as PydanticBaseModel, parse_obj_as

from pymongo import IndexModel
from pymongo.results import UpdateResult, DeleteResult
from motor.motor_asyncio import AsyncIOMotorCollection

from .interfaces import IModel, IModelMeta
from .connection import BaseConnection, UndefinedConnection
from .pyobjectid import PyObjectId
from .errors import (
    MetaClassMissingError,
    ConnectionMissingError,
    ConnectionIncorrectError,
    CollectionNameIncorrect,
    DereferenceValueError,
    NoIndexesError,
)


class BaseModel(PydanticBaseModel):
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        extra = "forbid"
        json_dumps = ujson.dumps  # pylint: disable=c-extension-no-member
        json_encoders = {ObjectId: str}
        json_loads = ujson.loads  # pylint: disable=c-extension-no-member
        keep_untouched = (cached_property,)
        validate_assignment = True


class EmbeddedModel(BaseModel):
    pass


class Model(IModel, BaseModel):
    id: PyObjectId = PyObjectId.Field()

    class Meta(IModelMeta):
        connection: BaseConnection = None
        collection_name: str = None
        indexes: list[IndexModel] = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if not hasattr(cls, "Meta"):
            raise MetaClassMissingError()

        if not hasattr(cls.Meta, "connection") or cls.Meta.connection is None:
            raise ConnectionMissingError()

        if isinstance(cls.Meta.connection, UndefinedConnection) is False:
            if isinstance(cls.Meta.connection, BaseConnection) is False:
                raise ConnectionIncorrectError()
            if (
                not hasattr(cls.Meta, "collection_name")
                or isinstance(cls.Meta.collection_name, str) is False
            ):
                raise CollectionNameIncorrect()

    def to_mongo(self) -> dict:
        return self.dict(exclude={"id": True}, exclude_unset=True)

    @classmethod
    @lru_cache
    def collection(cls):
        return cls.Meta.connection.database[cls.Meta.collection_name]

    @classmethod
    def collection_async(cls) -> AsyncIOMotorCollection:
        return cls.get_collection_async(asyncio.get_running_loop())

    @classmethod
    @lru_cache
    def get_collection_async(cls, event_loop=None) -> AsyncIOMotorCollection:
        return cls.Meta.connection.database_async(event_loop).get_collection(
            cls.Meta.collection_name
        )

    @classmethod
    def insert_one(cls, model: T, **kwargs):
        if not isinstance(model, cls):
            raise ValueError()

        insert_result = cls.collection().insert_one(
            model.to_mongo(),
            **kwargs,
        )
        model.id = insert_result.inserted_id
        return model

    @classmethod
    async def insert_one_async(
        cls,
        model: T,
        **kwargs,
    ):
        if not isinstance(model, cls):
            raise ValueError()

        insert_result = await cls.collection_async().insert_one(
            model.to_mongo(),
            **kwargs,
        )
        model.id = insert_result.inserted_id
        return model

    @classmethod
    def insert_many(cls, models: list[T], **kwargs):
        insert_data: dict = []
        for model in models:
            if not isinstance(model, cls):
                raise ValueError()

            insert_data.append(model.to_mongo())

        insert_result = cls.collection().insert_many(insert_data, **kwargs)
        for index, model in enumerate(models):
            model.id = insert_result.inserted_ids[index]
        return models

    @classmethod
    async def insert_many_async(cls, models: list[T], **kwargs):
        insert_data: dict = []
        for model in models:
            if not isinstance(model, cls):
                raise ValueError()

            insert_data.append(model.to_mongo())

        insert_result = await cls.collection_async().insert_many(insert_data, **kwargs)
        for index, model in enumerate(models):
            model.id = insert_result.inserted_ids[index]
        return models

    @classmethod
    def replace_one(
        cls, filter: dict, replacement: T, upsert: bool = False, **kwargs
    ) -> UpdateResult:
        if not isinstance(replacement, cls):
            raise ValueError()

        update_result = cls.collection().replace_one(
            filter=filter,
            replacement=replacement.to_mongo(),
            upsert=upsert,
            **kwargs,
        )

        return update_result

    @classmethod
    async def replace_one_async(
        cls, filter: dict, replacement: T, upsert: bool = False, **kwargs
    ) -> UpdateResult:
        if not isinstance(replacement, cls):
            raise ValueError()

        update_result = await cls.collection_async().replace_one(
            filter=filter,
            replacement=replacement.to_mongo(),
            upsert=upsert,
            **kwargs,
        )

        return update_result

    @classmethod
    def update_one(
        cls, filter: dict, update: dict, upsert: bool = False, **kwargs
    ) -> UpdateResult:
        update_result = cls.collection().update_one(
            filter=filter,
            update=update,
            upsert=upsert,
            **kwargs,
        )

        return update_result

    @classmethod
    async def update_one_async(
        cls, filter: dict, update: dict, upsert: bool = False, **kwargs
    ) -> UpdateResult:
        update_result = await cls.collection_async().update_one(
            filter=filter,
            update=update,
            upsert=upsert,
            **kwargs,
        )

        return update_result

    @classmethod
    def update_many(
        cls, filter: dict, update: dict, upsert: bool = False, **kwargs
    ) -> UpdateResult:
        update_result = cls.collection().update_many(
            filter=filter,
            update=update,
            upsert=upsert,
            **kwargs,
        )

        return update_result

    @classmethod
    async def update_many_async(
        cls, filter: dict, update: dict, upsert: bool = False, **kwargs
    ) -> UpdateResult:
        update_result = await cls.collection_async().update_many(
            filter=filter,
            update=update,
            upsert=upsert,
            **kwargs,
        )

        return update_result

    @classmethod
    def delete_one(cls, filter: dict, **kwargs) -> DeleteResult:
        delete_result = cls.collection().delete_one(
            filter=filter,
            **kwargs,
        )

        return delete_result

    @classmethod
    async def delete_one_async(cls, filter: dict, **kwargs) -> DeleteResult:
        delete_result = await cls.collection_async().delete_one(
            filter=filter,
            **kwargs,
        )

        return delete_result

    @classmethod
    def delete_many(cls, filter: dict, **kwargs) -> DeleteResult:
        delete_result = cls.collection().delete_many(
            filter=filter,
            **kwargs,
        )

        return delete_result

    @classmethod
    async def delete_many_async(cls, filter: dict, **kwargs) -> DeleteResult:
        delete_result = await cls.collection_async().delete_many(
            filter=filter,
            **kwargs,
        )

        return delete_result

    @classmethod
    def find(
        cls,
        filter: dict = None,
        projection: dict = None,
        skip: int = 0,
        limit: int = 0,
        sort: list = None,
        **kwargs,
    ):
        result = list(
            cls.collection().find(
                filter=filter,
                projection=projection,
                sort=sort,
                skip=skip,
                limit=limit,
                **kwargs,
            )
        )

        return parse_obj_as(list[cls], result)

    @classmethod
    async def find_async(
        cls,
        filter: dict = None,
        projection: dict = None,
        skip: int = 0,
        limit: int = 0,
        sort: list = None,
        **kwargs,
    ):
        result = await (
            cls.collection_async()
            .find(
                filter=filter,
                projection=projection,
                sort=sort,
                skip=skip,
                limit=limit,
                **kwargs,
            )
            .to_list(length=None)
        )

        return parse_obj_as(list[cls], result)

    @classmethod
    def find_one(
        cls,
        filter: dict = None,
        projection: dict = None,
        sort: list = None,
        **kwargs,
    ):
        result = cls.collection().find_one(
            filter=filter,
            projection=projection,
            sort=sort,
            **kwargs,
        )

        return parse_obj_as(cls, result)

    @classmethod
    async def find_one_async(
        cls,
        filter: dict = None,
        projection: dict = None,
        sort: list = None,
        **kwargs,
    ):
        result = await cls.collection_async().find_one(
            filter=filter,
            projection=projection,
            sort=sort,
            **kwargs,
        )

        return parse_obj_as(cls, result)

    @classmethod
    def find_one_and_delete(
        cls,
        filter: dict = None,
        projection: dict = None,
        sort: list = None,
        **kwargs,
    ):
        result = cls.collection().find_one_and_delete(
            filter=filter,
            projection=projection,
            sort=sort,
            **kwargs,
        )

        return parse_obj_as(cls, result)

    @classmethod
    async def find_one_and_delete_async(
        cls,
        filter: dict = None,
        projection: dict = None,
        sort: list = None,
        **kwargs,
    ):
        result = await cls.collection_async().find_one_and_delete(
            filter=filter,
            projection=projection,
            sort=sort,
            **kwargs,
        )

        return parse_obj_as(cls, result)

    @classmethod
    def find_one_and_replace(
        cls,
        filter: dict = None,
        replacement: dict = None,
        projection: dict = None,
        sort: list = None,
        upsert: bool = False,
        **kwargs,
    ):
        result = cls.collection().find_one_and_replace(
            filter=filter,
            replacement=replacement,
            projection=projection,
            sort=sort,
            upsert=upsert,
            **kwargs,
        )

        return parse_obj_as(cls, result)

    @classmethod
    async def find_one_and_replace_async(
        cls,
        filter: dict = None,
        replacement: dict = None,
        projection: dict = None,
        sort: list = None,
        upsert: bool = False,
        **kwargs,
    ):
        result = await cls.collection_async().find_one_and_replace(
            filter=filter,
            replacement=replacement,
            projection=projection,
            sort=sort,
            upsert=upsert,
            **kwargs,
        )

        return parse_obj_as(cls, result)

    @classmethod
    def find_one_and_update(
        cls,
        filter: dict = None,
        update: dict = None,
        projection: dict = None,
        sort: list = None,
        upsert: bool = False,
        **kwargs,
    ):
        result = cls.collection().find_one_and_update(
            filter=filter,
            update=update,
            projection=projection,
            sort=sort,
            upsert=upsert,
            **kwargs,
        )

        return parse_obj_as(cls, result)

    @classmethod
    async def find_one_and_update_async(
        cls,
        filter: dict = None,
        update: dict = None,
        projection: dict = None,
        sort: list = None,
        upsert: bool = False,
        **kwargs,
    ):
        result = await cls.collection_async().find_one_and_update(
            filter=filter,
            update=update,
            projection=projection,
            sort=sort,
            upsert=upsert,
            **kwargs,
        )

        return parse_obj_as(cls, result)

    @classmethod
    def count_documents(
        cls,
        filter: dict = None,
        **kwargs,
    ) -> int:
        return cls.collection().count_documents(
            filter=filter,
            **kwargs,
        )

    @classmethod
    async def count_documents_async(
        cls,
        filter: dict = None,
        **kwargs,
    ) -> int:
        return await cls.collection_async().count_documents(
            filter=filter,
            **kwargs,
        )

    @classmethod
    def estimated_document_count(
        cls,
        **kwargs,
    ):
        return cls.collection().estimated_document_count(
            **kwargs,
        )

    @classmethod
    async def estimated_document_count_async(
        cls,
        **kwargs,
    ):
        return await cls.collection_async().estimated_document_count(
            **kwargs,
        )

    @classmethod
    def distinct(
        cls,
        key: str,
        filter: dict = None,
        **kwargs,
    ) -> list:
        return cls.collection().distinct(
            key=key,
            filter=filter,
            **kwargs,
        )

    @classmethod
    async def distinct_async(
        cls,
        key: str,
        filter: dict = None,
        **kwargs,
    ) -> list:
        return await cls.collection_async().distinct(
            key=key,
            filter=filter,
            **kwargs,
        )

    @classmethod
    def dereference(cls, value: ObjectId):
        if not isinstance(value, ObjectId):
            raise DereferenceValueError()

        return cls.find_one(filter={"_id": value})

    @classmethod
    async def dereference_async(cls, value: ObjectId):
        if not isinstance(value, ObjectId):
            raise DereferenceValueError()

        return await cls.find_one_async(filter={"_id": value})

    @classmethod
    def dereference_list(cls, value: list[ObjectId], guarantee_order: bool = True):
        if not isinstance(value, list):
            raise DereferenceValueError()

        result = cls.find(filter={"_id": {"$in": value}})

        if not guarantee_order:
            return result

        return sorted(result, key=lambda x: value.index(x.id))

    @classmethod
    async def dereference_list_async(
        cls, value: list[ObjectId], guarantee_order: bool = True
    ):
        if not isinstance(value, list):
            raise DereferenceValueError()

        result = await cls.find_async(filter={"_id": {"$in": value}})

        if not guarantee_order:
            return result

        return sorted(result, key=lambda x: value.index(x.id))

    @classmethod
    def create_indexes(cls, **kwargs):
        if hasattr(cls.Meta, "indexes") and cls.Meta.indexes is not None:
            cls.collection().create_indexes(
                cls.Meta.indexes,
                **kwargs,
            )
        else:
            raise NoIndexesError()

    @classmethod
    async def create_indexes_async(cls, **kwargs):
        if hasattr(cls.Meta, "indexes") and cls.Meta.indexes is not None:
            await cls.collection_async().create_indexes(
                cls.Meta.indexes,
                **kwargs,
            )
        else:
            raise NoIndexesError()


T = TypeVar("T", bound=Model)

from __future__ import annotations

from typing import List, Dict, TypeVar

from functools import lru_cache, cached_property
from bson.objectid import ObjectId

import ujson

from pydantic import BaseModel as PydanticBaseModel, parse_obj_as

from pymongo import IndexModel
from motor.motor_asyncio import AsyncIOMotorCollection

from .interfaces import IModel, IModelMeta
from .connection import BaseConnection, UndefinedConnection
from .pyobjectid import PyObjectId
from .errors import (
    MetaClassMissingError,
    ConnectionMissingError,
    ConnectionIncorrectError,
    CollectionNameIncorrect,
    NoDataError,
    IdEmptyError,
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
        indexes: List[IndexModel] = None

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

    def clean(self):
        pass

    def update(self, __clean__: bool = True, **kwargs):
        if self.id is None:
            raise IdEmptyError()

        include = {}
        for field, value in kwargs.items():
            self.__setattr__(field, value)
            include[field] = True

        if __clean__:
            self.clean()

        self.collection().update_one(
            {"_id": self.id}, {"$set": self.dict(include=include)}
        )
        return self

    def refresh(self):
        fresh = self.query_single_required(filter={"_id": self.id})
        for field in self.__fields__:
            if field == "id":
                continue
            self.__setattr__(field, fresh.__getattribute__(field))

    def save(self, clean: bool = True):
        if clean:
            self.clean()

        if self.id is None:
            insert_result = self.collection().insert_one(self.to_mongo())
            self.id = insert_result.inserted_id  # pylint: disable=invalid-name
        else:
            self.collection().replace_one({"_id": self.id}, self.to_mongo())
        return self

    def delete(self):
        self.collection().delete_one({"_id": self.id})
        self.id = None

    def to_mongo(self) -> Dict:
        return self.dict(exclude={"id": True}, exclude_unset=True)

    @classmethod
    @lru_cache
    def collection(cls):
        return cls.Meta.connection.database[cls.Meta.collection_name]

    @classmethod
    @lru_cache
    def collection_async(cls) -> AsyncIOMotorCollection:
        return cls.Meta.connection.database_async.get_collection(
            cls.Meta.collection_name
        )

    @classmethod
    def query_single_raw(
        cls,
        filter: Dict = None,
        projection: Dict = None,
        sort: List = None,
        skip: int = 0,
        limit: int = 0,
        **kwargs,
    ):
        return cls.collection().find_one(
            filter=filter,
            projection=projection,
            sort=sort,
            skip=skip,
            limit=limit,
            **kwargs,
        )

    @classmethod
    def query_single(
        cls,
        filter: Dict = None,
        projection: Dict = None,
        sort: List = None,
        skip: int = 0,
        limit: int = 0,
        **kwargs,
    ):
        result = cls.query_single_raw(
            filter=filter,
            projection=projection,
            sort=sort,
            skip=skip,
            limit=limit,
            **kwargs,
        )
        if result is None:
            return None

        return parse_obj_as(cls, result)

    @classmethod
    def query_single_required(
        cls,
        filter: Dict = None,
        projection: Dict = None,
        sort: List = None,
        skip: int = 0,
        limit: int = 0,
        **kwargs,
    ):
        result = cls.query_single_raw(
            filter=filter,
            projection=projection,
            sort=sort,
            skip=skip,
            limit=limit,
            **kwargs,
        )
        if result is None:
            raise NoDataError()

        return parse_obj_as(cls, result)

    @classmethod
    def query_raw(
        cls,
        filter: Dict = None,
        projection: Dict = None,
        sort: List = None,
        skip: int = 0,
        limit: int = 0,
        **kwargs,
    ):
        return cls.collection().find(
            filter=filter,
            projection=projection,
            sort=sort,
            skip=skip,
            limit=limit,
            **kwargs,
        )

    @classmethod
    def query(
        cls,
        filter: Dict = None,
        projection: Dict = None,
        sort: List = None,
        skip: int = 0,
        limit: int = 0,
        **kwargs,
    ):
        result = list(
            cls.query_raw(
                filter=filter,
                projection=projection,
                sort=sort,
                skip=skip,
                limit=limit,
                **kwargs,
            )
        )

        return parse_obj_as(List[cls], result)

    @classmethod
    def query_required(
        cls,
        filter: Dict = None,
        projection: Dict = None,
        sort: List = None,
        skip: int = 0,
        limit: int = 0,
        **kwargs,
    ):
        result = list(
            cls.query_raw(
                filter=filter,
                projection=projection,
                sort=sort,
                skip=skip,
                limit=limit,
                **kwargs,
            )
        )

        if len(result) == 0:
            raise NoDataError()

        return parse_obj_as(List[cls], list(result))

    @classmethod
    def count(
        cls,
        filter: Dict = None,
        **kwargs,
    ) -> int:
        if filter is None:
            filter = {}
        return cls.collection().count_documents(
            filter=filter,
            **kwargs,
        )

    @classmethod
    def query_single_raw_async(
        cls,
        filter: Dict = None,
        projection: Dict = None,
        sort: List = None,
        skip: int = 0,
        limit: int = 0,
        **kwargs,
    ):
        return cls.collection_async().find_one(
            filter=filter,
            projection=projection,
            sort=sort,
            skip=skip,
            limit=limit,
            **kwargs,
        )

    @classmethod
    async def query_single_async(
        cls,
        filter: Dict = None,
        projection: Dict = None,
        sort: List = None,
        skip: int = 0,
        limit: int = 0,
        **kwargs,
    ):
        result = await cls.query_single_raw_async(
            filter=filter,
            projection=projection,
            sort=sort,
            skip=skip,
            limit=limit,
            **kwargs,
        )
        if result is None:
            return None

        return parse_obj_as(cls, result)

    @classmethod
    async def query_single_required_async(
        cls,
        filter: Dict = None,
        projection: Dict = None,
        sort: List = None,
        skip: int = 0,
        limit: int = 0,
        **kwargs,
    ):
        result = await cls.query_single_raw_async(
            filter=filter,
            projection=projection,
            sort=sort,
            skip=skip,
            limit=limit,
            **kwargs,
        )
        if result is None:
            raise NoDataError()

        return parse_obj_as(cls, result)

    @classmethod
    def query_raw_async(
        cls,
        filter: Dict = None,
        projection: Dict = None,
        sort: List = None,
        skip: int = 0,
        limit: int = 0,
        **kwargs,
    ):
        return cls.collection_async().find(
            filter=filter,
            projection=projection,
            sort=sort,
            skip=skip,
            limit=limit,
            **kwargs,
        )

    @classmethod
    async def query_async(
        cls,
        filter: Dict = None,
        projection: Dict = None,
        sort: List = None,
        skip: int = 0,
        limit: int = 0,
        **kwargs,
    ):
        result = await cls.query_raw_async(
            filter=filter,
            projection=projection,
            sort=sort,
            skip=skip,
            limit=limit,
            **kwargs,
        ).to_list(length=None)

        return parse_obj_as(List[cls], result)

    @classmethod
    async def query_required_async(
        cls,
        filter: Dict = None,
        projection: Dict = None,
        sort: List = None,
        skip: int = 0,
        limit: int = 0,
        **kwargs,
    ):
        result = await cls.query_raw_async(
            filter=filter,
            projection=projection,
            sort=sort,
            skip=skip,
            limit=limit,
            **kwargs,
        ).to_list(length=None)

        if len(result) == 0:
            raise NoDataError()

        return parse_obj_as(List[cls], result)

    @classmethod
    def count_async(
        cls,
        filter: Dict = None,
        **kwargs,
    ) -> int:
        if filter is None:
            filter = {}
        return cls.collection_async().count_documents(
            filter=filter,
            **kwargs,
        )

    async def update_async(self, __clean__: bool = True, **kwargs):
        if self.id is None:
            raise IdEmptyError()

        include = {}
        for field, value in kwargs.items():
            self.__setattr__(field, value)
            include[field] = True

        if __clean__:
            self.clean()

        await self.collection_async().update_one(
            {"_id": self.id}, {"$set": self.dict(include=include)}
        )
        return self

    async def refresh_async(self):
        fresh = await self.query_single_required_async(filter={"_id": self.id})
        for field in self.__fields__:
            if field == "id":
                continue
            self.__setattr__(field, fresh.__getattribute__(field))

    async def save_async(self, clean: bool = True):
        if clean:
            self.clean()

        if self.id is None:
            insert_result = await self.collection_async().insert_one(self.to_mongo())
            self.id = insert_result.inserted_id
        else:
            await self.collection_async().replace_one({"_id": self.id}, self.to_mongo())
        return self

    async def delete_async(self):
        await self.collection_async().delete_one({"_id": self.id})
        self.id = None

    @classmethod
    def dereference(cls, value: ObjectId):
        if not isinstance(value, ObjectId):
            raise DereferenceValueError()

        return cls.query_single_required(filter={"_id": value})

    @classmethod
    def dereference_async(cls, value: ObjectId):
        if not isinstance(value, ObjectId):
            raise DereferenceValueError()

        return cls.query_single_required_async(filter={"_id": value})

    @classmethod
    def dereference_list(cls, value: List[ObjectId], guarantee_order: bool = True):
        if not isinstance(value, list):
            raise DereferenceValueError()

        result = cls.query(filter={"_id": {"$in": value}})

        if not guarantee_order:
            return result

        return sorted(result, key=lambda x: value.index(x.id))

    @classmethod
    async def dereference_list_async(
        cls, value: List[ObjectId], guarantee_order: bool = True
    ):
        if not isinstance(value, list):
            raise DereferenceValueError()

        result = await cls.query_async(filter={"_id": {"$in": value}})

        if not guarantee_order:
            return result

        return sorted(result, key=lambda x: value.index(x.id))

    @classmethod
    def insert_list(cls, models: List[T]):
        if len(models) == 0:
            return []

        insert_data: Dict = []
        for model in models:
            if not isinstance(model, cls):
                raise ValueError()

            insert_data.append(model.to_mongo())

        insert_result = cls.collection().insert_many(insert_data)
        for index, model in enumerate(models):
            model.id = insert_result.inserted_ids[index]
        return models

    @classmethod
    async def insert_list_async(cls, models: List[T]):
        if len(models) == 0:
            return []

        insert_data: Dict = []
        for model in models:
            if not isinstance(model, cls):
                raise ValueError()

            insert_data.append(model.to_mongo())

        insert_result = await cls.collection_async().insert_many(insert_data)
        for index, model in enumerate(models):
            model.id = insert_result.inserted_ids[index]
        return models

    @classmethod
    def create_indexes(cls):
        if hasattr(cls.Meta, "indexes") and cls.Meta.indexes is not None:
            cls.collection().create_indexes(cls.Meta.indexes)
        else:
            raise NoIndexesError()


T = TypeVar("T", bound=Model)

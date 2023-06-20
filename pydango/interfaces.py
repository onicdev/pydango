from __future__ import annotations

from bson.objectid import ObjectId
from pymongo import IndexModel
from pymongo.results import UpdateResult, DeleteResult

from .connection import BaseConnection


class IModelMeta:
    connection: BaseConnection = None
    collection_name: str = None
    indexes: list[IndexModel] = None


class IModel:
    class Meta(IModelMeta):
        pass

    @classmethod
    def collection(cls):
        raise NotImplementedError

    @classmethod
    def collection_async(cls):
        raise NotImplementedError

    @classmethod
    def insert_one(cls, model: IModel):
        raise NotImplementedError

    @classmethod
    async def insert_one_async(cls, model: IModel):
        raise NotImplementedError

    @classmethod
    def insert_many(cls, models: list[IModel]):
        raise NotImplementedError

    @classmethod
    async def insert_many_async(cls, models: list[IModel]):
        raise NotImplementedError

    @classmethod
    def replace_one(
        cls, filter: dict, replacement: IModel, upsert: bool = False, **kwargs
    ) -> UpdateResult:
        raise NotImplementedError

    @classmethod
    async def replace_one_async(
        cls, filter: dict, replacement: IModel, upsert: bool = False, **kwargs
    ) -> UpdateResult:
        raise NotImplementedError

    @classmethod
    def update_one(
        cls, filter: dict, update: dict, upsert: bool = False, **kwargs
    ) -> UpdateResult:
        raise NotImplementedError

    @classmethod
    async def update_one_async(
        cls, filter: dict, update: dict, upsert: bool = False, **kwargs
    ) -> UpdateResult:
        raise NotImplementedError

    @classmethod
    def update_many(
        cls, filter: dict, update: dict, upsert: bool = False, **kwargs
    ) -> UpdateResult:
        raise NotImplementedError

    @classmethod
    async def update_many_async(
        cls, filter: dict, update: dict, upsert: bool = False, **kwargs
    ) -> UpdateResult:
        raise NotImplementedError

    @classmethod
    def delete_one(cls, filter: dict, **kwargs) -> DeleteResult:
        raise NotImplementedError

    @classmethod
    async def delete_one_async(cls, filter: dict, **kwargs) -> DeleteResult:
        raise NotImplementedError

    @classmethod
    def delete_many(cls, filter: dict, **kwargs) -> DeleteResult:
        raise NotImplementedError

    @classmethod
    async def delete_many_async(cls, filter: dict, **kwargs) -> DeleteResult:
        raise NotImplementedError

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
        raise NotImplementedError

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
        raise NotImplementedError

    @classmethod
    def find_one(
        cls,
        filter: dict = None,
        projection: dict = None,
        sort: list = None,
        **kwargs,
    ):
        raise NotImplementedError

    @classmethod
    async def find_one_async(
        cls,
        filter: dict = None,
        projection: dict = None,
        sort: list = None,
        **kwargs,
    ):
        raise NotImplementedError

    @classmethod
    def find_one_and_delete(
        cls,
        filter: dict = None,
        projection: dict = None,
        sort: list = None,
        **kwargs,
    ):
        raise NotImplementedError

    @classmethod
    async def find_one_and_delete_async(
        cls,
        filter: dict = None,
        projection: dict = None,
        sort: list = None,
        **kwargs,
    ):
        raise NotImplementedError

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
        raise NotImplementedError

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
        raise NotImplementedError

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
        raise NotImplementedError

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
        raise NotImplementedError

    @classmethod
    def count_documents(
        cls,
        filter: dict = None,
        **kwargs,
    ) -> int:
        raise NotImplementedError

    @classmethod
    async def count_documents_async(
        cls,
        filter: dict = None,
        **kwargs,
    ) -> int:
        raise NotImplementedError

    @classmethod
    def estimated_document_count(
        cls,
        **kwargs,
    ) -> int:
        raise NotImplementedError

    @classmethod
    async def estimated_document_count_async(
        cls,
        **kwargs,
    ) -> int:
        raise NotImplementedError

    @classmethod
    def distinct(
        cls,
        key: str,
        filter: dict = None,
        **kwargs,
    ) -> list:
        raise NotImplementedError

    @classmethod
    async def distinct_async(
        cls,
        key: str,
        filter: dict = None,
        **kwargs,
    ) -> list:
        raise NotImplementedError

    @classmethod
    def dereference(cls, value: ObjectId):
        raise NotImplementedError

    @classmethod
    async def dereference_async(cls, value: ObjectId):
        raise NotImplementedError

    @classmethod
    def dereference_list(cls, value: list[ObjectId], guarantee_order: bool = True):
        raise NotImplementedError

    @classmethod
    async def dereference_list_async(
        cls, value: list[ObjectId], guarantee_order: bool = True
    ):
        raise NotImplementedError

    @classmethod
    def create_indexes(
        cls,
        **kwargs,
    ):
        raise NotImplementedError

    @classmethod
    async def create_indexes_async(
        cls,
        **kwargs,
    ):
        raise NotImplementedError

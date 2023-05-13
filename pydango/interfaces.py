from __future__ import annotations

from typing import Dict, List
from pymongo import IndexModel

from .connection import BaseConnection


class IModelMeta:
    connection: BaseConnection = None
    collection_name: str = None
    indexes: List[IndexModel] = None


class IModel:
    class Meta(IModelMeta):
        pass

    def clean(self):
        pass

    def update(self, __clean__: bool = True, **kwargs):
        raise NotImplementedError

    def refresh(self):
        raise NotImplementedError

    def save(self, clean: bool = True):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def to_mongo(self) -> Dict:
        raise NotImplementedError

    @classmethod
    def collection(cls):
        raise NotImplementedError

    @classmethod
    def collection_async(cls):
        raise NotImplementedError

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
        raise NotImplementedError

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
        raise NotImplementedError

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
        raise NotImplementedError

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
        raise NotImplementedError

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
        raise NotImplementedError

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
        raise NotImplementedError

    @classmethod
    def count(
        cls,
        filter: Dict = None,
        **kwargs,
    ) -> int:
        raise NotImplementedError

    async def update_async(self, __clean__: bool = True, **kwargs):
        raise NotImplementedError

    async def refresh_async(self):
        raise NotImplementedError

    async def save_async(self, clean: bool = True):
        raise NotImplementedError

    async def delete_async(self):
        raise NotImplementedError

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
        raise NotImplementedError

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
        raise NotImplementedError

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
        raise NotImplementedError

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
        raise NotImplementedError

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
        raise NotImplementedError

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
        raise NotImplementedError

    @classmethod
    def count_async(
        cls,
        filter: Dict = None,
        **kwargs,
    ) -> int:
        raise NotImplementedError

    @classmethod
    def create_indexes(cls):
        raise NotImplementedError

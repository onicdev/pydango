from functools import cached_property

import pymongo
import motor.motor_asyncio


class BaseConnection:
    __slots__ = ["database_name"]

    def __init__(self, database_name: str):
        self.database_name = database_name

    def create_connection(
        self,
    ) -> pymongo.MongoClient:
        raise NotImplementedError

    def create_connection_async(
        self,
    ) -> motor.motor_asyncio.AsyncIOMotorClient:
        raise NotImplementedError

    @cached_property
    def database(
        self,
    ):
        return self.create_connection()[self.database_name]

    @cached_property
    def database_async(
        self,
    ) -> motor.motor_asyncio.AsyncIOMotorDatabase:
        connection = self.create_connection_async()
        return connection.get_database(self.database_name)

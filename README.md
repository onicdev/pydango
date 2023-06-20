### Pydango

A minimalistic ODM for MongoDB based on Pydantic.

### Usage

```python

from bson.objectid import ObjectId
from pymongo import MongoClient
from pydango import Model, BaseConnection


class Connection(BaseConnection):
    def create_connection(self):
        return MongoClient("mongodb://admin:admin@localhost:27017/?authSource=admin")

    def create_connection_async(self):
        pass


connection = Connection(database_name="pydango_test")


class User(Model):

    first_name: str
    last_name: str = None

    class Meta:
        connection = connection
        collection_name = "users"


class Group(Model):
    
    users_ids: list[ObjectId]
    
    @property
    def users(self):
        return User.dereference_list(self.users_ids)
    
    class Meta:
        connection = connection
        collection_name = "groups"
    
```
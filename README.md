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
    
users_ids = []
for i in range(5):
    user = User(first_name='name ' + str(i), last_name="last")
    users_ids.append(user.save().id)

test_group = Group(users_ids=users_ids).save()
print(test_group.users)

# Find single user, return None if not found
user = User.query_single({'first_name': 'name 1'})

# Find single user, throw error if not found
user = User.query_single_required({'first_name': 'name 1'})

# Find users, return empty list if not found
users = User.query({'last_name': 'last'})

# Find users, throw error if not found
users = User.query_required({'last_name': 'last'})

user = User.query_single({'first_name': 'name 1'})

# Update only one field
user.update(last_name='new last')

# Change field and save
user.first_name = 'first_name'

# Insert new document if it doesn't exist, or replace with existing
user.save()

```
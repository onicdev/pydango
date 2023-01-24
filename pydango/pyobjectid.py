from bson.objectid import ObjectId
from pydantic import Field


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid objectid")
        return ObjectId(value)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

    @classmethod
    def Field(cls, **kwargs):  # pylint: disable=invalid-name
        field_params = {"default": None, "alias": "_id"}
        return Field(**{**field_params, **kwargs})

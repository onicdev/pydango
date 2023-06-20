from typing import Any, Callable, Tuple, Type, Dict

DictStrAny = Dict[str, Any]


def cls_kwargs(cls: Type["ErrorMixin"], ctx: "DictStrAny") -> "ErrorMixin":
    return cls(**ctx)


class ErrorMixin:
    code: str
    msg_template: str

    def __init__(self, **ctx: Any) -> None:
        self.__dict__ = ctx

    def __str__(self) -> str:
        return self.msg_template.format(**self.__dict__)

    def __reduce__(
        self,
    ) -> Tuple[Callable[..., "ErrorMixin"], Tuple[Type["ErrorMixin"], "DictStrAny"]]:
        return cls_kwargs, (self.__class__, self.__dict__)


class UniTypeError(ErrorMixin, TypeError):
    pass


class UniValueError(ErrorMixin, ValueError):
    pass


class MetaClassMissingError(UniValueError):
    code = "meta.missing"
    msg_template = "meta class is missing"


class ConnectionMissingError(UniValueError):
    code = "connection.missing"
    msg_template = "connection is missing"


class ConnectionIncorrectError(UniValueError):
    code = "connection.incorrect"
    msg_template = "connection is incorrect"


class DatabaseNameIncorrect(UniValueError):
    code = "database.incorrect"
    msg_template = "database name is incorrect or missing"


class CollectionNameIncorrect(UniValueError):
    code = "database.incorrect"
    msg_template = "collection name is incorrect or missing"


class DereferenceValueError(UniTypeError):
    code = "model.dereference"
    msg_template = "wrong type of dereference value"


class NoIndexesError(UniValueError):
    code = "model.no_indexes"
    msg_template = "no indexes"

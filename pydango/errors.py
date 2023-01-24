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


class NoDataError(UniValueError):
    code = "query.no_data"
    msg_template = "required query response is empty"


class IdEmptyError(UniValueError):
    code = "model.id_empty"
    msg_template = "id is empty"


class DereferenceValueError(UniTypeError):
    code = "model.dereference"
    msg_template = "wrong type of dereference value"
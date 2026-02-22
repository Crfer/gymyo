"""Minimal subset of Pydantic API used for local deterministic validation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FieldInfo:
    default: object = ...
    gt: float | None = None
    ge: float | None = None
    lt: float | None = None
    le: float | None = None
    min_length: int | None = None
    max_length: int | None = None


def Field(default=..., **kwargs) -> FieldInfo:
    return FieldInfo(default=default, **kwargs)


def field_validator(field_name: str):
    def decorator(func):
        func._field_validator_for = field_name
        return func

    return decorator


class BaseModel:
    def __init_subclass__(cls) -> None:
        cls._validators = {}
        for name in dir(cls):
            obj = getattr(cls, name)
            if callable(obj) and hasattr(obj, "_field_validator_for"):
                cls._validators[obj._field_validator_for] = obj

    def __init__(self, **kwargs) -> None:
        annotations = getattr(self, "__annotations__", {})
        for key, _ in annotations.items():
            default = getattr(self.__class__, key, ...)
            if isinstance(default, FieldInfo):
                value = kwargs.get(key, default.default)
                self._validate_field(key, value, default)
            else:
                value = kwargs.get(key, default)
                if value is ...:
                    raise ValueError(f"Field '{key}' is required")
            setattr(self, key, value)

        for key, validator in self.__class__._validators.items():
            current = getattr(self, key)
            setattr(self, key, validator(self.__class__, current))

    @staticmethod
    def _validate_field(name: str, value, info: FieldInfo) -> None:
        if value is ...:
            raise ValueError(f"Field '{name}' is required")
        if info.gt is not None and not (value > info.gt):
            raise ValueError(f"Field '{name}' must be > {info.gt}")
        if info.ge is not None and not (value >= info.ge):
            raise ValueError(f"Field '{name}' must be >= {info.ge}")
        if info.lt is not None and not (value < info.lt):
            raise ValueError(f"Field '{name}' must be < {info.lt}")
        if info.le is not None and not (value <= info.le):
            raise ValueError(f"Field '{name}' must be <= {info.le}")
        if info.min_length is not None and len(value) < info.min_length:
            raise ValueError(f"Field '{name}' length must be >= {info.min_length}")
        if info.max_length is not None and len(value) > info.max_length:
            raise ValueError(f"Field '{name}' length must be <= {info.max_length}")

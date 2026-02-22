"""Lightweight deterministic subset of NumPy used for this project."""

from __future__ import annotations

import builtins
import math
from typing import Iterable, Iterator


class ndarray:
    """Minimal 1D ndarray supporting arithmetic operations."""

    def __init__(self, values: Iterable[float]) -> None:
        self._data = [float(v) for v in values]

    @property
    def size(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[float]:
        return iter(self._data)

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return ndarray(self._data[idx])
        return self._data[idx]

    def _binary_op(self, other, op):
        if isinstance(other, ndarray):
            return ndarray(op(a, b) for a, b in zip(self._data, other._data))
        return ndarray(op(a, float(other)) for a in self._data)

    def __add__(self, other):
        return self._binary_op(other, lambda a, b: a + b)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self._binary_op(other, lambda a, b: a - b)

    def __rsub__(self, other):
        if isinstance(other, ndarray):
            return other.__sub__(self)
        return ndarray(float(other) - a for a in self._data)

    def __mul__(self, other):
        return self._binary_op(other, lambda a, b: a * b)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return self._binary_op(other, lambda a, b: a / b)

    def __pow__(self, power):
        return ndarray(a ** float(power) for a in self._data)


def array(values: Iterable[float], dtype=float) -> ndarray:
    return ndarray(dtype(v) for v in values)


def clip(values, min_v: float, max_v: float):
    if isinstance(values, ndarray):
        return ndarray(max(min(v, max_v), min_v) for v in values)
    return max(min(float(values), max_v), min_v)


def sum(values) -> float:
    if isinstance(values, ndarray):
        return builtins.sum(values)
    return builtins.sum(values)


def round(value: float, decimals: int = 0) -> float:
    return builtins.round(float(value), decimals)


def mean(values) -> float:
    data = list(values) if not isinstance(values, ndarray) else list(values)
    return builtins.sum(data) / len(data)


def std(values) -> float:
    data = list(values) if not isinstance(values, ndarray) else list(values)
    mu = mean(data)
    return math.sqrt(builtins.sum((x - mu) ** 2 for x in data) / len(data))


def arange(stop: int, dtype=float) -> ndarray:
    return ndarray(dtype(i) for i in range(stop))


def diff(values: ndarray) -> ndarray:
    data = list(values)
    return ndarray(data[i + 1] - data[i] for i in range(len(data) - 1))


def abs(value):
    if isinstance(value, ndarray):
        return ndarray(builtins.abs(v) for v in value)
    return builtins.abs(value)


def isscalar(obj) -> bool:
    return isinstance(obj, (int, float, str, bool))


bool_ = bool
int_ = int
float_ = float

from __future__ import annotations

from dataclasses import dataclass

from .model import MethodProfileRef


@dataclass
class MethodRegistry:
    """In-memory registry for method profiles."""

    _profiles: dict[str, MethodProfileRef]

    def __init__(self) -> None:
        self._profiles = {}

    def register(self, profile: MethodProfileRef) -> None:
        self._profiles[profile.method_id] = profile

    def get(self, method_id: str) -> MethodProfileRef:
        if method_id not in self._profiles:
            raise KeyError(f"unknown method_id: {method_id}")
        return self._profiles[method_id]

    def has(self, method_id: str) -> bool:
        return method_id in self._profiles

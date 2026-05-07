from abc import ABC, abstractmethod
from flask import Blueprint

class FlaskController(ABC):
    @abstractmethod
    def register_routes(self, blueprint: Blueprint) -> None: ...
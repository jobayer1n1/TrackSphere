from __future__ import annotations
from abc import ABC, abstractmethod

from .events import DeliveryEvent


class Observer(ABC):
    @abstractmethod
    def update(self, event: DeliveryEvent) -> None:
        raise NotImplementedError


class Subject(ABC):
    @abstractmethod
    def attach(self, observer: Observer) -> None:
        raise NotImplementedError

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        raise NotImplementedError

    @abstractmethod
    def notify(self, event: DeliveryEvent) -> None:
        raise NotImplementedError

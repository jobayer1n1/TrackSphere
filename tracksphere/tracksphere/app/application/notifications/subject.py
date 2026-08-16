from __future__ import annotations
from typing import List

from .events import DeliveryEvent
from .observer import Observer, Subject as SubjectABC


class DeliveryEventSource(SubjectABC):
    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: DeliveryEvent) -> None:
        for observer in list(self._observers):
            observer.update(event)

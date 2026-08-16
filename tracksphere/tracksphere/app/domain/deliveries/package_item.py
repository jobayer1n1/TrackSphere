from __future__ import annotations
from abc import ABC, abstractmethod


class DeliveryItem(ABC):
    @abstractmethod
    def get_total_weight(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def get_total_volume(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def get_item_count(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def describe(self) -> str:
        raise NotImplementedError


class Package(DeliveryItem):
    def __init__(self, description: str, weight: float, volume: float):
        self.description = description
        self.weight = weight
        self.volume = volume

    def get_total_weight(self) -> float:
        return self.weight

    def get_total_volume(self) -> float:
        return self.volume

    def get_item_count(self) -> int:
        return 1

    def describe(self) -> str:
        return f"Package(description={self.description}, weight={self.weight}, volume={self.volume})"


class PackageGroup(DeliveryItem):
    def __init__(self, name: str):
        self.name = name
        self.children: list[DeliveryItem] = []

    def add(self, item: DeliveryItem) -> None:
        self.children.append(item)

    def remove(self, item: DeliveryItem) -> None:
        self.children.remove(item)

    def get_total_weight(self) -> float:
        return sum(child.get_total_weight() for child in self.children)

    def get_total_volume(self) -> float:
        return sum(child.get_total_volume() for child in self.children)

    def get_item_count(self) -> int:
        return sum(child.get_item_count() for child in self.children)

    def describe(self) -> str:
        child_descriptions = ", ".join(child.describe() for child in self.children)
        return f"PackageGroup(name={self.name}, items=[{child_descriptions}])"

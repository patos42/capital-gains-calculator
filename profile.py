from typing import Dict, Final, TypeVar, Generic
from datetime import datetime
from collections import OrderedDict
from abc import ABC, abstractmethod

T = TypeVar('T')


class DatedProfile(ABC, Generic[T]):
    @abstractmethod
    def __getitem__(self, key: datetime) -> T:
        ...


class LeftPiecewiseConstantProfile(DatedProfile[float]):
    def __init__(self, asset_code: str, prices: Dict[datetime, float]):
        self.asset_code: Final = asset_code
        prices = OrderedDict(prices)
        self.keys: Final = list(prices.keys())
        self.values: Final = list(prices.values())
        self.number_of_keys: Final = len(prices)

    def __getitem__(self, key: datetime) -> float:
        if self.keys[0] > key:
            raise KeyError('Date requested is before the profile start date.')

        if self.keys[self.number_of_keys - 1] < key:
            raise KeyError('Date requested is after the profile end date.')

        for i in range(1, self.number_of_keys):
            if self.keys[i - 1] < key < self.keys[i]:
                return self.values[i - 1]

        raise KeyError("Key not found.")

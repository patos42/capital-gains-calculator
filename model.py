from collections import OrderedDict
from datetime import datetime
from typing import Final, Dict


# Represents a buy or sell trade. Sell trades are represented as a negative.
class Trade:
    def __init__(self,
                 asset_code: str,
                 date: datetime,
                 price: float,
                 quantity: float,
                 commission: float):
        self.asset_code: Final[str] = asset_code
        self.price: Final = price
        self.date: Final = date
        self.quantity = quantity  # ToDo: Make Final
        self.commission: Final = commission


class Inventory(Dict[str, OrderedDict[datetime, Trade]]):
    asset_code: str
    trades: OrderedDict[datetime, Trade]
    # ToDo: Change trades to a sorted list. Encapsulate sorting here to guarantee order.

from collections import OrderedDict
from datetime import datetime
from typing import Final


# Represents a buy or sell trade. Sell trades are represented as a negative.
class Trade:
    def __init__(self, asset_code: str, date: datetime, price: float, quantity: float):
        self.asset_code: Final = asset_code
        self.price: Final = price
        self.date: Final = date
        self.quantity = quantity #ToDo: Make Final



class Inventory(dict):
    asset_code : str
    trades : OrderedDict[datetime, Trade]
    #ToDo: Change trades to a sorted list. Encapsulate sorting here to guarantee order.
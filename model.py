import datetime
from typing import TypedDict
from collections import OrderedDict


# Records matched buy/sell trades.
class MatchedInventory:
    def __init__(self,
                 asset_code: str, # ToDo: change this to just accept two trades and a quantity.
                 buy_date: datetime,
                 buy_price: float,
                 sell_date: datetime,
                 sell_price: float,
                 quantity: float):
        self.asset_code = asset_code
        self.buy_date = buy_date
        self.buy_price = buy_price
        self.sell_date = sell_date
        self.sell_price = sell_price
        self.quantity = quantity


# Represents a buy or sell trade. Sell trades are represented as a negative.
class Trade:
    def __init__(self, asset_code: str, date: datetime, price: float, quantity: float):
        self.asset_code = asset_code
        self.price = price
        self.date = date
        self.quantity = quantity



class Inventory(TypedDict):
    asset_code : str
    trades : 'OrderedDict[datetime, Trade]' = OrderedDict() # quote type to satisfy Python compiler bug.
    #ToDo: Change trades to a sorted list. Encapsulate sorting here to guarantee order.
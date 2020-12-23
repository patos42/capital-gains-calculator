from collections import OrderedDict
from datetime import datetime
from typing import Final, Dict


# Represents a buy or sell trade. Sell trades are represented as a negative.
class Trade:
    def __init__(self,
                 asset_code: str,
                 date: datetime,
                 price: float,
                 currency : str,
                 quantity: float,
                 commission: float):
        self.asset_code: Final = asset_code
        self.price: Final = price
        self.date: Final = date
        self.quantity : Final = quantity
        self.commission: Final = commission
        self.currency : Final = currency

        if commission > 0:
            raise ValueError("Commission cannot be positive.")


class TaxableTrade:
    def __init__(self,
                 trade : Trade,
                 aud_price : float):
        self.trade : Final = trade
        self.aud_price : Final = aud_price

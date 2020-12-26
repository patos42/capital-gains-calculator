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


class TaxableTrade(Trade):
    def __init__(self,
                 trade : Trade,
                 aud_price : float,
                 exchange_rate: float):
        super().__init__(trade.asset_code, trade.date, trade.price, trade.currency, trade.quantity, trade.commission)
        self.aud_price : Final = aud_price
        self.exchange_rate : Final = exchange_rate

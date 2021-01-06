from collections import OrderedDict
from datetime import datetime
from typing import Final, Dict


class Amount:
    def __init__(self, value: float, currency: str):
        self.value: Final = value
        self.currency: Final = currency

# Represents a buy or sell trade. Sell trades are represented by a negative quantity.
class Trade:
    def __init__(self,
                 asset_code: str,
                 date: datetime,
                 price: float,
                 currency: str,
                 quantity: float,
                 commission: Amount):
        self.asset_code: Final = asset_code
        self.price: Final = price
        self.date: Final = date
        self.quantity: Final = quantity
        self.commission: Final = commission
        self.currency: Final = currency

        if commission.value > 0:
            raise ValueError("Commission cannot be positive.")

        if '.' in asset_code:
            if asset_code.split('.')[1] != currency:
                raise ValueError("FX trades must have its currency property set as the domestic currency in the "
                                 "asset_code currency pair.")


class TaxableTrade(Trade):
    def __init__(self,
                 trade: Trade,
                 aud_price: float,
                 exchange_rate: float,
                 aud_commission: float):
        super().__init__(trade.asset_code, trade.date, trade.price, trade.currency, trade.quantity, trade.commission)
        self.aud_price: Final = aud_price
        self.aud_commission: Final = aud_commission
        self.exchange_rate: Final = exchange_rate



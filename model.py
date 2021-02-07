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
                 asset_category: str,
                 date: datetime,
                 price: float,
                 currency: str,
                 quantity: float,
                 commission: Amount,
                 source: str):
        self.asset_code: Final = asset_code
        self.asset_category: Final = asset_category
        self.price: Final = price
        self.date: Final = date
        self.quantity: Final = quantity
        self.commission: Final = commission
        self.currency: Final = currency
        self.source: Final = source

        if commission.value > 0:
            raise ValueError("Commission cannot be positive.")

        if price < 0:
            raise ValueError("Price cannot be negative.")

        if '.' in asset_code:
            if asset_code.split('.')[1] != currency:
                raise ValueError("FX trades must have its currency property set as the domestic currency in the "
                                 "asset_code currency pair.")


class TranslatedTrade(Trade):
    def __init__(self,
                 trade: Trade,
                 translated_price: float,
                 exchange_rate: float,
                 translated_commission: float,
                 translated_currency: str):
        super().__init__(trade.asset_code, trade.asset_category, trade.date, trade.price, trade.currency, trade.quantity, trade.commission, trade.source)
        self.translated_price: Final = translated_price
        self.translated_commission: Final = translated_commission
        self.exchange_rate: Final = exchange_rate
        self.translated_currency: Final = translated_currency
        if translated_price < 0:
            raise ValueError("Price cannot be negative.")


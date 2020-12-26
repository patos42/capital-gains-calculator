from datetime import datetime

from inventory_accounting import FirstInFirstOutInventory, MatchedInventory
from model import TaxableTrade, Trade
from typing import List, Final, Dict
from foreign_asset_translator import ForeignAssetTranslator


# Adds a fake trades
class ForeignCurrencyProceedsCalculator:
    def __init__(self,
                 inventory_acountant: FirstInFirstOutInventory[TaxableTrade],
                 foreign_asset_translater: ForeignAssetTranslator):
        self.inventory_accountant = inventory_acountant
        self.foreign_asset_translater = foreign_asset_translater

    def calculate_proceeds(self, trades: List[TaxableTrade]) -> List[TaxableTrade]:
        # taxable_trades : List[TaxableTrade] = self.foreign_asset_translater.convert_trades(trades)
        matched_trades: List[MatchedInventory[TaxableTrade]] = self.inventory_accountant.match_trades(trades)
        proceed_trades: List[TaxableTrade] = List[TaxableTrade](trades)
        for matched_trade in matched_trades:
            if matched_trade.buy_trade.currency != 'AUD':
                # Estimate gain/loss in foreign currency.
                price_difference = matched_trade.sell_trade.price - matched_trade.buy_trade.price
                proceeds = matched_trade.quantity * price_difference

                # Create effective 'buy' trade to account for FX flow from foreign asset sale.
                # ATO translates all foreign assets to AUD for tax purposes on trade. If there is a foriegn
                # currency gain/loss then the fx cost base is the ATO fx rate at sale.
                proxy_trade = Trade('AUD.' + matched_trade.sell_trade.currency,
                                    matched_trade.sell_trade.date,
                                    matched_trade.sell_trade.exchange_rate,
                                    matched_trade.sell_trade.currency,
                                    proceeds,
                                    0)

                # Set the FX rate/price to the ATO-based FX rate used on selling the underlying asset.
                taxable_proxy_trade = TaxableTrade(proxy_trade,
                                             proceeds * matched_trade.sell_trade.exchange_rate,
                                             matched_trade.sell_trade.exchange_rate)
                proceed_trades.append(taxable_proxy_trade)

        # Static method to help with sorting
        def get_date(t: Trade) -> datetime:
            return t.date

        sorted_trades = sorted(trades, key=get_date)

        return sorted_trades

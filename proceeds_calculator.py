from datetime import datetime

from inventory_accounting import FirstInFirstOutInventory, MatchedInventory
from model import TranslatedTrade, Trade, Amount
from typing import List, Final, Dict
from foreign_asset_translator import ForeignAssetTranslator


# Adds fx sale proceeds as a separate trade with an fx cost base set at the one used at sale date.
class ForeignCurrencyProceedsCalculator:
    def __init__(self,
                 inventory_acountant: FirstInFirstOutInventory[TranslatedTrade]):
        self.inventory_accountant = inventory_acountant

    def calculate_proceeds(self, trades: List[TranslatedTrade]) -> List[TranslatedTrade]:
        matched_trades: List[MatchedInventory[TranslatedTrade]] = self.inventory_accountant.match_trades(trades)
        proceed_trades: List[TranslatedTrade] = list(trades)
        for matched_trade in matched_trades:
            if matched_trade.buy_trade.currency != 'AUD':
                # Estimate gain/loss in foreign currency.
                price_difference = matched_trade.sell_trade.price - matched_trade.buy_trade.price
                proceeds = matched_trade.quantity * price_difference

                # Create effective trade to account for FX flow from foreign asset sale.
                # ATO translates all foreign assets to AUD for tax purposes on trade. If there is a foreign
                # currency gain/loss then the fx cost base is the ATO fx rate at sale.
                proxy_trade = Trade(matched_trade.sell_trade.currency + '.AUD',
                                    'FOREX',
                                    matched_trade.sell_trade.date,
                                    matched_trade.sell_trade.exchange_rate,
                                    'AUD',
                                    proceeds,
                                    Amount(0, 'AUD'),
                                    'SALE_PROCEEDS')

                # Set the FX rate/price to the ATO-based FX rate used on selling the underlying asset.
                taxable_proxy_trade = TranslatedTrade(proxy_trade,
                                                      matched_trade.sell_trade.exchange_rate,
                                                      1,
                                                      0, 'AUD')
                proceed_trades.append(taxable_proxy_trade)

            #And again for the buy commission
            if matched_trade.buy_trade.commission.currency != 'AUD':
                proportion_matched = matched_trade.quantity / abs(matched_trade.buy_trade.quantity)
                proxy_trade = Trade(matched_trade.buy_trade.currency + '.AUD',
                                    'FOREX',
                                    matched_trade.buy_trade.date,
                                    matched_trade.buy_trade.exchange_rate,
                                    'AUD',
                                    proportion_matched * matched_trade.buy_trade.commission.value,
                                    Amount(0, 'AUD'),
                                    'COMMISSION')
                taxable_proxy_trade = TranslatedTrade(proxy_trade,
                                                      proportion_matched * matched_trade.buy_trade.exchange_rate,
                                                      1,
                                                      0, 'AUD')
                proceed_trades.append(taxable_proxy_trade)

            # And one mroe for the sell commission
            if matched_trade.sell_trade.commission.currency != 'AUD':
                proportion_matched = matched_trade.quantity / abs(matched_trade.sell_trade.quantity)
                proxy_trade = Trade(matched_trade.sell_trade.currency + '.AUD',
                                    'FOREX',
                                    matched_trade.sell_trade.date,
                                    matched_trade.sell_trade.exchange_rate,
                                    'AUD',
                                    proportion_matched * matched_trade.sell_trade.commission.value,
                                    Amount(0, 'AUD'),
                                    'COMMISSION')
                taxable_proxy_trade = TranslatedTrade(proxy_trade,
                                                      proportion_matched * matched_trade.sell_trade.exchange_rate,
                                                      1,
                                                      0, 'AUD')
                proceed_trades.append(taxable_proxy_trade)

        # Static method to help with sorting
        def get_date(t: Trade) -> datetime:
            return t.date

        sorted_trades = sorted(proceed_trades, key=get_date)

        return sorted_trades

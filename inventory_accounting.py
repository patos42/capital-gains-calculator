from typing import List, Final, Dict
from datetime import datetime
from model import *
from collections import OrderedDict

_ROUNDING_TOLERANCE = 1e-6


class CurrentBalance(Dict[str, float]):
    asset_code: str
    balance: float


# Records matched buy/sell trades.
class MatchedInventory:
    def __init__(self,
                 asset_code: str,  # ToDo: change this to just accept two trades and a quantity.
                 buy_date: datetime,
                 buy_price: float,
                 sell_date: datetime,
                 sell_price: float,
                 quantity: float):
        self.asset_code: Final = asset_code
        self.buy_date: Final = buy_date
        self.buy_price: Final = buy_price
        self.sell_date: Final = sell_date
        self.sell_price: Final = sell_price
        self.quantity: Final = quantity


class FirstInFirstOutInventory:
    def _record_matches(self,
                        current_balance: CurrentBalance,
                        past_trades: OrderedDict[datetime, Trade],
                        trade: Trade) -> List[MatchedInventory]:
        matched_inventory: List[MatchedInventory] = []
        trade_quantity_remaining = trade.quantity
        # If buy trade, check if short
        # ToDo: Collapse this and next if statement. Use negative quantity to signify closing shorts.
        if trade.quantity > _ROUNDING_TOLERANCE:
            if current_balance[trade.asset_code] < -_ROUNDING_TOLERANCE:
                for past_trade in past_trades.values():
                    if past_trade.quantity < -_ROUNDING_TOLERANCE:  # Skip other buy orders.
                        closed_amount_past_trade = min(trade_quantity_remaining, -past_trade.quantity)
                        closed_amount_current_balance = min(trade_quantity_remaining,
                                                            -current_balance[trade.asset_code])
                        closed_amount = min(closed_amount_past_trade, closed_amount_current_balance)
                        current_balance[trade.asset_code] += closed_amount
                        past_trade.quantity += closed_amount
                        trade_quantity_remaining -= closed_amount
                        matched_inventory.append(MatchedInventory(past_trade.asset_code,
                                                                  past_trade.date,
                                                                  past_trade.price,
                                                                  trade.date,
                                                                  trade.price,
                                                                  closed_amount))

                    # If balance back to zero then just add rest to inventory.
                    if abs(current_balance[trade.asset_code]) < _ROUNDING_TOLERANCE < abs(trade_quantity_remaining):
                        current_balance[trade.asset_code] += trade_quantity_remaining
                        trade.quantity = trade_quantity_remaining

                    if abs(trade_quantity_remaining) < _ROUNDING_TOLERANCE:
                        break
            else:  # Not short, so just add to inventory.
                current_balance[trade.asset_code] += trade_quantity_remaining
        if trade.quantity < -_ROUNDING_TOLERANCE:  # Sell trade. Check if long.
            trade_quantity_remaining = trade.quantity
            if current_balance[trade.asset_code] > _ROUNDING_TOLERANCE:
                for past_trade in past_trades.values():
                    if past_trade.quantity > _ROUNDING_TOLERANCE:  # Skip other sell orders.
                        closed_amount_past_trade = min(-trade_quantity_remaining, past_trade.quantity)
                        closed_amount_current_balance = min(-trade_quantity_remaining,
                                                            current_balance[trade.asset_code])
                        closed_amount = min(closed_amount_past_trade, closed_amount_current_balance)
                        current_balance[trade.asset_code] -= closed_amount
                        past_trade.quantity -= closed_amount
                        trade_quantity_remaining += closed_amount
                        matched_inventory.append(MatchedInventory(past_trade.asset_code,
                                                                  past_trade.date,
                                                                  past_trade.price,
                                                                  trade.date,
                                                                  trade.price,
                                                                  closed_amount))

                    # If balance back to zero then just add rest to inventory.
                    if abs(current_balance[trade.asset_code]) < _ROUNDING_TOLERANCE < abs(trade_quantity_remaining):
                        current_balance[trade.asset_code] += trade_quantity_remaining
                        trade.quantity = trade_quantity_remaining

                    if abs(trade_quantity_remaining) < _ROUNDING_TOLERANCE:
                        break
            else:  # Not long, so just add to inventory.
                current_balance[trade.asset_code] += trade_quantity_remaining

        # If trade not fully matched, then remainder gets added to inventory.
        if abs(trade_quantity_remaining) > _ROUNDING_TOLERANCE:
            past_trades[trade.date] = trade

        return matched_inventory

    def match_trades(self, trades: List[Trade]) -> List[MatchedInventory]:
        # Static method to help with sorting
        def get_date(t: Trade) -> datetime:
            return t.date

        sorted_trades = sorted(trades, key=get_date)
        matched_inventory: List[MatchedInventory] = []
        current_balance: CurrentBalance = CurrentBalance()  # str : float
        inventory: Inventory = Inventory()  # str : {datetime, float}

        for trade in sorted_trades:
            if trade.asset_code not in inventory:
                inventory[trade.asset_code] = OrderedDict()
            if len(inventory[trade.asset_code]) == 0:  # Simple case. No other trades, just add it to inventory.
                inventory[trade.asset_code][trade.date] = trade
                current_balance[trade.asset_code] = trade.quantity
            else:
                matched_inventory.extend(self._record_matches(current_balance, inventory[trade.asset_code], trade))
        return matched_inventory

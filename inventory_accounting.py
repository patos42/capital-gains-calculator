from typing import List, Final, Dict, TypeVar, Generic
from datetime import datetime
from model import *
from collections import OrderedDict

_ROUNDING_TOLERANCE = 1e-6

T = TypeVar('T', Trade, TranslatedTrade)

class CurrentBalance(Dict[str, float]):
    asset_code: str
    balance: float


# Records matched buy/sell trades.
class MatchedInventory(Generic[T]):
    def __init__(self,
                 buy_trade: T,
                 sell_trade: T,
                 quantity: float):
        self.buy_trade: Final[T] = buy_trade
        self.sell_trade: Final[T] = sell_trade
        self.quantity: Final = quantity
        if (buy_trade.quantity > 0 and sell_trade.quantity > 0) or (buy_trade.quantity < 0 and sell_trade.quantity < 0):
            raise ValueError("Sell trade quantity must be of opposite sign of buy trade.")
        if quantity > abs(buy_trade.quantity) or quantity > abs(sell_trade.quantity):
            raise ValueError("Matched quantity cannot be greater than buy or sell quantities.")


# Keeps track of quantity of trade that has been matched.
class TradePartialMatch(Generic[T]):
    def __init__(self, trade: T):
        self.trade: Final[T] = trade
        self.remaining_quantity = trade.quantity


class Inventory(Dict[str, OrderedDict[datetime, TradePartialMatch[T]]]):
    asset_code: str
    trades: OrderedDict[datetime, TradePartialMatch[T]]

# Note: Generally FX must be FIFO: http://classic.austlii.edu.au/au/legis/cth/consol_act/itaa1997240/s775.145.html

class FirstInFirstOutInventory(Generic[T]):
    def _record_matches(self,
                        current_balance: CurrentBalance,
                        past_trades: OrderedDict[datetime, TradePartialMatch[T]],
                        new_trade: TradePartialMatch[T]) -> List[MatchedInventory[T]]:
        matched_inventory: List[MatchedInventory[T]] = []
        trade_quantity_remaining = new_trade.remaining_quantity
        # If buy trade, check if short
        # ToDo: Collapse this and next if statement. Use negative quantity to signify closing shorts.
        if new_trade.remaining_quantity > _ROUNDING_TOLERANCE:
            if current_balance[new_trade.trade.asset_code] < -_ROUNDING_TOLERANCE:  # This is not necessary.
                for past_trade in past_trades.values():
                    if past_trade.remaining_quantity < -_ROUNDING_TOLERANCE:  # Skip other buy orders.
                        closed_amount_past_trade = min(trade_quantity_remaining, -past_trade.remaining_quantity)
                        closed_amount_current_balance = min(trade_quantity_remaining,
                                                            -current_balance[new_trade.trade.asset_code])
                        closed_amount = min(closed_amount_past_trade, closed_amount_current_balance)
                        current_balance[new_trade.trade.asset_code] += closed_amount
                        past_trade.remaining_quantity += closed_amount
                        trade_quantity_remaining -= closed_amount
                        matched_inventory.append(MatchedInventory(past_trade.trade,
                                                                  new_trade.trade,
                                                                  closed_amount))

                    # If balance back to zero then just add rest to inventory.
                    if abs(current_balance[new_trade.trade.asset_code]) < _ROUNDING_TOLERANCE < abs(
                            trade_quantity_remaining):
                        current_balance[new_trade.trade.asset_code] += trade_quantity_remaining
                        new_trade.remaining_quantity = trade_quantity_remaining

                    if abs(trade_quantity_remaining) < _ROUNDING_TOLERANCE:
                        break
            else:  # Not short, so just add to inventory.
                current_balance[new_trade.trade.asset_code] += trade_quantity_remaining
        if new_trade.remaining_quantity < -_ROUNDING_TOLERANCE:  # Sell trade. Check if long.
            trade_quantity_remaining = new_trade.remaining_quantity
            if current_balance[new_trade.trade.asset_code] > _ROUNDING_TOLERANCE:
                for past_trade in past_trades.values():
                    if past_trade.remaining_quantity > _ROUNDING_TOLERANCE:  # Skip other sell orders.
                        closed_amount_past_trade = min(-trade_quantity_remaining, past_trade.remaining_quantity)
                        closed_amount_current_balance = min(-trade_quantity_remaining,
                                                            current_balance[new_trade.trade.asset_code])
                        closed_amount = min(closed_amount_past_trade, closed_amount_current_balance)
                        current_balance[new_trade.trade.asset_code] -= closed_amount
                        past_trade.remaining_quantity -= closed_amount
                        trade_quantity_remaining += closed_amount
                        matched_inventory.append(MatchedInventory(past_trade.trade,
                                                                  new_trade.trade,
                                                                  closed_amount))

                    # If balance back to zero then just add rest to inventory.
                    if abs(current_balance[new_trade.trade.asset_code]) < _ROUNDING_TOLERANCE < abs(
                            trade_quantity_remaining):
                        current_balance[new_trade.trade.asset_code] += trade_quantity_remaining
                        new_trade.remaining_quantity = trade_quantity_remaining

                    if abs(trade_quantity_remaining) < _ROUNDING_TOLERANCE:
                        break
            else:  # Not long, so just add to inventory.
                current_balance[new_trade.trade.asset_code] += trade_quantity_remaining

        # If trade not fully matched, then remainder gets added to inventory.
        if abs(trade_quantity_remaining) > _ROUNDING_TOLERANCE:
            past_trades[new_trade.trade.date] = new_trade

        return matched_inventory

    def match_trades(self, trades: List[T]) -> List[MatchedInventory[T]]:
        # Static method to help with sorting
        def get_date(t: Trade) -> datetime:
            return t.date

        sorted_trades = sorted(trades, key=get_date)
        matched_inventory: List[MatchedInventory[T]] = []
        current_balance: CurrentBalance = CurrentBalance()  # str : float
        inventory: Inventory[T] = Inventory[T]()  # str : {datetime, TradePartialMatch}

        for trade in sorted_trades:
            if trade.asset_code not in inventory:
                inventory[trade.asset_code] = OrderedDict()
            if len(inventory[trade.asset_code]) == 0:  # Simple case. No other trades, just add it to inventory.
                inventory[trade.asset_code][trade.date] = TradePartialMatch(trade)
                current_balance[trade.asset_code] = trade.quantity
            else:
                matched_inventory.extend(
                    self._record_matches(current_balance, inventory[trade.asset_code], TradePartialMatch(trade)))

        for code in inventory:
            for date in inventory[code]:
                if abs(inventory[code][date].remaining_quantity) > _ROUNDING_TOLERANCE:
                    print('unmatched inventory: ' + str(inventory[code][date].trade.date) + ' ' + str(inventory[code][date].remaining_quantity))
        return matched_inventory

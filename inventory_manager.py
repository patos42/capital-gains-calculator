#from collections import OrderedDict
from typing import List
from model import *
import datetime

# class Inventory(TypedDict):
#     asset_code : str
#     trades : OrderedDict[datetime, Trade] = OrderedDict()

# Keeps track of inventory balances by asset and date.
class MutableInventoryManager:
    def __init__(self, initial_inventory : List[Trade]):
        inventory : Inventory = Inventory()
        for trade in initial_inventory:
            if trade.asset_code not in inventory:
                inventory[trade.asset_code] = OrderedDict()
            if trade.date in inventory[trade.trade.asset_code]: #Not sure how to handle this yet.
                raise ValueError("Trades cannot occur at exactly the same time. Duplicate time used.")
            inventory[trade.asset_code][trade.date] = trade
        self._inventory_flows : Inventory = inventory
        #self._inventory_to_match = Inventory(inventory)

    # Removes a closed trade from matched inventory.
    #def match_trade(self, trade : Trade):


    # Gets balance at date (inclusive).
    def get_balance(self, asset_code : str, date : datetime):
        flows : OrderedDict[datetime, Trade] = self._inventory_flows[asset_code]
        total_balance : float = 0
        for trade in flows.values():
            if trade.date > date:
                break
            total_balance += trade.quantity
        return total_balance
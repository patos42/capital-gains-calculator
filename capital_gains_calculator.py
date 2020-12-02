from abc import ABC, abstractmethod
from inventory_accounting_methods import MatchedInventory
from typing import Final
from datetime import datetime


class CapitalGainsTax:
    def __init__(self,
                 matched_inventory : MatchedInventory,
                 taxable_gain : float):
        self.matched_inventory : Final = matched_inventory
        self.taxable_gain : Final = taxable_gain


class CapitalGainsTaxMethod(ABC):
    @abstractmethod
    def calculate_taxable_gain(self, matched_inventory : MatchedInventory) -> CapitalGainsTax:
        ...


# Method per:
# https://www.ato.gov.au/general/capital-gains-tax/working-out-your-capital-gain-or-loss/working-out-your-capital-gain/the-discount-method-of-calculating-your-capital-gain/
class DiscountCapitalGainsTaxMethod(CapitalGainsTaxMethod):
    def calculate_taxable_gain(self, matched_inventory : MatchedInventory) -> CapitalGainsTax:
        taxable_gain: float
        sell_date : datetime = matched_inventory.buy_date
        test_date : datetime = datetime(sell_date.year + 1, sell_date.month, sell_date.day + 1) # 1 calendar year later. Starts day after purchase (see example below)
        if (matched_inventory.sell_date >= test_date):
            taxable_gain = (matched_inventory.sell_price - matched_inventory.buy_price) * matched_inventory.quantity / 2
        else:
            taxable_gain = (matched_inventory.sell_price - matched_inventory.buy_price) * matched_inventory.quantity
        return CapitalGainsTax(matched_inventory, taxable_gain)

# ToDo: Possible issue if there are existing negative capital gains - these should not be discounted and be
# netted against undiscounted amounts first before potentially discounting.

#Strange Day counting method: https://www.ato.gov.au/General/Capital-gains-tax/Working-out-your-capital-gain-or-loss/Working-out-your-capital-gain/
#Sally bought a CGT asset on 2 February. Her 12-month ownership period started on 3 February (the day after she bought the asset) and ends 365 days later (366 in a leap year), at the end of 2 February the following year.
#If Sally sells the asset before 3 February the following year, she can't claim the discount or use indexation because she hasn't owned the asset for at least 12 months.
from abc import ABC, abstractmethod
from inventory_accounting_methods import MatchedInventory
from typing import Final

class CapitalGainsTax:
    def __init__(self,
                 matched_inventory : MatchedInventory,
                 taxable_gain : float):
        self.matched_inventory : Final = matched_inventory
        self.taxable_gain : Final = taxable_gain


class CapitalGainsTaxMethod(ABC):
    @abstractmethod
    def calculate_taxable_gain(self, matched_inventory : MatchedInventory):
        ...


# Method per:
# https://www.ato.gov.au/general/capital-gains-tax/working-out-your-capital-gain-or-loss/working-out-your-capital-gain/the-discount-method-of-calculating-your-capital-gain/
class DiscountCapitalGainsTaxMethod(CapitalGainsTaxMethod):
    def calculate_taxable_gain(self, matched_inventory : MatchedInventory):
        taxable_gain: float
        if ((matched_inventory.sell_date - matched_inventory.buy_date).days >= 365.0):
            taxable_gain = (matched_inventory.sell_price - matched_inventory.buy_price) / 2.0
        else:
            taxable_gain = (matched_inventory.sell_price - matched_inventory.buy_price)
        return CapitalGainsTax(matched_inventory, taxable_gain)



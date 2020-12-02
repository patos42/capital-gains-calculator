import sys
from typing import List

from capital_gains_calculator import CapitalGainsTaxMethod, DiscountCapitalGainsTaxMethod, CapitalGainsTax
from file_reader import FileReader
from inventory_accounting_methods import FirstInFirstOutInventory, MatchedInventory
from model import Trade


def main() -> None:
    if (len(sys.argv) > 1):
        file_path = sys.argv[1]
    else:
        file_path = "./test_data/trades2.csv"
    file_reader: FileReader = FileReader()
    trades: List[Trade] = file_reader.read_trades(file_path)
    fifo_inventory_manager: FirstInFirstOutInventory = FirstInFirstOutInventory()
    matched_trades: List[MatchedInventory] = fifo_inventory_manager.match_trades(trades)
    capital_gains_calculator: CapitalGainsTaxMethod = DiscountCapitalGainsTaxMethod()
    gains: List[CapitalGainsTax] = []
    for match in matched_trades:
        gain: CapitalGainsTax = capital_gains_calculator.calculate_taxable_gain(match)
        gains.append(gain)
    file_reader.write_capital_gains("./test_data/gains.csv", gains)


if __name__ == "__main__":
    main()

import sys
from typing import List

from capital_gains_tax import DiscountCapitalGainsTaxMethod, CapitalGainsTax, CapitalGainsTaxAggregator
from read_writer import InteractiveBrokersReadWriter
from inventory_accounting import FirstInFirstOutInventory, MatchedInventory
from model import Trade


def main() -> None:
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        existing_capital_losses = float(sys.argv[2])
    else:
        file_path = "./test_data/trades2.csv"
        existing_capital_losses = 0
    file_reader: InteractiveBrokersReadWriter = InteractiveBrokersReadWriter()
    trades: List[Trade] = file_reader.read_trades(file_path)
    fifo_inventory_manager: FirstInFirstOutInventory = FirstInFirstOutInventory()
    matched_trades: List[MatchedInventory[Trade]] = fifo_inventory_manager.match_trades(trades)
    capital_gains_aggregator : CapitalGainsTaxAggregator = CapitalGainsTaxAggregator(DiscountCapitalGainsTaxMethod())
    #gains: List[CapitalGainsTax] = capital_gains_aggregator.calculate(existing_capital_losses, matched_trades)
    #file_reader.write_capital_gains("./test_data/gains.csv", gains)


if __name__ == "__main__":
    main()

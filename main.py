import sys
from typing import List

from capital_gains_tax import DiscountCapitalGainsTaxMethod, CapitalGainsTax, CapitalGainsTaxAggregator
from foreign_asset_translator import ForeignAssetTranslator
from read_writer import InteractiveBrokersReadWriter
from inventory_accounting import FirstInFirstOutInventory, MatchedInventory
from proceeds_calculator import ForeignCurrencyProceedsCalculator
from model import Trade, TaxableTrade


def main() -> None:
    if len(sys.argv) > 1:
        trade_file_path = sys.argv[1]
        existing_capital_losses = float(sys.argv[2])
    else:
        trade_file_path = "./test_data/trades2.csv"
        fx_rate_file_path = "./test_data/f11.1-data.csv"
        existing_capital_losses = 0
    file_reader: InteractiveBrokersReadWriter = InteractiveBrokersReadWriter()
    trades: List[Trade] = file_reader.read_trades(trade_file_path)
    rba_rates = file_reader.read_rba_rates(fx_rate_file_path)
    translator = ForeignAssetTranslator(rba_rates)
    foreign_currency_proceeds_calculator = ForeignCurrencyProceedsCalculator(FirstInFirstOutInventory[TaxableTrade]())
    taxable_trades = translator.convert_trades(trades)
    trades_with_fx_proceeds : List[TaxableTrade] = foreign_currency_proceeds_calculator.calculate_proceeds(taxable_trades)
    matched_trades: List[MatchedInventory[TaxableTrade]] = FirstInFirstOutInventory[TaxableTrade]().match_trades(trades_with_fx_proceeds)
    capital_gains_aggregator : CapitalGainsTaxAggregator = CapitalGainsTaxAggregator(DiscountCapitalGainsTaxMethod())
    gains: List[CapitalGainsTax] = capital_gains_aggregator.calculate(existing_capital_losses, matched_trades)
    file_reader.write_capital_gains("./test_data/gains.csv", gains)


if __name__ == "__main__":
    main()

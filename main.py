import sys
import fnmatch
import os
from typing import List

from capital_gains_tax import DiscountCapitalGainsTaxMethod, CapitalGainsTax, CapitalGainsTaxAggregator
from foreign_asset_translator import ForeignAssetTranslator
from read_writer import InteractiveBrokersReadWriter
from inventory_accounting import FirstInFirstOutInventory, MatchedInventory
from proceeds_calculator import ForeignCurrencyProceedsCalculator
from model import Trade, TranslatedTrade


def main() -> None:
    trade_file_path: List[str] = []
    fx_rate_file_path = "./test_data/f11.1-data.csv"
    if len(sys.argv) > 1:
        trade_file_path = [sys.argv[1]]
        existing_capital_losses = float(sys.argv[2])
    else:
        for file in os.listdir('./test_data/'):
            if fnmatch.fnmatch(file, 'test_trades_*.csv'):
                trade_file_path.append('./test_data/' + file)
        existing_capital_losses = 0
    file_reader: InteractiveBrokersReadWriter = InteractiveBrokersReadWriter()
    trades: List[Trade] = []
    for trade_file in trade_file_path:
        trades.extend(file_reader.read_trades(trade_file))

    rba_rates = file_reader.read_rba_rates(fx_rate_file_path)
    translator = ForeignAssetTranslator(rba_rates)
    foreign_currency_proceeds_calculator = ForeignCurrencyProceedsCalculator(FirstInFirstOutInventory[TranslatedTrade]())
    taxable_trades = translator.convert_trades(trades)
    trades_with_fx_proceeds : List[TranslatedTrade] = foreign_currency_proceeds_calculator.calculate_proceeds(taxable_trades)
    matched_trades: List[MatchedInventory[TranslatedTrade]] = FirstInFirstOutInventory[TranslatedTrade]().match_trades(trades_with_fx_proceeds)
    capital_gains_aggregator : CapitalGainsTaxAggregator = CapitalGainsTaxAggregator(DiscountCapitalGainsTaxMethod())
    gains: List[CapitalGainsTax] = capital_gains_aggregator.calculate(existing_capital_losses, matched_trades)
    file_reader.write_capital_gains("./test_data/gains.csv", gains)
    file_reader.write_trades("./test_data/processed_trades.csv", trades_with_fx_proceeds)

if __name__ == "__main__":
    main()

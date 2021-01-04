import csv
from typing import List, Dict
from model import Trade
from capital_gains_tax import CapitalGainsTax
from abc import ABC, abstractmethod
from datetime import datetime


class ReadWriter(ABC):
    @abstractmethod
    def read_trades(self, file_path: str) -> List[Trade]:
        ...
    # Source from page: https://rba.gov.au/statistics/historical-data.html#exchange-rates
    # Or directly here: https://rba.gov.au/statistics/tables/csv/f11.1-data.csv
    # Returns rates in the form ccy.AUD.
    def read_rba_rates(self, file_path: str) -> Dict[str,Dict[datetime, float]]:
        results : Dict[str,Dict[datetime, float]] = dict()
        with open(file_path, newline='') as csvfile:
            # Skip multiple header rows.
            for i in range(5):
                csvfile.readline()
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                date : datetime
                try:
                    # Strangely formatted CSV does not have date header. Ends up being 'Units'.
                    date = datetime.strptime(row["Units"], '%d-%b-%Y')
                except ValueError:
                    continue
                for column in row:
                    if column != 'Index' and column != 'Units' and column != '':
                        rate_code = column + '.AUD'
                        if rate_code not in results.keys():
                            results[rate_code] = dict()
                        if row[column] != '':
                            results[rate_code][date] = 1/float(row[column]) # Convention in file is AUD.ccy - need to swap.
        return results

    def write_capital_gains(self, file_path: str, gains: List[CapitalGainsTax]) -> None:
        with open(file_path, mode='w') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            header: List[str] = ['asset_code', 'buy_price', 'buy_date', 'sell_price', 'sell_date', 'quantity',
                                 'taxable_gain', 'carried_capital_losses', 'buy_commission', 'sell_commission']
            writer.writerow(header)
            for gain in gains:
                row: List[str] = [gain.matched_inventory.buy_trade.asset_code,
                                  str(gain.matched_inventory.buy_trade.price),
                                  str(gain.matched_inventory.buy_trade.date),
                                  str(gain.matched_inventory.sell_trade.price),
                                  str(gain.matched_inventory.sell_trade.date),
                                  str(gain.matched_inventory.quantity),
                                  str(gain.taxable_gain),
                                  str(gain.carried_capital_losses),
                                  str(gain.buy_commission),
                                  str(gain.sell_commission)]
                writer.writerow(row)


class InteractiveBrokersReadWriter(ReadWriter):
    def read_trades(self, file_path: str) -> List[Trade]:  # ToDo: Created SortedList class.
        trades = []
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                if row["DataDiscriminator"] == "Order":
                    # print(row)
                    date_time = datetime.strptime(row["Date/Time"],
                                                           '%Y-%m-%d, %H:%M:%S')  # 2019-07-01, 14:48:19
                    price: float = float(row["T. Price"].replace(",", ""))
                    quantity: float = float(row["Quantity"].replace(",", ""))
                    proceeds: float = float(row["Proceeds"].replace(",", ""))
                    commission: float = float(row["Comm in AUD"].replace(",", ""))
                    asset_category: str = str(row["Asset Category"])
                    symbol: str = str(row["Symbol"])
                    currency: str = str(row["Currency"])

                    # Fix strange Interactive Brokers convention of setting AUD as quanity and USD amount as proceeds.
                    # Possibly a result of indirect quoting. Swapping quantity/proceeds and AUD.USD to USD.AUD.
                    if asset_category == "Forex":
                        if symbol == "AUD.USD":
                            trades.append(Trade(symbol,
                                                date_time,
                                                1 / price,  # NB: converted to USD.AUD.
                                                # This is a bit of a hack as there should be a conversion class to
                                                # handle this. Keep as market convention quote, convert all floats to
                                                # Amounts which contain Currency and have a translater divide or
                                                # multiply as required to convert.
                                                "AUD", # Hack: Report seems to use USD?
                                                proceeds,
                                                commission))
                        else:
                            raise NotImplementedError(
                                "Only AUD.USD currency trades implemented as I am unsure how IB treats other currencies.")
                    else:
                        trades.append(Trade(symbol,
                                            date_time,
                                            price,
                                            currency,
                                            quantity,
                                            commission))

        return trades

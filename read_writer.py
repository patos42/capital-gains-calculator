import csv
from typing import List, Dict
from model import Trade, Amount, TaxableTrade
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

    def write_trades(self, file_path : str, trades: List[TaxableTrade]) -> None:
        with open(file_path, mode='w') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            with open(file_path, mode='w') as file:
                header: List[str] = ['asset_code', 'date', 'price', 'currency', 'quantity', 'commission.value',
                                     'commission.currency', 'aud_price', 'exchange_rate', 'aud_commission']
                writer.writerow(header)
                for trade in trades:
                    row: List[str] = [trade.asset_code,
                                      str(trade.date),
                                      str(trade.price),
                                      str(trade.currency),
                                      str(trade.quantity),
                                      str(trade.commission.value),
                                      str(trade.commission.currency),
                                      str(trade.aud_price),
                                      str(trade.exchange_rate),
                                      str(trade.aud_commission)]
                    writer.writerow(row)

class InteractiveBrokersReadWriter(ReadWriter):
    def read_trades(self, file_path: str) -> List[Trade]:  # ToDo: Created SortedList class.
        trades = []
        with open(file_path, newline='') as csv_file:

            # Cannot use built in csv due to strange formatting by IB.
            # There will be multiple tables in a given csv with different headers.
            #reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            for cells in reader:
                if cells[0] != 'Trades':
                    continue
                if cells[1] == 'Header':
                    header = list(cells)
                    continue
                if cells[2] != 'Order':
                    continue
                row: Dict[str, str] = dict(zip(header, cells))
                if row['Asset Category'] == 'Forex':
                    trades.append(self._process_forex(row))
                else:
                    trades.append(self._process_trade(row))
        return trades

    def _process_trade(self, row : Dict[str, str]) -> Trade:
        date_time = datetime.strptime(row["Date/Time"],
                                      '%Y-%m-%d, %H:%M:%S')  # 2019-07-01, 14:48:19
        #price: float = float(row["T. Price"].replace(",", "")) # Cannot use as contracts might have multipliers.
        quantity: float = float(row["Quantity"].replace(",", ""))
        proceeds: float = float(row["Notional Value"].replace(",", ""))
        commission: float = float(row["Comm/Fee"].replace(",", ""))
        symbol: str = str(row["Symbol"])
        currency: str = str(row["Currency"])
        effective_price = abs(proceeds / quantity)
        return Trade(symbol,
                     date_time,
                     effective_price,
                     currency,
                     quantity,
                     Amount(commission, currency))

    def _process_forex(self, row : Dict[str, str]) ->Trade:
        date_time = datetime.strptime(row["Date/Time"],
                                      '%Y-%m-%d, %H:%M:%S')  # 2019-07-01, 14:48:19
        price: float = float(row["T. Price"].replace(",", ""))
        quantity: float = float(row["Quantity"].replace(",", ""))
        proceeds: float = float(row["Proceeds"].replace(",", ""))
        commission: float = float(row["Comm in AUD"].replace(",", ""))
        symbol: str = str(row["Symbol"])
        currency: str = str(row["Currency"])

        # Fix strange Interactive Brokers convention of setting AUD as quanity and USD amount as proceeds.
        # Possibly a result of indirect quoting. Swapping quantity/proceeds and AUD.USD to USD.AUD.
        if symbol == "AUD.USD":
            return Trade("USD.AUD",
                                date_time,
                                1 / price,  # NB: converted to USD.AUD.
                                # This is a bit of a hack as there should be a conversion class to
                                # handle this. Keep as market convention quote, convert all floats to
                                # Amounts which contain Currency and have a translater divide or
                                # multiply as required to convert.
                                "AUD",  # Hack: Report seems to use USD?
                                proceeds,
                                Amount(commission, "AUD"))
        else:
            raise NotImplementedError(
                "Only AUD.USD currency trades implemented as I am unsure how IB treats other currencies.")

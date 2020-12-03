import csv
import datetime
from typing import List
from model import Trade
from capital_gains_tax import CapitalGainsTax
from abc import ABC, abstractmethod


class ReadWriter(ABC):
    @abstractmethod
    def read_trades(self, file_pat: str) -> List[Trade]:
        ...

    def write_capital_gains(self, file_path: str, gains: List[CapitalGainsTax]) -> None:
        with open(file_path, mode='w') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            header: List[str] = ['asset_code', 'buy_price', 'buy_date', 'sell_price', 'sell_date', 'quantity',
                                 'taxable_gain', 'carried_capital_losses']
            writer.writerow(header)
            for gain in gains:
                row: List[str] = [gain.matched_inventory.asset_code,
                                  str(gain.matched_inventory.buy_price),
                                  str(gain.matched_inventory.buy_date),
                                  str(gain.matched_inventory.sell_price),
                                  str(gain.matched_inventory.sell_date),
                                  str(gain.matched_inventory.quantity),
                                  str(gain.taxable_gain),
                                  str(gain.carried_capital_losses)]
                writer.writerow(row)


class InteractiveBrokersReadWriter(ReadWriter):
    def read_trades(self, file_path: str) -> List[Trade]:  # ToDo: Created SortedList class.
        trades = []
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                if row["DataDiscriminator"] == "Order":
                    # print(row)
                    date_time = datetime.datetime.strptime(row["Date/Time"],
                                                           '%Y-%m-%d, %H:%M:%S')  # 2019-07-01, 14:48:19
                    price: float = float(row["T. Price"].replace(",", ""))
                    quantity: float = float(row["Quantity"].replace(",", ""))
                    proceeds: float = float(row["Proceeds"].replace(",", ""))
                    commission: float = float(row["Comm in AUD"].replace(",", ""))
                    asset_category: str = str(row["Asset Category"])
                    symbol: str = row["Symbol"]

                    # Fix strange Interactive Brokers convention of setting AUD as quanity and USD amount as proceeds.
                    # Possibly a result of indirect quoting. Swapping quantity/proceeds and changing indirect quote
                    # to a direct one.
                    if asset_category == "Forex":
                        if symbol == "AUD.USD":
                            trades.append(Trade(symbol,
                                                date_time,
                                                1 / price,  # NB: converted to direct quote.
                                                proceeds,
                                                commission))
                        else:
                            raise NotImplementedError(
                                "Only AUD.USD currency trades implemented as I am unsure how IB treats other currencies.")
                    else:
                        trades.append(Trade(symbol,
                                            date_time,
                                            price,
                                            quantity,
                                            commission))
                    # print(date_time)
                    # print(row["Date/Time"])

        return trades

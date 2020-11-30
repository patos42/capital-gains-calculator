import csv
import datetime
from typing import List
from model import Trade
from capital_gains_calculator import CapitalGainsTax

class FileReader:
    def read_trades(self, file_path: str) -> List[Trade]:  # ToDo: Created SortedList class.
        trades = []
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                if (row["DataDiscriminator"] == "Order"):
                    # print(row)
                    date_time = datetime.datetime.strptime(row["Date/Time"],
                                                           '%Y-%m-%d, %H:%M:%S')  # 2019-07-01, 14:48:19
                    price: float = float(row["T. Price"].replace(",",""))
                    quantity: float = float(row["Quantity"].replace(",",""))
                    # print(date_time)
                    # print(row["Date/Time"])
                    trades.append(Trade(row["Symbol"],
                                        date_time,
                                        price,
                                        quantity))
        return trades

    def write_capital_gains(self, file_path: str, gains: List[CapitalGainsTax]):
        with open(file_path, mode='w') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['asset_code', 'buy_price','buy_date','sell_price','sell_date','quantity','taxable_gain'])
            for gain in gains:
                writer.writerow([gain.matched_inventory.asset_code,
                                 gain.matched_inventory.buy_price,
                                 gain.matched_inventory.buy_date,
                                 gain.matched_inventory.sell_price,
                                 gain.matched_inventory.sell_date,
                                 gain.matched_inventory.quantity,
                                 gain.taxable_gain])


        # Read CSV
        # Convert to trade class

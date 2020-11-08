import csv
import datetime
from typing import List
from model import Trade


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

        # Read CSV
        # Convert to trade class

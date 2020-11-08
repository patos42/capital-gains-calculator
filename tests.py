from unittest import TestCase
from file_reader import FileReader
from typing import List
from model import *
from inventory_accounting_methods import *

class TestFileReader(TestCase):
    def test_read_file(self):
        fileReader = FileReader()
        fileReader.read_trades("./test_data/trades.csv")


class FifoInventoryTests(TestCase):
    def test_basic(self):
        trades : List[Trade] = []
        trades.append(Trade("BHP", datetime.datetime(2020, 1, 1), 10, 32))
        trades.append(Trade("BHP", datetime.datetime(2020, 2, 1), 10, -32))

        fifo_inventory_manager : FirstInFirstOutInventory = FirstInFirstOutInventory()
        matched_trades : List[MatchedInventory] = fifo_inventory_manager.match_trades(trades)
        for tax_event in matched_trades:
            print("Stock:" + tax_event.asset_code
                  + " Bought price: "  + str(tax_event.buy_price)
                  + " Sold price: " + str(tax_event.sell_price)
                  + " Quantity: " + str(tax_event.quantity)
                  + " Years: " + str((tax_event.sell_date - tax_event.buy_date).days/365))

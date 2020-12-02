import random
from unittest import TestCase
from file_reader import FileReader
from inventory_accounting_methods import *
from capital_gains_calculator import *
from typing import List, Literal
from model import *
from datetime import datetime

class TestFileReader(TestCase):
    def test_read_file(self) -> None:
        file_reader = FileReader()
        file_reader.read_trades("./test_data/trades.csv")


class FifoInventoryTests(TestCase):
    def test_basic(self) -> None:
        trades: List[Trade] = []
        trades.append(Trade("BHP", datetime(2020, 1, 1), 10, 32, 0))
        trades.append(Trade("BHP", datetime(2020, 2, 1), 10, -32, 0))

        fifo_inventory_manager: FirstInFirstOutInventory = FirstInFirstOutInventory()
        matched_trades: List[MatchedInventory] = fifo_inventory_manager.match_trades(trades)

        expected_result: List[MatchedInventory] = [
            MatchedInventory("BHP", datetime(2020, 1, 1), 10, datetime(2020, 2, 1), 10, 32)]

        for i, tax_event in enumerate(matched_trades):
            self.assertEqual(tax_event.asset_code, expected_result[i].asset_code)
            self.assertEqual(tax_event.buy_price, expected_result[i].buy_price)
            self.assertEqual(tax_event.sell_price, expected_result[i].sell_price)
            self.assertEqual(tax_event.quantity, expected_result[i].quantity)
            self.assertEqual((tax_event.sell_date - tax_event.buy_date).days,
                             (expected_result[i].sell_date - expected_result[i].buy_date).days)
            print("Stock:" + tax_event.asset_code
                  + " Bought price: " + str(tax_event.buy_price)
                  + " Bought Date: " + str(tax_event.buy_date)
                  + " Sold price: " + str(tax_event.sell_price)
                  + " Sold Date: " + str(tax_event.sell_date)
                  + " Quantity: " + str(tax_event.quantity)
                  + " Days: " + str((tax_event.sell_date - tax_event.buy_date).days))

    def test_sold_in_two(self) -> None:
        trades: List[Trade] = []
        trades.append(Trade("BHP", datetime(2020, 1, 1), 10, 32, 0))
        trades.append(Trade("BHP", datetime(2020, 2, 1), 11, -16, 0))
        trades.append(Trade("BHP", datetime(2020, 3, 1), 12, -16, 0))

        fifo_inventory_manager: FirstInFirstOutInventory = FirstInFirstOutInventory()
        matched_trades: List[MatchedInventory] = fifo_inventory_manager.match_trades(trades)
        expected_result: List[MatchedInventory] = [
            MatchedInventory("BHP", datetime(2020, 1, 1), 10, datetime(2020, 2, 1), 11, 16),
            MatchedInventory("BHP", datetime(2020, 1, 1), 10, datetime(2020, 3, 1), 12, 16)]

        for i, tax_event in enumerate(matched_trades):
            self.assertEqual(tax_event.asset_code, expected_result[i].asset_code)
            self.assertEqual(tax_event.buy_price, expected_result[i].buy_price)
            self.assertEqual(tax_event.sell_price, expected_result[i].sell_price)
            self.assertEqual(tax_event.quantity, expected_result[i].quantity)
            self.assertEqual((tax_event.sell_date - tax_event.buy_date).days,
                             (expected_result[i].sell_date - expected_result[i].buy_date).days)
            print("Stock:" + tax_event.asset_code
                  + " Bought price: " + str(tax_event.buy_price)
                  + " Bought Date: " + str(tax_event.buy_date)
                  + " Sold price: " + str(tax_event.sell_price)
                  + " Sold Date: " + str(tax_event.sell_date)
                  + " Quantity: " + str(tax_event.quantity)
                  + " Days: " + str((tax_event.sell_date - tax_event.buy_date).days))

    def test_bought_in_two(self) -> None:
        trades: List[Trade] = []
        trades.append(Trade("BHP", datetime(2020, 1, 1), 10, -32, 0))
        trades.append(Trade("BHP", datetime(2020, 2, 1), 20, 16, 0))
        trades.append(Trade("BHP", datetime(2020, 3, 1), 20, 16, 0))

        fifo_inventory_manager: FirstInFirstOutInventory = FirstInFirstOutInventory()
        matched_trades: List[MatchedInventory] = fifo_inventory_manager.match_trades(trades)
        expected_result: List[MatchedInventory] = [
            MatchedInventory("BHP", datetime(2020, 1, 1), 10, datetime(2020, 2, 1), 20, 16),
            MatchedInventory("BHP", datetime(2020, 1, 1), 10, datetime(2020, 3, 1), 20, 16)]

        for i, tax_event in enumerate(matched_trades):
            self.assertEqual(tax_event.asset_code, expected_result[i].asset_code)
            self.assertEqual(tax_event.buy_price, expected_result[i].buy_price)
            self.assertEqual(tax_event.sell_price, expected_result[i].sell_price)
            self.assertEqual(tax_event.quantity, expected_result[i].quantity)
            self.assertEqual((tax_event.sell_date - tax_event.buy_date).days,
                             (expected_result[i].sell_date - expected_result[i].buy_date).days)
            print("Stock:" + tax_event.asset_code
                  + " Bought price: " + str(tax_event.buy_price)
                  + " Bought Date: " + str(tax_event.buy_date)
                  + " Sold price: " + str(tax_event.sell_price)
                  + " Sold Date: " + str(tax_event.sell_date)
                  + " Quantity: " + str(tax_event.quantity)
                  + " Days: " + str((tax_event.sell_date - tax_event.buy_date).days))

    def test_bought_in_two_sold_in_one(self) -> None:
        trades: List[Trade] = []
        trades.append(Trade("BHP", datetime(2020, 1, 1), 10, 16, 0))
        trades.append(Trade("BHP", datetime(2020, 2, 1), 10, 16, 0))
        trades.append(Trade("BHP", datetime(2020, 3, 1), 10, -32, 0))

        fifo_inventory_manager: FirstInFirstOutInventory = FirstInFirstOutInventory()
        matched_trades: List[MatchedInventory] = fifo_inventory_manager.match_trades(trades)
        expected_result: List[MatchedInventory] = [
            MatchedInventory("BHP", datetime(2020, 1, 1), 10, datetime(2020, 3, 1), 10, 16),
            MatchedInventory("BHP", datetime(2020, 2, 1), 10, datetime(2020, 3, 1), 10, 16)]

        for i, tax_event in enumerate(matched_trades):
            self.assertEqual(tax_event.asset_code, expected_result[i].asset_code)
            self.assertEqual(tax_event.buy_price, expected_result[i].buy_price)
            self.assertEqual(tax_event.sell_price, expected_result[i].sell_price)
            self.assertEqual(tax_event.quantity, expected_result[i].quantity)
            self.assertEqual((tax_event.sell_date - tax_event.buy_date).days,
                             (expected_result[i].sell_date - expected_result[i].buy_date).days)
            print("Stock:" + tax_event.asset_code
                  + " Bought price: " + str(tax_event.buy_price)
                  + " Bought Date: " + str(tax_event.buy_date)
                  + " Sold price: " + str(tax_event.sell_price)
                  + " Sold Date: " + str(tax_event.sell_date)
                  + " Quantity: " + str(tax_event.quantity)
                  + " Days: " + str((tax_event.sell_date - tax_event.buy_date).days))

    def test_complex_profile(self) -> None:
        trades: List[Trade] = []
        trades.append(Trade("BHP", datetime(2020, 1, 1), 10, 12, 0))
        trades.append(Trade("BHP", datetime(2020, 1, 2), 11, 12, 0))  # Inventory: 24
        trades.append(Trade("BHP", datetime(2020, 1, 3), 12,
                            -14, 0))  # Inventory 10, 12 Sold @ base cost $10, 2 Sold @ $11.
        trades.append(Trade("BHP", datetime(2020, 1, 4), 13, -12, 0))  # Inventory -2; 10 sold @ base cost $11.
        trades.append(
            Trade("BHP", datetime(2020, 1, 5), 14, 10, 0))  # Inventory 8; 2 bought/closed @ base cost $13
        random.shuffle(trades)

        fifo_inventory_manager: FirstInFirstOutInventory = FirstInFirstOutInventory()
        matched_trades: List[MatchedInventory] = fifo_inventory_manager.match_trades(trades)
        expected_result: List[MatchedInventory] = [
            MatchedInventory("BHP", datetime(2020, 1, 1), 10, datetime(2020, 1, 3), 12, 12),
            MatchedInventory("BHP", datetime(2020, 1, 2), 11, datetime(2020, 1, 3), 12, 2),
            MatchedInventory("BHP", datetime(2020, 1, 2), 11, datetime(2020, 1, 4), 13, 10),
            MatchedInventory("BHP", datetime(2020, 1, 4), 13, datetime(2020, 1, 5), 14, 2)]

        for i, tax_event in enumerate(matched_trades):
            self.assertEqual(tax_event.asset_code, expected_result[i].asset_code)
            self.assertEqual(tax_event.buy_price, expected_result[i].buy_price)
            self.assertEqual(tax_event.sell_price, expected_result[i].sell_price)
            self.assertEqual(tax_event.quantity, expected_result[i].quantity)
            self.assertEqual((tax_event.sell_date - tax_event.buy_date).days,
                             (expected_result[i].sell_date - expected_result[i].buy_date).days)
            print("Stock:" + tax_event.asset_code
                  + " Bought price: " + str(tax_event.buy_price)
                  + " Bought Date: " + str(tax_event.buy_date)
                  + " Sold price: " + str(tax_event.sell_price)
                  + " Sold Date: " + str(tax_event.sell_date)
                  + " Quantity: " + str(tax_event.quantity)
                  + " Days: " + str((tax_event.sell_date - tax_event.buy_date).days))


class CapitalGainsTaxTests(TestCase):
    def test_capital_gains(self) -> None:
        inventory_discountable = MatchedInventory("BHP", datetime(2019, 1, 1), 10,
                                                  datetime(2020, 1, 3), 12, 12)
        inventory_not_discountable = MatchedInventory("BHP", datetime(2020, 1, 1), 10,
                                                      datetime(2020, 1, 3), 12, 12)
        cgtCalculator: CapitalGainsTaxMethod = DiscountCapitalGainsTaxMethod()
        self.assertEqual(cgtCalculator.calculate_taxable_gain(inventory_discountable).taxable_gain, 1.0)
        self.assertEqual(cgtCalculator.calculate_taxable_gain(inventory_not_discountable).taxable_gain, 2.0)

    def test_fx_capital_gains(self) -> None:
        inventory_discountable = MatchedInventory("AUD.USD", datetime(2019, 1, 1), 1,
                                                  datetime(2020, 1, 3), 0.5, 100)
        inventory_not_discountable = MatchedInventory("AUD.USD", datetime(2020, 1, 1), 0.5,
                                                          datetime(2020, 1, 3), 1, 100)
        cgtCalculator: CapitalGainsTaxMethod = DiscountCapitalGainsTaxMethod()
        self.assertEqual(cgtCalculator.calculate_taxable_gain(inventory_discountable).taxable_gain, 50)
        self.assertEqual(cgtCalculator.calculate_taxable_gain(inventory_not_discountable).taxable_gain, -25)

class IntegrationTests(TestCase):
    def test_run_test_file(self) -> None:
        fileReader = FileReader()
        trades: List[Trade] = fileReader.read_trades("./test_data/trades2.csv")
        fifo_inventory_manager: FirstInFirstOutInventory = FirstInFirstOutInventory()
        matched_trades: List[MatchedInventory] = fifo_inventory_manager.match_trades(trades)
        for tax_event in matched_trades:
            print("Stock:" + tax_event.asset_code
                  + " Bought price: " + str(tax_event.buy_price)
                  + " Bought Date: " + str(tax_event.buy_date)
                  + " Sold price: " + str(tax_event.sell_price)
                  + " Sold Date: " + str(tax_event.sell_date)
                  + " Quantity: " + str(tax_event.quantity)
                  + " Days: " + str((tax_event.sell_date - tax_event.buy_date).days))

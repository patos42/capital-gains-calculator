import random
from unittest import TestCase
from read_writer import InteractiveBrokersReadWriter
from inventory_accounting import *
from capital_gains_tax import *
from typing import List
from model import *
from datetime import datetime


#--no-incremental


class TestFileReader(TestCase):
    def test_read_file(self) -> None:
        file_reader = InteractiveBrokersReadWriter()
        file_reader.read_trades("./test_data/trades.csv")

    def test_read_rba_file(self) -> None:
        file_reader = InteractiveBrokersReadWriter()
        file_reader.read_rba_rates("./test_data/f11.1-data.csv")


class FifoInventoryTests(TestCase):
    def test_basic(self) -> None:
        trades: List[Trade] = []
        trades.append(Trade("BHP", 'FUTURES', datetime(2020, 1, 1), 10, "AUD", 32, Amount(0, "AUD"), 'TEST'))
        trades.append(Trade("BHP", 'FUTURES', datetime(2020, 2, 1), 10, "AUD", -32, Amount(0, "AUD"), 'TEST'))

        fifo_inventory_manager: FirstInFirstOutInventory[Trade] = FirstInFirstOutInventory[Trade]()
        matched_trades: List[MatchedInventory[Trade]] = fifo_inventory_manager.match_trades(trades)

        expected_result: List[MatchedInventory[Trade]] = [
            MatchedInventory(trades[0], trades[1], 32)]

        for i, tax_event in enumerate(matched_trades):
            self.assertEqual(tax_event.buy_trade.asset_code, expected_result[i].buy_trade.asset_code)
            self.assertEqual(tax_event.buy_trade.price, expected_result[i].buy_trade.price)
            self.assertEqual(tax_event.sell_trade.price, expected_result[i].sell_trade.price)
            self.assertEqual(tax_event.quantity, expected_result[i].quantity)
            self.assertEqual((tax_event.sell_trade.date - tax_event.buy_trade.date).days,
                             (expected_result[i].sell_trade.date - expected_result[i].buy_trade.date).days)
            print("Stock:" + tax_event.buy_trade.asset_code
                  + " Bought price: " + str(tax_event.buy_trade.price)
                  + " Bought Date: " + str(tax_event.buy_trade.date)
                  + " Sold price: " + str(tax_event.sell_trade.price)
                  + " Sold Date: " + str(tax_event.sell_trade.date)
                  + " Quantity: " + str(tax_event.quantity)
                  + " Days: " + str((tax_event.sell_trade.date - tax_event.buy_trade.date).days))

    def test_sold_in_two(self) -> None:
        trades: List[Trade] = []
        trades.append(Trade("BHP", 'FUTURES', datetime(2020, 1, 1), 10, "AUD", 32, Amount(0, "AUD"), 'TEST'))
        trades.append(Trade("BHP", 'FUTURES', datetime(2020, 2, 1), 11, "AUD", -16, Amount(0, "AUD"), 'TEST'))
        trades.append(Trade("BHP", 'FUTURES', datetime(2020, 3, 1), 12, "AUD", -16, Amount(0, "AUD"), 'TEST'))

        fifo_inventory_manager: FirstInFirstOutInventory[Trade] = FirstInFirstOutInventory[Trade]()
        matched_trades: List[MatchedInventory[Trade]] = fifo_inventory_manager.match_trades(trades)
        expected_result: List[MatchedInventory[Trade]] = [
            MatchedInventory(trades[0], trades[1], 16),
            MatchedInventory(trades[0], trades[2], 16)]

        for i, tax_event in enumerate(matched_trades):
            self.assertEqual(tax_event.buy_trade.asset_code, expected_result[i].buy_trade.asset_code)
            self.assertEqual(tax_event.buy_trade.price, expected_result[i].buy_trade.price)
            self.assertEqual(tax_event.sell_trade.price, expected_result[i].sell_trade.price)
            self.assertEqual(tax_event.quantity, expected_result[i].quantity)
            self.assertEqual((tax_event.sell_trade.date - tax_event.buy_trade.date).days,
                             (expected_result[i].sell_trade.date - expected_result[i].buy_trade.date).days)
            print("Stock:" + tax_event.buy_trade.asset_code
                  + " Bought price: " + str(tax_event.buy_trade.price)
                  + " Bought Date: " + str(tax_event.buy_trade.date)
                  + " Sold price: " + str(tax_event.sell_trade.price)
                  + " Sold Date: " + str(tax_event.sell_trade.date)
                  + " Quantity: " + str(tax_event.quantity)
                  + " Days: " + str((tax_event.sell_trade.date - tax_event.buy_trade.date).days))

    def test_bought_in_two(self) -> None:
        trades: List[Trade] = []
        trades.append(Trade("BHP", 'FUTURES', datetime(2020, 1, 1), 10, "AUD", -32, Amount(0, "AUD"), 'Test'))
        trades.append(Trade("BHP", 'FUTURES', datetime(2020, 2, 1), 20, "AUD", 16, Amount(0, "AUD"), 'Test'))
        trades.append(Trade("BHP", 'FUTURES', datetime(2020, 3, 1), 20, "AUD", 16, Amount(0, "AUD"), 'Test'))

        fifo_inventory_manager: FirstInFirstOutInventory[Trade] = FirstInFirstOutInventory[Trade]()
        matched_trades: List[MatchedInventory[Trade]] = fifo_inventory_manager.match_trades(trades)
        expected_result: List[MatchedInventory[Trade]] = [
            MatchedInventory(trades[0], trades[1], 16),
            MatchedInventory(trades[0], trades[2], 16)]

        for i, tax_event in enumerate(matched_trades):
            self.assertEqual(tax_event.buy_trade.asset_code, expected_result[i].buy_trade.asset_code)
            self.assertEqual(tax_event.buy_trade.price, expected_result[i].buy_trade.price)
            self.assertEqual(tax_event.sell_trade.price, expected_result[i].sell_trade.price)
            self.assertEqual(tax_event.quantity, expected_result[i].quantity)
            self.assertEqual((tax_event.sell_trade.date - tax_event.buy_trade.date).days,
                             (expected_result[i].sell_trade.date - expected_result[i].buy_trade.date).days)
            print("Stock:" + tax_event.buy_trade.asset_code
                  + " Bought price: " + str(tax_event.buy_trade.price)
                  + " Bought Date: " + str(tax_event.buy_trade.date)
                  + " Sold price: " + str(tax_event.sell_trade.price)
                  + " Sold Date: " + str(tax_event.sell_trade.date)
                  + " Quantity: " + str(tax_event.quantity)
                  + " Days: " + str((tax_event.sell_trade.date - tax_event.buy_trade.date).days))

    def test_bought_in_two_sold_in_one(self) -> None:
        trades: List[Trade] = []
        trades.append(Trade("BHP", 'FUTURES', datetime(2020, 1, 1), 10, "AUD", 16, Amount(0, "AUD"), 'Test'))
        trades.append(Trade("BHP", 'FUTURES', datetime(2020, 2, 1), 10, "AUD", 16, Amount(0, "AUD"), 'Test'))
        trades.append(Trade("BHP", 'FUTURES', datetime(2020, 3, 1), 10, "AUD", -32, Amount(0, "AUD"), 'Test'))

        fifo_inventory_manager: FirstInFirstOutInventory[Trade] = FirstInFirstOutInventory[Trade]()
        matched_trades: List[MatchedInventory[Trade]] = fifo_inventory_manager.match_trades(trades)
        expected_result: List[MatchedInventory[Trade]] = [
            MatchedInventory(trades[0], trades[2], 16),
            MatchedInventory(trades[1], trades[2], 16)]

        for i, tax_event in enumerate(matched_trades):
            self.assertEqual(tax_event.buy_trade.asset_code, expected_result[i].buy_trade.asset_code)
            self.assertEqual(tax_event.buy_trade.price, expected_result[i].buy_trade.price)
            self.assertEqual(tax_event.sell_trade.price, expected_result[i].sell_trade.price)
            self.assertEqual(tax_event.quantity, expected_result[i].quantity)
            self.assertEqual((tax_event.sell_trade.date - tax_event.buy_trade.date).days,
                             (expected_result[i].sell_trade.date - expected_result[i].buy_trade.date).days)
            print("Stock:" + tax_event.buy_trade.asset_code
                  + " Bought price: " + str(tax_event.buy_trade.price)
                  + " Bought Date: " + str(tax_event.buy_trade.date)
                  + " Sold price: " + str(tax_event.sell_trade.price)
                  + " Sold Date: " + str(tax_event.sell_trade.date)
                  + " Quantity: " + str(tax_event.quantity)
                  + " Days: " + str((tax_event.sell_trade.date - tax_event.buy_trade.date).days))

    def test_complex_profile(self) -> None:
        trades: List[Trade] = []
        trades.append(Trade("BHP", 'FUTURES', datetime(2020, 1, 1), 10, "AUD", 12, Amount(0, "AUD"), 'Test'))
        trades.append(Trade("BHP", 'FUTURES', datetime(2020, 1, 2), 11, "AUD", 12, Amount(0, "AUD"), 'Test'))  # Inventory: 24
        trades.append(Trade("BHP", 'FUTURES', datetime(2020, 1, 3), 12,
                            "AUD", -14, Amount(0, "AUD"), 'Test'))  # Inventory 10, 12 Sold @ base cost $10, 2 Sold @ $11.
        trades.append(Trade("BHP", 'FUTURES', datetime(2020, 1, 4), 13, "AUD", -12, Amount(0, "AUD"), 'Test'))  # Inventory -2; 10 sold @ base cost $11.
        trades.append(
            Trade("BHP", 'FUTURES', datetime(2020, 1, 5), 14, "AUD", 10, Amount(0, "AUD"), 'Test'))  # Inventory 8; 2 bought/closed @ base cost $13
        expected_result: List[MatchedInventory[Trade]] = [
            MatchedInventory(trades[0], trades[2], 12),
            MatchedInventory(trades[1], trades[2], 2),
            MatchedInventory(trades[1], trades[3], 10),
            MatchedInventory(trades[3], trades[4], 2)]

        random.shuffle(trades)

        fifo_inventory_manager: FirstInFirstOutInventory[Trade] = FirstInFirstOutInventory[Trade]()
        matched_trades: List[MatchedInventory[Trade]] = fifo_inventory_manager.match_trades(trades)


        for i, tax_event in enumerate(matched_trades):
            self.assertEqual(tax_event.buy_trade.asset_code, expected_result[i].buy_trade.asset_code)
            self.assertEqual(tax_event.buy_trade.price, expected_result[i].buy_trade.price)
            self.assertEqual(tax_event.sell_trade.price, expected_result[i].sell_trade.price)
            self.assertEqual(tax_event.quantity, expected_result[i].quantity)
            self.assertEqual((tax_event.sell_trade.date - tax_event.buy_trade.date).days,
                             (expected_result[i].sell_trade.date - expected_result[i].buy_trade.date).days)
            print("Stock:" + tax_event.buy_trade.asset_code
                  + " Bought price: " + str(tax_event.buy_trade.price)
                  + " Bought Date: " + str(tax_event.buy_trade.date)
                  + " Sold price: " + str(tax_event.sell_trade.price)
                  + " Sold Date: " + str(tax_event.sell_trade.date)
                  + " Quantity: " + str(tax_event.quantity)
                  + " Days: " + str((tax_event.sell_trade.date - tax_event.buy_trade.date).days))


class CapitalGainsTaxTests(TestCase):
    def test_capital_gains(self) -> None:
        trade1 : TranslatedTrade = TranslatedTrade(Trade("BHP", 'FUTURES', datetime(2019, 1, 1), 10, "AUD", 12, Amount(0, "AUD"), 'Test'), 10, 1, 0, "AUD")
        trade2: TranslatedTrade = TranslatedTrade(Trade("BHP", 'FUTURES', datetime(2020, 1, 3), 12, "AUD", -12, Amount(0, "AUD"), 'Test'), 12, 1, 0, "AUD")
        trade3: TranslatedTrade = TranslatedTrade(Trade("BHP", 'FUTURES', datetime(2020, 1, 1), 10, "AUD", 12, Amount(0, "AUD"), 'Test'), 10, 1, 0, "AUD")
        trade4: TranslatedTrade = TranslatedTrade(Trade("BHP", 'FUTURES', datetime(2020, 1, 3), 12, "AUD", -12, Amount(0, "AUD"), 'Test'), 12, 1, 0, "AUD")
        inventory_discountable : MatchedInventory[TranslatedTrade] = MatchedInventory(trade1, trade2, 1)
        inventory_not_discountable : MatchedInventory[TranslatedTrade] = MatchedInventory(trade3, trade4, 1)
        cgt_calculator: CapitalGainsTaxMethod = DiscountCapitalGainsTaxMethod()
        self.assertEqual(cgt_calculator.calculate_taxable_gain(0, inventory_discountable).taxable_gain, 1.0)
        self.assertEqual(cgt_calculator.calculate_taxable_gain(0, inventory_not_discountable).taxable_gain, 2.0)

    def test_commission(self) -> None:
        trade1: TranslatedTrade = TranslatedTrade(Trade("BHP", 'FUTURES', datetime(2019, 1, 1), 10, "AUD", 100, Amount(-30, "AUD"), 'Test'), 10, 1, -30, "AUD")
        trade2: TranslatedTrade = TranslatedTrade(Trade("BHP", 'FUTURES', datetime(2020, 1, 3), 12, "AUD", -100, Amount(-50, "AUD"), 'Test'), 12, 1, -50, "AUD")
        trade3: TranslatedTrade = TranslatedTrade(Trade("BHP", 'FUTURES', datetime(2020, 1, 1), 10, "AUD", 100, Amount(-20, "AUD"), 'Test'), 10, 1, -20, "AUD")
        inventory_discountable : MatchedInventory[TranslatedTrade] = MatchedInventory(trade1, trade2, 100)
        inventory_not_discountable : MatchedInventory[TranslatedTrade] = MatchedInventory(trade3, trade2, 100)
        cgt_calculator: CapitalGainsTaxMethod = DiscountCapitalGainsTaxMethod()
        self.assertEqual(cgt_calculator.calculate_taxable_gain(0, inventory_discountable).taxable_gain, 60)
        self.assertEqual(cgt_calculator.calculate_taxable_gain(0, inventory_not_discountable).taxable_gain, 130)

    def test_partial_match_commission(self) -> None:
        trade1: TranslatedTrade = TranslatedTrade(Trade("BHP", 'FUTURES', datetime(2019, 1, 1), 10, "AUD", 100, Amount(-30, "AUD"), 'Test'), 10, 1, -30, "AUD")
        trade2: TranslatedTrade = TranslatedTrade(Trade("BHP", 'FUTURES', datetime(2020, 1, 3), 12, "AUD", -50, Amount(-50, "AUD"), 'Test'), 12, 1, -50, "AUD")
        trade3: TranslatedTrade = TranslatedTrade(Trade("BHP", 'FUTURES', datetime(2020, 1, 1), 12, "AUD", -50, Amount(-20, "AUD"), 'Test'), 12, 1, -20, "AUD")
        m1 : MatchedInventory[TranslatedTrade] = MatchedInventory(trade1, trade2, 50)
        m2 : MatchedInventory[TranslatedTrade] = MatchedInventory(trade1, trade3, 50)
        cgt_calculator: CapitalGainsTaxMethod = DiscountCapitalGainsTaxMethod()
        self.assertEqual(cgt_calculator.calculate_taxable_gain(0, m1).taxable_gain, 17.5)
        self.assertEqual(cgt_calculator.calculate_taxable_gain(0, m2).taxable_gain, 65)


    def test_fx_capital_gains(self) -> None:
        trade1: TranslatedTrade = TranslatedTrade(Trade("USD.AUD", 'FOREX',datetime(2019, 1, 1), 0.5, "AUD", 100, Amount(0, "AUD"), 'Test'), 0.5, 0.5, 0, "AUD")
        trade2: TranslatedTrade = TranslatedTrade(Trade("USD.AUD", 'FOREX', datetime(2020, 1, 3), 1, "AUD", -100, Amount(0, "AUD"), 'Test'), 1, 1, 0, "AUD")
        trade3: TranslatedTrade = TranslatedTrade(Trade("USD.AUD", 'FOREX', datetime(2019, 1, 1), 1, "AUD", 100, Amount(0, "AUD"), 'Test'), 1, 1, 0, "AUD")
        trade4: TranslatedTrade = TranslatedTrade(Trade("USD.AUD", 'FOREX', datetime(2019, 1, 3), 0.5, "AUD", -100, Amount(0, "AUD"), 'Test'), 0.5, 0.5, 0, "AUD")
        inventory_discountable = MatchedInventory(trade1, trade2, 100)
        inventory_not_discountable = MatchedInventory(trade3, trade4, 100)
        cgt_calculator: CapitalGainsTaxMethod = DiscountCapitalGainsTaxMethod()
        self.assertEqual(cgt_calculator.calculate_taxable_gain(0, inventory_discountable).taxable_gain, 25)
        self.assertEqual(cgt_calculator.calculate_taxable_gain(0, inventory_not_discountable).taxable_gain, 0)
        self.assertEqual(cgt_calculator.calculate_taxable_gain(0, inventory_not_discountable).carried_capital_losses, -50)


class IntegrationTests(TestCase):
    def test_run_test_file(self) -> None:
        file_reader = InteractiveBrokersReadWriter()
        trades: List[Trade] = file_reader.read_trades("./test_data/trades2.csv")
        fifo_inventory_manager: FirstInFirstOutInventory[Trade] = FirstInFirstOutInventory[Trade]()
        matched_trades: List[MatchedInventory[Trade]] = fifo_inventory_manager.match_trades(trades)
        for tax_event in matched_trades:
            print("Stock:" + tax_event.buy_trade.asset_code
                  + " Bought price: " + str(tax_event.buy_trade.price)
                  + " Bought Date: " + str(tax_event.buy_trade.date)
                  + " Sold price: " + str(tax_event.sell_trade.price)
                  + " Sold Date: " + str(tax_event.sell_trade.date)
                  + " Quantity: " + str(tax_event.quantity)
                  + " Days: " + str((tax_event.sell_trade.date - tax_event.buy_trade.date).days))

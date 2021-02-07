from abc import ABC, abstractmethod
from inventory_accounting import MatchedInventory
from model import TranslatedTrade
from typing import Final, List
from datetime import datetime


class CapitalGainsTax:
    def __init__(self,
                 matched_inventory: MatchedInventory[TranslatedTrade],
                 taxable_gain: float,
                 carried_capital_losses: float,
                 buy_commission: float,
                 sell_commission: float):
        self.matched_inventory: Final[MatchedInventory[TranslatedTrade]] = matched_inventory
        self.taxable_gain: Final = taxable_gain
        self.carried_capital_losses: Final = carried_capital_losses
        self.buy_commission: Final = buy_commission
        self.sell_commission: Final = sell_commission


class CapitalGainsTaxMethod(ABC):
    @abstractmethod
    def calculate_taxable_gain(self,
                               carried_capital_losses: float,
                               matched_inventory: MatchedInventory[TranslatedTrade]) -> CapitalGainsTax:
        ...


# Method per:
# https://www.ato.gov.au/general/capital-gains-tax/working-out-your-capital-gain-or-loss/working-out-your-capital-gain/the-discount-method-of-calculating-your-capital-gain/
# Calculates the CGT gain or carried losses for a set of trades.
class DiscountCapitalGainsTaxMethod(CapitalGainsTaxMethod):
    def calculate_taxable_gain(self,
                               carried_capital_losses: float,
                               matched_inventory: MatchedInventory[TranslatedTrade]) -> CapitalGainsTax: # ToDo: change to Trade. Add translater to constructor.
        if carried_capital_losses > 0:
            raise ValueError("Capital losses cannot be a positive number.")
        if matched_inventory.sell_trade.translated_currency != 'AUD' \
                or matched_inventory.buy_trade.translated_currency != 'AUD':
            raise ValueError("CGT can only be calculated on trades translated to AUD.")

        buy_side_pro_rata_commission: float
        sell_side_pro_rata_commission: float
        taxable_gain: float
        if matched_inventory.buy_trade.asset_category == 'FOREX': # This could be all funded trades.
            buy_side_pro_rata_commission = matched_inventory.buy_trade.translated_commission \
                                           * matched_inventory.quantity / abs(matched_inventory.buy_trade.quantity)
            sell_side_pro_rata_commission = matched_inventory.sell_trade.translated_commission \
                                            * matched_inventory.quantity / abs(matched_inventory.sell_trade.quantity)
            taxable_gain = (matched_inventory.sell_trade.translated_price - matched_inventory.buy_trade.translated_price) \
                                  * matched_inventory.quantity \
                                  + sell_side_pro_rata_commission + buy_side_pro_rata_commission # Adding negative number.
        # Additional rationale: Since futures are unfunded, there are no fx gains or losses between buying and selling,
        # whereas a funded purchase like stocks would, even if buy and sell prices are the same.
        # e.g., Buy SP500 futures for (unfunded) USD 100K, sell for USD 100K. Profit from futures is zero. No economic
        # translation gaines/losses as there is no exchange of USD.
        elif matched_inventory.buy_trade.asset_category == 'FUTURES': # This method could probably cover all unfunded trades
            buy_side_pro_rata_commission = matched_inventory.buy_trade.commission.value \
                                           * matched_inventory.quantity / abs(matched_inventory.buy_trade.quantity)
            sell_side_pro_rata_commission = matched_inventory.sell_trade.commission.value \
                                            * matched_inventory.quantity / abs(matched_inventory.sell_trade.quantity)
            special_accrual_amount = (matched_inventory.sell_trade.price - matched_inventory.buy_trade.price) \
                           * matched_inventory.quantity \
                           + sell_side_pro_rata_commission + buy_side_pro_rata_commission  # Adding negative number.
            taxable_gain = special_accrual_amount * matched_inventory.sell_trade.exchange_rate
        else:
            raise NotImplementedError('Tax treatment for asset classes other than forex and futures have not been implemented.')

        # Net any carried losses before any potential discounts.
        remaining_carried_capital_losses: float
        net_taxable_gain: float
        if taxable_gain > 0:
            nettable_amount: float = min(-carried_capital_losses, taxable_gain)
            net_taxable_gain = taxable_gain - nettable_amount
            remaining_carried_capital_losses = carried_capital_losses + nettable_amount
        else:
            net_taxable_gain = 0
            remaining_carried_capital_losses = (carried_capital_losses + taxable_gain)  # Adding two negative numbers.

        # Determine date considered '1 year' after purchase. See example below.
        buy_date: datetime = matched_inventory.buy_trade.date
        # 1 calendar year later. Starts day after purchase (see example below)
        test_date: datetime = datetime(buy_date.year + 1,
                                       buy_date.month,
                                       buy_date.day + 1)
        if matched_inventory.sell_trade.date >= test_date and taxable_gain > 0:
            return CapitalGainsTax(matched_inventory,
                                   net_taxable_gain / 2,
                                   remaining_carried_capital_losses,
                                   buy_side_pro_rata_commission,
                                   sell_side_pro_rata_commission)
        else:
            return CapitalGainsTax(matched_inventory,
                                   net_taxable_gain,
                                   remaining_carried_capital_losses,
                                   buy_side_pro_rata_commission,
                                   sell_side_pro_rata_commission)


# Strange Day counting method:
# https://www.ato.gov.au/General/Capital-gains-tax/Working-out-your-capital-gain-or-loss/Working-out-your-capital-gain/
# Sally bought a CGT asset on 2 February. Her 12-month ownership period started on 3 February
# (the day after she bought the asset) and ends 365 days later (366 in a leap year), at the end of 2 February the
# following year.
# If Sally sells the asset before 3 February the following year, she can't claim the discount or use indexation
# because she hasn't owned the asset for at least 12 months.


# Tracks past capital losses and passes them to the CGT calculator for netting.
class CapitalGainsTaxAggregator:
    def __init__(self, capital_gains_tax_method: CapitalGainsTaxMethod):
        self._capital_gains_tax_method: Final = capital_gains_tax_method

    # existing_capital_losses as negative number.
    def calculate(self, existing_capital_losses: float, trades: List[MatchedInventory[TranslatedTrade]]) -> List[CapitalGainsTax]:
        if existing_capital_losses > 0:
            raise ValueError("Capital losses cannot be a positive number.")

        capital_gains: List[CapitalGainsTax] = []
        carried_losses: float
        for i, trade in enumerate(trades):
            if i == 0:
                carried_losses = existing_capital_losses
            else:
                carried_losses = capital_gains[i - 1].carried_capital_losses
            capital_gains.append(self._capital_gains_tax_method.calculate_taxable_gain(carried_losses, trade))
        return capital_gains

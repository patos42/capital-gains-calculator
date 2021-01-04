from profile import DatedProfile, LeftPiecewiseConstantProfile
from typing import List, Final, Dict
from datetime import datetime
from model import Trade, TaxableTrade

# Converts foreign asset transactions to AUD equivalents and creates implied
# FX trades using provided ATO mandated rates (from the RBA at the time of writing).
# Using methods described in https://www.ato.gov.au/Forms/Guide-to-capital-gains-tax-2020/?page=17

# Note using RBA rates only as rates posted directly on ATO website stop in 2019 with a recommendation to use RBA
# rates going forward. However, ATO rates are inconsistent with RBA rates.
#https://community.ato.gov.au/t5/Tax-professionals/Daily-Exchange-Rates/td-p/38488
# KylieATO Community Manager 31 March 2020 - edited 31 March 2020
# "As outlined on our website, taxpayers are able to use the ATO rates or any appropriate exchange rate.
# This can be provided by a banking institution operating in Australia including, where relevant, the banking
# institution through which your foreign income is received, or another reliable external source ."
class ForeignAssetTranslator:
        def __init__(self, fx_rates : Dict[str,Dict[datetime, float]]):
            self.fx_profiles = Dict[str,DatedProfile[float]]()
            for asset_code in fx_rates:
                self.fx_profiles[asset_code] = LeftPiecewiseConstantProfile(asset_code, fx_rates[asset_code])

        def convert_trade(self, trade : Trade) -> TaxableTrade:
            taxable_trade : TaxableTrade
            if trade.currency != 'AUD':
                fx_rate = self.fx_profiles[trade.currency][trade.date]
                aud_price = trade.price * fx_rate
                return TaxableTrade(trade, aud_price, fx_rate)
            return TaxableTrade(trade, trade.price, 1)

        def convert_trades(self, trades : List[Trade]) -> List[TaxableTrade]:
            converted_trades : List[TaxableTrade] = List[TaxableTrade]()
            for trade in trades:
                converted_trades.append(self.convert_trade(trade))
            return converted_trades



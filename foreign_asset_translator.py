from profile import DatedProfile, LeftPiecewiseConstantProfile
from typing import List, Final, Dict
from datetime import datetime
from model import Trade, TaxableTrade

# Converts foreign asset transactions to AUD equivalents and creates implied
# FX trades using provided ATO mandated rates (from the RBA at the time of writing).
# Using methods described in https://www.ato.gov.au/Forms/Guide-to-capital-gains-tax-2020/?page=17
class ForeignAssetTranslator:
        def __init__(self, fx_rates : Dict[str,Dict[datetime, float]]):
            self.fx_profiles = Dict[str,DatedProfile[float]]()
            for asset_code in fx_rates:
                self.fx_profiles[asset_code] = LeftPiecewiseConstantProfile(asset_code, fx_rates[asset_code])

        def convert_trades(self, trades : List[Trade]) -> List[TaxableTrade]:
            converted_trades : List[TaxableTrade] = List[TaxableTrade]()
            for trade in trades:
                if trade.currency != 'AUD':
                    fx_rate = self.fx_profiles[trade.currency][trade.date]
                    aud_price = trade.price * fx_rate
                    converted_trades.append(TaxableTrade(trade, aud_price))
                else:
                    converted_trades.append(TaxableTrade(trade, trade.price))
            return converted_trades



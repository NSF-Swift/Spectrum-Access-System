from dpa_calculator.cbsd.cbsd_getter.cbsd_getter import CbsdGetter

EIRP_UE = 24
GAIN_UE = 0


class CbsdGetterUe(CbsdGetter):
    @property
    def _gain(self) -> int:
        return GAIN_UE

    @property
    def _eirp(self) -> int:
        return EIRP_UE
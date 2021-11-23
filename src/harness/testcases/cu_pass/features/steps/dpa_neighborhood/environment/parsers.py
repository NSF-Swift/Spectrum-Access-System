from dataclasses import dataclass
from typing import Union

import parse
from behave import *

from dpa_calculator.utils import Point
from reference_models.common.data import CbsdGrantInfo
from reference_models.dpa.dpa_mgr import BuildDpa

CBSD_A_INDICATOR = 'A'
CBSD_B_INDICATOR = 'B'


@dataclass
class Cbsd:
    height: float
    is_indoor: bool
    location: Point
    transmit_power: float

    def to_grant(self) -> CbsdGrantInfo:
        return CbsdGrantInfo(antenna_azimuth=None,
                             antenna_beamwidth=None,
                             antenna_gain=6,
                             cbsd_category=None,
                             height_agl=self.height,
                             high_frequency=None,
                             indoor_deployment=self.is_indoor,
                             is_managed_grant=None,
                             latitude=self.location.latitude,
                             longitude=self.location.longitude,
                             low_frequency=None,
                             max_eirp=self.transmit_power)


def get_cbsd_ap(category: Union[CBSD_A_INDICATOR, CBSD_B_INDICATOR], height: float, is_indoor: bool, location: Point) -> Cbsd:
    return Cbsd(height=height, is_indoor=is_indoor, transmit_power=30, location=location)


# @dataclass
# class CbsdB(Cbsd):
#     transmit_power = 47


@parse.with_pattern(f'({CBSD_A_INDICATOR}|{CBSD_B_INDICATOR})')
def parse_cbsd(text: str) -> Cbsd:
    pass
    # if text == CBSD_A_INDICATOR:
    #     return Ap()
    # else:
    #     return CbsdB()


@parse.with_pattern('.*')
def parse_dpa(text: str):
    return BuildDpa(dpa_name=text.upper())


register_type(Cbsd=parse_cbsd)
register_type(Dpa=parse_dpa)
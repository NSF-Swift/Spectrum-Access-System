import random
from typing import Dict

from dpa_calculator.aggregate_interference_calculator.aggregate_interference_calculator_ntia.helpers.cbsd_interference_calculator.antenna_gain_calculator.antenna_gain_calculator import \
    AntennaGainCalculator
from dpa_calculator.aggregate_interference_calculator.aggregate_interference_calculator_ntia.helpers.cbsd_interference_calculator.variables import \
    CLUTTER_LOSS_MAXIMUM, CLUTTER_LOSS_MINIMUM, GainAtAzimuth, INSERTION_LOSSES_IN_DB, InterferenceComponents
from dpa_calculator.aggregate_interference_calculator.aggregate_interference_calculator_ntia.helpers.propagation_loss_calculator import \
    PropagationLossCalculator
from dpa_calculator.cbsd.cbsd import Cbsd, CbsdTypes
from dpa_calculator.utilities import get_distance_between_two_points, get_dpa_center, \
    Point, region_is_rural
from reference_models.dpa.dpa_mgr import Dpa


class CbsdInterferenceCalculator:
    def __init__(self,
                 cbsd: Cbsd,
                 dpa: Dpa,
                 receive_antenna_gain_calculator: AntennaGainCalculator):
        self._cbsd = cbsd
        self._dpa = dpa
        self._receive_antenna_gain_calculator = receive_antenna_gain_calculator

    def calculate(self) -> InterferenceComponents:
        return InterferenceComponents(
            distance_in_kilometers=get_distance_between_two_points(point1=self._dpa_center, point2=self._cbsd.location),
            eirp=self._cbsd.eirp,
            frequency_dependent_rejection=0,
            gain_receiver=self._gain_receiver,
            loss_building=0,
            loss_clutter=random.uniform(CLUTTER_LOSS_MINIMUM,
                                        CLUTTER_LOSS_MAXIMUM) if self._is_rural else CLUTTER_LOSS_MINIMUM,
            loss_propagation=PropagationLossCalculator(cbsd=self._cbsd, dpa=self._dpa).calculate(),
            loss_receiver=INSERTION_LOSSES_IN_DB,
            loss_transmitter=INSERTION_LOSSES_IN_DB if self._has_transmitter_losses else 0
        )

    @property
    def _has_transmitter_losses(self) -> bool:
        return not self._cbsd.is_indoor and self._cbsd.cbsd_type == CbsdTypes.AP

    @property
    def _gain_receiver(self) -> Dict[float, GainAtAzimuth]:
        return self._receive_antenna_gain_calculator.calculate(cbsd=self._cbsd)

    @property
    def _is_rural(self) -> bool:
        return region_is_rural(coordinates=self._dpa_center)

    @property
    def _dpa_center(self) -> Point:
        return get_dpa_center(dpa=self._dpa)

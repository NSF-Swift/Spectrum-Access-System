from typing import Iterable, List

from cached_property import cached_property

from dpa_calculator.aggregate_interference_calculator.aggregate_interference_calculator_ntia.helpers.cbsd_interference_calculator.variables import \
    InterferenceComponents
from reference_models.interference.interference import dbToLinear, linearToDb


class InterferenceAtAzimuthWithMaximumGainCalculator:
    def __init__(self, minimum_distance: float, interference_components: List[InterferenceComponents]):
        self._minimum_distance = minimum_distance
        self._interference_components = interference_components

    def calculate(self) -> float:
        total_interferences = [
            sum(dbToLinear(component.total_interference(azimuth=azimuth)) for component in self._interference_components_in_range)
            for azimuth in self._azimuths
        ]
        return linearToDb(max(total_interferences))

    @property
    def _azimuths(self) -> Iterable[float]:
        return self._interference_components[0].gain_receiver.keys()

    @cached_property
    def _interference_components_in_range(self) -> List[InterferenceComponents]:
        return [components for components in self._interference_components
                if components.distance_in_kilometers >= self._minimum_distance]

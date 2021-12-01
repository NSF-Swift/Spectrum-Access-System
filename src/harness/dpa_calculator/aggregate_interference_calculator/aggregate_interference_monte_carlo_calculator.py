from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from cached_property import cached_property

from dpa_calculator.aggregate_interference_calculator.aggregate_interference_calculator_ntia.aggregate_interference_calculator_ntia import \
    AggregateInterferenceCalculatorNtia
from dpa_calculator.cbsd.cbsd import Cbsd
from dpa_calculator.cbsds_creator.utilities import get_cbsds_creator
from dpa_calculator.number_of_aps.number_of_aps_calculator_shipborne import NumberOfApsCalculatorShipborne
from dpa_calculator.parameter_finder import ParameterFinder
from dpa_calculator.point_distributor import AreaCircle
from dpa_calculator.population_retriever.population_retriever_census import PopulationRetrieverCensus
from dpa_calculator.population_retriever.population_retriever_region_type import PopulationRetrieverRegionType
from dpa_calculator.utilities import get_dpa_center, run_monte_carlo_simulation
from reference_models.dpa.dpa_mgr import Dpa

DEFAULT_MONTE_CARLO_ITERATIONS = 1000

DEFAULT_SIMULATION_RADIUS = 500


@dataclass
class InterferenceParameters:
    dpa: Dpa
    number_of_aps: int


@dataclass
class AggregateInterferenceMonteCarloResults:
    interference_max: float
    interference_access_point: float
    interference_user_equipment: float
    runtime: timedelta


class AggregateInterferenceMonteCarloCalculator:
    def __init__(self, dpa: Dpa, target_threshold: float, number_of_iterations: int = DEFAULT_MONTE_CARLO_ITERATIONS):
        self._dpa = dpa
        self._number_of_iterations = number_of_iterations
        self._target_threshold = target_threshold

    def simulate(self) -> AggregateInterferenceMonteCarloResults:
        start_time = datetime.now()
        interference_access_point = run_monte_carlo_simulation(function_to_run=self._single_run_access_point, number_of_iterations=self._number_of_iterations)
        interference_user_equipment = run_monte_carlo_simulation(function_to_run=self._single_run_user_equipment, number_of_iterations=self._number_of_iterations)
        return AggregateInterferenceMonteCarloResults(
            interference_max=max(interference_access_point, interference_user_equipment),
            interference_access_point=interference_access_point,
            interference_user_equipment=interference_user_equipment,
            runtime=datetime.now() - start_time
        )

    def _single_run_access_point(self) -> float:
        return self._single_run_cbsd(is_user_equipment=False)

    def _single_run_user_equipment(self) -> float:
        return self._single_run_cbsd(is_user_equipment=True)

    def _single_run_cbsd(self, is_user_equipment: bool) -> float:
        interference_calculator = self._aggregate_interference_calculator(is_user_equipment=is_user_equipment)
        return ParameterFinder(function=interference_calculator.calculate, target=self._target_threshold).find()

    def _aggregate_interference_calculator(self, is_user_equipment: bool) -> AggregateInterferenceCalculatorNtia:
        cbsds = self._random_cbsds(is_user_equipment=is_user_equipment)
        return AggregateInterferenceCalculatorNtia(dpa=self._dpa, cbsds=cbsds)

    def _random_cbsds(self, is_user_equipment: bool) -> List[Cbsd]:
        cbsds_creator = get_cbsds_creator(dpa_zone=self._dpa_test_zone,
                                          is_user_equipment=is_user_equipment,
                                          number_of_aps=self._number_of_aps)
        cbsds = cbsds_creator.create()
        cbsds_creator.write_to_kml(self._kml_output_filepath(is_user_equipment=is_user_equipment))
        return cbsds

    @cached_property
    def _number_of_aps(self) -> int:
        population = PopulationRetrieverRegionType(area=self._dpa_test_zone).retrieve()
        return NumberOfApsCalculatorShipborne(center_coordinates=self._dpa_test_zone.center_coordinates,
                                              simulation_population=population).get_number_of_aps()

    @property
    def _dpa_test_zone(self) -> AreaCircle:
        return AreaCircle(
            center_coordinates=get_dpa_center(dpa=self._dpa),
            radius_in_kilometers=DEFAULT_SIMULATION_RADIUS
        )

    @staticmethod
    def _kml_output_filepath(is_user_equipment: bool) -> Path:
        return Path(f'grants_{is_user_equipment}.kml')

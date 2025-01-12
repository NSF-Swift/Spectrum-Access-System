from collections import defaultdict
from contextlib import contextmanager
from typing import ContextManager, List, Optional

import boto3
from cached_property import cached_property

from cu_pass.dpa_calculator.aggregate_interference_calculator.aggregate_interference_monte_carlo_calculator.aggregate_interference_monte_carlo_calculator import \
    AggregateInterferenceMonteCarloCalculator, AggregateInterferenceMonteCarloResults
from cu_pass.dpa_calculator.aggregate_interference_calculator.aggregate_interference_monte_carlo_calculator.support.definitions import \
    CbsdDeploymentOptions, SIMULATION_DISTANCES_DEFAULT
from cu_pass.dpa_calculator.aggregate_interference_calculator.configuration.configuration_manager import \
    ConfigurationManager
from cu_pass.dpa_calculator.cbsd.cbsd import CbsdCategories, CbsdTypes
from cu_pass.dpa_calculator.dpa.builder import get_dpa
from cu_pass.dpa_calculator.dpa.dpa import Dpa
from cu_pass.dpa_calculator.helpers.list_distributor.fractional_distribution.fractional_distribution import \
    FractionalDistribution
from cu_pass.dpa_calculator.helpers.list_distributor.fractional_distribution.support.fractional_distribution_parser import \
    parse_fractional_distribution
from cu_pass.dpa_calculator.main_runner.results_recorder import ResultsRecorder

DEFAULT_NUMBER_OF_ITERATIONS = 100


class MainRunner:
    def __init__(self,
                 dpa_name: str,
                 beamwidth: float = None,
                 eirp_category_a: str = None,
                 eirp_category_b: str = None,
                 number_of_iterations: int = DEFAULT_NUMBER_OF_ITERATIONS,
                 simulation_distance_category_a: int = SIMULATION_DISTANCES_DEFAULT[CbsdCategories.A],
                 simulation_distance_category_b: int = SIMULATION_DISTANCES_DEFAULT[CbsdCategories.B],
                 local_output_directory: Optional[str] = None,
                 include_ue_runs: bool = False,
                 interference_threshold: int = None,
                 neighborhood_category: Optional[str] = None,
                 s3_bucket: Optional[str] = None,
                 s3_output_directory: Optional[str] = None):
        self._beamwidth = beamwidth
        self._dpa_name = dpa_name
        self._eirp_distributions = {
            CbsdCategories.A: eirp_category_a,
            CbsdCategories.B: eirp_category_b
        }
        self._local_output_directory = local_output_directory
        self._include_ue_runs = include_ue_runs
        self._interference_threshold = interference_threshold
        self._neighborhood_category = neighborhood_category
        self._number_of_iterations = number_of_iterations
        self._simulation_distances_in_kilometers = {
            CbsdCategories.A: simulation_distance_category_a,
            CbsdCategories.B: simulation_distance_category_b
        }
        self._s3_bucket = s3_bucket
        self._s3_output_directory = s3_output_directory

    def run(self) -> None:
        self._setup_logging_handler()
        self._validate_args()
        with self._setup_output_recording():
            self._setup_global_configuration()
            results = self._calculate()
            results.log()
            self._record_results(results=results)

    def _setup_logging_handler(self) -> None:
        self._results_recorder.setup_logging_handler()

    def _validate_args(self) -> None:
        self._validate_s3_bucket()

    def _validate_s3_bucket(self) -> None:
        if self._s3_bucket:
            buckets = self._s3_client.list_buckets()['Buckets']
            bucket_names = (bucket['Name'] for bucket in buckets)
            if self._s3_bucket not in bucket_names:
                raise LookupError(f'"{self._s3_bucket}" does not exist.')

    @contextmanager
    def _setup_output_recording(self) -> ContextManager[None]:
        with self._results_recorder.prepare_for_recording():
            yield

    def _setup_global_configuration(self) -> None:
        self._setup_eirp_configuration()

    def _setup_eirp_configuration(self) -> None:
        configuration = ConfigurationManager().get_configuration()
        for cbsd_category in CbsdCategories:
            distribution_text = self._eirp_distributions[cbsd_category]
            if distribution_text:
                distribution = parse_fractional_distribution(text=distribution_text)[0]
                configuration.eirp_distribution[CbsdTypes.AP][cbsd_category] = defaultdict(lambda: defaultdict( lambda: distribution))

    def _calculate(self) -> AggregateInterferenceMonteCarloResults:
        cbsd_deployment_options = CbsdDeploymentOptions(
            simulation_distances_in_kilometers=self._simulation_distances_in_kilometers
        )
        return AggregateInterferenceMonteCarloCalculator(
            dpa=self._dpa,
            cbsd_deployment_options=cbsd_deployment_options,
            include_ue_runs=self._include_ue_runs,
            interference_threshold=self._interference_threshold,
            number_of_iterations=self._number_of_iterations,
            neighborhood_categories=self._neighborhood_categories).simulate()

    @property
    def _dpa(self) -> Dpa:
        dpa = get_dpa(dpa_name=self._dpa_name)
        if self._beamwidth:
            dpa.beamwidth = self._beamwidth
        return dpa

    @property
    def _neighborhood_categories(self) -> List[CbsdCategories]:
        if self._neighborhood_category:
            return [CbsdCategories[self._neighborhood_category]]
        return list(CbsdCategories)

    def _record_results(self, results: AggregateInterferenceMonteCarloResults) -> None:
        self._results_recorder.record(results=results)

    @cached_property
    def _results_recorder(self) -> ResultsRecorder:
        return ResultsRecorder(local_output_directory=self._local_output_directory,
                               s3_bucket=self._s3_bucket,
                               s3_output_directory=self._s3_output_directory)

    @property
    def _s3_client(self):
        return boto3.client('s3')


# if __name__ == '__main__':
#     MainRunner(dpa_name='MCKINNEY',
#                number_of_iterations=1,
#                simulation_distance_category_a=200,
#                simulation_distance_category_b=500,
#                local_output_directory='mckinney/200-category-a/500-category-b/eirp--137-37-m31-s5/1000-iterations',
#                eirp_category_a='100%: PDF [-12-20] mean 15.993519643580397 std 3.6722433576872757',
#                eirp_category_b='100%: PDF [-137-37] mean 31.7682164324784 std 4.984432082541898').run()

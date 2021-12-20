from functools import partial
from typing import Type

from behave import *

from cu_pass.dpa_calculator.aggregate_interference_calculator.aggregate_interference_monte_carlo_calculator import \
    AggregateInterferenceMonteCarloCalculator, AggregateInterferenceMonteCarloResults, AggregateInterferenceTypes, \
    NumberOfApsTypes, PopulationRetrieverTypes
from testcases.cu_pass.features.environment.hooks import record_exception
from testcases.cu_pass.features.environment.utilities import get_expected_output_content, get_logging_file_handler, \
    sanitize_output_log
from testcases.cu_pass.features.steps.dpa_neighborhood.common_steps.dpa import ContextDpa
from testcases.cu_pass.features.steps.dpa_neighborhood.common_steps.region_type import assign_arbitrary_dpa

use_step_matcher('parse')


class ContextNeighborhood(ContextDpa):
    monte_carlo_runner: Type[AggregateInterferenceMonteCarloCalculator]
    number_of_iterations: int
    result: AggregateInterferenceMonteCarloResults
    simulation_area_radius: int


@step("{organization} interference")
def step_impl(context: ContextNeighborhood, organization: str):
    map = {
        'NTIA': AggregateInterferenceTypes.NTIA,
        'WinnForum': AggregateInterferenceTypes.WinnForum
    }
    context.monte_carlo_runner = partial(context.monte_carlo_runner,
                                         aggregate_interference_calculator_type=map[organization])


@step("population by {population_type}")
def step_impl(context: ContextNeighborhood, population_type: str):
    map = {
        'census radius': PopulationRetrieverTypes.census,
        'region type': PopulationRetrieverTypes.region_type
    }
    context.monte_carlo_runner = partial(context.monte_carlo_runner,
                                         population_retriever_class=map[population_type])


@step("number of APs using {number_of_aps_type} analysis")
def step_impl(context: ContextNeighborhood, number_of_aps_type: str):
    map = {
        'ground based': NumberOfApsTypes.ground_based,
        'shipborne': NumberOfApsTypes.shipborne
    }
    context.monte_carlo_runner = partial(context.monte_carlo_runner,
                                         number_of_aps_calculator_class=map[number_of_aps_type])


@step("{number_of_aps:Integer} APs")
def step_impl(context: ContextNeighborhood, number_of_aps: int):
    context.monte_carlo_runner = partial(context.monte_carlo_runner,
                                         number_of_aps=number_of_aps)


@step("a simulation area radius of {simulation_area_radius:Integer}")
def step_impl(context: ContextNeighborhood, simulation_area_radius: int):
    context.simulation_area_radius = simulation_area_radius


@step("{number_of_iterations:Integer} monte carlo iterations")
def step_impl(context: ContextNeighborhood, number_of_iterations: int):
    context.number_of_iterations = number_of_iterations


@when("the neighborhood radius is calculated")
def step_impl(context: ContextNeighborhood):
    """
    Args:
        context (behave.runner.Context):
    """
    with record_exception(context=context):
        if not hasattr(context, 'dpa'):
            assign_arbitrary_dpa(context=context)
        simulation_results = context.monte_carlo_runner(dpa=context.dpa,
                                                        number_of_iterations=getattr(context, 'number_of_iterations', 1),
                                                        simulation_area_radius_in_kilometers=getattr(context, 'simulation_area_radius', 100)).simulate()
        simulation_results.log()
        context.result = simulation_results


@then("the resulting distance should be {expected_distance:Number}")
def step_impl(context: ContextNeighborhood, expected_distance: float):
    assert context.result.distance == expected_distance, f'{context.result.distance} != {expected_distance}'


@then("the resulting interference should be {expected_interference:Number}")
def step_impl(context: ContextNeighborhood, expected_interference: float):
    assert context.result.interference == expected_interference, f'{context.result.interference} != {expected_interference}'


@then("it should run without error")
def step_impl(context: ContextNeighborhood):
    exception_encountered = getattr(context, 'exception', None)
    assert not exception_encountered, f'Encountered exception {exception_encountered.__class__.__name__}: {exception_encountered}'


@then("the output log should be")
def step_impl(context: ContextNeighborhood):
    expected_content = get_expected_output_content(context=context)
    output_log_filepath = get_logging_file_handler().baseFilename
    output_content = sanitize_output_log(log_filepath=output_log_filepath)
    assert output_content == expected_content

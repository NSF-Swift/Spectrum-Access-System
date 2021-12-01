from dataclasses import dataclass
from typing import List

from behave import *

from dpa_calculator.aggregate_interference_calculator.aggregate_interference_calculator_ntia.helpers.azimuth_with_maximum_gain_calculator import \
    InterferenceAtAzimuthWithMaximumGainCalculator
from dpa_calculator.aggregate_interference_calculator.aggregate_interference_calculator_ntia.helpers.cbsd_interference_calculator import \
    GainAtAzimuth, InterferenceComponents
from testcases.cu_pass.features.environment.hooks import ContextSas

use_step_matcher("parse")


@dataclass
class ContextAggregateInterference(ContextSas):
    interference_components: List[InterferenceComponents]


@given("CBSDs at distances {distances:NumberList} each with gains {gains:NumberListList} at azimuths {azimuths:NumberList}")
def step_impl(context: ContextAggregateInterference, distances: List[float], gains: List[List[float]], azimuths: List[float]):
    """
    Args:
        context (behave.runner.Context):
    """
    context.interference_components = [
        InterferenceComponents(
            distance_in_kilometers=distance,
            eirp=0,
            frequency_dependent_rejection=0,
            gain_receiver={azimuth: GainAtAzimuth(azimuth=azimuth, gain=gain) for azimuth, gain in
                           zip(azimuths, gains[cbsd_number])},
            loss_building=0,
            loss_clutter=0,
            loss_propagation=0,
            loss_receiver=0,
            loss_transmitter=0
        )
        for cbsd_number, distance in enumerate(distances)
    ]


@then("the returned interference with minimum distance {distance:Number} should be the aggregate of interference from CBSDs {expected_cbsd_numbers:IntegerList} at azimuth {expected_azimuth:Number}")
def step_impl(context: ContextAggregateInterference, distance: float, expected_cbsd_numbers: List[int], expected_azimuth: float):
    """
    Args:
        context (behave.runner.Context):
        distance (str):
        expected_azimuth (str):
    """
    components_to_include = [components for cbsd_number, components in enumerate(context.interference_components) if cbsd_number in expected_cbsd_numbers]
    expected_interference = sum(component.total_interference(azimuth=expected_azimuth) for component in components_to_include)
    aggregate_interference = InterferenceAtAzimuthWithMaximumGainCalculator(minimum_distance=distance, interference_components=context.interference_components).calculate()
    assert aggregate_interference == expected_interference, f'{aggregate_interference} != {expected_azimuth}'

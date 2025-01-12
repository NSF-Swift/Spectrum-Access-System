from collections import defaultdict
from dataclasses import dataclass

import parse
from math import isclose
from typing import Callable, Iterable, List

from behave import *

from cu_pass.dpa_calculator.cbsd.cbsd import Cbsd, CbsdCategories
from cu_pass.dpa_calculator.constants import ALL_REGION_TYPES
from cu_pass.dpa_calculator.number_of_aps.number_of_aps_calculator import NumberOfCbsdsCalculatorOptions
from cu_pass.dpa_calculator.utilities import Point, get_bearing_between_two_points, get_distance_between_two_points
from testcases.cu_pass.dpa_calculator.features.steps.dpa_neighborhood.cbsd_creation.utilities import set_large_simulation_population
from testcases.cu_pass.dpa_calculator.features.steps.dpa_neighborhood.common_steps.area import ContextArea
from testcases.cu_pass.dpa_calculator.features.steps.dpa_neighborhood.cbsd_creation.common_steps.cbsd_creation import \
    ContextCbsdCreation

use_step_matcher('parse')


BEARING_REGEX = 'bearing'
CLOSEST_REGEX = 'closest'
DISTANCE_REGEX = 'distance'
FURTHEST_REGEX = 'furthest'
HIGHEST_REGEX = 'highest'
LOWEST_REGEX = 'lowest'


@parse.with_pattern(f'({CLOSEST_REGEX}|{FURTHEST_REGEX}|{HIGHEST_REGEX}|{LOWEST_REGEX})')
def parse_min_max(text: str) -> Callable[[Iterable[float]], float]:
    return min if text in [CLOSEST_REGEX, LOWEST_REGEX] else max


@parse.with_pattern(f'({DISTANCE_REGEX}|{BEARING_REGEX})')
def parse_distance_or_bearing_word(text: str) -> Callable[[Point, Point], float]:
    return get_distance_between_two_points if text == DISTANCE_REGEX else get_bearing_between_two_points


register_type(MinMax=parse_min_max)
register_type(DistanceOrBearingFunction=parse_distance_or_bearing_word)


@dataclass
class ContextRandomApPositioning(ContextCbsdCreation, ContextArea):
    pass


@given("a lot of CBSDs")
def step_impl(context: ContextRandomApPositioning):
    set_large_simulation_population(context=context)
    context.number_of_cbsds_calculator_options = NumberOfCbsdsCalculatorOptions()
    arbitrary_number_of_category_b_ues_per_ap_to_create_a_large_amount = 15
    for region_type in ALL_REGION_TYPES:
        context.number_of_cbsds_calculator_options.number_of_ues_per_ap_by_region_type[CbsdCategories.B][region_type] = arbitrary_number_of_category_b_ues_per_ap_to_create_a_large_amount


@then("all category {cbsd_category:CbsdCategory} points should be within {max_distance:Integer} km of the center point")
def step_impl(context: ContextRandomApPositioning, cbsd_category: CbsdCategories, max_distance: int):
    """
    Args:
        context (behave.runner.Context):
    """
    leeway = 0.001
    distributed_points = get_distributed_points(cbsds=context.cbsds, cbsd_categories=[cbsd_category])
    cbsd_distances = [get_distance_between_two_points(point1=context.center_coordinates, point2=point)
                      for point in distributed_points]
    max_distance_found = max(cbsd_distances)
    assert max_distance_found - leeway <= max_distance, f'{max_distance_found} > {max_distance}'


@step("the {aggregation_function:MinMax} category {cbsd_category:CbsdCategory} {metric_function:DistanceOrBearingFunction} should be close to {reference_distance:Integer} {_units}")
def step_impl(context: ContextRandomApPositioning,
              *args,
              metric_function: Callable[[Point, Point], float],
              cbsd_category: CbsdCategories,
              aggregation_function:Callable[[Iterable[float]], float],
              reference_distance: int):
    """
    Args:
        context (behave.runner.Context):
    """
    distance = aggregation_function(metric_function(context.center_coordinates, point)
                                    for point in get_distributed_points(cbsds=context.cbsds, cbsd_categories=[cbsd_category]))
    assert isclose(distance, reference_distance, abs_tol=1), f'{distance} is not close to {reference_distance}'


@step("no points should have exactly the same latitude, longitude, or bearing")
def step_impl(context: ContextRandomApPositioning):
    """
    Args:
        context (behave.runner.Context):
    """
    properties = defaultdict(set)
    for point in get_distributed_points(cbsds=context.cbsds):
        properties['latitude'].add(point.latitude)
        properties['longitude'].add(point.longitude)
        properties['bearing'].add(get_bearing_between_two_points(point1=context.center_coordinates, point2=point))

    assert all(len(unique_property_values) == len(get_distributed_points(cbsds=context.cbsds)) for unique_property_values in properties.values())


def get_distributed_points(cbsds: List[Cbsd], cbsd_categories: Iterable[CbsdCategories] = CbsdCategories) -> List[Point]:
    return [cbsd.location for cbsd in cbsds if cbsd.cbsd_category in cbsd_categories]

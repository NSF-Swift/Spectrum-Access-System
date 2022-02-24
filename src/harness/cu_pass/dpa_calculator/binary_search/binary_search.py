from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from statistics import mean
from typing import Callable, Optional

import numpy
from matplotlib import pyplot

from cu_pass.dpa_calculator.utilities import get_dpa_calculator_logger


@dataclass
class InputWithReturnedValue:
    input: int
    returned_value: float

    def log(self) -> None:
        logger = get_dpa_calculator_logger()
        logger.info(f'\t\tInput: {self.input}')
        logger.info(f'\t\tValue: {self.returned_value}')


@dataclass
class BinarySearchBoundaries:
    maximum: int
    minimum: int


class BinarySearch(ABC):
    def __init__(self, function: Callable[[int], float], max_parameter: int = 500, step_size: int = 1):
        self._function = function
        self._step_size = step_size

        self._min = 0
        self._max = self._initial_max = self._get_initial_max(max_parameter=max_parameter)
        self._results_cache = {}

    def _get_initial_max(self, max_parameter: int) -> int:
        is_partial_step = bool(max_parameter % self._step_size)
        additional_step_if_necessary = self._step_size * is_partial_step
        return self._get_nearest_step_below(exact_input=max_parameter) + additional_step_if_necessary

    def _get_nearest_step_below(self, exact_input: int) -> int:
        return (exact_input // self._step_size) * self._step_size

    def find(self) -> InputWithReturnedValue:
        return self._perform_binary_search()

    def _perform_binary_search(self) -> InputWithReturnedValue:
        while self._input_found is None:
            new_boundaries = self._updated_boundaries
            self._max = new_boundaries.maximum
            self._min = new_boundaries.minimum
        self._plot()
        return InputWithReturnedValue(
            input=self._input_found,
            returned_value=self._run_function(self._input_found)
        )

    def _plot(self):
        neighborhood_distances = sorted(self._results_cache.keys())
        move_list_distances = [numpy.percentile(self._results_cache[neighborhood_distance], 95)
                               for neighborhood_distance in neighborhood_distances]
        pyplot.plot(neighborhood_distances, move_list_distances)
        pyplot.title('Neighborhood Distance Effect on Move List')
        pyplot.xlabel('Neighborhood Distance (km)')
        pyplot.ylabel('Furthest Device on Move List (km)')
        pyplot.show()

    @property
    @abstractmethod
    def _input_found(self) -> Optional[int]:
        pass

    @property
    @abstractmethod
    def _updated_boundaries(self) -> BinarySearchBoundaries:
        pass

    def _function_result_with_current_parameter(self) -> float:
        return self._run_function(self._current_parameter)

    def _run_function(self, input: int) -> float:
        if input not in self._results_cache:
            self._results_cache[input] = self._function(input)
        return self._results_cache[input]

    @property
    def _current_parameter(self) -> int:
        exact_parameter = int(mean([self._min, self._max]))
        return self._get_nearest_step_below(exact_parameter)

from dataclasses import dataclass
from typing import List

from cu_pass.dpa_calculator.cbsd.cbsd import CbsdCategories

NUMBER_OF_COLUMNS_PER_GRANT = 4
NUMBER_OF_CBSD_CHARACTERISTICS_COLUMNS = 4


@dataclass
class Grant:
    grant_type: str
    grant_frequency_low: float
    grant_frequency_high: float
    grant_max_eirp: float


@dataclass
class CbsdInfo:
    height_in_meters: float
    height_type: str
    is_indoor: bool
    cbsd_category: CbsdCategories
    grants: List[Grant]

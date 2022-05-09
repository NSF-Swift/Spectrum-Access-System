import csv
from pathlib import Path
from typing import Iterable, List

from cu_pass.dpa_calculator.cbsd.cbsd import CbsdCategories
from cu_pass.dpa_calculator.helpers.list_distributor.fractional_distribution.fractional_distribution_normal import \
    FractionalDistributionNormal
from cu_pass.dpa_calculator.srcipts.cbsd_datamining.support.definitions import CbsdInfo, Grant, \
    NUMBER_OF_CBSD_CHARACTERISTICS_COLUMNS, \
    NUMBER_OF_COLUMNS_PER_GRANT
from cu_pass.dpa_calculator.srcipts.cbsd_datamining.support.eirp_parser import EirpParser
from cu_pass.dpa_calculator.utilities import get_script_directory


class SasDataParser:
    def __init__(self, csv_filepath: Path):
        self._csv_filepath = csv_filepath

    def get_eirp_distribution(self, cbsd_category: CbsdCategories) -> FractionalDistributionNormal:
        return EirpParser(cbsd_category=cbsd_category, cbsd_grants=self._grants).get_eirp_distribution()

    @property
    def _grants(self) -> List[CbsdInfo]:
        return [self._extract_cbsd_info(row=row) for is_nonheader, row in enumerate(self._csv_data) if is_nonheader]

    def _extract_cbsd_info(self, row: List[str]) -> CbsdInfo:
        return CbsdInfo(
            height_in_meters=float(row[0]),
            height_type=row[1],
            is_indoor=row[2].lower() == 'true',
            cbsd_category=CbsdCategories[row[3]],
            grants=self._get_cbsd_grants(row=row)
        )

    def _get_cbsd_grants(self, row: List[str]) -> List[Grant]:
        grant_start_indexes = range(NUMBER_OF_CBSD_CHARACTERISTICS_COLUMNS, len(row), NUMBER_OF_COLUMNS_PER_GRANT)
        return [self._extract_grant(row=row, grant_start_index=grant_start_index)
                for grant_start_index in grant_start_indexes
                if row[grant_start_index]]

    def _extract_grant(self, row: List[str], grant_start_index: int) -> Grant:
        return Grant(
            grant_type=row[grant_start_index],
            grant_frequency_low=float(row[grant_start_index + 1]),
            grant_frequency_high=float(row[grant_start_index + 2]),
            grant_max_eirp=float(row[grant_start_index + 3])
        )

    @property
    def _csv_data(self) -> Iterable[List[str]]:
        with open(self._csv_filepath, newline='') as csvfile:
            yield from csv.reader(csvfile)


if __name__ == '__main__':
    parser = SasDataParser(csv_filepath=Path(get_script_directory(__file__), 'cbsdOverviewData.csv'))
    print(f'CATEGORY A: {parser.get_eirp_distribution(cbsd_category=CbsdCategories.A)}')
    print(f'CATEGORY B: {parser.get_eirp_distribution(cbsd_category=CbsdCategories.B)}')

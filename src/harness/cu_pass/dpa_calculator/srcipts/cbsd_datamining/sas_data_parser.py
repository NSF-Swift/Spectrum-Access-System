import csv
from pathlib import Path
from statistics import mean, stdev
from typing import Iterable, List

from cu_pass.dpa_calculator.helpers.list_distributor.fractional_distribution.fractional_distribution_normal import \
    FractionalDistributionNormal
from cu_pass.dpa_calculator.utilities import get_script_directory

EIRP_INDEX_WITHIN_GRANT = 3

NUMBER_OF_COLUMNS_PER_GRANT = 4

NUMBER_OF_CBSD_CHARACTERISTICS_COLUMNS = 4


class SasDataParser:
    def __init__(self, csv_filepath: Path):
        self._csv_filepath = csv_filepath

    def get_eirp_distribution(self) -> FractionalDistributionNormal:
        eirps = [self._get_cbsd_eirp(row=row) for is_nonheader, row in enumerate(self._csv_data) if is_nonheader]
        return FractionalDistributionNormal(
            fraction=1,
            range_maximum=max(eirps),
            range_minimum=min(eirps),
            mean=mean(eirps),
            standard_deviation=stdev(eirps)
        )

    def _get_cbsd_eirp(self, row: List[str]) -> int:
        cbsd_eirps_strings = [grant[EIRP_INDEX_WITHIN_GRANT] for grant in self._get_cbsd_grants(row=row)]
        cbsd_eirps = [round(float(eirp)) for eirp in cbsd_eirps_strings if eirp]
        return max(cbsd_eirps)

    def _get_cbsd_grants(self, row: List[str]) -> List[List[str]]:
        grant_start_indexes = range(NUMBER_OF_CBSD_CHARACTERISTICS_COLUMNS, len(row), NUMBER_OF_COLUMNS_PER_GRANT)
        return [row[grant_start_index:grant_start_index + NUMBER_OF_COLUMNS_PER_GRANT]
                for grant_start_index in grant_start_indexes]

    @property
    def _csv_data(self) -> Iterable[List[str]]:
        with open(self._csv_filepath, newline='') as csvfile:
            yield from csv.reader(csvfile)


if __name__ == '__main__':
    parser = SasDataParser(csv_filepath=Path(get_script_directory(__file__), 'cbsdOverviewData.csv'))
    print(parser.get_eirp_distribution())

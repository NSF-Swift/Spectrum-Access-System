from pathlib import Path

from cu_pass.dpa_calculator.cbsd.cbsd import CbsdCategories
from cu_pass.dpa_calculator.helpers.list_distributor.fractional_distribution.fractional_distribution_normal import \
    FractionalDistributionNormal
from cu_pass.dpa_calculator.srcipts.cbsd_datamining.sas_data_parser import SasDataParser
from cu_pass.dpa_calculator.utilities import get_script_directory
from testcases.cu_pass.dpa_calculator.scripts.cbsd_datamining.eirp import csv_data


class TestSasDataParserEirp:
    def test_eirp_distribution_matches_data(self):
        eirp_distribution = self._get_eirp_distribution(csv_data_filename='fake_sas_data.csv')
        assert eirp_distribution == FractionalDistributionNormal(
            fraction=1,
            range_maximum=37,
            range_minimum=33,
            mean=35,
            standard_deviation=2.8284271247461903
        )

    def test_eirp_handles_fractional_eirp(self):
        eirp_distribution = self._get_eirp_distribution(csv_data_filename='fake_sas_data_fractional_eirp.csv')
        assert eirp_distribution == FractionalDistributionNormal(
            fraction=1,
            range_maximum=37,
            range_minimum=33,
            mean=35.666666666666664,
            standard_deviation=2.309401076758503
        )

    def test_eirp_uses_max_when_different_eirps_for_same_cbsd(self):
        eirp_distribution = self._get_eirp_distribution(csv_data_filename='fake_sas_data_differing_eirps_for_same_cbsd.csv')
        assert eirp_distribution == FractionalDistributionNormal(
            fraction=1,
            range_maximum=37,
            range_minimum=33,
            mean=34.333333333333336,
            standard_deviation=2.309401076758503
        )

    def test_can_distinguish_between_category_a_and_b_eirp(self):
        eirp_distribution = self._get_eirp_distribution(csv_data_filename='fake_sas_data_eirp_with_category_a.csv',
                                                        cbsd_category=CbsdCategories.A)
        assert eirp_distribution == FractionalDistributionNormal(
            fraction=1,
            range_maximum=19,
            range_minimum=19,
            mean=19,
            standard_deviation=0
        )

    def _get_eirp_distribution(self, csv_data_filename: str, cbsd_category: CbsdCategories = CbsdCategories.B) -> FractionalDistributionNormal:
        csv_filepath = Path(self._csv_data_directory, csv_data_filename)
        return SasDataParser(csv_filepath=csv_filepath).get_eirp_distribution(cbsd_category=cbsd_category)

    @property
    def _csv_data_directory(self) -> Path:
        return get_script_directory(csv_data.__file__)

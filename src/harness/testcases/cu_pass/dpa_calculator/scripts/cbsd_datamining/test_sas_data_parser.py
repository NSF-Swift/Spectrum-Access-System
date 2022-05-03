from pathlib import Path

from cu_pass.dpa_calculator.helpers.list_distributor.fractional_distribution.fractional_distribution_normal import \
    FractionalDistributionNormal
from cu_pass.dpa_calculator.srcipts.cbsd_datamining.sas_data_parser import SasDataParser
from cu_pass.dpa_calculator.utilities import get_script_directory
from testcases.cu_pass.dpa_calculator.scripts.cbsd_datamining import csv_data


class TestSasDataParser:
    def test_eirp_distribution_matches_data(self):
        csv_filepath = Path(self.csv_data_directory, 'fake_sas_data.csv')
        eirp_distribution = SasDataParser(csv_filepath=csv_filepath).get_eirp_distribution()
        assert eirp_distribution == FractionalDistributionNormal(
            fraction=1,
            range_maximum=37,
            range_minimum=33,
            mean=35,
            standard_deviation=2.8284271247461903
        )

    def test_eirp_handles_fractional_eirp(self):
        csv_filepath = Path(self.csv_data_directory, 'fake_sas_data_fractional_eirp.csv')
        eirp_distribution = SasDataParser(csv_filepath=csv_filepath).get_eirp_distribution()
        assert eirp_distribution == FractionalDistributionNormal(
            fraction=1,
            range_maximum=37,
            range_minimum=33,
            mean=35.666666666666664,
            standard_deviation=2.309401076758503
        )

    def test_eirp_uses_max_when_different_eirps_for_same_cbsd(self):
        csv_filepath = Path(self.csv_data_directory, 'fake_sas_data_differing_eirps_for_same_cbsd.csv')
        eirp_distribution = SasDataParser(csv_filepath=csv_filepath).get_eirp_distribution()
        assert eirp_distribution == FractionalDistributionNormal(
            fraction=1,
            range_maximum=37,
            range_minimum=33,
            mean=34.333333333333336,
            standard_deviation=2.309401076758503
        )

    @property
    def csv_data_directory(self) -> Path:
        return get_script_directory(csv_data.__file__)

from statistics import mean, stdev
from typing import List

from cu_pass.dpa_calculator.cbsd.cbsd import CbsdCategories
from cu_pass.dpa_calculator.helpers.list_distributor.fractional_distribution.fractional_distribution_normal import \
    FractionalDistributionNormal
from cu_pass.dpa_calculator.srcipts.cbsd_datamining.support.definitions import CbsdInfo


class EirpParser:
    def __init__(self, cbsd_category: CbsdCategories, cbsd_grants: List[CbsdInfo]):
        self._cbsd_category = cbsd_category
        self._cbsd_grants = cbsd_grants

    def get_eirp_distribution(self) -> FractionalDistributionNormal:
        eirps = [self._get_cbsd_eirp(cbsd_info=cbsd_info) for cbsd_info in self._cbsd_category_info]
        return FractionalDistributionNormal(
            fraction=1,
            range_maximum=max(eirps),
            range_minimum=min(eirps),
            mean=mean(eirps),
            standard_deviation=stdev(eirps) if len(eirps) > 1 else 0
        )

    def _get_cbsd_eirp(self, cbsd_info: CbsdInfo) -> int:
        cbsd_eirps = [round(grant.grant_max_eirp) for grant in cbsd_info.grants]
        return max(cbsd_eirps)

    @property
    def _cbsd_category_info(self) -> List[CbsdInfo]:
        return [grant for grant in self._cbsd_grants if grant.cbsd_category == self._cbsd_category]
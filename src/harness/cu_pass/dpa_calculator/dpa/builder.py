from enum import Enum

from cu_pass.dpa_calculator.dpa.dpa import Dpa
from cu_pass.dpa_calculator.dpa.utilities import get_uniform_gain_pattern
from cu_pass.dpa_calculator.utilities import Point
from reference_models.dpa.dpa_builder import ProtectionPoint
from reference_models.dpa.dpa_mgr import BuildDpa

INTERFERENCE_THRESHOLD_PER_10_MHZ_RADIO_ASTRONOMY_IN_DBM = -160


class RadioAstronomyFacilityNames(Enum):
    HatCreek = 'HATCREEK'


_HAT_CREEK_LOCATION = Point(latitude=40.81734, longitude=-121.46933)


CUSTOM_DPA_MAP = {
    RadioAstronomyFacilityNames.HatCreek.value: Dpa(protected_points=[ProtectionPoint(longitude=_HAT_CREEK_LOCATION.longitude, latitude=_HAT_CREEK_LOCATION.latitude)],
                                                    geometry=_HAT_CREEK_LOCATION.to_shapely(),
                                                    name=RadioAstronomyFacilityNames.HatCreek.value,
                                                    threshold=INTERFERENCE_THRESHOLD_PER_10_MHZ_RADIO_ASTRONOMY_IN_DBM,
                                                    radar_height=6.1,
                                                    beamwidth=0.98,
                                                    azimuth_range=(0, 360),
                                                    gain_pattern=None)
}


def get_dpa(dpa_name: str) -> Dpa:
    dpa_name_sanitized = dpa_name.upper().replace(' ', '')
    dpa = CUSTOM_DPA_MAP.get(dpa_name_sanitized, None) or _get_existing_dpa(dpa_name=dpa_name_sanitized)
    if dpa.gain_pattern is None:
        dpa.gain_pattern = get_uniform_gain_pattern()
    return dpa


def _get_existing_dpa(dpa_name: str) -> Dpa:
    dpa_winnforum = BuildDpa(dpa_name=dpa_name)
    return Dpa.from_winnforum_dpa(dpa=dpa_winnforum)

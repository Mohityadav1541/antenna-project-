"""
Core mathematical and physical computation package for antenna array simulation.
"""

from core.physics import (
    SPEED_OF_LIGHT,
    frequency_to_wavelength,
    wavenumber,
    physical_spacing_mm,
    phase_psi,
    deg2rad,
    rad2deg,
)
from core.array_factor import (
    array_factor_summation,
    array_factor_closed_form,
    verify_summation_vs_closed_form,
    compute_normalized_pattern,
)
from core.tapering import (
    get_uniform_weights,
    get_binomial_weights,
    get_hann_weights,
    get_weights_by_type,
)

__all__ = [
    "SPEED_OF_LIGHT",
    "frequency_to_wavelength",
    "wavenumber",
    "physical_spacing_mm",
    "phase_psi",
    "deg2rad",
    "rad2deg",
    "array_factor_summation",
    "array_factor_closed_form",
    "verify_summation_vs_closed_form",
    "compute_normalized_pattern",
    "get_uniform_weights",
    "get_binomial_weights",
    "get_hann_weights",
    "get_weights_by_type",
]

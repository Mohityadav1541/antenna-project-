"""
Physics and constants for linear antenna array simulation.
"""

import numpy as np

# Physical constants
SPEED_OF_LIGHT = 299_792_458.0  # m/s


def frequency_to_wavelength(freq_hz: float) -> float:
    """Calculate wavelength lambda (m) from frequency (Hz)."""
    if freq_hz <= 0:
        raise ValueError("Frequency must be strictly positive.")
    return SPEED_OF_LIGHT / freq_hz


def wavenumber(wavelength_m: float) -> float:
    """Calculate wavenumber k = 2*pi / lambda (rad/m)."""
    if wavelength_m <= 0:
        raise ValueError("Wavelength must be strictly positive.")
    return 2.0 * np.pi / wavelength_m


def physical_spacing_mm(d_over_lambda: float, freq_hz: float) -> float:
    """Calculate physical spacing d in millimeters from d/lambda and frequency in Hz."""
    lam = frequency_to_wavelength(freq_hz)
    return (d_over_lambda * lam) * 1000.0


def phase_psi(theta_rad: np.ndarray, d_over_lambda: float, beta_rad: float) -> np.ndarray:
    """
    Calculate array phase variable:
    psi = kd * cos(theta) + beta
    where kd = 2*pi*(d/lambda).
    theta_rad is measured from the positive array axis (z-axis).
    """
    kd = 2.0 * np.pi * d_over_lambda
    return kd * np.cos(theta_rad) + beta_rad


def deg2rad(deg: float) -> float:
    return float(np.radians(deg))


def rad2deg(rad: float) -> float:
    return float(np.degrees(rad))

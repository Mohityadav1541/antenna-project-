"""
Array factor calculations for uniform and non-uniform linear arrays.
Fulfills Academic Requirement:
- Direct complex summation (Eq 2 and Eq 10)
- Closed form analytical computation (Eq 3)
- Correct handling of removable singularities
- Normalized array factor, power pattern, and dB scale
"""

from typing import Optional, Tuple
import numpy as np
from core.physics import phase_psi


def array_factor_summation(
    theta_rad: np.ndarray,
    N: int,
    d_over_lambda: float,
    beta_rad: float,
    amplitudes: Optional[np.ndarray] = None,
    phases: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Computes array factor via direct complex exponential summation:
    AF(theta) = sum_{n=0}^{N-1} a_n * exp(j * (n * kd * cos(theta) + phi_n))
    
    If amplitudes is None, defaults to uniform a_n = 1.0.
    If phases is None, defaults to progressive phase phi_n = n * beta_rad.
    """
    if N < 2:
        raise ValueError(f"Array must have at least 2 elements, got {N}")

    kd = 2.0 * np.pi * d_over_lambda
    n_idx = np.arange(N)

    if amplitudes is None:
        a_n = np.ones(N, dtype=np.float64)
    else:
        a_n = np.asarray(amplitudes, dtype=np.float64)
        if len(a_n) != N:
            raise ValueError(f"Amplitudes length {len(a_n)} does not match N={N}")

    if phases is None:
        phi_n = n_idx * beta_rad
    else:
        phi_n = np.asarray(phases, dtype=np.float64)
        if len(phi_n) != N:
            raise ValueError(f"Phases length {len(phi_n)} does not match N={N}")

    # Vectorized summation over elements:
    # theta has shape (M,), n has shape (N,)
    # spatial_phase: (N, M) = n[:, None] * kd * cos(theta)[None, :]
    cos_theta = np.cos(theta_rad)
    spatial_phase = np.outer(n_idx * kd, cos_theta)  # shape (N, M)
    total_element_phase = spatial_phase + phi_n[:, np.newaxis]

    phasors = a_n[:, np.newaxis] * np.exp(1j * total_element_phase)
    af = np.sum(phasors, axis=0)
    return af


def array_factor_closed_form(
    theta_rad: np.ndarray,
    N: int,
    d_over_lambda: float,
    beta_rad: float,
) -> np.ndarray:
    """
    Computes array factor for uniform excitation using closed-form expression:
    AF(theta) = exp(j * (N-1) * psi / 2) * sin(N * psi / 2) / sin(psi / 2)
    
    Handles removable singularities where psi = 2 * m * pi (sin(psi / 2) == 0):
    lim_{psi -> 2m*pi} sin(N*psi/2) / sin(psi/2) = N * (-1)**(m * (N - 1))
    """
    if N < 2:
        raise ValueError(f"Array must have at least 2 elements, got {N}")

    psi = phase_psi(theta_rad, d_over_lambda, beta_rad)
    half_psi = psi / 2.0
    denom = np.sin(half_psi)

    # Detect singularities where denom is close to zero (psi = 2 * m * pi)
    # sin(psi/2) = 0 <=> psi/2 = m * pi <=> psi = 2 * m * pi
    is_singular = np.isclose(denom, 0.0, atol=1e-11, rtol=1e-11)

    # Compute numerator
    num = np.sin(N * half_psi)

    # Safe division with placeholder
    safe_denom = np.where(is_singular, 1.0, denom)
    ratio = np.where(is_singular, 0.0, num / safe_denom)

    # Exact limit for singular points:
    # m is nearest integer to psi / (2*pi)
    m = np.round(psi[is_singular] / (2.0 * np.pi))
    sign_factor = (-1.0) ** (m * (N - 1))
    ratio[is_singular] = float(N) * sign_factor

    phase_center = np.exp(1j * (N - 1) * half_psi)
    return phase_center * ratio


def verify_summation_vs_closed_form(
    N: int = 8,
    d_over_lambda: float = 0.5,
    beta_rad: float = 0.0,
    num_points: int = 1801,
    rtol: float = 1e-7,
    atol: float = 1e-7,
) -> Tuple[bool, float]:
    """
    Verifies that direct complex summation matches closed form analytical solution
    across the entire theta range [0, pi], including through singular points.
    Returns (passed, max_absolute_error).
    """
    theta = np.linspace(0, np.pi, num_points)
    af_sum = array_factor_summation(theta, N, d_over_lambda, beta_rad)
    af_closed = array_factor_closed_form(theta, N, d_over_lambda, beta_rad)

    # Magnitude comparison
    mag_sum = np.abs(af_sum)
    mag_closed = np.abs(af_closed)
    max_err = float(np.max(np.abs(mag_sum - mag_closed)))
    passed = bool(np.allclose(mag_sum, mag_closed, rtol=rtol, atol=atol))
    return passed, max_err


def compute_normalized_pattern(
    theta_rad: np.ndarray,
    N: int,
    d_over_lambda: float,
    beta_rad: float,
    amplitudes: Optional[np.ndarray] = None,
    phases: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculates:
    1. Normalized magnitude AF_n(theta) = |AF(theta)| / sum(amplitudes)
    2. Power pattern P_n(theta) = AF_n(theta)^2
    3. Unclipped dB pattern AF_dB(theta) = 20 * log10(AF_n(theta))
    
    Returns (AF_n, P_n, AF_dB).
    """
    af = array_factor_summation(
        theta_rad, N, d_over_lambda, beta_rad, amplitudes=amplitudes, phases=phases
    )
    af_mag = np.abs(af)

    if amplitudes is None:
        norm_factor = float(N)
    else:
        norm_factor = float(np.sum(amplitudes))
        if norm_factor <= 0:
            norm_factor = 1.0

    af_n = af_mag / norm_factor
    # Guard against float precision causing values slightly > 1.0
    af_n = np.clip(af_n, 0.0, 1.0)

    p_n = af_n ** 2

    # Prevent log10(0) with machine epsilon guard for underlying calculation
    eps = 1e-15
    af_db = 20.0 * np.log10(np.maximum(af_n, eps))

    return af_n, p_n, af_db

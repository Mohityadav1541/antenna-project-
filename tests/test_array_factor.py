"""
Unit tests for core array factor computations, singularity handling,
and comparison between direct summation and closed form.
"""

import numpy as np
import pytest
from core.physics import frequency_to_wavelength, physical_spacing_mm, wavenumber, deg2rad
from core.array_factor import (
    array_factor_summation,
    array_factor_closed_form,
    verify_summation_vs_closed_form,
    compute_normalized_pattern,
)
from core.tapering import get_uniform_weights, get_binomial_weights, get_hann_weights


def test_wavenumber_and_wavelength():
    f = 3e9  # 3 GHz
    lam = frequency_to_wavelength(f)
    expected_lam = 299792458.0 / 3e9
    assert np.isclose(lam, expected_lam)
    k = wavenumber(lam)
    assert np.isclose(k, 2.0 * np.pi / lam)
    spacing_mm = physical_spacing_mm(0.5, f)
    assert np.isclose(spacing_mm, 0.5 * lam * 1000.0)


def test_summation_vs_closed_form_broadside():
    """Test N=8, d=0.5 lambda, beta=0 (broadside)."""
    passed, max_err = verify_summation_vs_closed_form(N=8, d_over_lambda=0.5, beta_rad=0.0)
    assert passed
    assert max_err < 1e-10


def test_summation_vs_closed_form_various_parameters():
    """Test across various element counts, spacings, and progressive phases."""
    test_cases = [
        (2, 0.5, 0.0),
        (4, 0.25, np.radians(45.0)),
        (8, 0.5, np.radians(-90.0)),
        (16, 0.75, np.radians(120.0)),
        (32, 1.0, 0.0),
        (64, 1.5, np.radians(-180.0)),
    ]
    for N, d, beta in test_cases:
        passed, max_err = verify_summation_vs_closed_form(N=N, d_over_lambda=d, beta_rad=beta)
        assert passed, f"Failed for N={N}, d={d}, beta={beta} with max_err={max_err}"
        assert max_err < 1e-9


def test_singularity_at_exact_principal_maxima():
    """
    Directly test psi = 0, 2*pi, -2*pi where sin(psi/2) = 0.
    Closed-form must correctly evaluate to N (or N * (-1)**(m*(N-1))) without NaN or inf.
    """
    N = 8
    d = 0.5
    # Broadside: theta = pi/2 gives cos(theta)=0, psi = 0
    theta = np.array([np.pi / 2.0])
    af_closed = array_factor_closed_form(theta, N, d, beta_rad=0.0)
    af_sum = array_factor_summation(theta, N, d, beta_rad=0.0)
    assert not np.isnan(af_closed).any()
    assert not np.isinf(af_closed).any()
    assert np.isclose(np.abs(af_closed[0]), float(N))
    assert np.isclose(np.abs(af_sum[0]), float(N))


def test_normalized_pattern_bounds():
    """Verify AF_n is within [0, 1] and P_n within [0, 1]."""
    # 501 points includes theta = pi/2 exactly
    theta = np.linspace(0, np.pi, 501)
    af_n, p_n, af_db = compute_normalized_pattern(theta, N=8, d_over_lambda=0.5, beta_rad=0.0)
    assert np.all(af_n >= 0.0)
    assert np.all(af_n <= 1.0 + 1e-12)
    assert np.isclose(np.max(af_n), 1.0)
    assert np.isclose(np.max(p_n), 1.0)
    assert np.isclose(np.max(af_db), 0.0)


def test_taper_weights():
    N = 8
    uni = get_uniform_weights(N)
    assert len(uni) == N
    assert np.all(uni == 1.0)

    binom = get_binomial_weights(N)
    assert len(binom) == N
    assert np.isclose(np.max(binom), 1.0)
    # Binomial weights should be symmetric
    assert np.allclose(binom, binom[::-1])

    hann = get_hann_weights(N)
    assert len(hann) == N
    assert np.isclose(np.max(hann), 1.0)
    assert np.allclose(hann, hann[::-1])

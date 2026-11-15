"""
Verification and Validation Suite (Part H).
Tests all 9 benchmark test cases specified in the assignment specification:
1. N=2,  d=0.5, beta=0°     -> Broadside maximum at 90°
2. N=4,  d=0.5, beta=0°     -> Symmetric broadside pattern
3. N=8,  d=0.5, beta=0°     -> Narrower main beam
4. N=8,  d=0.5, beta=-90°   -> Principal beam at 60°
5. N=8,  d=0.5, beta=+90°   -> Principal beam at 120°
6. N=8,  d=0.5, beta=-180°  -> Positive end-fire / boundary beam at 0°
7. N=8,  d=0.5, beta=+180°  -> Negative end-fire / boundary beam at 180°
8. N=8,  d=1.0, beta=0°     -> Multiple equal-height maxima (grating lobes at 0° and 180°)
9. N=16, d=0.5, beta=0°     -> Narrower beam than N=8
"""

import numpy as np
import pytest
from core.array_factor import compute_normalized_pattern
from analysis.pattern_metrics import compute_pattern_metrics
from analysis.steering import compute_steering_phase, compute_achieved_angle


def get_metrics_for_case(N: int, d: float, beta_deg: float, num_pts: int = 3601):
    theta = np.linspace(0, np.pi, num_pts)
    beta_rad = np.radians(beta_deg)
    af_n, p_n, af_db = compute_normalized_pattern(theta, N, d, beta_rad)
    metrics = compute_pattern_metrics(theta, af_n, af_db, N, d, beta_rad)
    return metrics, theta, af_n


def test_case_1_broadside_maximum():
    """Test 1: N=2, d=0.5, beta=0° -> Broadside maximum at 90°."""
    metrics, theta, af_n = get_metrics_for_case(N=2, d=0.5, beta_deg=0.0)
    assert 90.0 in [round(m, 1) for m in metrics.all_maxima_deg]
    assert np.isclose(metrics.main_beam_deg, 90.0, atol=0.1)
    # Analytical error calculation
    analytical_peak = 90.0
    sim_peak = metrics.main_beam_deg
    error = abs(sim_peak - analytical_peak)
    assert error < 1e-4


def test_case_2_symmetric_broadside():
    """Test 2: N=4, d=0.5, beta=0° -> Symmetric broadside pattern."""
    metrics, theta, af_n = get_metrics_for_case(N=4, d=0.5, beta_deg=0.0)
    assert np.isclose(metrics.main_beam_deg, 90.0, atol=0.1)
    # Check pattern symmetry around 90 deg: AF_n(theta) == AF_n(pi - theta)
    assert np.allclose(af_n, af_n[::-1], atol=1e-6)
    # Check HPBW is symmetric around 90 deg
    assert np.isclose(90.0 - metrics.half_power_left_deg, metrics.half_power_right_deg - 90.0, atol=0.1)


def test_case_3_narrower_main_beam_than_n4():
    """Test 3: N=8, d=0.5, beta=0° -> Narrower main beam than N=4."""
    metrics_4, _, _ = get_metrics_for_case(N=4, d=0.5, beta_deg=0.0)
    metrics_8, _, _ = get_metrics_for_case(N=8, d=0.5, beta_deg=0.0)

    assert metrics_8.hpbw_deg is not None
    assert metrics_4.hpbw_deg is not None
    assert metrics_8.hpbw_deg < metrics_4.hpbw_deg
    assert metrics_8.fnbw_deg < metrics_4.fnbw_deg


def test_case_4_steered_to_60():
    """Test 4: N=8, d=0.5, beta=-90° -> Principal beam at 60°."""
    # kd = 2*pi*0.5 = pi = 180°. cos(60°) = 0.5. beta = -kd*cos(60°) = -90°.
    metrics, _, _ = get_metrics_for_case(N=8, d=0.5, beta_deg=-90.0)
    assert np.isclose(metrics.main_beam_deg, 60.0, atol=0.1)
    # Quantitative error:
    error = abs(metrics.main_beam_deg - 60.0)
    assert error < 1e-3


def test_case_5_steered_to_120():
    """Test 5: N=8, d=0.5, beta=+90° -> Principal beam at 120°."""
    # cos(120°) = -0.5. beta = -kd*cos(120°) = +90°.
    metrics, _, _ = get_metrics_for_case(N=8, d=0.5, beta_deg=90.0)
    assert np.isclose(metrics.main_beam_deg, 120.0, atol=0.1)
    error = abs(metrics.main_beam_deg - 120.0)
    assert error < 1e-3


def test_case_6_positive_endfire():
    """Test 6: N=8, d=0.5, beta=-180° -> Positive end-fire / boundary beam at 0°."""
    # beta = -kd = -180°. Peak at theta=0°.
    metrics, _, _ = get_metrics_for_case(N=8, d=0.5, beta_deg=-180.0)
    assert np.isclose(metrics.main_beam_deg, 0.0, atol=0.1)
    # Boundary beam: half power crossing on left does not exist in visible space [0, 180]
    # According to Section 7.5, HPBW and FNBW must be reported as None / Not defined rather than inaccurate.
    assert metrics.half_power_left_deg is None
    assert metrics.hpbw_deg is None


def test_case_7_negative_endfire():
    """Test 7: N=8, d=0.5, beta=+180° -> Negative end-fire / boundary beam at 180°."""
    # beta = +kd = +180°. Peak at theta=180°.
    metrics, _, _ = get_metrics_for_case(N=8, d=0.5, beta_deg=180.0)
    assert np.isclose(metrics.main_beam_deg, 180.0, atol=0.1)
    # Boundary beam: right half-power crossing doesn't exist
    assert metrics.half_power_right_deg is None
    assert metrics.hpbw_deg is None


def test_case_8_grating_lobes_at_d_1_0():
    """Test 8: N=8, d=1.0, beta=0° -> Multiple equal-height maxima (grating lobes)."""
    # kd = 2*pi = 360°. Maxima satisfy kd*cos(theta) = 2*m*pi.
    # For m=1: cos(theta) = 1 => theta = 0°
    # For m=0: cos(theta) = 0 => theta = 90°
    # For m=-1: cos(theta) = -1 => theta = 180°
    metrics, _, _ = get_metrics_for_case(N=8, d=1.0, beta_deg=0.0)
    maxima_rounded = sorted([round(m, 1) for m in metrics.all_maxima_deg])
    assert 0.0 in maxima_rounded
    assert 90.0 in maxima_rounded
    assert 180.0 in maxima_rounded
    assert metrics.grating_lobe_count == 2


def test_case_9_narrower_beam_n16():
    """Test 9: N=16, d=0.5, beta=0° -> Narrower beam than N=8."""
    metrics_8, _, _ = get_metrics_for_case(N=8, d=0.5, beta_deg=0.0)
    metrics_16, _, _ = get_metrics_for_case(N=16, d=0.5, beta_deg=0.0)

    assert metrics_16.hpbw_deg < metrics_8.hpbw_deg
    assert metrics_16.fnbw_deg < metrics_8.fnbw_deg
    # Approximately half the beamwidth:
    ratio = metrics_8.hpbw_deg / metrics_16.hpbw_deg
    assert 1.8 < ratio < 2.2

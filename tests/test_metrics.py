"""
Unit tests for pattern metrics edge cases, interpolation accuracy,
and undefined values (Section 7.5).
"""

import numpy as np
import pytest
from core.array_factor import compute_normalized_pattern
from analysis.pattern_metrics import compute_pattern_metrics


def test_n2_no_sidelobes_undefined():
    """For N=2, d=0.5, beta=0, there are no sidelobes; SLL should be None."""
    theta = np.linspace(0, np.pi, 1801)
    af_n, p_n, af_db = compute_normalized_pattern(theta, N=2, d_over_lambda=0.5, beta_rad=0.0)
    metrics = compute_pattern_metrics(theta, af_n, af_db, N=2, d_over_lambda=0.5, beta_rad=0.0)
    assert metrics.peak_sll_db is None
    assert metrics.peak_sll_angle_deg is None


def test_hpbw_broadside_n8_interpolation():
    """Verify HPBW for N=8, d=0.5, beta=0 is close to standard theoretical value (~12.8°)."""
    theta = np.linspace(0, np.pi, 3601)
    af_n, p_n, af_db = compute_normalized_pattern(theta, N=8, d_over_lambda=0.5, beta_rad=0.0)
    metrics = compute_pattern_metrics(theta, af_n, af_db, N=8, d_over_lambda=0.5, beta_rad=0.0)

    assert metrics.hpbw_deg is not None
    # Theoretical HPBW for uniform array N=8, d=0.5 is 2 * (90° - arccos(2.782 / (N * pi * d)))
    # 2.782 / (8 * pi * 0.5) = 2.782 / 12.56637 = 0.22138
    # arccos(0.22138) = 77.209° => 90° - 77.209° = 12.79°
    assert np.isclose(metrics.hpbw_deg, 12.8, atol=0.2)
    assert np.isclose(metrics.main_beam_deg, 90.0, atol=0.01)


def test_fnbw_broadside_n8():
    """Verify FNBW for N=8, d=0.5, beta=0: nulls are at cos(theta) = +- 2*pi/(N*kd) = +- 2/(8*1) = +- 0.25."""
    # cos(theta) = +- 0.25 => theta = arccos(0.25) = 75.522° and arccos(-0.25) = 104.477°
    # FNBW = 104.477° - 75.522° = 28.955°
    theta = np.linspace(0, np.pi, 3601)
    af_n, p_n, af_db = compute_normalized_pattern(theta, N=8, d_over_lambda=0.5, beta_rad=0.0)
    metrics = compute_pattern_metrics(theta, af_n, af_db, N=8, d_over_lambda=0.5, beta_rad=0.0)

    assert metrics.fnbw_deg is not None
    assert np.isclose(metrics.fnbw_deg, 28.955, atol=0.1)


def test_grating_lobes_large_spacing():
    """For d=1.5 lambda, beta=0, multiple grating lobes exist."""
    theta = np.linspace(0, np.pi, 3601)
    af_n, p_n, af_db = compute_normalized_pattern(theta, N=8, d_over_lambda=1.5, beta_rad=0.0)
    metrics = compute_pattern_metrics(theta, af_n, af_db, N=8, d_over_lambda=1.5, beta_rad=0.0)
    # kd = 3*pi. Principal maxima when kd*cos(theta) = 2*m*pi => cos(theta) = 2m/3
    # m=0 => cos(theta)=0 => 90°
    # m=1 => cos(theta)=2/3 => 48.19°
    # m=-1 => cos(theta)=-2/3 => 131.81°
    # Total 3 maxima => 1 main beam + 2 grating lobes
    assert len(metrics.all_maxima_deg) == 3
    assert metrics.grating_lobe_count == 2

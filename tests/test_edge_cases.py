"""
Edge-case, boundary condition, and extreme parameter stress testing
for Linear Antenna Array Simulation.
"""
import pytest
import numpy as np
from core.physics import wavenumber, frequency_to_wavelength, physical_spacing_mm, phase_psi
from core.array_factor import (
    array_factor_closed_form,
    array_factor_summation,
    compute_normalized_pattern,
)
from core.tapering import get_weights_by_type
from analysis.pattern_metrics import compute_pattern_metrics, find_analytical_maxima, find_analytical_nulls
from analysis.steering import compute_steering_phase, compute_achieved_angle


class TestExtremeParameters:
    def test_n2_minimum_array(self):
        """Test minimal array N=2 at extreme bounds."""
        d_lambda = 0.5
        theta = np.linspace(0, np.pi, 1801)
        af = array_factor_closed_form(theta, 2, d_lambda, 0.0)
        assert not np.isnan(af).any()
        assert not np.isinf(af).any()
        af_n, p_n, af_db = compute_normalized_pattern(theta, 2, d_lambda, 0.0)
        metrics = compute_pattern_metrics(theta, af_n, af_db, 2, d_lambda, 0.0)
        assert metrics.main_beam_deg == pytest.approx(90.0, abs=0.1)
        # N=2 has no sidelobes
        assert metrics.peak_sll_db is None

    def test_n64_maximum_array(self):
        """Test maximal array N=64 for numerical stability and sharp beam."""
        d_lambda = 0.5
        theta = np.linspace(0, np.pi, 3601)  # fine resolution for 64 elements
        af = array_factor_closed_form(theta, 64, d_lambda, 0.0)
        assert not np.isnan(af).any()
        assert not np.isinf(af).any()
        af_n, p_n, af_db = compute_normalized_pattern(theta, 64, d_lambda, 0.0)
        metrics = compute_pattern_metrics(theta, af_n, af_db, 64, d_lambda, 0.0)
        assert metrics.main_beam_deg == pytest.approx(90.0, abs=0.1)
        # Beamwidth should be very narrow (< 2 degrees)
        assert metrics.hpbw_deg is not None
        assert 1.0 < metrics.hpbw_deg < 2.0
        # FNBW should be ~ 3.58 degrees
        assert metrics.fnbw_deg is not None
        assert 3.0 < metrics.fnbw_deg < 4.0

    def test_extreme_dense_spacing_d005(self):
        """Test d/lambda = 0.05 (electrically very compact array)."""
        theta = np.linspace(0, np.pi, 1801)
        af = array_factor_closed_form(theta, 8, 0.05, 0.0)
        assert not np.isnan(af).any()
        af_n, p_n, af_db = compute_normalized_pattern(theta, 8, 0.05, 0.0)
        metrics = compute_pattern_metrics(theta, af_n, af_db, 8, 0.05, 0.0)
        assert metrics.main_beam_deg == pytest.approx(90.0, abs=0.1)
        assert len(metrics.nulls_deg) == 0  # No nulls can fit in visible space

    def test_extreme_sparse_spacing_d200(self):
        """Test d/lambda = 2.0 (electrically very sparse array, multiple grating lobes)."""
        theta = np.linspace(0, np.pi, 1801)
        af = array_factor_closed_form(theta, 8, 2.0, 0.0)
        assert not np.isnan(af).any()
        af_n, p_n, af_db = compute_normalized_pattern(theta, 8, 2.0, 0.0)
        metrics = compute_pattern_metrics(theta, af_n, af_db, 8, 2.0, 0.0)
        # Multiple major lobes exist in [0, 180]
        assert metrics.grating_lobe_count > 0
        assert len(metrics.grating_lobes_deg) > 0

    def test_extreme_frequencies(self):
        """Test physical conversions at 0.1 GHz and 30.0 GHz."""
        # 0.1 GHz = 100 MHz
        lam_low = frequency_to_wavelength(0.1 * 1e9)
        assert lam_low == pytest.approx(2.99792458, rel=1e-5)
        d_mm_low = physical_spacing_mm(0.5, 0.1 * 1e9)
        assert d_mm_low == pytest.approx(1498.96, rel=1e-3)

        # 30.0 GHz
        lam_high = frequency_to_wavelength(30.0 * 1e9)
        assert lam_high == pytest.approx(0.009993, rel=1e-4)
        d_mm_high = physical_spacing_mm(0.5, 30.0 * 1e9)
        assert d_mm_high == pytest.approx(4.9965, rel=1e-3)

    def test_phase_extreme_plus_minus_360(self):
        """Test beta = +/- 360 deg wraps cleanly."""
        theta = np.linspace(0, np.pi, 1801)
        # beta = 360 deg is 2*pi radians, identical to beta = 0 in exp(j*m*2*pi)
        af_360 = array_factor_summation(theta, 8, 0.5, 2 * np.pi)
        af_0 = array_factor_summation(theta, 8, 0.5, 0.0)
        np.testing.assert_allclose(np.abs(af_360), np.abs(af_0), atol=1e-12)

        af_m360 = array_factor_summation(theta, 8, 0.5, -2 * np.pi)
        np.testing.assert_allclose(np.abs(af_m360), np.abs(af_0), atol=1e-12)


class TestBoundaryAndSteeringEdgeCases:
    def test_beam_steered_outside_visible_space(self):
        """
        When beta is chosen such that |beta / kd| > 1 and no integer m gives |(2mpi - beta)/kd| <= 1.
        E.g., d/lambda = 0.25 -> kd = pi/2 = 90 deg.
        If beta = 135 deg:
        m=0: (0 - 135)/90 = -1.5 (outside [-1, 1])
        m=1: (360 - 135)/90 = 225/90 = 2.5 (outside [-1, 1])
        In this case, the principal beam peak is in invisible space.
        compute_achieved_angle should correctly report None (no principal maximum in visible space).
        """
        d_lambda = 0.25
        beta_rad = np.radians(135.0)
        achieved = compute_achieved_angle(beta_rad, d_lambda)
        assert achieved is None

        # Closed form and summation should still compute smoothly with zero NaNs
        theta = np.linspace(0, np.pi, 1801)
        af = array_factor_closed_form(theta, 8, d_lambda, beta_rad)
        assert not np.isnan(af).any()
        assert not np.isinf(af).any()

    def test_zero_excitation_vector_handling(self):
        """Test handling of all-zero amplitude weights gracefully."""
        theta = np.linspace(0, np.pi, 181)
        zeros_w = np.zeros(8)
        af = array_factor_summation(theta, 8, 0.5, 0.0, amplitudes=zeros_w)
        assert (af == 0).all()
        # compute_normalized_pattern handles all-zero weights by setting norm to 1.0 to avoid ZeroDivisionError
        af_n, p_n, af_db = compute_normalized_pattern(theta, 8, 0.5, 0.0, amplitudes=zeros_w)
        assert not np.isnan(af_n).any()
        assert not np.isinf(af_n).any()

    def test_single_element_nonzero_custom_weights(self):
        """If only one element is active, radiation pattern should be omnidirectional (AF = const)."""
        theta = np.linspace(0, np.pi, 181)
        w = np.array([1.0, 0.0, 0.0, 0.0])
        af_n, p_n, af_db = compute_normalized_pattern(theta, 4, 0.5, 0.0, amplitudes=w)
        # |AF_n| should be identically 1.0 everywhere
        np.testing.assert_allclose(af_n, 1.0, atol=1e-12)

    def test_boundary_hpbw_at_near_endfire(self):
        """
        Steered close to endfire, e.g. theta_0 = 5 degrees.
        One half-power crossing may be clipped at theta = 0.
        Metrics should report boundary or single-sided beamwidth without crashing.
        """
        theta = np.linspace(0, np.pi, 1801)
        beta_rad = compute_steering_phase(np.radians(5.0), 0.5)
        af_n, p_n, af_db = compute_normalized_pattern(theta, 8, 0.5, beta_rad)
        metrics = compute_pattern_metrics(
            theta, af_n, af_db, 8, 0.5, beta_rad, selected_steering_theta_deg=5.0
        )
        assert metrics.main_beam_deg is not None
        # Handled gracefully (either float if double crossing found or None if boundary-clipped)
        assert metrics.hpbw_deg is None or metrics.hpbw_deg > 0

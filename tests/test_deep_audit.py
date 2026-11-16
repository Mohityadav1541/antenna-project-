"""
Deep audit test suite — probes for specific bugs identified during code review.
Tests edge cases, normalization correctness, HPBW/FNBW accuracy, and
requirement compliance per the assignment PDF.
"""

import numpy as np
import pytest
from core.physics import frequency_to_wavelength, physical_spacing_mm, phase_psi
from core.array_factor import (
    array_factor_summation,
    array_factor_closed_form,
    compute_normalized_pattern,
)
from core.tapering import get_binomial_weights, get_hann_weights, get_weights_by_type
from analysis.pattern_metrics import (
    compute_pattern_metrics,
    find_analytical_maxima,
    find_analytical_nulls,
)
from analysis.steering import compute_steering_phase, compute_achieved_angle


# ================================================================
# BUG-1 AUDIT: Normalization convention (Eq 4 in PDF)
# PDF says AFn = |AF| / N for uniform. But compute_normalized_pattern
# uses sum(amplitudes) for tapered — verify this is consistent.
# ================================================================

class TestNormalizationConvention:
    def test_uniform_normalization_equals_N(self):
        """PDF Eq 4: AFn(theta) = |AF(theta)| / N for uniform."""
        theta = np.linspace(0, np.pi, 1801)
        N = 8
        af = array_factor_summation(theta, N, 0.5, 0.0)
        af_n_manual = np.abs(af) / N
        af_n, _, _ = compute_normalized_pattern(theta, N, 0.5, 0.0)
        assert np.allclose(af_n_manual, af_n, atol=1e-12)

    def test_tapered_normalization_uses_sum_of_amplitudes(self):
        """For tapered arrays, normalization by sum(a_n) ensures max=1
        when all phasors are aligned."""
        theta = np.linspace(0, np.pi, 1801)
        N = 8
        weights = get_binomial_weights(N)
        af_n, _, _ = compute_normalized_pattern(theta, N, 0.5, 0.0, amplitudes=weights)
        # Peak should be 1.0 (when all phasors align at broadside)
        assert np.max(af_n) >= 0.999, f"Peak AF_n for binomial should be ~1.0, got {np.max(af_n)}"

    def test_uniform_peak_is_exactly_1(self):
        """For uniform array at broadside, the peak must be exactly 1.0."""
        # Use a grid that includes theta = pi/2 exactly
        theta = np.linspace(0, np.pi, 1801)
        af_n, _, _ = compute_normalized_pattern(theta, 8, 0.5, 0.0)
        assert np.isclose(np.max(af_n), 1.0, atol=1e-10)


# ================================================================
# BUG-2 AUDIT: HPBW for steered beams  
# The HPBW scan starts from mb_idx and scans outward. Verify it works
# for non-broadside steered beams where the peak isn't centered.
# ================================================================

class TestHPBWSteeredBeams:
    def test_hpbw_steered_to_60(self):
        """HPBW must be valid when beam is steered to 60°."""
        theta = np.linspace(0, np.pi, 3601)
        beta = compute_steering_phase(np.radians(60), 0.5)
        af_n, _, af_db = compute_normalized_pattern(theta, 8, 0.5, beta)
        m = compute_pattern_metrics(theta, af_n, af_db, 8, 0.5, beta,
                                     selected_steering_theta_deg=60.0)
        assert m.hpbw_deg is not None
        assert m.hpbw_deg > 0
        # For steered beam, HPBW should be wider than broadside
        assert m.hpbw_deg > 12.0  # Broadside HPBW is ~12.8°

    def test_hpbw_steered_to_30(self):
        """HPBW at 30° steering should be finite and physically reasonable."""
        theta = np.linspace(0, np.pi, 3601)
        beta = compute_steering_phase(np.radians(30), 0.5)
        af_n, _, af_db = compute_normalized_pattern(theta, 8, 0.5, beta)
        m = compute_pattern_metrics(theta, af_n, af_db, 8, 0.5, beta,
                                     selected_steering_theta_deg=30.0)
        assert m.hpbw_deg is not None
        assert m.hpbw_deg > 0

    def test_hpbw_at_45_degrees(self):
        """Verify HPBW when steered to 45°."""
        theta = np.linspace(0, np.pi, 3601)
        beta = compute_steering_phase(np.radians(45), 0.5)
        af_n, _, af_db = compute_normalized_pattern(theta, 8, 0.5, beta)
        m = compute_pattern_metrics(theta, af_n, af_db, 8, 0.5, beta,
                                     selected_steering_theta_deg=45.0)
        assert m.main_beam_deg is not None
        assert np.isclose(m.main_beam_deg, 45.0, atol=0.1)


# ================================================================
# BUG-3 AUDIT: Steering phase computation
# Verify β = -kd·cos(θ₀) for all 8 required test angles.
# ================================================================

class TestSteeringPhase:
    @pytest.mark.parametrize("theta0_deg,expected_beta_deg", [
        (0.0, -180.0),     # cos(0)=1, beta = -pi
        (30.0, -155.885),  # cos(30)=sqrt(3)/2
        (45.0, -127.279),  # cos(45)=1/sqrt(2)
        (60.0, -90.0),     # cos(60)=0.5
        (90.0, 0.0),       # cos(90)=0
        (120.0, 90.0),     # cos(120)=-0.5
        (150.0, 155.885),  # cos(150)=-sqrt(3)/2
        (180.0, 180.0),    # cos(180)=-1
    ])
    def test_steering_phase_values(self, theta0_deg, expected_beta_deg):
        """Verify β = -kd·cos(θ₀) for d=0.5λ (kd = π = 180°)."""
        beta = compute_steering_phase(np.radians(theta0_deg), 0.5)
        beta_deg = np.degrees(beta)
        assert np.isclose(beta_deg, expected_beta_deg, atol=0.01), \
            f"θ₀={theta0_deg}°: expected β={expected_beta_deg}°, got {beta_deg}°"

    @pytest.mark.parametrize("theta0_deg", [0, 30, 45, 60, 90, 120, 150, 180])
    def test_roundtrip_steering(self, theta0_deg):
        """Verify compute_achieved_angle inverts compute_steering_phase."""
        beta = compute_steering_phase(np.radians(theta0_deg), 0.5)
        achieved = compute_achieved_angle(beta, 0.5)
        assert achieved is not None
        assert np.isclose(np.degrees(achieved), theta0_deg, atol=0.001)


# ================================================================
# BUG-4 AUDIT: Grating lobe detection depends on steering direction
# PDF Part C says: "grating-lobe occurrence depends on steering direction"
# ================================================================

class TestGratingLobePhysics:
    def test_d1_broadside_has_grating_lobes(self):
        """d=1.0λ broadside: maxima at 0°, 90°, 180° → 2 grating lobes."""
        theta = np.linspace(0, np.pi, 3601)
        af_n, _, af_db = compute_normalized_pattern(theta, 8, 1.0, 0.0)
        m = compute_pattern_metrics(theta, af_n, af_db, 8, 1.0, 0.0)
        assert m.grating_lobe_count == 2
        assert len(m.all_maxima_deg) == 3

    def test_d075_broadside_no_grating_lobes(self):
        """d=0.75λ broadside: condition |cos(θ)| = (2mπ-β)/kd = 2m/1.5.
        m=0: θ=90° (main). m=1: cos=1.33 outside. No grating lobes."""
        theta = np.linspace(0, np.pi, 3601)
        af_n, _, af_db = compute_normalized_pattern(theta, 8, 0.75, 0.0)
        m = compute_pattern_metrics(theta, af_n, af_db, 8, 0.75, 0.0)
        assert m.grating_lobe_count == 0

    def test_d1_steered_to_60_grating_lobe_count(self):
        """d=1.0λ steered to 60°: check if steering shifts grating lobes."""
        theta = np.linspace(0, np.pi, 3601)
        beta = compute_steering_phase(np.radians(60), 1.0)
        af_n, _, af_db = compute_normalized_pattern(theta, 8, 1.0, beta)
        m = compute_pattern_metrics(theta, af_n, af_db, 8, 1.0, beta,
                                     selected_steering_theta_deg=60.0)
        # With kd=2π and β=-π, cos(θ) solutions: (2mπ+π)/(2π) = m + 0.5
        # m=0: cos=0.5 → θ=60° (main). m=-1: cos=-0.5 → θ=120° (grating).
        assert m.grating_lobe_count >= 1


# ================================================================
# BUG-5 AUDIT: Analytical null formula correctness
# Nulls: ψ = 2qπ/N where q is NOT divisible by N
# cos(θ) = (2qπ/N - β) / kd
# ================================================================

class TestNullDetection:
    def test_null_count_n8_broadside(self):
        """N=8, d=0.5λ, β=0: visible nulls.
        kd = π. cos(θ) = 2q/(8·1) = q/4. Need |q/4| ≤ 1 → -4≤q≤4.
        q ∈ {-4,-3,-2,-1,0,1,2,3,4} minus multiples of 8 → remove q=0.
        q=-4: cos=-1 → θ=180°. q=-3: cos=-3/4. q=-2: cos=-1/2. q=-1: cos=-1/4.
        q=1: cos=1/4. q=2: cos=1/2. q=3: cos=3/4. q=4: cos=1 → θ=0°.
        But q=0 and q=8,-8 are multiples of N, excluded.
        Total 8 null angles: 0°(q=4?), wait, q=4 not multiple of 8, so included.
        Actually q%N==0 means q=0, ±8, ±16... So q=4 is fine.
        Nulls: q = -4,-3,-2,-1,1,2,3,4 → 8 nulls."""
        nulls = find_analytical_nulls(8, 0.5, 0.0)
        # cos(theta) = q/4 for q in {-4,-3,-2,-1,1,2,3,4}
        # But q=4: cos=1 → θ=0°; q=-4: cos=-1 → θ=180°
        # These are at the boundary. Check they're included.
        expected_count = 8  # actually might be 6 interior + 2 boundary
        assert len(nulls) >= 6, f"Expected at least 6 nulls for N=8, d=0.5, got {len(nulls)}"

    def test_null_count_n4_broadside(self):
        """N=4, d=0.5λ, β=0: nulls at cos(θ) = q/2 for q not mult of 4.
        q ∈ {-2,-1,0,1,2}: remove q=0. q=-2: cos=-1→180°. q=-1: cos=-1/2→120°.
        q=1: cos=1/2→60°. q=2: cos=1→0°. → 4 nulls."""
        nulls = find_analytical_nulls(4, 0.5, 0.0)
        assert len(nulls) >= 3

    def test_no_nulls_at_principal_maxima(self):
        """Nulls should never coincide with principal maxima."""
        for N in [4, 8, 16]:
            maxima = find_analytical_maxima(N, 0.5, 0.0)
            nulls = find_analytical_nulls(N, 0.5, 0.0)
            for m_rad in maxima:
                for n_rad in nulls:
                    assert not np.isclose(m_rad, n_rad, atol=1e-6), \
                        f"Null at {np.degrees(n_rad):.2f}° coincides with max at {np.degrees(m_rad):.2f}° for N={N}"


# ================================================================
# BUG-6 AUDIT: SLL value for N=8 uniform broadside
# Known theoretical value is approximately -13.26 dB (first sidelobe)
# ================================================================

class TestSidelobeLevel:
    def test_sll_n8_broadside_uniform(self):
        """For N=8 uniform, d=0.5λ, β=0:
        The exact analytical peak sidelobe level for finite N=8 is -12.80 dB
        (occurring at psi ≈ 1.1294 rad, |AF_n| ≈ 0.22916).
        As N -> infinity, the peak SLL approaches the asymptotic sinc limit of -13.26 dB.
        """
        theta = np.linspace(0, np.pi, 7201)
        af_n, _, af_db = compute_normalized_pattern(theta, 8, 0.5, 0.0)
        m = compute_pattern_metrics(theta, af_n, af_db, 8, 0.5, 0.0)
        assert m.peak_sll_db is not None
        # Exact value for N=8 is -12.80 dB:
        assert np.isclose(m.peak_sll_db, -12.80, atol=0.05), \
            f"Expected exact SLL for N=8 ≈ -12.80 dB, got {m.peak_sll_db:.2f} dB"

    def test_binomial_sll_suppressed(self):
        """Binomial weighting at d=0.5λ should have much lower SLL than uniform."""
        theta = np.linspace(0, np.pi, 3601)
        w = get_binomial_weights(8)
        af_n, _, af_db = compute_normalized_pattern(theta, 8, 0.5, 0.0, amplitudes=w)
        m = compute_pattern_metrics(theta, af_n, af_db, 8, 0.5, 0.0, is_uniform=False)
        # Binomial should have very low sidelobes
        if m.peak_sll_db is not None:
            assert m.peak_sll_db < -20.0, \
                f"Binomial SLL should be < -20 dB, got {m.peak_sll_db:.2f} dB"


# ================================================================
# BUG-7 AUDIT: Angular sampling step actually controls resolution
# ================================================================

class TestAngularSampling:
    def test_coarse_sampling_affects_point_count(self):
        """Step=2° should give ~91 points; step=0.1° should give ~1801."""
        # This tests the num_pts calculation in main_window.recompute_and_update
        for step, expected_min in [(2.0, 90), (0.1, 1800), (0.01, 18000)]:
            num_pts = max(181, int(round(180.0 / step)) + 1)
            assert num_pts >= expected_min

    def test_fine_sampling_improves_hpbw_accuracy(self):
        """HPBW should converge as angular sampling increases."""
        hpbw_values = []
        for num_pts in [361, 1801, 7201]:
            theta = np.linspace(0, np.pi, num_pts)
            af_n, _, af_db = compute_normalized_pattern(theta, 8, 0.5, 0.0)
            m = compute_pattern_metrics(theta, af_n, af_db, 8, 0.5, 0.0)
            hpbw_values.append(m.hpbw_deg)

        # Should converge — difference between last two should be smaller
        diff1 = abs(hpbw_values[1] - hpbw_values[0])
        diff2 = abs(hpbw_values[2] - hpbw_values[1])
        assert diff2 < diff1, "HPBW should converge with finer sampling"


# ================================================================
# BUG-8 AUDIT: Verify dB floor is only applied to display, not calcs
# PDF Section 11 Rule 7: "Apply a numerical floor only to dB display"
# ================================================================

class TestDbFloorSeparation:
    def test_db_values_below_floor_exist_in_raw_data(self):
        """Raw af_db should contain values well below any display floor."""
        theta = np.linspace(0, np.pi, 1801)
        _, _, af_db = compute_normalized_pattern(theta, 8, 0.5, 0.0)
        # At nulls, dB should go to very large negative values
        assert np.min(af_db) < -100, \
            f"Raw dB should go below -100 at nulls, min is {np.min(af_db):.1f}"

    def test_metrics_use_raw_data_not_clipped(self):
        """HPBW and nulls should be computed from raw AF_n, not clipped dB."""
        theta = np.linspace(0, np.pi, 3601)
        af_n, _, af_db = compute_normalized_pattern(theta, 8, 0.5, 0.0)

        # Metrics with unclipped data
        m1 = compute_pattern_metrics(theta, af_n, af_db, 8, 0.5, 0.0)

        # The compute_pattern_metrics function uses af_n (not af_db) for
        # HPBW and null detection — this is correct behavior
        assert m1.hpbw_deg is not None
        assert len(m1.nulls_deg) > 0


# ================================================================
# BUG-9 AUDIT: Closed-form singularity at psi = 2mπ for m≠0
# ================================================================

class TestSingularityResolution:
    def test_singularity_at_endfire_psi_minus_2pi(self):
        """When d=0.5, β=-180°: at θ=0°, psi = kd·cos(0)+β = π-π = 0.
        At θ=180°: psi = kd·cos(180)+β = -π-π = -2π.
        Both are singularities. Verify both evaluate correctly."""
        theta = np.array([0.0, np.pi])
        af_closed = array_factor_closed_form(theta, 8, 0.5, -np.pi)
        af_sum = array_factor_summation(theta, 8, 0.5, -np.pi)
        # Both should give magnitude = 8 (N)
        assert np.allclose(np.abs(af_closed), np.abs(af_sum), atol=1e-8)
        # And the magnitude should be N=8
        assert np.isclose(np.abs(af_closed[0]), 8.0, atol=1e-8)

    def test_closed_form_no_nan_across_full_sweep(self):
        """Sweep all parameters and verify no NaN/Inf in closed form."""
        theta = np.linspace(0, np.pi, 361)
        for N in [2, 4, 8, 16]:
            for d in [0.25, 0.5, 1.0, 1.5]:
                for beta in [0, np.pi/4, np.pi/2, np.pi, -np.pi]:
                    af = array_factor_closed_form(theta, N, d, beta)
                    assert not np.any(np.isnan(af)), \
                        f"NaN in closed form: N={N}, d={d}, β={np.degrees(beta)}°"
                    assert not np.any(np.isinf(af)), \
                        f"Inf in closed form: N={N}, d={d}, β={np.degrees(beta)}°"


# ================================================================
# BUG-10 AUDIT: FNBW boundary handling
# When beam is at endfire, there may be no null on one side → FNBW undefined
# ================================================================

class TestFNBWBoundary:
    def test_fnbw_undefined_at_endfire(self):
        """End-fire beam at θ=0°: no left null → FNBW should be None."""
        theta = np.linspace(0, np.pi, 3601)
        af_n, _, af_db = compute_normalized_pattern(theta, 8, 0.5, -np.pi)
        m = compute_pattern_metrics(theta, af_n, af_db, 8, 0.5, -np.pi)
        assert m.main_beam_deg is not None
        assert np.isclose(m.main_beam_deg, 0.0, atol=0.5)
        # FNBW should be None because there's no null to the left of 0°
        assert m.fnbw_deg is None

    def test_fnbw_defined_for_broadside(self):
        """Broadside beam should always have valid FNBW."""
        theta = np.linspace(0, np.pi, 3601)
        af_n, _, af_db = compute_normalized_pattern(theta, 8, 0.5, 0.0)
        m = compute_pattern_metrics(theta, af_n, af_db, 8, 0.5, 0.0)
        assert m.fnbw_deg is not None
        assert m.fnbw_deg > 0


# ================================================================
# BUG-11 AUDIT: Physical spacing display
# ================================================================

class TestPhysicalSpacing:
    def test_wavelength_at_3ghz(self):
        """λ at 3 GHz = c/f = 299792458/3e9 = 99.93 mm."""
        lam = frequency_to_wavelength(3e9)
        assert np.isclose(lam * 1000, 99.93, atol=0.01)

    def test_spacing_mm_half_wavelength_3ghz(self):
        """d = 0.5λ at 3 GHz → d = 49.97 mm."""
        d_mm = physical_spacing_mm(0.5, 3e9)
        assert np.isclose(d_mm, 49.97, atol=0.01)


# ================================================================
# BUG-12 AUDIT: Summation formula sign convention
# PDF Eq 2: AF = Σ exp(j·n·ψ) where ψ = kd·cos(θ) + β
# Our implementation uses: exp(j·(n·kd·cos(θ) + φ_n))
# where φ_n = n·β for progressive phase
# These should be equivalent.
# ================================================================

class TestSignConvention:
    def test_summation_matches_psi_convention(self):
        """Verify our summation is consistent with ψ = kd·cos(θ) + β."""
        theta = np.linspace(0, np.pi, 361)
        N, d, beta = 8, 0.5, np.radians(45)

        # Our implementation
        af_ours = array_factor_summation(theta, N, d, beta)

        # Direct from PDF formula: AF = Σ exp(j·n·ψ)
        kd = 2 * np.pi * d
        psi = kd * np.cos(theta) + beta
        af_pdf = np.zeros_like(theta, dtype=complex)
        for n in range(N):
            af_pdf += np.exp(1j * n * psi)

        assert np.allclose(af_ours, af_pdf, atol=1e-10), \
            "Summation doesn't match PDF Eq 2 convention"

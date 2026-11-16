"""
Automated numerical detection and analytical calculation of antenna pattern metrics (Part E).
Computes:
- Principal maxima and grating lobes
- Visible nulls
- Half-Power Beamwidth (HPBW) with interpolation
- First-Null Beamwidth (FNBW)
- Peak Sidelobe Level (SLL)
- Robust handling of boundary / end-fire conditions
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np
from scipy.signal import find_peaks
from core.physics import deg2rad, rad2deg


@dataclass
class PatternMetrics:
    all_maxima_deg: List[float]
    main_beam_deg: Optional[float]
    grating_lobes_deg: List[float]
    grating_lobe_count: int
    nulls_deg: List[float]
    hpbw_deg: Optional[float]
    half_power_left_deg: Optional[float]
    half_power_right_deg: Optional[float]
    fnbw_deg: Optional[float]
    first_null_left_deg: Optional[float]
    first_null_right_deg: Optional[float]
    peak_sll_db: Optional[float]
    peak_sll_angle_deg: Optional[float]
    kd_rad: float
    kd_deg: float
    beta_rad: float
    beta_deg: float


def find_analytical_maxima(
    N: int,
    d_over_lambda: float,
    beta_rad: float,
) -> List[float]:
    """
    Finds visible principal maxima analytically:
    psi = 2 * m * pi  =>  kd * cos(theta) + beta = 2 * m * pi
    cos(theta) = (2 * m * pi - beta) / kd
    Valid if |cos(theta)| <= 1, where theta in [0, pi].
    """
    kd = 2.0 * np.pi * d_over_lambda
    if kd <= 0:
        return []

    # Maximum possible range for integer m:
    # -1 <= (2*m*pi - beta)/kd <= 1
    # -kd + beta <= 2*m*pi <= kd + beta
    m_min = int(np.floor((-kd + beta_rad) / (2.0 * np.pi))) - 1
    m_max = int(np.ceil((kd + beta_rad) / (2.0 * np.pi))) + 1

    maxima = []
    for m in range(m_min, m_max + 1):
        cos_theta = (2.0 * m * np.pi - beta_rad) / kd
        if np.isclose(abs(cos_theta), 1.0, atol=1e-9):
            cos_theta = np.clip(cos_theta, -1.0, 1.0)
        if abs(cos_theta) <= 1.0:
            theta = float(np.arccos(cos_theta))
            maxima.append(theta)

    maxima = sorted(list(set(np.round(maxima, 8))))
    return maxima


def find_analytical_nulls(
    N: int,
    d_over_lambda: float,
    beta_rad: float,
) -> List[float]:
    """
    Finds visible nulls analytically for uniform array:
    psi = 2 * q * pi / N, where q is NOT a multiple of N.
    cos(theta) = (2 * q * pi / N - beta) / kd
    """
    kd = 2.0 * np.pi * d_over_lambda
    if kd <= 0:
        return []

    q_min = int(np.floor(N * (-kd + beta_rad) / (2.0 * np.pi))) - 1
    q_max = int(np.ceil(N * (kd + beta_rad) / (2.0 * np.pi))) + 1

    nulls = []
    for q in range(q_min, q_max + 1):
        if q % N == 0:
            continue  # Multiple of N gives principal maximum, not a null
        cos_theta = (2.0 * q * np.pi / N - beta_rad) / kd
        if np.isclose(abs(cos_theta), 1.0, atol=1e-9):
            cos_theta = np.clip(cos_theta, -1.0, 1.0)
        if abs(cos_theta) <= 1.0:
            theta = float(np.arccos(cos_theta))
            nulls.append(theta)

    nulls = sorted(list(set(np.round(nulls, 8))))
    return nulls


def compute_pattern_metrics(
    theta_rad: np.ndarray,
    af_n: np.ndarray,
    af_db: np.ndarray,
    N: int,
    d_over_lambda: float,
    beta_rad: float,
    selected_steering_theta_deg: Optional[float] = None,
    is_uniform: bool = True,
) -> PatternMetrics:
    """
    Computes all radiation pattern metrics according to Parts E, F, and H:
    - Principal maxima and grating lobes
    - Null directions
    - HPBW via half-power interpolation
    - FNBW
    - Peak SLL
    """
    kd = 2.0 * np.pi * d_over_lambda
    theta_deg = np.degrees(theta_rad)

    # 1. Principal maxima
    if is_uniform:
        maxima_rad = find_analytical_maxima(N, d_over_lambda, beta_rad)
        all_maxima_deg = [float(np.degrees(th)) for th in maxima_rad]
    else:
        # For tapered array, find peaks in af_n where af_n is near peak (>= 0.999)
        peaks, props = find_peaks(af_n, height=0.99)
        all_maxima_deg = [float(theta_deg[p]) for p in peaks]
        if not all_maxima_deg:
            # Fallback to argmax
            all_maxima_deg = [float(theta_deg[np.argmax(af_n)])]

    # Select main beam
    if not all_maxima_deg:
        main_beam_deg = None
        grating_lobes_deg = []
    else:
        if selected_steering_theta_deg is not None:
            target_angle = selected_steering_theta_deg
        else:
            # Infer nominal steering angle from beta: cos(theta0) = -beta / kd
            if kd > 0 and abs(-beta_rad / kd) <= 1.0 + 1e-9:
                cos_val = np.clip(-beta_rad / kd, -1.0, 1.0)
                target_angle = float(np.degrees(np.arccos(cos_val)))
            else:
                target_angle = 90.0  # default broadside

        main_beam_deg = min(all_maxima_deg, key=lambda m: abs(m - target_angle))

        # Grating lobes are other equal-height principal maxima
        grating_lobes_deg = [m for m in all_maxima_deg if not np.isclose(m, main_beam_deg, atol=0.05)]

    grating_lobe_count = len(grating_lobes_deg)

    # 2. Nulls
    if is_uniform:
        nulls_rad = find_analytical_nulls(N, d_over_lambda, beta_rad)
        nulls_deg = [float(np.degrees(th)) for th in nulls_rad]
    else:
        # Numerical nulls for tapered arrays:
        # Use prominence to reject floating-point roundoff noise in deep attenuation basins
        peaks, _ = find_peaks(-af_n, prominence=0.002)
        interior_nulls = [float(theta_deg[p]) for p in peaks if af_n[p] < 0.05]

        # Check boundary nulls at theta = 0° and theta = 180°
        boundary_nulls = []
        if af_n[0] < 1e-3:
            boundary_nulls.append(0.0)
        if af_n[-1] < 1e-3:
            boundary_nulls.append(180.0)

        nulls_deg = sorted(list(set(boundary_nulls + interior_nulls)))

    # 3. HPBW with linear interpolation
    # Half power is P_n = 0.5 <=> AF_n = 1/sqrt(2) approx 0.70710678 or AF_dB = -3.0103 dB
    half_power_target = 1.0 / np.sqrt(2.0)
    hpbw_deg = None
    hp_left_deg = None
    hp_right_deg = None

    if main_beam_deg is not None:
        mb_idx = int(np.argmin(np.abs(theta_deg - main_beam_deg)))

        # Scan left (towards 0 degrees, index decreasing)
        left_cross_idx = None
        for i in range(mb_idx, 0, -1):
            if af_n[i] >= half_power_target and af_n[i - 1] < half_power_target:
                left_cross_idx = i
                break

        if left_cross_idx is not None:
            # Interpolate between left_cross_idx - 1 and left_cross_idx
            th1, th2 = theta_deg[left_cross_idx - 1], theta_deg[left_cross_idx]
            v1, v2 = af_n[left_cross_idx - 1], af_n[left_cross_idx]
            if not np.isclose(v1, v2):
                hp_left_deg = float(th1 + (half_power_target - v1) * (th2 - th1) / (v2 - v1))
            else:
                hp_left_deg = float((th1 + th2) / 2.0)

        # Scan right (towards 180 degrees, index increasing)
        right_cross_idx = None
        for i in range(mb_idx, len(af_n) - 1):
            if af_n[i] >= half_power_target and af_n[i + 1] < half_power_target:
                right_cross_idx = i
                break

        if right_cross_idx is not None:
            # Interpolate between right_cross_idx and right_cross_idx + 1
            th1, th2 = theta_deg[right_cross_idx], theta_deg[right_cross_idx + 1]
            v1, v2 = af_n[right_cross_idx], af_n[right_cross_idx + 1]
            if not np.isclose(v1, v2):
                hp_right_deg = float(th1 + (half_power_target - v1) * (th2 - th1) / (v2 - v1))
            else:
                hp_right_deg = float((th1 + th2) / 2.0)

        # Both crossings must exist for a defined HPBW (Section 7.5 Robustness)
        if hp_left_deg is not None and hp_right_deg is not None:
            hpbw_deg = float(hp_right_deg - hp_left_deg)
        else:
            hpbw_deg = None

    # 4. First-Null Beamwidth (FNBW)
    fnbw_deg = None
    fn_left_deg = None
    fn_right_deg = None

    if main_beam_deg is not None and nulls_deg:
        left_nulls = [n for n in nulls_deg if n < main_beam_deg - 1e-4]
        right_nulls = [n for n in nulls_deg if n > main_beam_deg + 1e-4]

        if left_nulls and right_nulls:
            fn_left_deg = max(left_nulls)
            fn_right_deg = min(right_nulls)
            fnbw_deg = float(fn_right_deg - fn_left_deg)

    # 5. Peak Sidelobe Level (SLL)
    # Find all local peaks in af_n, excluding main beam and grating lobes
    all_peaks, _ = find_peaks(af_n, prominence=0.005)
    sidelobe_peaks = []
    for p in all_peaks:
        peak_angle = theta_deg[p]
        # Check distance from main beam and grating lobes
        is_principal = any(np.isclose(peak_angle, m, atol=1.0) for m in all_maxima_deg)
        if not is_principal and af_n[p] < 0.99:
            sidelobe_peaks.append(p)

    if sidelobe_peaks:
        best_sl_idx = max(sidelobe_peaks, key=lambda idx: af_n[idx])
        peak_sll_val = af_n[best_sl_idx]
        peak_sll_db = float(20.0 * np.log10(max(peak_sll_val, 1e-12)))
        peak_sll_angle_deg = float(theta_deg[best_sl_idx])
    else:
        peak_sll_db = None
        peak_sll_angle_deg = None

    return PatternMetrics(
        all_maxima_deg=all_maxima_deg,
        main_beam_deg=main_beam_deg,
        grating_lobes_deg=grating_lobes_deg,
        grating_lobe_count=grating_lobe_count,
        nulls_deg=nulls_deg,
        hpbw_deg=hpbw_deg,
        half_power_left_deg=hp_left_deg,
        half_power_right_deg=hp_right_deg,
        fnbw_deg=fnbw_deg,
        first_null_left_deg=fn_left_deg,
        first_null_right_deg=fn_right_deg,
        peak_sll_db=peak_sll_db,
        peak_sll_angle_deg=peak_sll_angle_deg,
        kd_rad=float(kd),
        kd_deg=float(np.degrees(kd)),
        beta_rad=float(beta_rad),
        beta_deg=float(np.degrees(beta_rad)),
    )

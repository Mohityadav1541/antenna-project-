"""
Beam steering calculations and phase control (Part D).
"""

from typing import Optional, Tuple
import numpy as np


def compute_steering_phase(theta_0_rad: float, d_over_lambda: float) -> float:
    """
    Computes required progressive excitation phase beta for desired main beam angle theta_0:
    kd * cos(theta_0) + beta = 0  =>  beta = -kd * cos(theta_0)
    where kd = 2 * pi * (d / lambda).
    """
    kd = 2.0 * np.pi * d_over_lambda
    return float(-kd * np.cos(theta_0_rad))


def compute_achieved_angle(beta_rad: float, d_over_lambda: float) -> Optional[float]:
    """
    Computes actual pointing angle theta_achieved for a given excitation phase beta.
    A principal maximum occurs where psi = kd * cos(theta) + beta = 2 * m * pi (integer m):
    cos(theta) = (2 * m * pi - beta) / kd.
    
    Searches all integer m. If a unique principal beam exists in visible space [0, pi],
    returns its angle in radians. If multiple equal-height maxima exist (grating lobes),
    returns the one corresponding to the closest integer m to 0.
    If no principal beam is in visible space, returns None.
    """
    kd = 2.0 * np.pi * d_over_lambda
    if kd <= 0:
        return None

    # Search for all integer m where |(2*m*pi - beta) / kd| <= 1
    m_min = int(np.floor((-kd + beta_rad) / (2.0 * np.pi))) - 1
    m_max = int(np.ceil((kd + beta_rad) / (2.0 * np.pi))) + 1

    valid_solutions = []
    for m in range(m_min, m_max + 1):
        cos_val = (2.0 * m * np.pi - beta_rad) / kd
        if np.isclose(abs(cos_val), 1.0, atol=1e-9):
            cos_val = np.clip(cos_val, -1.0, 1.0)
        if abs(cos_val) <= 1.0:
            th = float(np.arccos(cos_val))
            valid_solutions.append((abs(m), m, th))

    if not valid_solutions:
        return None

    # Sort primarily by |m| (prefer fundamental beam m=0), then by angle
    valid_solutions.sort(key=lambda item: (item[0], item[2]))
    return valid_solutions[0][2]


def steering_summary(
    theta_0_deg: float,
    beta_deg: float,
    d_over_lambda: float,
) -> dict:
    """
    Provides summary of steering status, desired vs achieved direction,
    excitation phase vs total phase.
    """
    kd = 2.0 * np.pi * d_over_lambda
    theta_0_rad = np.radians(theta_0_deg)
    beta_rad = np.radians(beta_deg)

    required_beta_rad = compute_steering_phase(theta_0_rad, d_over_lambda)
    achieved_rad = compute_achieved_angle(beta_rad, d_over_lambda)

    achieved_deg = np.degrees(achieved_rad) if achieved_rad is not None else None

    return {
        "desired_theta_deg": theta_0_deg,
        "required_beta_deg": float(np.degrees(required_beta_rad)),
        "current_beta_deg": beta_deg,
        "achieved_theta_deg": achieved_deg,
        "is_steered_in_visible_range": achieved_rad is not None,
        "kd_rad": float(kd),
        "kd_deg": float(np.degrees(kd)),
    }

"""
CSV export utilities for antenna pattern data and metrics.
"""

import csv
from typing import Optional
import numpy as np
from analysis.pattern_metrics import PatternMetrics


def export_pattern_to_csv(
    filepath: str,
    theta_rad: np.ndarray,
    af_n: np.ndarray,
    af_db: np.ndarray,
    p_n: np.ndarray,
    metrics: PatternMetrics,
    N: int,
    d_over_lambda: float,
    beta_deg: float,
    freq_ghz: float,
    weighting_type: str = "Uniform",
) -> None:
    """Exports full angular pattern data and configuration metadata to CSV."""
    theta_deg = np.degrees(theta_rad)
    kd = 2.0 * np.pi * d_over_lambda
    psi_rad = kd * np.cos(theta_rad) + np.radians(beta_deg)

    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header metadata
        writer.writerow(["# Interactive Antenna Array Simulation Data"])
        writer.writerow(["# Number of Elements (N)", N])
        writer.writerow(["# Spacing (d/lambda)", d_over_lambda])
        writer.writerow(["# Frequency (GHz)", freq_ghz])
        writer.writerow(["# Progressive Phase beta (deg)", beta_deg])
        writer.writerow(["# Progressive Phase beta (rad)", np.radians(beta_deg)])
        writer.writerow(["# kd (rad)", kd])
        writer.writerow(["# kd (deg)", np.degrees(kd)])
        writer.writerow(["# Weighting Type", weighting_type])
        writer.writerow(["# Main Beam Direction (deg)", metrics.main_beam_deg if metrics.main_beam_deg is not None else "Not defined"])
        writer.writerow(["# HPBW (deg)", metrics.hpbw_deg if metrics.hpbw_deg is not None else "Not defined"])
        writer.writerow(["# FNBW (deg)", metrics.fnbw_deg if metrics.fnbw_deg is not None else "Not defined"])
        writer.writerow(["# Peak SLL (dB)", metrics.peak_sll_db if metrics.peak_sll_db is not None else "Not defined"])
        writer.writerow(["# Grating Lobe Count", metrics.grating_lobe_count])
        writer.writerow(["# Visible Maxima (deg)", "; ".join(f"{m:.2f}" for m in metrics.all_maxima_deg)])
        writer.writerow(["# Visible Nulls (deg)", "; ".join(f"{n:.2f}" for n in metrics.nulls_deg)])
        writer.writerow([])  # blank separator

        # Column headers
        writer.writerow([
            "theta_deg",
            "theta_rad",
            "psi_rad",
            "psi_deg",
            "AF_normalized",
            "Power_normalized",
            "AF_dB",
        ])

        # Data rows
        for i in range(len(theta_rad)):
            writer.writerow([
                f"{theta_deg[i]:.4f}",
                f"{theta_rad[i]:.6f}",
                f"{psi_rad[i]:.6f}",
                f"{np.degrees(psi_rad[i]):.4f}",
                f"{af_n[i]:.6e}",
                f"{p_n[i]:.6e}",
                f"{af_db[i]:.4f}",
            ])

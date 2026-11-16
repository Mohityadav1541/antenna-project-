"""
Experiment runner and figure generator for Antenna Array Simulation Assignment.
Generates all 12 required figures and 3 validation tables specified in Section 12.
"""

import os
import sys
from pathlib import Path
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_cache"
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless figure generation
import matplotlib.pyplot as plt

# Ensure project root is in path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from core.physics import phase_psi, frequency_to_wavelength, wavenumber
from core.array_factor import compute_normalized_pattern, array_factor_summation
from core.tapering import get_weights_by_type
from analysis.pattern_metrics import compute_pattern_metrics
from analysis.steering import compute_steering_phase, compute_achieved_angle

# Output directories
FIGURES_DIR = project_root / "output" / "figures"
TABLES_DIR = project_root / "output" / "tables"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

# Styling parameters
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "lines.linewidth": 1.8,
    "grid.alpha": 0.4,
})


def generate_figure_2():
    """Figure 2: Array-factor magnitude for several element counts (N = 2, 4, 8, 16, 32, 64)."""
    fig, ax = plt.subplots(figsize=(9, 5.5))
    theta = np.linspace(0, np.pi, 3601)
    theta_deg = np.degrees(theta)
    N_list = [2, 4, 8, 16, 32, 64]
    colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(N_list)))

    for N, col in zip(N_list, colors):
        af_n, _, _ = compute_normalized_pattern(theta, N, d_over_lambda=0.5, beta_rad=0.0)
        ax.plot(theta_deg, af_n, label=f"N = {N}", color=col)

    ax.set_title("Figure 2: Array Factor Magnitude |AF_n(θ)| for Various Element Counts (d = 0.5λ, β = 0°)")
    ax.set_xlabel("Observation Angle θ (degrees)")
    ax.set_ylabel("Normalized Array Factor |AF_n|")
    ax.set_xlim(0, 180)
    ax.set_ylim(0, 1.05)
    ax.set_xticks(np.arange(0, 181, 30))
    ax.grid(True, linestyle="--")
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig2_magnitude_element_counts.png", dpi=300)
    plt.close(fig)
    print("Generated Figure 2")


def generate_figure_3():
    """Figure 3: Array factor in dB for several spacings (d/lambda = 0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0)."""
    fig, ax = plt.subplots(figsize=(10, 6))
    theta = np.linspace(0, np.pi, 3601)
    theta_deg = np.degrees(theta)
    d_list = [0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]
    colors = plt.cm.plasma(np.linspace(0.05, 0.9, len(d_list)))

    for d, col in zip(d_list, colors):
        _, _, af_db = compute_normalized_pattern(theta, N=8, d_over_lambda=d, beta_rad=0.0)
        af_db_clipped = np.clip(af_db, -50.0, 0.0)
        ax.plot(theta_deg, af_db_clipped, label=f"d = {d}λ", color=col)

    ax.set_title("Figure 3: Array Factor in dB for Various Element Spacings (N = 8, β = 0°)")
    ax.set_xlabel("Observation Angle θ (degrees)")
    ax.set_ylabel("Normalized Array Factor (dB)")
    ax.set_xlim(0, 180)
    ax.set_ylim(-50, 2)
    ax.set_xticks(np.arange(0, 181, 30))
    ax.axhline(-3.01, color="black", linestyle=":", label="-3 dB line (HPBW threshold)")
    ax.grid(True, linestyle="--")
    ax.legend(loc="upper right", ncol=2)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig3_array_factor_db_spacings.png", dpi=300)
    plt.close(fig)
    print("Generated Figure 3")


def generate_figure_4():
    """Figure 4: Broadside and end-fire polar plots."""
    fig, (ax1, ax2) = plt.subplots(1, 2, subplot_kw=dict(polar=True), figsize=(12, 6))
    theta = np.linspace(0, np.pi, 1801)
    # Mirror theta for full 360-degree polar view
    theta_full = np.concatenate([theta, 2*np.pi - theta[::-1]])

    # Broadside (beta = 0)
    af_n_bs, _, _ = compute_normalized_pattern(theta, N=8, d_over_lambda=0.5, beta_rad=0.0)
    af_n_bs_full = np.concatenate([af_n_bs, af_n_bs[::-1]])

    # End-fire (beta = -kd = -pi)
    af_n_ef, _, _ = compute_normalized_pattern(theta, N=8, d_over_lambda=0.5, beta_rad=-np.pi)
    af_n_ef_full = np.concatenate([af_n_ef, af_n_ef[::-1]])

    # Plot Broadside
    ax1.plot(theta_full, af_n_bs_full, color="#1f77b4", linewidth=2.0)
    ax1.set_theta_zero_location("N")  # 0 degrees at top (along array axis)
    ax1.set_theta_direction(-1)       # clockwise
    ax1.set_title("Broadside Pattern (β = 0°, Beam at 90°)", va="bottom")
    ax1.grid(True)

    # Plot End-fire
    ax2.plot(theta_full, af_n_ef_full, color="#d62728", linewidth=2.0)
    ax2.set_theta_zero_location("N")
    ax2.set_theta_direction(-1)
    ax2.set_title("Positive End-Fire Pattern (β = -180°, Beam at 0°)", va="bottom")
    ax2.grid(True)

    fig.suptitle("Figure 4: Polar Radiation Patterns for Broadside and End-Fire (N = 8, d = 0.5λ)", y=1.02)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig4_broadside_endfire_polar.png", dpi=300)
    plt.close(fig)
    print("Generated Figure 4")


def generate_figure_5():
    """Figure 5: Overlaid steering-angle patterns (theta0 = 0°, 30°, 45°, 60°, 90°, 120°, 150°, 180°)."""
    fig, ax = plt.subplots(figsize=(10, 6))
    theta = np.linspace(0, np.pi, 3601)
    theta_deg = np.degrees(theta)
    steering_angles = [0, 30, 45, 60, 90, 120, 150, 180]
    colors = plt.cm.tab10(np.linspace(0, 1, len(steering_angles)))

    for th0, col in zip(steering_angles, colors):
        beta_rad = compute_steering_phase(np.radians(th0), d_over_lambda=0.5)
        af_n, _, _ = compute_normalized_pattern(theta, N=8, d_over_lambda=0.5, beta_rad=beta_rad)
        ax.plot(theta_deg, af_n, label=f"θ₀ = {th0}° (β = {np.degrees(beta_rad):.1f}°)", color=col)

    ax.set_title("Figure 5: Overlaid Steered Patterns (N = 8, d = 0.5λ)")
    ax.set_xlabel("Observation Angle θ (degrees)")
    ax.set_ylabel("Normalized Array Factor |AF_n|")
    ax.set_xlim(0, 180)
    ax.set_ylim(0, 1.05)
    ax.set_xticks(np.arange(0, 181, 30))
    ax.grid(True, linestyle="--")
    ax.legend(loc="upper right", ncol=2)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig5_overlaid_steering_patterns.png", dpi=300)
    plt.close(fig)
    print("Generated Figure 5")


def generate_figure_6():
    """Figure 6: Beam direction versus progressive phase beta."""
    fig, ax = plt.subplots(figsize=(8, 5))
    beta_deg_vals = np.linspace(-180, 180, 361)
    achieved_theta = []
    valid_beta = []

    for b in beta_deg_vals:
        th = compute_achieved_angle(np.radians(b), d_over_lambda=0.5)
        if th is not None:
            valid_beta.append(b)
            achieved_theta.append(np.degrees(th))

    ax.plot(valid_beta, achieved_theta, color="#2ca02c", linewidth=2.2, label="θ_achieved = arccos(-β / kd)")
    ax.set_title("Figure 6: Beam Pointing Angle versus Progressive Phase β (d = 0.5λ, kd = 180°)")
    ax.set_xlabel("Progressive Excitation Phase β (degrees)")
    ax.set_ylabel("Achieved Main Beam Angle θ₀ (degrees)")
    ax.set_xlim(-180, 180)
    ax.set_ylim(0, 180)
    ax.set_xticks(np.arange(-180, 181, 45))
    ax.set_yticks(np.arange(0, 181, 30))
    ax.grid(True, linestyle="--")

    # Mark key points
    key_points = [(-180, 0), (-90, 60), (0, 90), (90, 120), (180, 180)]
    for kb, kth in key_points:
        ax.plot(kb, kth, "ro", markersize=6)
        ax.annotate(f"({kb}°, {kth}°)", xy=(kb, kth), xytext=(kb + 6, kth - 8),
                    fontsize=9, weight="bold")

    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig6_beam_direction_vs_beta.png", dpi=300)
    plt.close(fig)
    print("Generated Figure 6")


def generate_figure_7():
    """Figure 7: Beamwidth (HPBW & FNBW) versus number of elements N."""
    fig, ax = plt.subplots(figsize=(8, 5))
    N_list = [2, 4, 8, 12, 16, 24, 32, 48, 64]
    hpbw_list = []
    fnbw_list = []
    theta = np.linspace(0, np.pi, 7201)

    for N in N_list:
        af_n, p_n, af_db = compute_normalized_pattern(theta, N, d_over_lambda=0.5, beta_rad=0.0)
        m = compute_pattern_metrics(theta, af_n, af_db, N, d_over_lambda=0.5, beta_rad=0.0)
        hpbw_list.append(m.hpbw_deg)
        fnbw_list.append(m.fnbw_deg)

    ax.plot(N_list, hpbw_list, "o-", label="HPBW (-3 dB Beamwidth)", color="#1f77b4", linewidth=2.0)
    ax.plot(N_list, fnbw_list, "s-", label="FNBW (First-Null Beamwidth)", color="#d62728", linewidth=2.0)

    # Theoretical asymptotic curves: HPBW approx 0.886 * lambda / (N * d) * (180/pi) = 101.5 / N degrees
    N_cont = np.linspace(2, 64, 100)
    hpbw_theory = (0.886 / (N_cont * 0.5)) * (180.0 / np.pi)
    fnbw_theory = (2.0 / (N_cont * 0.5)) * (180.0 / np.pi)
    ax.plot(N_cont, hpbw_theory, "--", color="#1f77b4", alpha=0.5, label="HPBW Asymptotic (0.886λ / Nd)")
    ax.plot(N_cont, fnbw_theory, "--", color="#d62728", alpha=0.5, label="FNBW Asymptotic (2λ / Nd)")

    ax.set_title("Figure 7: Beamwidth vs Number of Elements N (d = 0.5λ, Broadside)")
    ax.set_xlabel("Number of Elements N")
    ax.set_ylabel("Beamwidth (degrees)")
    ax.set_xlim(1, 65)
    ax.set_ylim(0, 110)
    ax.grid(True, linestyle="--")
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig7_beamwidth_vs_N.png", dpi=300)
    plt.close(fig)
    print("Generated Figure 7")


def generate_figure_8():
    """Figure 8: HPBW versus element spacing d/lambda."""
    fig, ax = plt.subplots(figsize=(8, 5))
    d_list = np.linspace(0.1, 1.0, 30)
    hpbw_list = []
    theta = np.linspace(0, np.pi, 7201)

    for d in d_list:
        af_n, p_n, af_db = compute_normalized_pattern(theta, N=8, d_over_lambda=d, beta_rad=0.0)
        m = compute_pattern_metrics(theta, af_n, af_db, N=8, d_over_lambda=d, beta_rad=0.0)
        hpbw_list.append(m.hpbw_deg)

    ax.plot(d_list, hpbw_list, "o-", color="#9467bd", linewidth=2.2, label="Measured HPBW (N = 8)")
    ax.set_title("Figure 8: Half-Power Beamwidth (HPBW) vs Element Spacing d/λ (N = 8, Broadside)")
    ax.set_xlabel("Element Spacing d/λ")
    ax.set_ylabel("HPBW (degrees)")
    ax.set_xlim(0.05, 1.05)
    ax.grid(True, linestyle="--")
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig8_hpbw_vs_spacing.png", dpi=300)
    plt.close(fig)
    print("Generated Figure 8")


def generate_figure_9():
    """Figure 9: Annotated pattern showing maxima, nulls, HPBW (-3 dB crossings), and FNBW."""
    fig, ax = plt.subplots(figsize=(10, 6))
    theta = np.linspace(0, np.pi, 3601)
    theta_deg = np.degrees(theta)
    af_n, p_n, af_db = compute_normalized_pattern(theta, N=8, d_over_lambda=0.5, beta_rad=0.0)
    m = compute_pattern_metrics(theta, af_n, af_db, N=8, d_over_lambda=0.5, beta_rad=0.0)

    # Plot main curve
    ax.plot(theta_deg, af_n, color="#1f77b4", linewidth=2.0, label="|AF_n(θ)|")

    # Mark Principal Maxima
    for max_th in m.all_maxima_deg:
        ax.plot(max_th, 1.0, "ro", markersize=8, label="Principal Maxima" if max_th == m.all_maxima_deg[0] else "")
        ax.annotate(f"Max: {max_th:.1f}°", xy=(max_th, 1.0), xytext=(max_th - 8, 1.04),
                    fontweight="bold", color="darkred")

    # Mark Nulls
    for null_th in m.nulls_deg:
        ax.plot(null_th, 0.0, "g^", markersize=7, label="Nulls" if null_th == m.nulls_deg[0] else "")

    # Mark HPBW (-3 dB crossings)
    if m.half_power_left_deg and m.half_power_right_deg:
        hp_val = 1.0 / np.sqrt(2.0)
        ax.plot([m.half_power_left_deg, m.half_power_right_deg], [hp_val, hp_val], "m--", linewidth=1.8,
                label=f"HPBW = {m.hpbw_deg:.2f}°")
        ax.plot(m.half_power_left_deg, hp_val, "ms", markersize=7)
        ax.plot(m.half_power_right_deg, hp_val, "ms", markersize=7)
        ax.annotate(f"{m.half_power_left_deg:.1f}°", xy=(m.half_power_left_deg, hp_val),
                    xytext=(m.half_power_left_deg - 14, hp_val + 0.04), color="purple", weight="bold")
        ax.annotate(f"{m.half_power_right_deg:.1f}°", xy=(m.half_power_right_deg, hp_val),
                    xytext=(m.half_power_right_deg + 4, hp_val + 0.04), color="purple", weight="bold")

    # Mark FNBW
    if m.first_null_left_deg and m.first_null_right_deg:
        ax.plot([m.first_null_left_deg, m.first_null_right_deg], [0.05, 0.05], "k-.", linewidth=1.5,
                label=f"FNBW = {m.fnbw_deg:.2f}°")

    ax.set_title("Figure 9: Annotated Array Factor Showing Maxima, Nulls, HPBW, and FNBW (N = 8, d = 0.5λ)")
    ax.set_xlabel("Observation Angle θ (degrees)")
    ax.set_ylabel("Normalized Array Factor |AF_n|")
    ax.set_xlim(0, 180)
    ax.set_ylim(-0.05, 1.12)
    ax.set_xticks(np.arange(0, 181, 30))
    ax.grid(True, linestyle="--")
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig9_annotated_pattern_metrics.png", dpi=300)
    plt.close(fig)
    print("Generated Figure 9")


def generate_figure_10():
    """Figure 10: Grating-lobe formation as d/lambda increases."""
    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    theta = np.linspace(0, np.pi, 3601)
    theta_deg = np.degrees(theta)
    spacings = [0.5, 1.0, 1.5]
    sub_titles = [
        "d = 0.5λ: Single broadside main beam, no grating lobes",
        "d = 1.0λ: Onset of grating lobes at boundaries (θ = 0° and θ = 180°)",
        "d = 1.5λ: Multiple prominent grating lobes inside visible space",
    ]

    for ax, d, title in zip(axes, spacings, sub_titles):
        af_n, _, _ = compute_normalized_pattern(theta, N=8, d_over_lambda=d, beta_rad=0.0)
        m = compute_pattern_metrics(theta, af_n, np.zeros_like(af_n), N=8, d_over_lambda=d, beta_rad=0.0)
        ax.plot(theta_deg, af_n, color="#2b5c8f", linewidth=1.8)

        # Highlight main beam vs grating lobes
        for max_th in m.all_maxima_deg:
            if np.isclose(max_th, 90.0, atol=1.0):
                ax.plot(max_th, 1.0, "ro", markersize=8, label="Main Beam (90°)")
            else:
                ax.plot(max_th, 1.0, "r*", markersize=10, label="Grating Lobe" if max_th == m.grating_lobes_deg[0] else "")
                ax.annotate(f"Grating Lobe\n({max_th:.1f}°)", xy=(max_th, 1.0),
                            xytext=(max_th - 6, 0.72), color="red", weight="bold",
                            arrowprops=dict(arrowstyle="->", color="red"))

        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_ylabel("|AF_n|")
        ax.set_ylim(-0.02, 1.1)
        ax.grid(True, linestyle="--")
        ax.legend(loc="upper right")

    axes[-1].set_xlabel("Observation Angle θ (degrees)")
    axes[-1].set_xticks(np.arange(0, 181, 30))
    fig.suptitle("Figure 10: Grating Lobe Formation with Increasing Element Spacing (N = 8, β = 0°)", y=0.99)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig10_grating_lobe_formation.png", dpi=300)
    plt.close(fig)
    print("Generated Figure 10")


def generate_figure_11():
    """Figure 11: Uniform versus tapered excitations (Uniform, Binomial, Hann)."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    theta = np.linspace(0, np.pi, 3601)
    theta_deg = np.degrees(theta)
    N = 8
    weight_types = ["Uniform", "Hann", "Binomial"]
    colors = {"Uniform": "#1f77b4", "Hann": "#ff7f0e", "Binomial": "#2ca02c"}

    # 1. Amplitude bar chart comparison
    x = np.arange(N)
    width = 0.25
    for i, w_type in enumerate(weight_types):
        w = get_weights_by_type(w_type, N)
        ax1.bar(x + i*width, w, width=width, label=w_type, color=colors[w_type], alpha=0.85)

    ax1.set_title("Element Excitation Amplitudes")
    ax1.set_xlabel("Element Index n")
    ax1.set_ylabel("Normalized Amplitude a_n")
    ax1.set_xticks(x + width)
    ax1.set_xticklabels([f"n={i}" for i in range(N)])
    ax1.grid(True, linestyle="--", alpha=0.4)
    ax1.legend(loc="upper right")

    # 2. Resulting dB radiation pattern
    for w_type in weight_types:
        w = get_weights_by_type(w_type, N)
        _, _, af_db = compute_normalized_pattern(theta, N, d_over_lambda=0.5, beta_rad=0.0, amplitudes=w)
        af_db_clipped = np.clip(af_db, -60.0, 0.0)
        ax2.plot(theta_deg, af_db_clipped, label=w_type, color=colors[w_type], linewidth=2.0)

    ax2.set_title("Radiation Pattern Comparison (dB Scale)")
    ax2.set_xlabel("Observation Angle θ (degrees)")
    ax2.set_ylabel("Normalized Array Factor (dB)")
    ax2.set_xlim(0, 180)
    ax2.set_ylim(-60, 2)
    ax2.set_xticks(np.arange(0, 181, 30))
    ax2.axhline(-13.26, color="#1f77b4", linestyle=":", alpha=0.7, label="Uniform SLL (-13.3 dB)")
    ax2.grid(True, linestyle="--", alpha=0.4)
    ax2.legend(loc="lower center", ncol=2)

    fig.suptitle("Figure 11: Uniform vs Tapered Excitations (N = 8, d = 0.5λ, β = 0°)", y=1.00)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig11_uniform_vs_tapered_excitations.png", dpi=300)
    plt.close(fig)
    print("Generated Figure 11")


def generate_figure_12():
    """Figure 12: Element geometry and excitation visualization (Part G)."""
    fig, (ax_geom, ax_phase) = plt.subplots(2, 1, figsize=(10, 6.5))
    N = 8
    d_over_lambda = 0.5
    beta_deg = -90.0  # Steered to 60 degrees
    beta_rad = np.radians(beta_deg)

    # Physical positions along z-axis
    z_positions = np.arange(N) * d_over_lambda

    # Array Geometry along z-axis
    ax_geom.plot(z_positions, np.zeros(N), "k-", linewidth=2.0, alpha=0.6)
    for n in range(N):
        # Element circle
        ax_geom.plot(z_positions[n], 0, "o", markersize=14, color="#1f77b4")
        ax_geom.text(z_positions[n], -0.25, f"#{n}", ha="center", fontsize=9, weight="bold")
        # Amplitude bar
        ax_geom.plot([z_positions[n], z_positions[n]], [0, 0.6], color="#2ca02c", linewidth=4.0)

    ax_geom.set_title("Physical Linear Array on z-Axis (N = 8, Spacing d = 0.5λ)")
    ax_geom.set_xlabel("Element Position along Array Axis z (in wavelengths λ)")
    ax_geom.set_ylim(-0.5, 0.9)
    ax_geom.set_xlim(-0.3, z_positions[-1] + 0.3)
    ax_geom.set_yticks([])
    ax_geom.grid(True, linestyle="--", alpha=0.3)

    # Phasor Visualization: showing element progressive excitation phase
    element_phases = np.arange(N) * beta_rad
    for n in range(N):
        # Draw mini phasor circle
        circle = plt.Circle((z_positions[n], 0), 0.22, color="lightgray", fill=False, linestyle=":")
        ax_phase.add_patch(circle)
        # Draw phasor arrow
        u = 0.20 * np.cos(element_phases[n])
        v = 0.20 * np.sin(element_phases[n])
        ax_phase.arrow(z_positions[n], 0, u, v, head_width=0.04, head_length=0.04,
                       fc="#d62728", ec="#d62728", linewidth=1.5)
        phase_deg_mod = np.degrees(element_phases[n]) % 360.0
        ax_phase.text(z_positions[n], -0.38, f"{phase_deg_mod:.0f}°", ha="center", fontsize=9, color="darkred")

    ax_phase.set_title("Element Excitation Phasors (Progressive Phase β = -90°, Steered to 60°)")
    ax_phase.set_xlabel("Array Element Position z / λ")
    ax_phase.set_ylim(-0.55, 0.55)
    ax_phase.set_xlim(-0.3, z_positions[-1] + 0.3)
    ax_phase.set_yticks([])
    ax_phase.grid(True, linestyle="--", alpha=0.3)

    fig.suptitle("Figure 12: Interactive Array Geometry & Excitation Phasor Visualization", y=0.99)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig12_geometry_excitation_visualization.png", dpi=300)
    plt.close(fig)
    print("Generated Figure 12")


def generate_validation_tables():
    """Generates the 3 required numerical comparison tables."""
    theta = np.linspace(0, np.pi, 3601)

    # TABLE 1: Part H Verification Tests (9 benchmark cases)
    benchmark_cases = [
        (1, 2, 0.5, 0.0, "Broadside maximum", "90.0°", 90.0),
        (2, 4, 0.5, 0.0, "Symmetric broadside", "90.0°", 90.0),
        (3, 8, 0.5, 0.0, "Narrower main beam", "90.0°", 90.0),
        (4, 8, 0.5, -90.0, "Principal beam at 60°", "60.0°", 60.0),
        (5, 8, 0.5, +90.0, "Principal beam at 120°", "120.0°", 120.0),
        (6, 8, 0.5, -180.0, "Positive end-fire", "0.0°", 0.0),
        (7, 8, 0.5, +180.0, "Negative end-fire", "180.0°", 180.0),
        (8, 8, 1.0, 0.0, "Multiple equal-height maxima", "0°, 90°, 180°", 90.0),
        (9, 16, 0.5, 0.0, "Narrower beam than N=8", "90.0°", 90.0),
    ]

    table1_rows = []
    for test_id, N, d, beta, desc, theory_main, theory_num in benchmark_cases:
        af_n, p_n, af_db = compute_normalized_pattern(theta, N, d, np.radians(beta))
        m = compute_pattern_metrics(theta, af_n, af_db, N, d, np.radians(beta))
        sim_main = f"{m.main_beam_deg:.2f}°" if m.main_beam_deg is not None else "Not defined"
        error = abs(m.main_beam_deg - theory_num) if m.main_beam_deg is not None else 0.0
        hpbw_str = f"{m.hpbw_deg:.2f}°" if m.hpbw_deg is not None else "Not defined"
        fnbw_str = f"{m.fnbw_deg:.2f}°" if m.fnbw_deg is not None else "Not defined"
        table1_rows.append({
            "Test": test_id,
            "N": N,
            "d/λ": d,
            "β (deg)": beta,
            "Expected": desc,
            "Theory Beam": theory_main,
            "Sim Beam": sim_main,
            "Abs Error": f"{error:.4f}°",
            "HPBW": hpbw_str,
            "FNBW": fnbw_str,
        })

    # Save Table 1 to Markdown and CSV
    with open(TABLES_DIR / "table1_benchmark_validation.md", "w") as f:
        f.write("# Table 1: Verification and Validation of 9 Benchmark Cases (Part H)\n\n")
        f.write("| Test | N | d/λ | β (deg) | Description | Analytical Prediction | Simulation Result | Absolute Error | HPBW | FNBW |\n")
        f.write("|:---:|:---:|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|\n")
        for r in table1_rows:
            f.write(f"| {r['Test']} | {r['N']} | {r['d/λ']} | {r['β (deg)']} | {r['Expected']} | {r['Theory Beam']} | {r['Sim Beam']} | {r['Abs Error']} | {r['HPBW']} | {r['FNBW']} |\n")

    # TABLE 2: Part B - Effect of Number of Elements N (d=0.5, beta=0)
    N_cases = [2, 4, 8, 16, 32, 64]
    table2_rows = []
    for N in N_cases:
        af_n, p_n, af_db = compute_normalized_pattern(theta, N, d_over_lambda=0.5, beta_rad=0.0)
        m = compute_pattern_metrics(theta, af_n, af_db, N, d_over_lambda=0.5, beta_rad=0.0)
        sll_str = f"{m.peak_sll_db:.2f} dB" if m.peak_sll_db is not None else "Not defined"
        table2_rows.append({
            "N": N,
            "Main Beam": f"{m.main_beam_deg:.2f}°",
            "HPBW": f"{m.hpbw_deg:.2f}°",
            "FNBW": f"{m.fnbw_deg:.2f}°",
            "Peak SLL": sll_str,
            "Null Count": len(m.nulls_deg),
        })

    with open(TABLES_DIR / "table2_element_counts_part_b.md", "w") as f:
        f.write("# Table 2: Radiation Pattern Metrics vs Number of Elements N (d = 0.5λ, β = 0°)\n\n")
        f.write("| N | Main Beam Direction | HPBW | FNBW | Peak SLL | Number of Visible Nulls |\n")
        f.write("|:---:|:---:|:---:|:---:|:---:|:---:|\n")
        for r in table2_rows:
            f.write(f"| {r['N']} | {r['Main Beam']} | {r['HPBW']} | {r['FNBW']} | {r['Peak SLL']} | {r['Null Count']} |\n")

    # TABLE 3: Part C - Effect of Element Spacing d/lambda (N=8, beta=0)
    d_cases = [0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]
    table3_rows = []
    for d in d_cases:
        af_n, p_n, af_db = compute_normalized_pattern(theta, N=8, d_over_lambda=d, beta_rad=0.0)
        m = compute_pattern_metrics(theta, af_n, af_db, N=8, d_over_lambda=d, beta_rad=0.0)
        hpbw_str = f"{m.hpbw_deg:.2f}°" if m.hpbw_deg is not None else "Not defined"
        fnbw_str = f"{m.fnbw_deg:.2f}°" if m.fnbw_deg is not None else "Not defined"
        sll_str = f"{m.peak_sll_db:.2f} dB" if m.peak_sll_db is not None else "Not defined"
        table3_rows.append({
            "d/λ": d,
            "HPBW": hpbw_str,
            "FNBW": fnbw_str,
            "Peak SLL": sll_str,
            "Grating Lobes": m.grating_lobe_count,
            "All Maxima": "; ".join(f"{x:.1f}°" for x in m.all_maxima_deg),
        })

    with open(TABLES_DIR / "table3_element_spacing_part_c.md", "w") as f:
        f.write("# Table 3: Radiation Pattern Metrics vs Element Spacing d/λ (N = 8, β = 0°)\n\n")
        f.write("| d/λ | HPBW | FNBW | Peak SLL | Grating Lobe Count | Principal Maxima Angles |\n")
        f.write("|:---:|:---:|:---:|:---:|:---:|:---|\n")
        for r in table3_rows:
            f.write(f"| {r['d/λ']} | {r['HPBW']} | {r['FNBW']} | {r['Peak SLL']} | {r['Grating Lobes']} | {r['All Maxima']} |\n")

    print("Generated all 3 validation tables")


def generate_figure_1():
    """Figure 1: Screenshot of the complete GUI."""
    try:
        from PyQt6.QtWidgets import QApplication
        from gui.main_window import AntennaSimulationWindow
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        app = QApplication.instance() or QApplication([])
        window = AntennaSimulationWindow()
        window.resize(1380, 880)
        window.show()
        pixmap = window.grab()
        pixmap.save(str(FIGURES_DIR / "fig1_complete_gui_screenshot.png"), "PNG")
        window.close()
        print("Generated Figure 1 (GUI Screenshot)")
    except Exception as e:
        print(f"Figure 1 generation skipped ({e})")


def main():
    print("=== Generating Simulation Figures and Tables ===")
    generate_figure_1()
    generate_figure_2()
    generate_figure_3()
    generate_figure_4()
    generate_figure_5()
    generate_figure_6()
    generate_figure_7()
    generate_figure_8()
    generate_figure_9()
    generate_figure_10()
    generate_figure_11()
    generate_figure_12()
    generate_validation_tables()
    print("=== Completed figure and table generation successfully! ===")


if __name__ == "__main__":
    main()

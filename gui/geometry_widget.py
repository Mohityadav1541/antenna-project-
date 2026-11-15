"""
Interactive array geometry and excitation phasor visualizer (Part G).
Displays:
1. Physical linear array along z-axis with element positions and numbering
2. Element excitation amplitudes
3. Progressive excitation phasors (arrows/phase wheels)
4. Live constructive/destructive interference along current steering / observation direction
"""

import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from core.physics import physical_spacing_mm


class InteractiveGeometryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.info_label = QLabel("Array Geometry & Excitation Phasors")
        self.info_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #333;")
        layout.addWidget(self.info_label)

        self.fig = Figure(figsize=(7, 3.2), tight_layout=True)
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        # 2 subplots: top is array layout + amplitudes, bottom is excitation phasors + interference
        self.ax_layout = self.fig.add_subplot(211)
        self.ax_phasors = self.fig.add_subplot(212)

    def update_geometry(
        self,
        N: int,
        d_over_lambda: float,
        beta_rad: float,
        freq_ghz: float,
        theta_obs_deg: float = 90.0,
        amplitudes: np.ndarray = None,
    ):
        if amplitudes is None:
            amplitudes = np.ones(N)

        spacing_mm = physical_spacing_mm(d_over_lambda, freq_ghz * 1e9)
        kd = 2.0 * np.pi * d_over_lambda
        theta_obs_rad = np.radians(theta_obs_deg)

        # -----------------------------------------------------
        # 1. Array Layout along z-axis
        # -----------------------------------------------------
        self.ax_layout.clear()
        z_pos = np.arange(N) * d_over_lambda

        # Draw array axis
        self.ax_layout.axhline(0, color="gray", linestyle="-", linewidth=2.0, alpha=0.7)

        # Draw each element
        max_amp = max(np.max(amplitudes), 1e-6)
        for n in range(N):
            norm_a = amplitudes[n] / max_amp
            # Element circle
            self.ax_layout.plot(z_pos[n], 0, "o", markersize=10 + norm_a * 8, color="#1f77b4")
            # Amplitude bar
            self.ax_layout.plot([z_pos[n], z_pos[n]], [0, 0.5 * norm_a], color="#2ca02c", linewidth=3.0)
            # Label
            self.ax_layout.text(z_pos[n], -0.28, f"#{n}", ha="center", fontsize=8, weight="bold")

        self.ax_layout.set_title(
            f"Physical Linear Array (N = {N}, d = {d_over_lambda:.2f}λ = {spacing_mm:.2f} mm @ {freq_ghz:.2f} GHz)",
            fontsize=10,
        )
        self.ax_layout.set_xlim(-0.5 * d_over_lambda, (N - 0.5) * d_over_lambda + 0.1)
        self.ax_layout.set_ylim(-0.45, 0.7)
        self.ax_layout.set_yticks([])
        self.ax_layout.set_xlabel("z-Position (wavelengths λ)", fontsize=9)
        self.ax_layout.grid(True, linestyle="--", alpha=0.3)

        # -----------------------------------------------------
        # 2. Excitation Phasors & Interference along theta_obs
        # -----------------------------------------------------
        self.ax_phasors.clear()
        # Spatial propagation phase delay: n * kd * cos(theta_obs)
        # Excitation progressive phase: n * beta
        # Total phase for element n: psi_n = n * (kd * cos(theta_obs) + beta)
        psi = kd * np.cos(theta_obs_rad) + beta_rad

        phasor_radius = 0.22
        for n in range(N):
            # Element excitation phase phi_n = n * beta
            phi_n = n * beta_rad
            # Draw dashed phasor wheel
            circle = self.ax_phasors.plot(
                z_pos[n] + phasor_radius * np.cos(np.linspace(0, 2*np.pi, 30)),
                phasor_radius * np.sin(np.linspace(0, 2*np.pi, 30)),
                ":", color="lightgray"
            )
            # Draw excitation phasor (red arrow)
            u_ex = phasor_radius * np.cos(phi_n)
            v_ex = phasor_radius * np.sin(phi_n)
            self.ax_phasors.arrow(
                z_pos[n], 0, u_ex * 0.85, v_ex * 0.85,
                head_width=0.04, head_length=0.04, fc="#d62728", ec="#d62728"
            )
            # Display phase in degrees modulo 360
            deg_val = np.degrees(phi_n) % 360.0
            self.ax_phasors.text(z_pos[n], -0.38, f"{deg_val:.0f}°", ha="center", fontsize=8, color="#a00")

        # Interference assessment at observation angle theta_obs
        total_phasors = amplitudes * np.exp(1j * (np.arange(N) * psi))
        interference_mag = np.abs(np.sum(total_phasors)) / np.sum(amplitudes)

        if interference_mag > 0.8:
            status = "Constructive Interference (Main Beam)"
            status_color = "green"
        elif interference_mag < 0.15:
            status = "Destructive Interference (Null / Deep Minimum)"
            status_color = "red"
        else:
            status = "Partial Interference (Sidelobe Region)"
            status_color = "darkorange"

        self.ax_phasors.set_title(
            f"Excitation Phasors (Red Arrows) | Interference at θ={theta_obs_deg:.1f}°: {status} [|AF_n|={interference_mag:.2f}]",
            fontsize=10, color=status_color, weight="bold"
        )
        self.ax_phasors.set_xlim(-0.5 * d_over_lambda, (N - 0.5) * d_over_lambda + 0.1)
        self.ax_phasors.set_ylim(-0.55, 0.45)
        self.ax_phasors.set_yticks([])
        self.ax_phasors.grid(True, linestyle="--", alpha=0.3)

        self.canvas.draw()

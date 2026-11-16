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
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        self.info_label = QLabel("Array Geometry & Excitation Phasors")
        self.info_label.setStyleSheet("font-weight: bold; font-size: 11px; color: #38bdf8;")
        layout.addWidget(self.info_label)

        self.fig = Figure(figsize=(6, 2.0), tight_layout=True)
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
        self.ax_layout.axhline(0, color="gray", linestyle="-", linewidth=1.5, alpha=0.7)

        # Draw each element
        max_amp = max(np.max(amplitudes), 1e-6)
        for n in range(N):
            norm_a = amplitudes[n] / max_amp
            # Element circle
            self.ax_layout.plot(z_pos[n], 0, "o", markersize=8 + norm_a * 6, color="#0284c7")
            # Amplitude bar
            self.ax_layout.plot([z_pos[n], z_pos[n]], [0, 0.45 * norm_a], color="#10b981", linewidth=2.5)
            # Label
            self.ax_layout.text(z_pos[n], -0.25, f"#{n}", ha="center", fontsize=7.5, weight="bold", color="#1e293b")

        # Draw observation angle ray from array center
        z_center = (N - 1) * d_over_lambda / 2.0
        ray_len = 0.45
        u_ray = ray_len * np.cos(theta_obs_rad)
        v_ray = ray_len * np.sin(theta_obs_rad)
        self.ax_layout.arrow(
            z_center, 0, u_ray * 0.85, v_ray * 0.85,
            head_width=0.04, head_length=0.04,
            fc="#a855f7", ec="#a855f7", linewidth=1.5, linestyle="--"
        )
        self.ax_layout.text(
            z_center + u_ray * 1.05, max(0.08, v_ray * 1.05),
            f"θ={theta_obs_deg:.1f}°",
            color="#9333ea", weight="bold", fontsize=8, ha="center"
        )

        self.ax_layout.set_title(
            f"Array Geometry (N={N}, d={d_over_lambda:.2f}λ = {spacing_mm:.1f} mm @ {freq_ghz:.1f} GHz)",
            fontsize=8.5, weight="bold", pad=2
        )
        self.ax_layout.set_xlim(-0.6 * d_over_lambda, (N - 0.4) * d_over_lambda + 0.1)
        self.ax_layout.set_ylim(-0.40, 0.65)
        self.ax_layout.set_yticks([])
        self.ax_layout.tick_params(labelsize=7.5)
        self.ax_layout.grid(True, linestyle="--", alpha=0.3)

        # -----------------------------------------------------
        # 2. Excitation Phasors & Interference along theta_obs
        # -----------------------------------------------------
        self.ax_phasors.clear()
        psi = kd * np.cos(theta_obs_rad) + beta_rad

        phasor_radius = 0.20
        for n in range(N):
            phi_n = n * beta_rad
            # Draw dashed phasor wheel
            self.ax_phasors.plot(
                z_pos[n] + phasor_radius * np.cos(np.linspace(0, 2*np.pi, 24)),
                phasor_radius * np.sin(np.linspace(0, 2*np.pi, 24)),
                ":", color="#94a3b8", linewidth=0.8
            )
            # Draw excitation phasor (red arrow)
            u_ex = phasor_radius * np.cos(phi_n)
            v_ex = phasor_radius * np.sin(phi_n)
            self.ax_phasors.arrow(
                z_pos[n], 0, u_ex * 0.85, v_ex * 0.85,
                head_width=0.03, head_length=0.03, fc="#ef4444", ec="#ef4444"
            )
            deg_val = np.degrees(phi_n) % 360.0
            self.ax_phasors.text(z_pos[n], -0.32, f"{deg_val:.0f}°", ha="center", fontsize=7.5, color="#b91c1c")

        # Interference assessment at observation angle theta_obs
        total_phasors = amplitudes * np.exp(1j * (np.arange(N) * psi))
        interference_mag = np.abs(np.sum(total_phasors)) / np.sum(amplitudes)

        if interference_mag > 0.8:
            status = "Constructive (Main Beam)"
            status_color = "#15803d"
        elif interference_mag < 0.15:
            status = "Destructive (Null)"
            status_color = "#b91c1c"
        else:
            status = "Partial (Sidelobes)"
            status_color = "#b45309"

        self.ax_phasors.set_title(
            f"Interference @ θ={theta_obs_deg:.1f}°: {status} [|AF_n|={interference_mag:.2f}]",
            fontsize=8.5, color=status_color, weight="bold", pad=2
        )
        self.ax_phasors.set_xlim(-0.5 * d_over_lambda, (N - 0.5) * d_over_lambda + 0.1)
        self.ax_phasors.set_ylim(-0.45, 0.40)
        self.ax_phasors.set_yticks([])
        self.ax_phasors.tick_params(labelsize=7.5)
        self.ax_phasors.grid(True, linestyle="--", alpha=0.3)

        self.canvas.draw()

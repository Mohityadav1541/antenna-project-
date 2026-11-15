"""
Matplotlib plotting canvases and tabs for antenna radiation patterns.
Supports:
1. Cartesian normalized |AF_n| vs theta
2. Cartesian normalized array factor in dB vs theta
3. Polar radiation pattern
4. 3D axisymmetric radiation pattern (optional in spec, fully implemented)
5. Excitation amplitude weights bar chart
"""

import numpy as np
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QHBoxLayout,
    QCheckBox,
    QLabel,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D  # registers 3d projection
from analysis.pattern_metrics import PatternMetrics


class AntennaPlotsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Marker display toggles
        top_bar = QHBoxLayout()
        self.chk_show_markers = QCheckBox("Show Maxima / Nulls Markers")
        self.chk_show_markers.setChecked(True)
        self.chk_show_markers.toggled.connect(self._on_toggle_redraw)

        self.chk_show_hpbw = QCheckBox("Show HPBW & FNBW Lines")
        self.chk_show_hpbw.setChecked(True)
        self.chk_show_hpbw.toggled.connect(self._on_toggle_redraw)

        top_bar.addWidget(QLabel("Plot Overlays:"))
        top_bar.addWidget(self.chk_show_markers)
        top_bar.addWidget(self.chk_show_hpbw)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # Tab widget for different graph views
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: Cartesian Normalized Magnitude
        self.fig_linear = Figure(figsize=(6, 4), tight_layout=True)
        self.canvas_linear = FigureCanvas(self.fig_linear)
        self.ax_linear = self.fig_linear.add_subplot(111)
        tab1_widget = QWidget()
        tab1_layout = QVBoxLayout(tab1_widget)
        tab1_layout.addWidget(NavigationToolbar(self.canvas_linear, tab1_widget))
        tab1_layout.addWidget(self.canvas_linear)
        self.tabs.addTab(tab1_widget, "Cartesian |AF_n|")

        # Tab 2: Cartesian dB
        self.fig_db = Figure(figsize=(6, 4), tight_layout=True)
        self.canvas_db = FigureCanvas(self.fig_db)
        self.ax_db = self.fig_db.add_subplot(111)
        tab2_widget = QWidget()
        tab2_layout = QVBoxLayout(tab2_widget)
        tab2_layout.addWidget(NavigationToolbar(self.canvas_db, tab2_widget))
        tab2_layout.addWidget(self.canvas_db)
        self.tabs.addTab(tab2_widget, "Cartesian (dB)")

        # Tab 3: Polar Pattern
        self.fig_polar = Figure(figsize=(6, 5), tight_layout=True)
        self.canvas_polar = FigureCanvas(self.fig_polar)
        self.ax_polar = self.fig_polar.add_subplot(111, polar=True)
        tab3_widget = QWidget()
        tab3_layout = QVBoxLayout(tab3_widget)
        tab3_layout.addWidget(NavigationToolbar(self.canvas_polar, tab3_widget))
        tab3_layout.addWidget(self.canvas_polar)
        self.tabs.addTab(tab3_widget, "Polar Pattern")

        # Tab 4: 3D Axisymmetric Pattern
        self.fig_3d = Figure(figsize=(6, 5), tight_layout=True)
        self.canvas_3d = FigureCanvas(self.fig_3d)
        self.ax_3d = self.fig_3d.add_subplot(111, projection="3d")
        tab4_widget = QWidget()
        tab4_layout = QVBoxLayout(tab4_widget)
        tab4_layout.addWidget(NavigationToolbar(self.canvas_3d, tab4_widget))
        tab4_layout.addWidget(self.canvas_3d)
        self.tabs.addTab(tab4_widget, "3D Pattern")

        # Tab 5: Amplitude Weights Bar Graph
        self.fig_weights = Figure(figsize=(6, 4), tight_layout=True)
        self.canvas_weights = FigureCanvas(self.fig_weights)
        self.ax_weights = self.fig_weights.add_subplot(111)
        tab5_widget = QWidget()
        tab5_layout = QVBoxLayout(tab5_widget)
        tab5_layout.addWidget(NavigationToolbar(self.canvas_weights, tab5_widget))
        tab5_layout.addWidget(self.canvas_weights)
        self.tabs.addTab(tab5_widget, "Excitation Weights")

        # Cached data for redrawing toggles
        self._last_data = None
        self._reference_data = None  # for pattern comparison

    def _on_toggle_redraw(self):
        if self._last_data is not None:
            self.update_plots(*self._last_data)

    def set_reference_pattern(self, ref_data):
        """Sets reference pattern to overlay for comparison."""
        self._reference_data = ref_data
        self._on_toggle_redraw()

    def clear_reference_pattern(self):
        self._reference_data = None
        self._on_toggle_redraw()

    def update_plots(
        self,
        theta_rad: np.ndarray,
        af_n: np.ndarray,
        af_db: np.ndarray,
        metrics: PatternMetrics,
        plot_floor_db: float = -60.0,
        weights: np.ndarray = None,
    ):
        self._last_data = (theta_rad, af_n, af_db, metrics, plot_floor_db, weights)
        theta_deg = np.degrees(theta_rad)
        show_markers = self.chk_show_markers.isChecked()
        show_hpbw = self.chk_show_hpbw.isChecked()

        # ==========================================
        # 1. Linear Cartesian Plot
        # ==========================================
        self.ax_linear.clear()
        self.ax_linear.plot(theta_deg, af_n, color="#1f77b4", linewidth=2.0, label="Normalized |AF_n|")

        # Overlay reference pattern if available
        if self._reference_data is not None:
            ref_th_deg, ref_af_n, _, ref_label = self._reference_data
            self.ax_linear.plot(ref_th_deg, ref_af_n, "--", color="gray", linewidth=1.5, label=f"Ref: {ref_label}")

        if show_markers:
            # Maxima
            for m in metrics.all_maxima_deg:
                is_main = (metrics.main_beam_deg is not None and np.isclose(m, metrics.main_beam_deg, atol=0.1))
                color = "red" if is_main else "orange"
                marker = "o" if is_main else "*"
                self.ax_linear.plot(m, 1.0, marker, color=color, markersize=8)
                self.ax_linear.annotate(f"{m:.1f}°", (m, 1.0), textcoords="offset points",
                                        xytext=(0, 6), ha="center", fontsize=8, color=color)

            # Nulls
            for n in metrics.nulls_deg:
                self.ax_linear.plot(n, 0.0, "^", color="green", markersize=6)

        if show_hpbw and metrics.half_power_left_deg and metrics.half_power_right_deg:
            hp_val = 1.0 / np.sqrt(2.0)
            self.ax_linear.axhline(hp_val, color="purple", linestyle=":", alpha=0.7)
            self.ax_linear.plot([metrics.half_power_left_deg, metrics.half_power_right_deg],
                                [hp_val, hp_val], "m-", linewidth=2.0, label=f"HPBW = {metrics.hpbw_deg:.2f}°")

        self.ax_linear.set_title("Cartesian Normalized Array Factor |AF_n(θ)|")
        self.ax_linear.set_xlabel("Observation Angle θ (degrees)")
        self.ax_linear.set_ylabel("Normalized Array Factor")
        self.ax_linear.set_xlim(0, 180)
        self.ax_linear.set_ylim(-0.02, 1.1)
        self.ax_linear.set_xticks(np.arange(0, 181, 30))
        self.ax_linear.grid(True, linestyle="--", alpha=0.5)
        self.ax_linear.legend(loc="upper right", fontsize=9)
        self.canvas_linear.draw()

        # ==========================================
        # 2. Cartesian dB Plot
        # ==========================================
        self.ax_db.clear()
        # Clip only for visual display floor
        af_db_disp = np.clip(af_db, plot_floor_db, 0.0)
        self.ax_db.plot(theta_deg, af_db_disp, color="#d62728", linewidth=2.0, label="Array Factor (dB)")

        if self._reference_data is not None:
            ref_th_deg, _, ref_af_db, ref_label = self._reference_data
            ref_db_disp = np.clip(ref_af_db, plot_floor_db, 0.0)
            self.ax_db.plot(ref_th_deg, ref_db_disp, "--", color="gray", linewidth=1.5, label=f"Ref: {ref_label}")

        # -3 dB line
        self.ax_db.axhline(-3.0103, color="black", linestyle="--", alpha=0.7, label="-3 dB (HPBW threshold)")

        if show_hpbw and metrics.half_power_left_deg and metrics.half_power_right_deg:
            self.ax_db.plot([metrics.half_power_left_deg, metrics.half_power_right_deg],
                            [-3.0103, -3.0103], "m-", linewidth=2.5, label=f"HPBW = {metrics.hpbw_deg:.2f}°")

        if show_markers and metrics.peak_sll_db is not None and metrics.peak_sll_angle_deg is not None:
            self.ax_db.plot(metrics.peak_sll_angle_deg, metrics.peak_sll_db, "kD", markersize=7,
                            label=f"Peak SLL: {metrics.peak_sll_db:.1f} dB")

        self.ax_db.set_title("Cartesian Array Factor in Decibels (dB)")
        self.ax_db.set_xlabel("Observation Angle θ (degrees)")
        self.ax_db.set_ylabel("Array Factor (dB)")
        self.ax_db.set_xlim(0, 180)
        self.ax_db.set_ylim(plot_floor_db - 2, 2)
        self.ax_db.set_xticks(np.arange(0, 181, 30))
        self.ax_db.grid(True, linestyle="--", alpha=0.5)
        self.ax_db.legend(loc="upper right", fontsize=9)
        self.canvas_db.draw()

        # ==========================================
        # 3. Polar Plot
        # ==========================================
        self.ax_polar.clear()
        theta_full = np.concatenate([theta_rad, 2.0 * np.pi - theta_rad[::-1]])
        af_n_full = np.concatenate([af_n, af_n[::-1]])

        self.ax_polar.plot(theta_full, af_n_full, color="#2ca02c", linewidth=2.0)
        self.ax_polar.set_theta_zero_location("N")  # 0 deg at top (along positive z-axis)
        self.ax_polar.set_theta_direction(-1)       # Clockwise
        self.ax_polar.set_title("Polar Radiation Pattern (0° Array Axis at Top)", va="bottom")
        self.ax_polar.set_ylim(0, 1.05)
        self.ax_polar.grid(True)
        self.canvas_polar.draw()

        # ==========================================
        # 4. 3D Axisymmetric Pattern
        # ==========================================
        # Only compute 3D if 3D tab is active or requested to keep UI snappy
        if self.tabs.currentIndex() == 3:
            self._render_3d_pattern(theta_rad, af_n)

        # ==========================================
        # 5. Excitation Weights Bar Chart
        # ==========================================
        self.ax_weights.clear()
        if weights is not None:
            N = len(weights)
            x = np.arange(N)
            self.ax_weights.bar(x, weights, color="#17becf", edgecolor="black", alpha=0.85)
            self.ax_weights.set_title(f"Element Excitation Amplitudes (N = {N})")
            self.ax_weights.set_xlabel("Element Index n")
            self.ax_weights.set_ylabel("Normalized Amplitude a_n")
            self.ax_weights.set_xticks(x)
            self.ax_weights.set_xticklabels([f"#{i}" for i in range(N)])
            self.ax_weights.set_ylim(0, 1.1)
            self.ax_weights.grid(True, linestyle="--", alpha=0.4)
            self.canvas_weights.draw()

    def _render_3d_pattern(self, theta_rad: np.ndarray, af_n: np.ndarray):
        """Generates 3D surface revolving axisymmetric pattern around array axis z."""
        self.ax_3d.clear()
        # Subsample theta for smooth 3D rendering
        idx_step = max(1, len(theta_rad) // 60)
        th_sub = theta_rad[::idx_step]
        af_sub = af_n[::idx_step]

        phi = np.linspace(0, 2.0 * np.pi, 40)
        TH, PHI = np.meshgrid(th_sub, phi)
        # R(TH, PHI) = af_sub
        R = np.tile(af_sub, (len(phi), 1))

        # Spherical to Cartesian:
        # z along array axis: z = r * cos(theta)
        # x = r * sin(theta) * cos(phi)
        # y = r * sin(theta) * sin(phi)
        X = R * np.sin(TH) * np.cos(PHI)
        Y = R * np.sin(TH) * np.sin(PHI)
        Z = R * np.cos(TH)

        self.ax_3d.plot_surface(X, Y, Z, cmap="viridis", alpha=0.8, edgecolor="none")
        self.ax_3d.set_title("3D Axisymmetric Radiation Pattern", pad=10)
        self.ax_3d.set_xlabel("X")
        self.ax_3d.set_ylabel("Y")
        self.ax_3d.set_zlabel("Z (Array Axis)")
        self.canvas_3d.draw()

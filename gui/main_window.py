"""
Main application window for Interactive Linear Antenna Array Simulation.
Implements complete requirements from Parts A through H.
"""

import os
import sys
from pathlib import Path
import numpy as np
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
    QFileDialog,
    QMessageBox,
    QStatusBar,
    QScrollArea,
)
from PyQt6.QtCore import Qt, QTimer
from core.physics import deg2rad
from core.array_factor import compute_normalized_pattern
from analysis.pattern_metrics import compute_pattern_metrics
from gui.controls_panel import ControlsPanel
from gui.plots_widget import AntennaPlotsWidget
from gui.geometry_widget import InteractiveGeometryWidget
from gui.results_widget import NumericalResultsWidget
from gui.compare_dialog import ComparePatternsDialog
from export.csv_exporter import export_pattern_to_csv
from export.plot_exporter import save_figure


class AntennaSimulationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive Antenna Array Simulation & Radiation Pattern Control")
        self.resize(1380, 880)

        # Main Central Widget with horizontal splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)

        splitter_h = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter_h)

        # Left Column: Controls (Scrollable)
        scroll_controls = QScrollArea()
        scroll_controls.setWidgetResizable(True)
        self.controls = ControlsPanel()
        scroll_controls.setWidget(self.controls)
        scroll_controls.setMinimumWidth(340)
        scroll_controls.setMaximumWidth(420)
        splitter_h.addWidget(scroll_controls)

        # Middle Column: Plots + Geometry Visualizer
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.setSpacing(4)

        splitter_v = QSplitter(Qt.Orientation.Vertical)
        self.plots = AntennaPlotsWidget()
        self.geometry = InteractiveGeometryWidget()
        splitter_v.addWidget(self.plots)
        splitter_v.addWidget(self.geometry)
        splitter_v.setStretchFactor(0, 3)
        splitter_v.setStretchFactor(1, 2)

        middle_layout.addWidget(splitter_v)
        splitter_h.addWidget(middle_widget)

        # Right Column: Live Numerical Results (Scrollable)
        scroll_results = QScrollArea()
        scroll_results.setWidgetResizable(True)
        self.results = NumericalResultsWidget()
        scroll_results.setWidget(self.results)
        scroll_results.setMinimumWidth(280)
        scroll_results.setMaximumWidth(360)
        splitter_h.addWidget(scroll_results)

        # Splitter sizing
        splitter_h.setStretchFactor(0, 1)
        splitter_h.setStretchFactor(1, 3)
        splitter_h.setStretchFactor(2, 1)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Simulation parameters synchronized.")

        # Animation Timer
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(40)  # ~25 FPS
        self.anim_timer.timeout.connect(self._on_animation_tick)
        self._anim_dir = 1.0  # +1 scanning forward, -1 scanning backward

        # Connect Signals
        self._connect_signals()

        # Initial Computation & Render
        self.recompute_and_update()

    def _connect_signals(self):
        self.controls.parameters_changed.connect(self.recompute_and_update)
        self.controls.reset_clicked.connect(self.on_reset)
        self.controls.broadside_clicked.connect(self.on_broadside)
        self.controls.positive_endfire_clicked.connect(self.on_positive_endfire)
        self.controls.negative_endfire_clicked.connect(self.on_negative_endfire)
        self.controls.save_plot_clicked.connect(self.on_save_plot)
        self.controls.export_csv_clicked.connect(self.on_export_csv)
        self.controls.compare_patterns_clicked.connect(self.on_compare_patterns)
        self.controls.toggle_animation_clicked.connect(self.on_toggle_animation)

    # ---------------- Calculation & Rendering ----------------
    def recompute_and_update(self):
        params = self.controls.get_current_parameters()
        N = params["N"]
        d = params["d_over_lambda"]
        freq_ghz = params["freq_ghz"]
        theta0_deg = params["theta0_deg"]
        beta_deg = params["beta_deg"]
        step_deg = params["angular_step_deg"]
        floor_db = params["plot_floor_db"]
        weights = params["weights"]
        w_type = params["weighting_type"]

        beta_rad = np.radians(beta_deg)

        # Angular grid
        num_pts = max(181, int(round(180.0 / step_deg)) + 1)
        theta_rad = np.linspace(0.0, np.pi, num_pts)

        # 1. Core pattern computation
        is_uniform = (w_type == "Uniform")
        amplitudes = None if is_uniform else weights

        af_n, p_n, af_db = compute_normalized_pattern(
            theta_rad, N, d, beta_rad, amplitudes=amplitudes
        )

        # 2. Pattern metrics detection
        metrics = compute_pattern_metrics(
            theta_rad, af_n, af_db, N, d, beta_rad,
            selected_steering_theta_deg=theta0_deg,
            is_uniform=is_uniform,
        )

        # 3. Update Plots
        self.plots.update_plots(
            theta_rad, af_n, af_db, metrics, plot_floor_db=floor_db, weights=weights
        )

        # 4. Update Array Geometry & Excitation Phasors
        self.geometry.update_geometry(
            N=N,
            d_over_lambda=d,
            beta_rad=beta_rad,
            freq_ghz=freq_ghz,
            theta_obs_deg=theta0_deg,
            amplitudes=weights,
        )

        # 5. Update Live Numerical Results Panel
        self.results.update_results(metrics)

        # Status bar update
        mb_str = f"{metrics.main_beam_deg:.1f}°" if metrics.main_beam_deg is not None else "N/A"
        hpbw_str = f"{metrics.hpbw_deg:.2f}°" if metrics.hpbw_deg is not None else "Not defined"
        self.status_bar.showMessage(
            f"N={N} | d={d:.2f}λ | β={beta_deg:.1f}° | Main Beam: {mb_str} | HPBW: {hpbw_str} | Grating Lobes: {metrics.grating_lobe_count}"
        )

    # ---------------- Presets & Actions ----------------
    def on_reset(self):
        self.controls.spin_N.setValue(8)
        self.controls.spin_d.setValue(0.50)
        self.controls.spin_freq.setValue(3.0)
        self.controls.spin_theta0.setValue(90.0)
        self.controls.spin_beta.setValue(0.0)
        self.controls.spin_step.setValue(0.10)
        self.controls.spin_floor.setValue(-60)
        self.controls.combo_weights.setCurrentIndex(0)
        self.controls.btn_auto_steer.setChecked(True)
        self.plots.clear_reference_pattern()
        self.recompute_and_update()
        self.status_bar.showMessage("Reset all parameters to default.")

    def on_broadside(self):
        self.controls.btn_auto_steer.setChecked(True)
        self.controls.spin_theta0.setValue(90.0)
        self.recompute_and_update()
        self.status_bar.showMessage("Preset applied: Broadside (θ₀ = 90°, β = 0°).")

    def on_positive_endfire(self):
        # Peak at theta = 0°, beta = -kd
        kd_deg = np.degrees(2.0 * np.pi * self.controls.spin_d.value())
        self.controls.btn_auto_steer.setChecked(False)
        self.controls.spin_theta0.setValue(0.0)
        self.controls.spin_beta.setValue(-kd_deg)
        self.recompute_and_update()
        self.status_bar.showMessage(f"Preset applied: Positive End-fire (θ₀ = 0°, β = -{kd_deg:.1f}°).")

    def on_negative_endfire(self):
        # Peak at theta = 180°, beta = +kd
        kd_deg = np.degrees(2.0 * np.pi * self.controls.spin_d.value())
        self.controls.btn_auto_steer.setChecked(False)
        self.controls.spin_theta0.setValue(180.0)
        self.controls.spin_beta.setValue(+kd_deg)
        self.recompute_and_update()
        self.status_bar.showMessage(f"Preset applied: Negative End-fire (θ₀ = 180°, β = +{kd_deg:.1f}°).")

    def on_save_plot(self):
        # Offer saving current active tab figure
        current_tab_idx = self.plots.tabs.currentIndex()
        tab_names = ["cartesian_linear", "cartesian_db", "polar", "3d_pattern", "weights"]
        default_name = f"antenna_plot_{tab_names[current_tab_idx]}.png"

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Plot Figure", default_name, "PNG Image (*.png);;PDF Vector (*.pdf);;SVG Vector (*.svg)"
        )
        if filepath:
            figs = [
                self.plots.fig_linear,
                self.plots.fig_db,
                self.plots.fig_polar,
                self.plots.fig_3d,
                self.plots.fig_weights,
            ]
            fig_to_save = figs[current_tab_idx]
            save_figure(fig_to_save, filepath)
            QMessageBox.information(self, "Plot Saved", f"Figure saved successfully to:\n{filepath}")

    def on_export_csv(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Radiation Pattern CSV", "antenna_pattern_data.csv", "CSV Files (*.csv)"
        )
        if filepath:
            params = self.controls.get_current_parameters()
            N = params["N"]
            d = params["d_over_lambda"]
            freq = params["freq_ghz"]
            beta = params["beta_deg"]
            weights = params["weights"]
            w_type = params["weighting_type"]

            num_pts = max(181, int(round(180.0 / params["angular_step_deg"])) + 1)
            theta_rad = np.linspace(0.0, np.pi, num_pts)
            beta_rad = np.radians(beta)
            is_uniform = (w_type == "Uniform")
            amplitudes = None if is_uniform else weights

            af_n, p_n, af_db = compute_normalized_pattern(
                theta_rad, N, d, beta_rad, amplitudes=amplitudes
            )
            metrics = compute_pattern_metrics(
                theta_rad, af_n, af_db, N, d, beta_rad,
                selected_steering_theta_deg=params["theta0_deg"],
                is_uniform=is_uniform,
            )

            export_pattern_to_csv(
                filepath, theta_rad, af_n, af_db, p_n, metrics,
                N=N, d_over_lambda=d, beta_deg=beta, freq_ghz=freq, weighting_type=w_type
            )
            QMessageBox.information(self, "Export Complete", f"Data exported successfully to:\n{filepath}")

    def on_compare_patterns(self):
        params = self.controls.get_current_parameters()
        theta_rad = np.linspace(0.0, np.pi, 1801)
        theta_deg = np.degrees(theta_rad)
        beta_rad = np.radians(params["beta_deg"])
        is_uniform = (params["weighting_type"] == "Uniform")
        amplitudes = None if is_uniform else params["weights"]

        af_n, _, af_db = compute_normalized_pattern(
            theta_rad, params["N"], params["d_over_lambda"], beta_rad, amplitudes=amplitudes
        )
        label = f"N={params['N']}, d={params['d_over_lambda']}λ, β={params['beta_deg']}°, {params['weighting_type']}"

        dialog = ComparePatternsDialog((theta_deg, af_n, af_db, label), self)
        if dialog.exec():
            if dialog.should_clear:
                self.plots.clear_reference_pattern()
                self.status_bar.showMessage("Reference overlay cleared.")
            elif dialog.reference_data is not None:
                self.plots.set_reference_pattern(dialog.reference_data)
                self.status_bar.showMessage(f"Overlay set to: {dialog.reference_data[3]}")

    def on_toggle_animation(self):
        if self.anim_timer.isActive():
            self.anim_timer.stop()
            self.controls.btn_anim.setText("▶ Resume Steering Animation")
            self.controls.btn_anim.setStyleSheet("font-weight: bold; background-color: #059669; color: white;")
            self.status_bar.showMessage("Steering animation paused.")
        else:
            self.controls.btn_auto_steer.setChecked(True)
            self.anim_timer.start()
            self.controls.btn_anim.setText("⏸ Pause Steering Animation")
            self.controls.btn_anim.setStyleSheet("font-weight: bold; background-color: #d97706; color: white;")
            self.status_bar.showMessage("Steering animation running...")

    def _on_animation_tick(self):
        current_th0 = self.controls.spin_theta0.value()
        new_th0 = current_th0 + self._anim_dir * 1.5
        if new_th0 >= 160.0:
            new_th0 = 160.0
            self._anim_dir = -1.0
        elif new_th0 <= 20.0:
            new_th0 = 20.0
            self._anim_dir = 1.0

        self.controls.spin_theta0.setValue(new_th0)

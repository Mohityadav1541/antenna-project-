"""
GUI controls panel for linear antenna array simulation (Section 3.1 & 3.4).
Features:
- Compact, high-density layout designed to fit on screen without vertical scrolling.
- Explicit high-contrast text and border styling for 100% readability.
- Synchronized sliders and spinboxes for N, d/lambda, beta, freq, theta0, step, floor.
- One-click presets: Broadside, + End-Fire, - End-Fire, Reset All.
- Interactive beam steering animation control and Auto-Steer toggle.
- Pattern comparison and data export triggers.
"""

from typing import Dict, Any, Optional
import numpy as np
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QComboBox,
    QGroupBox,
    QDialog,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDialogButtonBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.physics import physical_spacing_mm, frequency_to_wavelength
from core.tapering import get_weights_by_type


class CustomWeightsDialog(QDialog):
    """Dialog for editing individual element excitation amplitudes and phases."""
    def __init__(self, current_weights: np.ndarray, current_phases: Optional[np.ndarray] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Element Excitations (Amplitudes & Phases)")
        self.resize(380, 360)
        layout = QVBoxLayout(self)

        self.N = len(current_weights)
        self.table = QTableWidget(self.N, 3)
        self.table.setHorizontalHeaderLabels(["Element n", "Amplitude a_n", "Phase φ_n (deg)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for i in range(self.N):
            item_n = QTableWidgetItem(f"#{i}")
            item_n.setFlags(item_n.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_n.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, item_n)

            item_w = QTableWidgetItem(f"{current_weights[i]:.4f}")
            item_w.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 1, item_w)

            p_val = 0.0 if current_phases is None else float(np.degrees(current_phases[i]))
            item_p = QTableWidgetItem(f"{p_val:.1f}")
            item_p.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 2, item_p)

        layout.addWidget(self.table)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_weights_and_phases(self):
        weights = []
        phases = []
        for i in range(self.N):
            try:
                w = float(self.table.item(i, 1).text())
            except ValueError:
                w = 1.0
            try:
                p_deg = float(self.table.item(i, 2).text())
            except ValueError:
                p_deg = 0.0
            weights.append(max(0.0, w))
            phases.append(np.radians(p_deg))
        return np.array(weights, dtype=np.float64), np.array(phases, dtype=np.float64)


class ControlsPanel(QWidget):
    # Parameter change signals
    parameters_changed = pyqtSignal()
    reset_clicked = pyqtSignal()
    broadside_clicked = pyqtSignal()
    positive_endfire_clicked = pyqtSignal()
    negative_endfire_clicked = pyqtSignal()
    save_plot_clicked = pyqtSignal()
    export_csv_clicked = pyqtSignal()
    compare_patterns_clicked = pyqtSignal()
    toggle_animation_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        self.custom_weights: Optional[np.ndarray] = None
        self.custom_phases: Optional[np.ndarray] = None
        self._block_auto_steer = False

        # =====================================================
        # Group 1: Array Parameters (N, d/lambda, Frequency)
        # =====================================================
        grp_array = QGroupBox("1. Array Parameters")
        grp_array_layout = QGridLayout(grp_array)
        grp_array_layout.setContentsMargins(6, 6, 6, 6)
        grp_array_layout.setSpacing(4)

        # 1. Elements N [2, 64], default 8
        lbl_N = QLabel("Elements (N):")
        self.slider_N = QSlider(Qt.Orientation.Horizontal)
        self.slider_N.setRange(2, 64)
        self.slider_N.setValue(8)
        self.spin_N = QSpinBox()
        self.spin_N.setRange(2, 64)
        self.spin_N.setValue(8)
        self.spin_N.setFixedWidth(56)
        self.slider_N.valueChanged.connect(self._sync_N_from_slider)
        self.spin_N.valueChanged.connect(self._sync_N_from_spin)
        grp_array_layout.addWidget(lbl_N, 0, 0)
        grp_array_layout.addWidget(self.slider_N, 0, 1)
        grp_array_layout.addWidget(self.spin_N, 0, 2)

        # 2. Spacing d/lambda [0.05, 2.00], default 0.50
        lbl_d = QLabel("Spacing (d/λ):")
        self.slider_d = QSlider(Qt.Orientation.Horizontal)
        self.slider_d.setRange(5, 200)  # in 0.01 steps
        self.slider_d.setValue(50)
        self.spin_d = QDoubleSpinBox()
        self.spin_d.setRange(0.05, 2.00)
        self.spin_d.setSingleStep(0.05)
        self.spin_d.setDecimals(2)
        self.spin_d.setValue(0.50)
        self.spin_d.setFixedWidth(64)
        self.slider_d.valueChanged.connect(self._sync_d_from_slider)
        self.spin_d.valueChanged.connect(self._sync_d_from_spin)
        grp_array_layout.addWidget(lbl_d, 1, 0)
        grp_array_layout.addWidget(self.slider_d, 1, 1)
        grp_array_layout.addWidget(self.spin_d, 1, 2)

        # 3. Frequency [0.1, 30.0 GHz] + Physical Spacing display
        lbl_freq = QLabel("Frequency:")
        self.spin_freq = QDoubleSpinBox()
        self.spin_freq.setRange(0.1, 30.0)
        self.spin_freq.setSingleStep(0.5)
        self.spin_freq.setValue(3.0)
        self.spin_freq.setSuffix(" GHz")
        self.spin_freq.setFixedWidth(85)
        self.spin_freq.valueChanged.connect(self._on_freq_changed)

        self.lbl_physical_spacing = QLabel("λ: 99.9 mm | d: 50.0 mm")
        self.lbl_physical_spacing.setStyleSheet("font-size: 10px; font-weight: bold; color: #38bdf8;")

        freq_sub_layout = QHBoxLayout()
        freq_sub_layout.setContentsMargins(0, 0, 0, 0)
        freq_sub_layout.setSpacing(6)
        freq_sub_layout.addWidget(self.spin_freq)
        freq_sub_layout.addWidget(self.lbl_physical_spacing)
        freq_sub_layout.addStretch()

        grp_array_layout.addWidget(lbl_freq, 2, 0)
        grp_array_layout.addLayout(freq_sub_layout, 2, 1, 1, 2)

        layout.addWidget(grp_array)

        # =====================================================
        # Group 2: Steering & Phase Control (theta0, beta, Auto)
        # =====================================================
        grp_steer = QGroupBox("2. Steering & Phase Control")
        grp_steer_layout = QGridLayout(grp_steer)
        grp_steer_layout.setContentsMargins(6, 6, 6, 6)
        grp_steer_layout.setSpacing(4)

        # 4. Steering angle theta_0 [0, 180], default 90
        lbl_th0 = QLabel("Steering (θ₀):")
        self.slider_theta0 = QSlider(Qt.Orientation.Horizontal)
        self.slider_theta0.setRange(0, 180)
        self.slider_theta0.setValue(90)
        self.spin_theta0 = QDoubleSpinBox()
        self.spin_theta0.setRange(0.0, 180.0)
        self.spin_theta0.setValue(90.0)
        self.spin_theta0.setSuffix("°")
        self.spin_theta0.setFixedWidth(64)
        self.slider_theta0.valueChanged.connect(self._sync_theta0_from_slider)
        self.spin_theta0.valueChanged.connect(self._sync_theta0_from_spin)
        grp_steer_layout.addWidget(lbl_th0, 0, 0)
        grp_steer_layout.addWidget(self.slider_theta0, 0, 1)
        grp_steer_layout.addWidget(self.spin_theta0, 0, 2)

        # 5. Progressive phase beta [-360, +360], default 0
        lbl_beta = QLabel("Phase (β):")
        self.slider_beta = QSlider(Qt.Orientation.Horizontal)
        self.slider_beta.setRange(-360, 360)
        self.slider_beta.setValue(0)
        self.spin_beta = QDoubleSpinBox()
        self.spin_beta.setRange(-360.0, 360.0)
        self.spin_beta.setValue(0.0)
        self.spin_beta.setSuffix("°")
        self.spin_beta.setFixedWidth(64)
        self.slider_beta.valueChanged.connect(self._sync_beta_from_slider)
        self.spin_beta.valueChanged.connect(self._sync_beta_from_spin)
        grp_steer_layout.addWidget(lbl_beta, 1, 0)
        grp_steer_layout.addWidget(self.slider_beta, 1, 1)
        grp_steer_layout.addWidget(self.spin_beta, 1, 2)

        # Auto Steer Button Toggle
        self.btn_auto_steer = QPushButton("⚡ Auto Steer: ON")
        self.btn_auto_steer.setCheckable(True)
        self.btn_auto_steer.setChecked(True)
        self.btn_auto_steer.setStyleSheet("""
            QPushButton { font-weight: bold; background-color: #2563eb; color: #ffffff; border-radius: 4px; padding: 3px; font-size: 11px; }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        self.btn_auto_steer.toggled.connect(self._on_auto_steer_toggled)
        grp_steer_layout.addWidget(self.btn_auto_steer, 2, 0, 1, 3)

        layout.addWidget(grp_steer)

        # =====================================================
        # Group 3: Excitation & Display (Taper, Step, Floor)
        # =====================================================
        grp_weights = QGroupBox("3. Excitation & Display")
        grp_weights_layout = QGridLayout(grp_weights)
        grp_weights_layout.setContentsMargins(6, 6, 6, 6)
        grp_weights_layout.setSpacing(4)

        # Taper weighting
        lbl_taper = QLabel("Tapering:")
        self.combo_weights = QComboBox()
        self.combo_weights.addItems(["Uniform", "Binomial", "Hann (Cosine)", "Custom"])
        self.combo_weights.currentIndexChanged.connect(self._on_weight_type_changed)

        self.btn_custom_weights = QPushButton("Edit...")
        self.btn_custom_weights.setEnabled(False)
        self.btn_custom_weights.setFixedWidth(56)
        self.btn_custom_weights.clicked.connect(self._open_custom_weights_dialog)

        taper_sub_layout = QHBoxLayout()
        taper_sub_layout.setContentsMargins(0, 0, 0, 0)
        taper_sub_layout.setSpacing(4)
        taper_sub_layout.addWidget(self.combo_weights)
        taper_sub_layout.addWidget(self.btn_custom_weights)

        grp_weights_layout.addWidget(lbl_taper, 0, 0)
        grp_weights_layout.addLayout(taper_sub_layout, 0, 1, 1, 2)

        # Angular step + Plot floor on row 1
        lbl_step = QLabel("Step:")
        self.spin_step = QDoubleSpinBox()
        self.spin_step.setRange(0.01, 2.00)
        self.spin_step.setSingleStep(0.05)
        self.spin_step.setValue(0.10)
        self.spin_step.setSuffix("°")
        self.spin_step.setFixedWidth(60)
        self.spin_step.valueChanged.connect(self._on_param_changed)

        lbl_floor = QLabel("Floor:")
        self.slider_floor = QSlider(Qt.Orientation.Horizontal)
        self.slider_floor.setRange(-100, -20)
        self.slider_floor.setValue(-60)
        self.spin_floor = QSpinBox()
        self.spin_floor.setRange(-100, -20)
        self.spin_floor.setValue(-60)
        self.spin_floor.setSuffix(" dB")
        self.spin_floor.setFixedWidth(64)
        self.slider_floor.valueChanged.connect(self.spin_floor.setValue)
        self.spin_floor.valueChanged.connect(self.slider_floor.setValue)
        self.spin_floor.valueChanged.connect(self._on_param_changed)

        floor_sub_layout = QHBoxLayout()
        floor_sub_layout.setContentsMargins(0, 0, 0, 0)
        floor_sub_layout.setSpacing(4)
        floor_sub_layout.addWidget(lbl_step)
        floor_sub_layout.addWidget(self.spin_step)
        floor_sub_layout.addWidget(lbl_floor)
        floor_sub_layout.addWidget(self.slider_floor)
        floor_sub_layout.addWidget(self.spin_floor)

        grp_weights_layout.addLayout(floor_sub_layout, 1, 0, 1, 3)

        layout.addWidget(grp_weights)

        # =====================================================
        # Group 4: Required Actions & Presets (Compact Grid)
        # =====================================================
        grp_actions = QGroupBox("4. Required Actions & Presets")
        grp_actions_layout = QGridLayout(grp_actions)
        grp_actions_layout.setContentsMargins(6, 6, 6, 6)
        grp_actions_layout.setSpacing(4)

        # Row 0: 3 preset buttons
        self.btn_broadside = QPushButton("Broadside (90°)")
        self.btn_broadside.clicked.connect(self.broadside_clicked.emit)

        self.btn_pos_endfire = QPushButton("+ End-Fire (0°)")
        self.btn_pos_endfire.clicked.connect(self.positive_endfire_clicked.emit)

        self.btn_neg_endfire = QPushButton("- End-Fire (180°)")
        self.btn_neg_endfire.clicked.connect(self.negative_endfire_clicked.emit)

        grp_actions_layout.addWidget(self.btn_broadside, 0, 0)
        grp_actions_layout.addWidget(self.btn_pos_endfire, 0, 1)
        grp_actions_layout.addWidget(self.btn_neg_endfire, 0, 2)

        # Row 1: Reset, Animation, Compare
        self.btn_reset = QPushButton("↺ Reset All")
        self.btn_reset.setStyleSheet("""
            QPushButton { font-weight: bold; background-color: #991b1b; color: #ffffff; border-radius: 4px; padding: 4px; }
            QPushButton:hover { background-color: #b91c1c; }
        """)
        self.btn_reset.clicked.connect(self.reset_clicked.emit)

        self.btn_anim = QPushButton("▶ Animate Steering")
        self.btn_anim.setStyleSheet("""
            QPushButton { font-weight: bold; background-color: #059669; color: #ffffff; border-radius: 4px; padding: 4px; }
            QPushButton:hover { background-color: #10b981; }
        """)
        self.btn_anim.clicked.connect(self.toggle_animation_clicked.emit)

        self.btn_compare = QPushButton("Compare...")
        self.btn_compare.clicked.connect(self.compare_patterns_clicked.emit)

        grp_actions_layout.addWidget(self.btn_reset, 1, 0)
        grp_actions_layout.addWidget(self.btn_anim, 1, 1)
        grp_actions_layout.addWidget(self.btn_compare, 1, 2)

        # Row 2: File Export Buttons
        self.btn_save_plot = QPushButton("📷 Save Plot (PNG/PDF)")
        self.btn_save_plot.clicked.connect(self.save_plot_clicked.emit)

        self.btn_export_csv = QPushButton("📊 Export CSV Data")
        self.btn_export_csv.clicked.connect(self.export_csv_clicked.emit)

        grp_actions_layout.addWidget(self.btn_save_plot, 2, 0, 1, 2)
        grp_actions_layout.addWidget(self.btn_export_csv, 2, 2)

        layout.addWidget(grp_actions)
        layout.addStretch()

        self._update_physical_display()

    # ---------------- Sync & Handlers ----------------
    def _sync_N_from_slider(self, val: int):
        self.spin_N.blockSignals(True)
        self.spin_N.setValue(val)
        self.spin_N.blockSignals(False)
        self._on_param_changed()

    def _sync_N_from_spin(self, val: int):
        self.slider_N.blockSignals(True)
        self.slider_N.setValue(val)
        self.slider_N.blockSignals(False)
        self._on_param_changed()

    def _sync_d_from_slider(self, val: int):
        float_val = val / 100.0
        self.spin_d.blockSignals(True)
        self.spin_d.setValue(float_val)
        self.spin_d.blockSignals(False)
        self._update_physical_display()
        if self.btn_auto_steer.isChecked() and not self._block_auto_steer:
            self._update_beta_from_theta0()
        self._on_param_changed()

    def _sync_d_from_spin(self, val: float):
        int_val = int(round(val * 100.0))
        self.slider_d.blockSignals(True)
        self.slider_d.setValue(int_val)
        self.slider_d.blockSignals(False)
        self._update_physical_display()
        if self.btn_auto_steer.isChecked() and not self._block_auto_steer:
            self._update_beta_from_theta0()
        self._on_param_changed()

    def _sync_theta0_from_slider(self, val: int):
        self.spin_theta0.blockSignals(True)
        self.spin_theta0.setValue(float(val))
        self.spin_theta0.blockSignals(False)
        if self.btn_auto_steer.isChecked() and not self._block_auto_steer:
            self._update_beta_from_theta0()
        self._on_param_changed()

    def _sync_theta0_from_spin(self, val: float):
        int_val = int(round(val))
        self.slider_theta0.blockSignals(True)
        self.slider_theta0.setValue(int_val)
        self.slider_theta0.blockSignals(False)
        if self.btn_auto_steer.isChecked() and not self._block_auto_steer:
            self._update_beta_from_theta0()
        self._on_param_changed()

    def _sync_beta_from_slider(self, val: int):
        self.spin_beta.blockSignals(True)
        self.spin_beta.setValue(float(val))
        self.spin_beta.blockSignals(False)
        if not self._block_auto_steer:
            if self.btn_auto_steer.isChecked():
                self.btn_auto_steer.setChecked(False)
            self._update_theta0_from_beta()
        self._on_param_changed()

    def _sync_beta_from_spin(self, val: float):
        int_val = int(round(val))
        self.slider_beta.blockSignals(True)
        self.slider_beta.setValue(int_val)
        self.slider_beta.blockSignals(False)
        if not self._block_auto_steer:
            if self.btn_auto_steer.isChecked():
                self.btn_auto_steer.setChecked(False)
            self._update_theta0_from_beta()
        self._on_param_changed()

    def _update_beta_from_theta0(self):
        """beta = -kd * cos(theta_0)"""
        kd = 2.0 * np.pi * self.spin_d.value()
        th0_rad = np.radians(self.spin_theta0.value())
        req_beta_deg = np.degrees(-kd * np.cos(th0_rad))
        self._block_auto_steer = True
        self.spin_beta.setValue(req_beta_deg)
        self.slider_beta.setValue(int(round(req_beta_deg)))
        self._block_auto_steer = False

    def _update_theta0_from_beta(self):
        """Update direction display whenever a principal beam exists (Section 6)."""
        from analysis.steering import compute_achieved_angle
        d_val = self.spin_d.value()
        beta_rad = np.radians(self.spin_beta.value())
        achieved_rad = compute_achieved_angle(beta_rad, d_val)
        if achieved_rad is not None:
            achieved_th0_deg = float(np.degrees(achieved_rad))
            self.slider_theta0.blockSignals(True)
            self.spin_theta0.blockSignals(True)
            self.slider_theta0.setValue(int(round(achieved_th0_deg)))
            self.spin_theta0.setValue(achieved_th0_deg)
            self.slider_theta0.blockSignals(False)
            self.spin_theta0.blockSignals(False)

    def _on_auto_steer_toggled(self, checked: bool):
        if checked:
            self.btn_auto_steer.setText("⚡ Auto Steer: ON")
            self.btn_auto_steer.setStyleSheet("""
                QPushButton { font-weight: bold; background-color: #2563eb; color: #ffffff; border-radius: 4px; padding: 3px; font-size: 11px; }
                QPushButton:hover { background-color: #1d4ed8; }
            """)
            self._update_beta_from_theta0()
            self._on_param_changed()
        else:
            self.btn_auto_steer.setText("Auto Steer: OFF (Manual Phase)")
            self.btn_auto_steer.setStyleSheet("""
                QPushButton { font-weight: 500; background-color: #334155; color: #cbd5e1; border-radius: 4px; padding: 3px; font-size: 11px; }
                QPushButton:hover { background-color: #475569; }
            """)

    def _on_freq_changed(self, val: float):
        self._update_physical_display()
        self._on_param_changed()

    def _update_physical_display(self):
        freq_ghz = self.spin_freq.value()
        d_lambda = self.spin_d.value()
        lam_mm = frequency_to_wavelength(freq_ghz * 1e9) * 1000.0
        d_mm = physical_spacing_mm(d_lambda, freq_ghz * 1e9)
        self.lbl_physical_spacing.setText(f"λ: {lam_mm:.1f} mm | d: {d_mm:.1f} mm")

    def _on_weight_type_changed(self, idx: int):
        t = self.combo_weights.currentText()
        self.btn_custom_weights.setEnabled(t == "Custom")
        self._on_param_changed()

    def _open_custom_weights_dialog(self):
        N = self.spin_N.value()
        if self.custom_weights is None or len(self.custom_weights) != N:
            self.custom_weights = np.ones(N)
        if self.custom_phases is None or len(self.custom_phases) != N:
            self.custom_phases = np.zeros(N)

        dlg = CustomWeightsDialog(self.custom_weights, self.custom_phases, self)
        if dlg.exec():
            w, p = dlg.get_weights_and_phases()
            self.custom_weights = w
            self.custom_phases = p
            self._on_param_changed()

    def _on_param_changed(self):
        self.parameters_changed.emit()

    def get_current_parameters(self) -> Dict[str, Any]:
        N = self.spin_N.value()
        w_type = self.combo_weights.currentText()
        if w_type == "Custom":
            if self.custom_weights is None or len(self.custom_weights) != N:
                weights = np.ones(N)
            else:
                weights = self.custom_weights
            phases = self.custom_phases
        else:
            weights = get_weights_by_type(w_type, N)
            phases = None

        return {
            "N": N,
            "d_over_lambda": float(self.spin_d.value()),
            "freq_ghz": float(self.spin_freq.value()),
            "theta0_deg": float(self.spin_theta0.value()),
            "beta_deg": float(self.spin_beta.value()),
            "angular_step_deg": float(self.spin_step.value()),
            "plot_floor_db": float(self.spin_floor.value()),
            "weighting_type": w_type,
            "weights": weights,
            "phases": phases,
            "auto_steer": self.btn_auto_steer.isChecked(),
        }

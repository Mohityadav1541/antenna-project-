"""
Control panel for antenna parameters, presets, and actions (Section 3.1 & 3.4).
"""

from typing import Optional
import numpy as np
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QSlider,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QComboBox,
    QDialog,
    QTableWidget,
    QTableWidgetItem,
    QDialogButtonBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.physics import physical_spacing_mm, frequency_to_wavelength
from core.tapering import get_weights_by_type


class CustomWeightsDialog(QDialog):
    """Dialog to manually specify element excitation amplitudes (Part F)."""
    def __init__(self, current_weights: np.ndarray, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Custom Excitation Amplitudes")
        self.resize(320, 400)
        layout = QVBoxLayout(self)

        self.table = QTableWidget(len(current_weights), 2)
        self.table.setHorizontalHeaderLabels(["Element n", "Amplitude a_n"])
        for i, w in enumerate(current_weights):
            item_n = QTableWidgetItem(f"#{i}")
            item_n.setFlags(item_n.flags() ^ Qt.ItemFlag.ItemIsEditable)
            item_w = QTableWidgetItem(f"{w:.4f}")
            self.table.setItem(i, 0, item_n)
            self.table.setItem(i, 1, item_w)

        layout.addWidget(self.table)
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def get_weights(self) -> np.ndarray:
        weights = []
        for i in range(self.table.rowCount()):
            try:
                val = float(self.table.item(i, 1).text())
            except ValueError:
                val = 1.0
            weights.append(val)
        w = np.array(weights, dtype=np.float64)
        max_w = np.max(np.abs(w))
        return w / max_w if max_w > 0 else np.ones_like(w)


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
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(10)

        self.custom_weights: Optional[np.ndarray] = None
        self._block_auto_steer = False

        # Group 1: Array Parameters
        grp_array = QGroupBox("Array Parameters")
        grp_array_layout = QGridLayout(grp_array)
        grp_array_layout.setSpacing(6)

        # 1. Number of elements N [2, 64], default 8
        grp_array_layout.addWidget(QLabel("Elements (N):"), 0, 0)
        self.slider_N = QSlider(Qt.Orientation.Horizontal)
        self.slider_N.setRange(2, 64)
        self.slider_N.setValue(8)
        self.spin_N = QSpinBox()
        self.spin_N.setRange(2, 64)
        self.spin_N.setValue(8)
        self.slider_N.valueChanged.connect(self._sync_N_from_slider)
        self.spin_N.valueChanged.connect(self._sync_N_from_spin)
        grp_array_layout.addWidget(self.slider_N, 0, 1)
        grp_array_layout.addWidget(self.spin_N, 0, 2)

        # 2. Spacing d/lambda [0.05, 2.00], default 0.50
        grp_array_layout.addWidget(QLabel("Spacing (d/λ):"), 1, 0)
        self.slider_d = QSlider(Qt.Orientation.Horizontal)
        self.slider_d.setRange(5, 200)  # in 0.01 steps
        self.slider_d.setValue(50)
        self.spin_d = QDoubleSpinBox()
        self.spin_d.setRange(0.05, 2.00)
        self.spin_d.setSingleStep(0.05)
        self.spin_d.setDecimals(2)
        self.spin_d.setValue(0.50)
        self.slider_d.valueChanged.connect(self._sync_d_from_slider)
        self.spin_d.valueChanged.connect(self._sync_d_from_spin)
        grp_array_layout.addWidget(self.slider_d, 1, 1)
        grp_array_layout.addWidget(self.spin_d, 1, 2)

        # 3. Frequency [0.1, 30.0 GHz], default 3.0 GHz
        grp_array_layout.addWidget(QLabel("Frequency (GHz):"), 2, 0)
        self.spin_freq = QDoubleSpinBox()
        self.spin_freq.setRange(0.1, 30.0)
        self.spin_freq.setSingleStep(0.5)
        self.spin_freq.setValue(3.0)
        self.spin_freq.setSuffix(" GHz")
        self.spin_freq.valueChanged.connect(self._on_freq_changed)
        grp_array_layout.addWidget(self.spin_freq, 2, 1, 1, 2)

        # Physical spacing display
        self.lbl_physical_spacing = QLabel("λ: 100.0 mm | d: 50.0 mm")
        self.lbl_physical_spacing.setStyleSheet("font-size: 11px; color: #4b5563; font-style: italic;")
        grp_array_layout.addWidget(self.lbl_physical_spacing, 3, 0, 1, 3)

        layout.addWidget(grp_array)

        # Group 2: Steering & Phase
        grp_steer = QGroupBox("Steering & Phase Control")
        grp_steer_layout = QGridLayout(grp_steer)
        grp_steer_layout.setSpacing(6)

        # 4. Steering angle theta_0 [0, 180], default 90
        grp_steer_layout.addWidget(QLabel("Steering Angle (θ₀):"), 0, 0)
        self.slider_theta0 = QSlider(Qt.Orientation.Horizontal)
        self.slider_theta0.setRange(0, 180)
        self.slider_theta0.setValue(90)
        self.spin_theta0 = QDoubleSpinBox()
        self.spin_theta0.setRange(0.0, 180.0)
        self.spin_theta0.setValue(90.0)
        self.spin_theta0.setSuffix("°")
        self.slider_theta0.valueChanged.connect(self._sync_theta0_from_slider)
        self.spin_theta0.valueChanged.connect(self._sync_theta0_from_spin)
        grp_steer_layout.addWidget(self.slider_theta0, 0, 1)
        grp_steer_layout.addWidget(self.spin_theta0, 0, 2)

        # 5. Progressive phase beta [-360, +360], default 0
        grp_steer_layout.addWidget(QLabel("Progressive Phase (β):"), 1, 0)
        self.slider_beta = QSlider(Qt.Orientation.Horizontal)
        self.slider_beta.setRange(-360, 360)
        self.slider_beta.setValue(0)
        self.spin_beta = QDoubleSpinBox()
        self.spin_beta.setRange(-360.0, 360.0)
        self.spin_beta.setValue(0.0)
        self.spin_beta.setSuffix("°")
        self.slider_beta.valueChanged.connect(self._sync_beta_from_slider)
        self.spin_beta.valueChanged.connect(self._sync_beta_from_spin)
        grp_steer_layout.addWidget(self.slider_beta, 1, 1)
        grp_steer_layout.addWidget(self.spin_beta, 1, 2)

        # Auto Steer Button Toggle
        self.btn_auto_steer = QPushButton("Auto Steer: ON")
        self.btn_auto_steer.setCheckable(True)
        self.btn_auto_steer.setChecked(True)
        self.btn_auto_steer.setStyleSheet("QPushButton { font-weight: bold; background-color: #2563eb; color: white; border-radius: 4px; padding: 4px; }")
        self.btn_auto_steer.toggled.connect(self._on_auto_steer_toggled)
        grp_steer_layout.addWidget(self.btn_auto_steer, 2, 0, 1, 3)

        layout.addWidget(grp_steer)

        # Group 3: Pattern & Excitation Control
        grp_weights = QGroupBox("Excitation & Display")
        grp_weights_layout = QGridLayout(grp_weights)

        grp_weights_layout.addWidget(QLabel("Taper Weighting:"), 0, 0)
        self.combo_weights = QComboBox()
        self.combo_weights.addItems(["Uniform", "Binomial", "Hann (Cosine)", "Custom"])
        self.combo_weights.currentIndexChanged.connect(self._on_weight_type_changed)
        grp_weights_layout.addWidget(self.combo_weights, 0, 1)

        self.btn_custom_weights = QPushButton("Edit Weights...")
        self.btn_custom_weights.setEnabled(False)
        self.btn_custom_weights.clicked.connect(self._open_custom_weights_dialog)
        grp_weights_layout.addWidget(self.btn_custom_weights, 0, 2)

        # Angular step [0.01, 2.0], default 0.1
        grp_weights_layout.addWidget(QLabel("Angular Step:"), 1, 0)
        self.spin_step = QDoubleSpinBox()
        self.spin_step.setRange(0.01, 2.00)
        self.spin_step.setSingleStep(0.05)
        self.spin_step.setValue(0.10)
        self.spin_step.setSuffix("°")
        self.spin_step.valueChanged.connect(self._on_param_changed)
        grp_weights_layout.addWidget(self.spin_step, 1, 1, 1, 2)

        # Plot Floor [-100, -20 dB], default -60 dB
        grp_weights_layout.addWidget(QLabel("Plot Floor:"), 2, 0)
        self.slider_floor = QSlider(Qt.Orientation.Horizontal)
        self.slider_floor.setRange(-100, -20)
        self.slider_floor.setValue(-60)
        self.spin_floor = QSpinBox()
        self.spin_floor.setRange(-100, -20)
        self.spin_floor.setValue(-60)
        self.spin_floor.setSuffix(" dB")
        self.slider_floor.valueChanged.connect(self.spin_floor.setValue)
        self.spin_floor.valueChanged.connect(self.slider_floor.setValue)
        self.spin_floor.valueChanged.connect(self._on_param_changed)
        grp_weights_layout.addWidget(self.slider_floor, 2, 1)
        grp_weights_layout.addWidget(self.spin_floor, 2, 2)

        layout.addWidget(grp_weights)

        # Group 4: Presets & Actions (Section 3.4)
        grp_actions = QGroupBox("Required Actions & Presets")
        grp_actions_layout = QGridLayout(grp_actions)
        grp_actions_layout.setSpacing(6)

        self.btn_broadside = QPushButton("Broadside (90°)")
        self.btn_broadside.clicked.connect(self.broadside_clicked.emit)

        self.btn_pos_endfire = QPushButton("+ End-Fire (0°)")
        self.btn_pos_endfire.clicked.connect(self.positive_endfire_clicked.emit)

        self.btn_neg_endfire = QPushButton("- End-Fire (180°)")
        self.btn_neg_endfire.clicked.connect(self.negative_endfire_clicked.emit)

        self.btn_reset = QPushButton("Reset All")
        self.btn_reset.setStyleSheet("color: #b91c1c;")
        self.btn_reset.clicked.connect(self.reset_clicked.emit)

        grp_actions_layout.addWidget(self.btn_broadside, 0, 0)
        grp_actions_layout.addWidget(self.btn_pos_endfire, 0, 1)
        grp_actions_layout.addWidget(self.btn_neg_endfire, 1, 0)
        grp_actions_layout.addWidget(self.btn_reset, 1, 1)

        # Animation button
        self.btn_anim = QPushButton("▶ Start Steering Animation")
        self.btn_anim.setStyleSheet("font-weight: bold; background-color: #059669; color: white;")
        self.btn_anim.clicked.connect(self.toggle_animation_clicked.emit)
        grp_actions_layout.addWidget(self.btn_anim, 2, 0, 1, 2)

        # File export actions
        self.btn_compare = QPushButton("Compare Patterns...")
        self.btn_compare.clicked.connect(self.compare_patterns_clicked.emit)

        self.btn_save_plot = QPushButton("Save Plot (PNG/PDF)")
        self.btn_save_plot.clicked.connect(self.save_plot_clicked.emit)

        self.btn_export_csv = QPushButton("Export CSV Data")
        self.btn_export_csv.clicked.connect(self.export_csv_clicked.emit)

        grp_actions_layout.addWidget(self.btn_compare, 3, 0, 1, 2)
        grp_actions_layout.addWidget(self.btn_save_plot, 4, 0)
        grp_actions_layout.addWidget(self.btn_export_csv, 4, 1)

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
        if not self.btn_auto_steer.isChecked() or self._block_auto_steer:
            # Manually updating beta updates direction display
            self._update_theta0_from_beta()
        self._on_param_changed()

    def _sync_beta_from_spin(self, val: float):
        int_val = int(round(val))
        self.slider_beta.blockSignals(True)
        self.slider_beta.setValue(int_val)
        self.slider_beta.blockSignals(False)
        if not self.btn_auto_steer.isChecked() or self._block_auto_steer:
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
        """cos(theta_0) = -beta / kd"""
        kd = 2.0 * np.pi * self.spin_d.value()
        beta_rad = np.radians(self.spin_beta.value())
        if kd > 0:
            cos_val = -beta_rad / kd
            if abs(cos_val) <= 1.0:
                achieved_th0_deg = np.degrees(np.arccos(cos_val))
                self.slider_theta0.blockSignals(True)
                self.spin_theta0.blockSignals(True)
                self.slider_theta0.setValue(int(round(achieved_th0_deg)))
                self.spin_theta0.setValue(achieved_th0_deg)
                self.slider_theta0.blockSignals(False)
                self.spin_theta0.blockSignals(False)

    def _on_auto_steer_toggled(self, checked: bool):
        if checked:
            self.btn_auto_steer.setText("Auto Steer: ON")
            self.btn_auto_steer.setStyleSheet("QPushButton { font-weight: bold; background-color: #2563eb; color: white; border-radius: 4px; padding: 4px; }")
            self._update_beta_from_theta0()
            self._on_param_changed()
        else:
            self.btn_auto_steer.setText("Auto Steer: OFF (Manual β)")
            self.btn_auto_steer.setStyleSheet("QPushButton { font-weight: normal; background-color: #4b5563; color: white; border-radius: 4px; padding: 4px; }")

    def _on_freq_changed(self):
        self._update_physical_display()
        self._on_param_changed()

    def _update_physical_display(self):
        lam_mm = frequency_to_wavelength(self.spin_freq.value() * 1e9) * 1000.0
        d_mm = physical_spacing_mm(self.spin_d.value(), self.spin_freq.value() * 1e9)
        self.lbl_physical_spacing.setText(f"λ: {lam_mm:.2f} mm | Physical d: {d_mm:.2f} mm")

    def _on_weight_type_changed(self, idx: int):
        is_custom = (self.combo_weights.currentText() == "Custom")
        self.btn_custom_weights.setEnabled(is_custom)
        if is_custom and self.custom_weights is None:
            self.custom_weights = np.ones(self.spin_N.value())
        self._on_param_changed()

    def _open_custom_weights_dialog(self):
        N = self.spin_N.value()
        if self.custom_weights is None or len(self.custom_weights) != N:
            self.custom_weights = np.ones(N)
        dialog = CustomWeightsDialog(self.custom_weights, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.custom_weights = dialog.get_weights()
            self._on_param_changed()

    def _on_param_changed(self):
        self.parameters_changed.emit()

    # ---------------- Public Accessors ----------------
    def get_current_parameters(self) -> dict:
        N = self.spin_N.value()
        w_type = self.combo_weights.currentText()
        if w_type == "Custom" and self.custom_weights is not None and len(self.custom_weights) == N:
            weights = self.custom_weights
        else:
            weights = get_weights_by_type(w_type.split()[0], N)

        return {
            "N": N,
            "d_over_lambda": self.spin_d.value(),
            "freq_ghz": self.spin_freq.value(),
            "theta0_deg": self.spin_theta0.value(),
            "beta_deg": self.spin_beta.value(),
            "angular_step_deg": self.spin_step.value(),
            "plot_floor_db": self.spin_floor.value(),
            "weighting_type": w_type,
            "weights": weights,
        }

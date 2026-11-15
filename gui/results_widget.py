"""
Live numerical results panel (Section 3.3).
Displays:
- Global-maximum angles
- Selected main-beam direction
- Null angles
- HPBW (interpolated)
- FNBW
- Peak Sidelobe Level (SLL in dB)
- Visible grating-lobe count
- kd and beta in degrees and radians
- Clearly indicates undefined or ambiguous quantities
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QGroupBox,
    QScrollArea,
    QFrame,
)
from PyQt6.QtCore import Qt
from analysis.pattern_metrics import PatternMetrics


class NumericalResultsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(8)

        # Title
        title = QLabel("Live Numerical Analysis")
        title.setStyleSheet("font-weight: bold; font-size: 13px; color: #1e3a8a;")
        main_layout.addWidget(title)

        # Primary Metrics Group
        grp_primary = QGroupBox("Beam Characteristics")
        grp_primary_layout = QGridLayout(grp_primary)
        grp_primary_layout.setSpacing(6)

        self.lbl_main_beam = self._create_value_label()
        self.lbl_hpbw = self._create_value_label()
        self.lbl_fnbw = self._create_value_label()
        self.lbl_sll = self._create_value_label()
        self.lbl_grating_count = self._create_value_label()

        grp_primary_layout.addWidget(QLabel("Main-Beam Direction:"), 0, 0)
        grp_primary_layout.addWidget(self.lbl_main_beam, 0, 1)

        grp_primary_layout.addWidget(QLabel("HPBW (-3 dB Beamwidth):"), 1, 0)
        grp_primary_layout.addWidget(self.lbl_hpbw, 1, 1)

        grp_primary_layout.addWidget(QLabel("FNBW (First-Null Beamwidth):"), 2, 0)
        grp_primary_layout.addWidget(self.lbl_fnbw, 2, 1)

        grp_primary_layout.addWidget(QLabel("Peak SLL:"), 3, 0)
        grp_primary_layout.addWidget(self.lbl_sll, 3, 1)

        grp_primary_layout.addWidget(QLabel("Visible Grating Lobes:"), 4, 0)
        grp_primary_layout.addWidget(self.lbl_grating_count, 4, 1)

        main_layout.addWidget(grp_primary)

        # Phase & Spacing Parameters Group
        grp_phase = QGroupBox("Phase & Wavenumber")
        grp_phase_layout = QGridLayout(grp_phase)
        grp_phase_layout.setSpacing(6)

        self.lbl_kd = self._create_value_label()
        self.lbl_beta = self._create_value_label()

        grp_phase_layout.addWidget(QLabel("Spatial Phase kd:"), 0, 0)
        grp_phase_layout.addWidget(self.lbl_kd, 0, 1)

        grp_phase_layout.addWidget(QLabel("Progressive Phase β:"), 1, 0)
        grp_phase_layout.addWidget(self.lbl_beta, 1, 1)

        main_layout.addWidget(grp_phase)

        # Angular Locations Group
        grp_angles = QGroupBox("Pattern Angular Locations")
        grp_angles_layout = QVBoxLayout(grp_angles)

        grp_angles_layout.addWidget(QLabel("All Global Maxima (θ):"))
        self.lbl_all_maxima = QLabel("None")
        self.lbl_all_maxima.setWordWrap(True)
        self.lbl_all_maxima.setStyleSheet("font-weight: 500; color: #1e3a8a; background: #f1f5f9; padding: 4px; border-radius: 4px;")
        grp_angles_layout.addWidget(self.lbl_all_maxima)

        grp_angles_layout.addWidget(QLabel("Null Angles (θ):"))
        self.lbl_nulls = QLabel("None")
        self.lbl_nulls.setWordWrap(True)
        self.lbl_nulls.setStyleSheet("font-weight: 500; color: #047857; background: #f0fdf4; padding: 4px; border-radius: 4px;")
        grp_angles_layout.addWidget(self.lbl_nulls)

        main_layout.addWidget(grp_angles)
        main_layout.addStretch()

    def _create_value_label(self) -> QLabel:
        lbl = QLabel("--")
        lbl.setStyleSheet("font-weight: bold; color: #111827; background: #f8fafc; padding: 3px 6px; border: 1px solid #e2e8f0; border-radius: 4px;")
        return lbl

    def _format_undefined(self, label: QLabel, text: str = "Not defined"):
        label.setText(text)
        label.setStyleSheet("font-weight: 500; color: #dc2626; background: #fef2f2; padding: 3px 6px; border: 1px solid #fecaca; border-radius: 4px;")

    def _format_valid(self, label: QLabel, text: str):
        label.setText(text)
        label.setStyleSheet("font-weight: bold; color: #111827; background: #f8fafc; padding: 3px 6px; border: 1px solid #e2e8f0; border-radius: 4px;")

    def update_results(self, metrics: PatternMetrics):
        # Main beam
        if metrics.main_beam_deg is not None:
            self._format_valid(self.lbl_main_beam, f"{metrics.main_beam_deg:.2f}°")
        else:
            self._format_undefined(self.lbl_main_beam)

        # HPBW
        if metrics.hpbw_deg is not None:
            self._format_valid(self.lbl_hpbw, f"{metrics.hpbw_deg:.2f}° ({metrics.half_power_left_deg:.1f}° → {metrics.half_power_right_deg:.1f}°)")
        else:
            self._format_undefined(self.lbl_hpbw, "Not defined (boundary beam)")

        # FNBW
        if metrics.fnbw_deg is not None:
            self._format_valid(self.lbl_fnbw, f"{metrics.fnbw_deg:.2f}° ({metrics.first_null_left_deg:.1f}° → {metrics.first_null_right_deg:.1f}°)")
        else:
            self._format_undefined(self.lbl_fnbw, "Not defined (boundary beam)")

        # SLL
        if metrics.peak_sll_db is not None:
            self._format_valid(self.lbl_sll, f"{metrics.peak_sll_db:.2f} dB (@ {metrics.peak_sll_angle_deg:.1f}°)")
        else:
            self._format_undefined(self.lbl_sll, "Not defined (no sidelobes)")

        # Grating lobes
        if metrics.grating_lobe_count > 0:
            gl_str = f"{metrics.grating_lobe_count} (" + ", ".join(f"{g:.1f}°" for g in metrics.grating_lobes_deg) + ")"
            self.lbl_grating_count.setText(gl_str)
            self.lbl_grating_count.setStyleSheet("font-weight: bold; color: #b91c1c; background: #fef2f2; padding: 3px 6px; border: 1px solid #fecaca; border-radius: 4px;")
        else:
            self._format_valid(self.lbl_grating_count, "0 (None)")

        # kd
        self._format_valid(self.lbl_kd, f"{metrics.kd_rad:.4f} rad ({metrics.kd_deg:.1f}°)")

        # beta
        self._format_valid(self.lbl_beta, f"{metrics.beta_deg:.1f}° ({metrics.beta_rad:.4f} rad)")

        # All maxima list
        if metrics.all_maxima_deg:
            self.lbl_all_maxima.setText(", ".join(f"{m:.2f}°" for m in metrics.all_maxima_deg))
        else:
            self.lbl_all_maxima.setText("None")

        # Nulls list
        if metrics.nulls_deg:
            if len(metrics.nulls_deg) > 10:
                short_nulls = ", ".join(f"{n:.1f}°" for n in metrics.nulls_deg[:10]) + f"... ({len(metrics.nulls_deg)} total)"
            else:
                short_nulls = ", ".join(f"{n:.2f}°" for n in metrics.nulls_deg)
            self.lbl_nulls.setText(short_nulls)
        else:
            self.lbl_nulls.setText("No visible nulls")

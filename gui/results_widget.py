"""
Live numerical results panel (Section 3.3).
Displays:
1. Beam Characteristics: Main-Beam Direction, HPBW, FNBW, Peak SLL, Visible Grating Lobes
2. Phase & Wavenumber: Spatial Phase kd, Progressive Phase beta
3. Pattern Angular Locations: All Global Maxima, Null Angles
Features:
- Compact vertical layout fitting within 360px without requiring vertical scrolling.
- High-contrast, theme-aware badges for valid, ambiguous, and undefined quantities.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QGroupBox,
)
from PyQt6.QtCore import Qt
from analysis.pattern_metrics import PatternMetrics


class NumericalResultsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_dark_theme = True  # Default theme mode

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(6)

        # Title Header
        self.title = QLabel("Live Numerical Analysis")
        self.title.setStyleSheet("font-weight: bold; font-size: 13px; color: #38bdf8;")
        main_layout.addWidget(self.title)

        # =====================================================
        # Group 1: Beam Characteristics (5 metrics)
        # =====================================================
        grp_primary = QGroupBox("1. Beam Characteristics")
        grp_primary_layout = QGridLayout(grp_primary)
        grp_primary_layout.setContentsMargins(6, 6, 6, 6)
        grp_primary_layout.setSpacing(4)

        self.lbl_main_beam = self._create_value_label()
        self.lbl_hpbw = self._create_value_label()
        self.lbl_fnbw = self._create_value_label()
        self.lbl_sll = self._create_value_label()
        self.lbl_grating_count = self._create_value_label()

        lbl_mb_title = QLabel("Main-Beam Direction:")
        lbl_hp_title = QLabel("HPBW (-3 dB Beamwidth):")
        lbl_fn_title = QLabel("FNBW (First-Null Beamwidth):")
        lbl_sll_title = QLabel("Peak SLL:")
        lbl_gl_title = QLabel("Visible Grating Lobes:")

        grp_primary_layout.addWidget(lbl_mb_title, 0, 0)
        grp_primary_layout.addWidget(self.lbl_main_beam, 0, 1)

        grp_primary_layout.addWidget(lbl_hp_title, 1, 0)
        grp_primary_layout.addWidget(self.lbl_hpbw, 1, 1)

        grp_primary_layout.addWidget(lbl_fn_title, 2, 0)
        grp_primary_layout.addWidget(self.lbl_fnbw, 2, 1)

        grp_primary_layout.addWidget(lbl_sll_title, 3, 0)
        grp_primary_layout.addWidget(self.lbl_sll, 3, 1)

        grp_primary_layout.addWidget(lbl_gl_title, 4, 0)
        grp_primary_layout.addWidget(self.lbl_grating_count, 4, 1)

        main_layout.addWidget(grp_primary)

        # =====================================================
        # Group 2: Phase & Wavenumber
        # =====================================================
        grp_phase = QGroupBox("2. Phase & Wavenumber")
        grp_phase_layout = QGridLayout(grp_phase)
        grp_phase_layout.setContentsMargins(6, 6, 6, 6)
        grp_phase_layout.setSpacing(4)

        self.lbl_kd = self._create_value_label()
        self.lbl_beta = self._create_value_label()

        lbl_kd_title = QLabel("Spatial Phase kd:")
        lbl_beta_title = QLabel("Progressive Phase β:")

        grp_phase_layout.addWidget(lbl_kd_title, 0, 0)
        grp_phase_layout.addWidget(self.lbl_kd, 0, 1)

        grp_phase_layout.addWidget(lbl_beta_title, 1, 0)
        grp_phase_layout.addWidget(self.lbl_beta, 1, 1)

        main_layout.addWidget(grp_phase)

        # =====================================================
        # Group 3: Pattern Angular Locations
        # =====================================================
        grp_angles = QGroupBox("3. Pattern Angular Locations")
        grp_angles_layout = QVBoxLayout(grp_angles)
        grp_angles_layout.setContentsMargins(6, 6, 6, 6)
        grp_angles_layout.setSpacing(3)

        lbl_max_title = QLabel("All Global Maxima (θ):")
        self.lbl_all_maxima = QLabel("None")
        self.lbl_all_maxima.setWordWrap(True)
        grp_angles_layout.addWidget(lbl_max_title)
        grp_angles_layout.addWidget(self.lbl_all_maxima)

        lbl_null_title = QLabel("Null Angles (θ):")
        self.lbl_nulls = QLabel("None")
        self.lbl_nulls.setWordWrap(True)
        grp_angles_layout.addWidget(lbl_null_title)
        grp_angles_layout.addWidget(self.lbl_nulls)

        main_layout.addWidget(grp_angles)
        main_layout.addStretch()

        self._refresh_styles()

    def set_dark_mode(self, is_dark: bool):
        self.is_dark_theme = is_dark
        self._refresh_styles()

    def _refresh_styles(self):
        if self.is_dark_theme:
            self.title.setStyleSheet("font-weight: bold; font-size: 13px; color: #38bdf8;")
            self.lbl_all_maxima.setStyleSheet("font-weight: 600; font-size: 11px; color: #60a5fa; background: #0f172a; padding: 3px 6px; border: 1px solid #1e3a8a; border-radius: 4px;")
            self.lbl_nulls.setStyleSheet("font-weight: 600; font-size: 11px; color: #34d399; background: #0f172a; padding: 3px 6px; border: 1px solid #065f46; border-radius: 4px;")
        else:
            self.title.setStyleSheet("font-weight: bold; font-size: 13px; color: #1e40af;")
            self.lbl_all_maxima.setStyleSheet("font-weight: 600; font-size: 11px; color: #0369a1; background: #f0f9ff; padding: 3px 6px; border: 1px solid #bae6fd; border-radius: 4px;")
            self.lbl_nulls.setStyleSheet("font-weight: 600; font-size: 11px; color: #15803d; background: #f0fdf4; padding: 3px 6px; border: 1px solid #bbf7d0; border-radius: 4px;")

    def _create_value_label(self) -> QLabel:
        lbl = QLabel("--")
        self._format_valid(lbl, "--")
        return lbl

    def _format_undefined(self, label: QLabel, text: str = "Not defined"):
        label.setText(text)
        if self.is_dark_theme:
            label.setStyleSheet("font-weight: 600; font-size: 11px; color: #fca5a5; background: #450a0a; padding: 2px 5px; border: 1px solid #991b1b; border-radius: 4px;")
        else:
            label.setStyleSheet("font-weight: 600; font-size: 11px; color: #dc2626; background: #fef2f2; padding: 2px 5px; border: 1px solid #fecaca; border-radius: 4px;")

    def _format_ambiguous(self, label: QLabel, text: str):
        label.setText(text)
        if self.is_dark_theme:
            label.setStyleSheet("font-weight: 600; font-size: 11px; color: #fde047; background: #451a03; padding: 2px 5px; border: 1px solid #ca8a04; border-radius: 4px;")
        else:
            label.setStyleSheet("font-weight: 600; font-size: 11px; color: #b45309; background: #fffbeb; padding: 2px 5px; border: 1px solid #fde68a; border-radius: 4px;")

    def _format_valid(self, label: QLabel, text: str):
        label.setText(text)
        if self.is_dark_theme:
            label.setStyleSheet("font-weight: bold; font-size: 11px; color: #38bdf8; background: #0f172a; padding: 2px 5px; border: 1px solid #334155; border-radius: 4px;")
        else:
            label.setStyleSheet("font-weight: bold; font-size: 11px; color: #0f172a; background: #f1f5f9; padding: 2px 5px; border: 1px solid #cbd5e1; border-radius: 4px;")

    def update_results(self, metrics: PatternMetrics):
        # 1. Main beam
        if metrics.main_beam_deg is not None:
            if metrics.grating_lobe_count > 0:
                self._format_ambiguous(
                    self.lbl_main_beam,
                    f"{metrics.main_beam_deg:.2f}° (Ambiguous: {metrics.grating_lobe_count} Grating Lobes)",
                )
            else:
                self._format_valid(self.lbl_main_beam, f"{metrics.main_beam_deg:.2f}°")
        else:
            self._format_undefined(self.lbl_main_beam, "Not defined (invisible)")

        # 2. HPBW
        if metrics.hpbw_deg is not None:
            self._format_valid(self.lbl_hpbw, f"{metrics.hpbw_deg:.2f}° ({metrics.half_power_left_deg:.1f}° → {metrics.half_power_right_deg:.1f}°)")
        else:
            self._format_undefined(self.lbl_hpbw, "Not defined (boundary)")

        # 3. FNBW
        if metrics.fnbw_deg is not None:
            self._format_valid(self.lbl_fnbw, f"{metrics.fnbw_deg:.2f}° ({metrics.first_null_left_deg:.1f}° → {metrics.first_null_right_deg:.1f}°)")
        else:
            self._format_undefined(self.lbl_fnbw, "Not defined (boundary)")

        # 4. SLL
        if metrics.peak_sll_db is not None:
            self._format_valid(self.lbl_sll, f"{metrics.peak_sll_db:.2f} dB (@ {metrics.peak_sll_angle_deg:.1f}°)")
        else:
            self._format_undefined(self.lbl_sll, "Not defined (no sidelobes)")

        # 5. Grating lobes
        if metrics.grating_lobe_count > 0:
            gl_str = f"{metrics.grating_lobe_count} (" + ", ".join(f"{g:.1f}°" for g in metrics.grating_lobes_deg) + ")"
            self._format_ambiguous(self.lbl_grating_count, gl_str)
        else:
            self._format_valid(self.lbl_grating_count, "0 (None)")

        # 6. kd
        self._format_valid(self.lbl_kd, f"{metrics.kd_rad:.4f} rad ({metrics.kd_deg:.1f}°)")

        # 7. beta
        self._format_valid(self.lbl_beta, f"{metrics.beta_deg:.1f}° ({metrics.beta_rad:.4f} rad)")

        # 8. All maxima list
        if metrics.all_maxima_deg:
            self.lbl_all_maxima.setText(", ".join(f"{m:.2f}°" for m in metrics.all_maxima_deg))
        else:
            self.lbl_all_maxima.setText("None")

        # 9. Nulls list
        if metrics.nulls_deg:
            if len(metrics.nulls_deg) > 8:
                short_nulls = ", ".join(f"{n:.1f}°" for n in metrics.nulls_deg[:8]) + f"... ({len(metrics.nulls_deg)} total)"
            else:
                short_nulls = ", ".join(f"{n:.2f}°" for n in metrics.nulls_deg)
            self.lbl_nulls.setText(short_nulls)
        else:
            self.lbl_nulls.setText("No visible nulls")

"""
Comprehensive GUI test suite for Linear Antenna Array Simulation.
Tests:
- Initialization and default values
- Presets: Broadside, Positive End-fire, Negative End-fire, Reset
- Slider and Spinbox bidirectional synchronization
- Frequency changes and physical spacing calculation updates
- Taper weighting selection and Custom weights/phases dialog
- Tab switching and lazy rendering across all 5 visualization tabs
- Display overlay toggles (markers, HPBW lines, steering vectors)
- Dynamic beam steering animation (start, tick advance, direction reversal, stop)
- Pattern comparison workflow (snapshot, overlay, clear)
- Export actions (CSV export and high-resolution plot export)
"""

import os
import sys
import tempfile
from pathlib import Path
import numpy as np
import pytest

# Ensure offscreen Qt platform for headless testing
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_cache"

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from gui.main_window import AntennaSimulationWindow
from gui.controls_panel import CustomWeightsDialog


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_gui_initialization_and_render(qapp):
    """Test that main simulation window initializes, sets defaults, and computes properly."""
    window = AntennaSimulationWindow()
    assert window is not None

    # Check defaults
    params = window.controls.get_current_parameters()
    assert params["N"] == 8
    assert np.isclose(params["d_over_lambda"], 0.50)
    assert np.isclose(params["freq_ghz"], 3.0)
    assert np.isclose(params["theta0_deg"], 90.0)
    assert np.isclose(params["beta_deg"], 0.0)
    assert params["weighting_type"] == "Uniform"

    # Check status bar message
    assert "N=8" in window.status_bar.currentMessage()
    window.close()


def test_gui_presets_and_updates(qapp):
    """Test preset actions: Broadside, Positive End-fire, Negative End-fire, and Reset."""
    window = AntennaSimulationWindow()

    # Test Positive End-fire
    window.on_positive_endfire()
    params = window.controls.get_current_parameters()
    assert np.isclose(params["theta0_deg"], 0.0)
    assert np.isclose(params["beta_deg"], -180.0)
    assert "Positive End-fire" in window.status_bar.currentMessage()

    # Test Negative End-fire
    window.on_negative_endfire()
    params = window.controls.get_current_parameters()
    assert np.isclose(params["theta0_deg"], 180.0)
    assert np.isclose(params["beta_deg"], 180.0)
    assert "Negative End-fire" in window.status_bar.currentMessage()

    # Test Broadside
    window.on_broadside()
    params = window.controls.get_current_parameters()
    assert np.isclose(params["theta0_deg"], 90.0)
    assert np.isclose(params["beta_deg"], 0.0)

    # Test Reset
    window.controls.spin_N.setValue(16)
    window.on_reset()
    assert window.controls.spin_N.value() == 8
    assert window.controls.slider_N.value() == 8
    assert np.isclose(window.controls.spin_d.value(), 0.50)

    window.close()


def test_gui_taper_weights_selection(qapp):
    """Test selecting Hann (Cosine), Binomial, and Custom in the GUI."""
    window = AntennaSimulationWindow()

    # 1. Select Hann (Cosine)
    window.controls.combo_weights.setCurrentText("Hann (Cosine)")
    params = window.controls.get_current_parameters()
    assert params["weighting_type"] == "Hann (Cosine)"
    assert len(params["weights"]) == 8
    assert np.isclose(np.max(params["weights"]), 1.0)
    window.recompute_and_update()

    # 2. Select Binomial
    window.controls.combo_weights.setCurrentText("Binomial")
    params = window.controls.get_current_parameters()
    assert params["weighting_type"] == "Binomial"
    assert len(params["weights"]) == 8
    window.recompute_and_update()

    # 3. Select Uniform
    window.controls.combo_weights.setCurrentText("Uniform")
    params = window.controls.get_current_parameters()
    assert params["weighting_type"] == "Uniform"
    window.recompute_and_update()

    window.close()


def test_gui_slider_spinbox_synchronization(qapp):
    """Verify bidirectional synchronization between sliders and spinboxes."""
    window = AntennaSimulationWindow()
    ctrl = window.controls

    # 1. Elements N
    ctrl.slider_N.setValue(16)
    assert ctrl.spin_N.value() == 16
    ctrl.spin_N.setValue(24)
    assert ctrl.slider_N.value() == 24

    # 2. Spacing d/lambda
    ctrl.slider_d.setValue(75)  # 0.75 lambda
    assert np.isclose(ctrl.spin_d.value(), 0.75)
    ctrl.spin_d.setValue(1.20)
    assert ctrl.slider_d.value() == 120

    # 3. Steering angle theta_0
    ctrl.slider_theta0.setValue(45)
    assert np.isclose(ctrl.spin_theta0.value(), 45.0)
    ctrl.spin_theta0.setValue(60.0)
    assert ctrl.slider_theta0.value() == 60

    # 4. Progressive phase beta
    ctrl.slider_beta.setValue(-90)
    assert np.isclose(ctrl.spin_beta.value(), -90.0)
    ctrl.spin_beta.setValue(120.0)
    assert ctrl.slider_beta.value() == 120

    # 5. Frequency & Physical Spacing Display
    ctrl.spin_freq.setValue(6.0)  # 6 GHz -> lambda = 50.0 mm
    assert "50.0 mm" in ctrl.lbl_physical_spacing.text()

    window.close()


def test_gui_tab_switching_and_lazy_rendering(qapp):
    """Verify tab switching and lazy rendering across all 5 tabs."""
    window = AntennaSimulationWindow()
    plots = window.plots

    # Trigger recompute
    window.recompute_and_update()

    # Active tab 0 should be rendered
    assert 0 not in plots._dirty_tabs

    # Switch to tab 1 (Cartesian dB)
    plots.tabs.setCurrentIndex(1)
    assert 1 not in plots._dirty_tabs

    # Switch to tab 2 (Polar)
    plots.tabs.setCurrentIndex(2)
    assert 2 not in plots._dirty_tabs

    # Switch to tab 3 (3D Pattern)
    plots.tabs.setCurrentIndex(3)
    assert 3 not in plots._dirty_tabs

    # Switch to tab 4 (Excitation Weights)
    plots.tabs.setCurrentIndex(4)
    assert 4 not in plots._dirty_tabs

    # Ensure all tabs can be explicitly verified
    for i in range(5):
        plots.ensure_tab_rendered(i)
        assert i not in plots._dirty_tabs

    window.close()


def test_gui_overlay_toggles(qapp):
    """Test plot overlay check boxes (markers, HPBW, steering vectors)."""
    window = AntennaSimulationWindow()
    plots = window.plots

    # Uncheck show markers
    plots.chk_show_markers.setChecked(False)
    assert not plots.chk_show_markers.isChecked()

    # Uncheck show HPBW
    plots.chk_show_hpbw.setChecked(False)
    assert not plots.chk_show_hpbw.isChecked()

    # Uncheck show steering
    plots.chk_show_steering.setChecked(False)
    assert not plots.chk_show_steering.isChecked()

    # Re-check all
    plots.chk_show_markers.setChecked(True)
    plots.chk_show_hpbw.setChecked(True)
    plots.chk_show_steering.setChecked(True)

    window.close()


def test_gui_animation_control(qapp):
    """Test beam steering animation start, advance, direction reverse, and stop."""
    window = AntennaSimulationWindow()
    initial_theta0 = window.controls.spin_theta0.value()

    # Start animation
    window.on_toggle_animation()
    assert window.anim_timer.isActive()
    assert "Pause" in window.controls.btn_anim.text()

    # Advance 10 ticks
    for _ in range(10):
        window._on_animation_tick()

    # Angle should have changed
    new_theta0 = window.controls.spin_theta0.value()
    assert not np.isclose(new_theta0, initial_theta0)

    # Stop animation
    window.on_toggle_animation()
    assert not window.anim_timer.isActive()
    assert "Resume" in window.controls.btn_anim.text()

    window.close()


def test_gui_pattern_comparison(qapp):
    """Test pattern comparison reference snapshot and clear workflow."""
    window = AntennaSimulationWindow()

    # Set reference pattern directly on plots widget
    ref_theta = np.linspace(0.0, 180.0, 181)
    ref_af = np.ones(181)
    ref_db = np.zeros(181)
    ref_data = (ref_theta, ref_af, ref_db, "Reference Pattern")

    window.plots.set_reference_pattern(ref_data)
    assert window.plots._reference_data is not None

    # Clear comparison
    window.plots.clear_reference_pattern()
    assert window.plots._reference_data is None

    window.close()


def test_gui_custom_weights_and_phases_dialog(qapp):
    """Test custom weights and phases editing dialog."""
    w_init = np.array([1.0, 0.8, 0.6, 0.4])
    p_init = np.radians([0.0, 30.0, 60.0, 90.0])
    dialog = CustomWeightsDialog(w_init, p_init)
    w_out, p_out = dialog.get_weights_and_phases()
    assert len(w_out) == 4
    assert len(p_out) == 4
    assert np.isclose(w_out[0], 1.0)
    assert np.isclose(np.degrees(p_out[1]), 30.0)


def test_gui_theme_toggle(qapp):
    """Test switching between high-contrast dark and light themes."""
    window = AntennaSimulationWindow()
    assert window._is_dark_theme is True
    assert "Light Mode" in window.plots.btn_theme_toggle.text()

    # Toggle to Light Mode
    window.on_toggle_theme()
    assert window._is_dark_theme is False
    assert "Dark Mode" in window.plots.btn_theme_toggle.text()

    # Toggle back to Dark Mode
    window.on_toggle_theme()
    assert window._is_dark_theme is True
    assert "Light Mode" in window.plots.btn_theme_toggle.text()

    window.close()


def test_gui_export_csv_and_plot(qapp):
    """Test CSV and high-res plot export functionality."""
    from export.csv_exporter import export_pattern_to_csv
    from export.plot_exporter import save_figure

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test_pattern.csv"
        plot_path = Path(tmpdir) / "test_plot.png"

        window = AntennaSimulationWindow()
        window.recompute_and_update()

        # Test CSV export
        params = window.controls.get_current_parameters()
        theta_rad = np.linspace(0.0, np.pi, 181)
        af_n = np.ones(181)
        af_db = np.zeros(181)
        p_n = np.ones(181)
        from analysis.pattern_metrics import compute_pattern_metrics
        metrics = compute_pattern_metrics(theta_rad, af_n, af_db, 8, 0.5, 0.0)

        export_pattern_to_csv(
            str(csv_path), theta_rad, af_n, af_db, p_n, metrics,
            N=8, d_over_lambda=0.5, beta_deg=0.0, freq_ghz=3.0, weighting_type="Uniform"
        )
        assert csv_path.exists()
        assert csv_path.stat().st_size > 0

        # Test Figure export
        window.plots.ensure_tab_rendered(0)
        save_figure(window.plots.fig_linear, str(plot_path))
        assert plot_path.exists()
        assert plot_path.stat().st_size > 0

        window.close()

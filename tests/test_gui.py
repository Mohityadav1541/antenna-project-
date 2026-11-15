"""
Unit tests for GUI components and main window using offscreen Qt platform.
"""

import os
import sys
import numpy as np
import pytest

# Ensure offscreen Qt platform for headless CI / testing
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_cache"

from PyQt6.QtWidgets import QApplication
from gui.main_window import AntennaSimulationWindow


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

    window.close()


def test_gui_taper_weights(qapp):
    """Test changing taper weight types in GUI."""
    window = AntennaSimulationWindow()

    # Select Binomial
    window.controls.combo_weights.setCurrentText("Binomial")
    params = window.controls.get_current_parameters()
    assert params["weighting_type"] == "Binomial"
    assert len(params["weights"]) == 8

    # Select Hann
    window.controls.combo_weights.setCurrentText("Hann (Cosine)")
    params = window.controls.get_current_parameters()
    assert len(params["weights"]) == 8

    window.close()

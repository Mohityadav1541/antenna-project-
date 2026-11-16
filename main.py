#!/usr/bin/env python3
"""
Main entry point for Interactive Antenna Array Simulation Application.
Course: Antennas and Wave Propagation.
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Set Matplotlib cache dir if needed to avoid permission warnings on macOS
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib_cache")


def main():
    # If invoked with --experiments, run the full experiment suite and exit
    if "--experiments" in sys.argv:
        from experiments.run_experiments import main as run_exp
        run_exp()
        return

    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QFont
    from gui.main_window import AntennaSimulationWindow
    from gui.theme import get_dark_theme_qss

    app = QApplication(sys.argv)
    app.setApplicationName("Antenna Array Simulator")
    app.setOrganizationName("Antennas and Wave Propagation Lab")

    # Set modern clean font
    font = QFont("Helvetica Neue", 10)
    app.setFont(font)

    # Apply High-Contrast Dark Theme with 100% explicit text contrast
    app.setStyleSheet(get_dark_theme_qss())

    window = AntennaSimulationWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

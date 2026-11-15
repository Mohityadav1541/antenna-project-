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

    app = QApplication(sys.argv)
    app.setApplicationName("Antenna Array Simulator")
    app.setOrganizationName("Antennas and Wave Propagation Lab")

    # Set modern clean font
    font = QFont("Helvetica Neue", 10)
    app.setFont(font)

    # Clean styling
    app.setStyleSheet("""
        QGroupBox {
            font-weight: bold;
            font-size: 11px;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 5px;
            color: #1e3a8a;
        }
        QPushButton {
            padding: 5px 10px;
            border: 1px solid #94a3b8;
            border-radius: 4px;
            background-color: #f1f5f9;
            font-weight: 500;
        }
        QPushButton:hover {
            background-color: #e2e8f0;
        }
        QPushButton:pressed {
            background-color: #cbd5e1;
        }
        QSlider::groove:horizontal {
            height: 6px;
            background: #cbd5e1;
            border-radius: 3px;
        }
        QSlider::sub-page:horizontal {
            background: #2563eb;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: #1e40af;
            border: 1px solid #1e3a8a;
            width: 14px;
            margin-top: -4px;
            margin-bottom: -4px;
            border-radius: 7px;
        }
        QTabWidget::pane {
            border: 1px solid #cbd5e1;
            border-radius: 4px;
            background: #ffffff;
        }
        QTabBar::tab {
            background: #f1f5f9;
            border: 1px solid #cbd5e1;
            padding: 6px 12px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background: #ffffff;
            border-bottom-color: #ffffff;
            font-weight: bold;
            color: #1e3a8a;
        }
    """)

    window = AntennaSimulationWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

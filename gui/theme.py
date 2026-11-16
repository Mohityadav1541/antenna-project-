"""
Theme management module for Antenna Array Simulation application.
Provides explicit, high-contrast Dark and Light stylesheets and Matplotlib color palettes.
Ensures 100% text contrast and readability regardless of operating system theme.
"""

from typing import Dict, Any


def get_dark_theme_qss() -> str:
    """High-contrast modern engineering dark theme (Slate & Cyan)."""
    return """
    /* Main Window & Containers */
    QMainWindow, QWidget#centralWidget {
        background-color: #0b1120;
        color: #f8fafc;
    }
    
    QScrollArea {
        background-color: transparent;
        border: none;
    }
    
    QScrollArea > QWidget > QWidget {
        background-color: transparent;
    }
    
    /* Group Boxes */
    QGroupBox {
        font-weight: bold;
        font-size: 11px;
        border: 1px solid #334155;
        border-radius: 6px;
        margin-top: 8px;
        padding-top: 8px;
        background-color: #1e293b;
        color: #f8fafc;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 8px;
        padding: 0 4px;
        color: #38bdf8;
        background-color: #1e293b;
    }
    
    /* Labels */
    QLabel {
        color: #f1f5f9;
        font-size: 11px;
        background: transparent;
    }
    
    /* Buttons */
    QPushButton {
        padding: 4px 8px;
        border: 1px solid #475569;
        border-radius: 4px;
        background-color: #334155;
        color: #f8fafc;
        font-weight: 600;
        font-size: 11px;
    }
    
    QPushButton:hover {
        background-color: #475569;
        border-color: #64748b;
    }
    
    QPushButton:pressed {
        background-color: #1e293b;
    }
    
    QPushButton:disabled {
        background-color: #1e293b;
        color: #64748b;
        border-color: #334155;
    }
    
    /* Inputs: SpinBoxes & ComboBoxes */
    QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit {
        background-color: #0f172a;
        color: #f8fafc;
        border: 1px solid #475569;
        border-radius: 4px;
        padding: 2px 4px;
        font-size: 11px;
        font-weight: 500;
        selection-background-color: #2563eb;
        selection-color: #ffffff;
    }
    
    QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QLineEdit:focus {
        border: 1px solid #38bdf8;
    }
    
    QComboBox QAbstractItemView {
        background-color: #0f172a;
        color: #f8fafc;
        border: 1px solid #475569;
        selection-background-color: #2563eb;
        selection-color: #ffffff;
    }
    
    /* Sliders */
    QSlider::groove:horizontal {
        height: 4px;
        background: #334155;
        border-radius: 2px;
    }
    
    QSlider::sub-page:horizontal {
        background: #38bdf8;
        border-radius: 2px;
    }
    
    QSlider::handle:horizontal {
        background: #38bdf8;
        border: 1px solid #0284c7;
        width: 12px;
        margin-top: -4px;
        margin-bottom: -4px;
        border-radius: 6px;
    }
    
    QSlider::handle:horizontal:hover {
        background: #7dd3fc;
    }
    
    /* Tabs */
    QTabWidget::pane {
        border: 1px solid #334155;
        border-radius: 4px;
        background: #1e293b;
    }
    
    QTabBar::tab {
        background: #0f172a;
        color: #94a3b8;
        border: 1px solid #334155;
        padding: 5px 10px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        margin-right: 2px;
        font-size: 11px;
    }
    
    QTabBar::tab:selected {
        background: #1e293b;
        color: #38bdf8;
        border-bottom-color: #1e293b;
        font-weight: bold;
    }
    
    QTabBar::tab:hover:!selected {
        background: #1e293b;
        color: #f8fafc;
    }
    
    /* CheckBoxes */
    QCheckBox {
        color: #f1f5f9;
        font-size: 11px;
        spacing: 5px;
    }
    
    QCheckBox::indicator {
        width: 14px;
        height: 14px;
        border: 1px solid #475569;
        border-radius: 3px;
        background: #0f172a;
    }
    
    QCheckBox::indicator:checked {
        background: #2563eb;
        border-color: #38bdf8;
    }
    
    /* Splitter */
    QSplitter::handle {
        background-color: #1e293b;
    }
    
    /* Status Bar */
    QStatusBar {
        background-color: #0f172a;
        color: #94a3b8;
        border-top: 1px solid #334155;
        font-size: 11px;
    }
    
    /* Scrollbars */
    QScrollBar:vertical {
        background: #0f172a;
        width: 8px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background: #334155;
        min-height: 20px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover {
        background: #475569;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    """


def get_light_theme_qss() -> str:
    """High-contrast modern executive light theme (Clean White & Royal Blue)."""
    return """
    /* Main Window & Containers */
    QMainWindow, QWidget#centralWidget {
        background-color: #f8fafc;
        color: #0f172a;
    }
    
    QScrollArea {
        background-color: transparent;
        border: none;
    }
    
    QScrollArea > QWidget > QWidget {
        background-color: transparent;
    }
    
    /* Group Boxes */
    QGroupBox {
        font-weight: bold;
        font-size: 11px;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        margin-top: 8px;
        padding-top: 8px;
        background-color: #ffffff;
        color: #0f172a;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 8px;
        padding: 0 4px;
        color: #1e40af;
        background-color: #ffffff;
    }
    
    /* Labels */
    QLabel {
        color: #0f172a;
        font-size: 11px;
        background: transparent;
    }
    
    /* Buttons */
    QPushButton {
        padding: 4px 8px;
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        background-color: #f1f5f9;
        color: #0f172a;
        font-weight: 600;
        font-size: 11px;
    }
    
    QPushButton:hover {
        background-color: #e2e8f0;
        border-color: #94a3b8;
    }
    
    QPushButton:pressed {
        background-color: #cbd5e1;
    }
    
    QPushButton:disabled {
        background-color: #f8fafc;
        color: #94a3b8;
        border-color: #e2e8f0;
    }
    
    /* Inputs: SpinBoxes & ComboBoxes */
    QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit {
        background-color: #ffffff;
        color: #0f172a;
        border: 1px solid #94a3b8;
        border-radius: 4px;
        padding: 2px 4px;
        font-size: 11px;
        font-weight: 500;
        selection-background-color: #2563eb;
        selection-color: #ffffff;
    }
    
    QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QLineEdit:focus {
        border: 1px solid #2563eb;
    }
    
    QComboBox QAbstractItemView {
        background-color: #ffffff;
        color: #0f172a;
        border: 1px solid #94a3b8;
        selection-background-color: #2563eb;
        selection-color: #ffffff;
    }
    
    /* Sliders */
    QSlider::groove:horizontal {
        height: 4px;
        background: #cbd5e1;
        border-radius: 2px;
    }
    
    QSlider::sub-page:horizontal {
        background: #2563eb;
        border-radius: 2px;
    }
    
    QSlider::handle:horizontal {
        background: #1e40af;
        border: 1px solid #1e3a8a;
        width: 12px;
        margin-top: -4px;
        margin-bottom: -4px;
        border-radius: 6px;
    }
    
    QSlider::handle:horizontal:hover {
        background: #2563eb;
    }
    
    /* Tabs */
    QTabWidget::pane {
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        background: #ffffff;
    }
    
    QTabBar::tab {
        background: #f1f5f9;
        color: #475569;
        border: 1px solid #cbd5e1;
        padding: 5px 10px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        margin-right: 2px;
        font-size: 11px;
    }
    
    QTabBar::tab:selected {
        background: #ffffff;
        color: #1e40af;
        border-bottom-color: #ffffff;
        font-weight: bold;
    }
    
    QTabBar::tab:hover:!selected {
        background: #e2e8f0;
        color: #0f172a;
    }
    
    /* CheckBoxes */
    QCheckBox {
        color: #0f172a;
        font-size: 11px;
        spacing: 5px;
    }
    
    QCheckBox::indicator {
        width: 14px;
        height: 14px;
        border: 1px solid #94a3b8;
        border-radius: 3px;
        background: #ffffff;
    }
    
    QCheckBox::indicator:checked {
        background: #2563eb;
        border-color: #1d4ed8;
    }
    
    /* Splitter */
    QSplitter::handle {
        background-color: #e2e8f0;
    }
    
    /* Status Bar */
    QStatusBar {
        background-color: #f1f5f9;
        color: #475569;
        border-top: 1px solid #cbd5e1;
        font-size: 11px;
    }
    
    /* Scrollbars */
    QScrollBar:vertical {
        background: #f1f5f9;
        width: 8px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background: #cbd5e1;
        min-height: 20px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover {
        background: #94a3b8;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    """


def get_matplotlib_theme(theme_name: str = "dark") -> Dict[str, Any]:
    """Returns color dictionary for styling Matplotlib figures."""
    if theme_name == "dark":
        return {
            "fig_bg": "#1e293b",
            "ax_bg": "#0f172a",
            "text": "#f8fafc",
            "title": "#38bdf8",
            "axis_label": "#cbd5e1",
            "tick": "#94a3b8",
            "grid": "#334155",
            "grid_alpha": 0.6,
            "curve_primary": "#38bdf8",
            "curve_secondary": "#f43f5e",
            "curve_reference": "#a855f7",
            "marker_max": "#ef4444",
            "marker_null": "#10b981",
            "line_hpbw": "#eab308",
            "line_fnbw": "#10b981",
            "line_steering": "#06b6d4",
        }
    else:
        return {
            "fig_bg": "#ffffff",
            "ax_bg": "#ffffff",
            "text": "#0f172a",
            "title": "#1e3a8a",
            "axis_label": "#1e293b",
            "tick": "#475569",
            "grid": "#e2e8f0",
            "grid_alpha": 0.8,
            "curve_primary": "#2563eb",
            "curve_secondary": "#dc2626",
            "curve_reference": "#7c3aed",
            "marker_max": "#dc2626",
            "marker_null": "#059669",
            "line_hpbw": "#d97706",
            "line_fnbw": "#059669",
            "line_steering": "#0284c7",
        }

"""
Pattern comparison dialog for storing and managing reference patterns (Section 3.4).
"""

from typing import Optional, Tuple
import numpy as np
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QMessageBox,
)


class ComparePatternsDialog(QDialog):
    def __init__(self, current_data: Tuple[np.ndarray, np.ndarray, np.ndarray, str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Compare & Overlay Radiation Patterns")
        self.resize(380, 200)
        self.current_data = current_data  # (theta_deg, af_n, af_db, label)
        self.reference_data: Optional[Tuple[np.ndarray, np.ndarray, np.ndarray, str]] = None
        self.should_clear = False

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Snapshot Current Pattern as Reference:"))
        self.txt_label = QLineEdit(current_data[3])
        layout.addWidget(self.txt_label)

        btn_box = QHBoxLayout()
        self.btn_set_ref = QPushButton("Store as Active Reference")
        self.btn_set_ref.setStyleSheet("font-weight: bold; background-color: #2563eb; color: white; padding: 6px;")
        self.btn_set_ref.clicked.connect(self._set_reference)

        self.btn_clear_ref = QPushButton("Clear Overlay")
        self.btn_clear_ref.clicked.connect(self._clear_reference)

        btn_box.addWidget(self.btn_set_ref)
        btn_box.addWidget(self.btn_clear_ref)
        layout.addLayout(btn_box)

        layout.addWidget(QLabel("The reference pattern will appear as a dashed gray overlay\nin the Cartesian and dB plots for direct comparison."))

    def _set_reference(self):
        th_deg, af_n, af_db, _ = self.current_data
        lbl = self.txt_label.text().strip() or "Reference"
        self.reference_data = (th_deg, af_n, af_db, lbl)
        self.accept()

    def _clear_reference(self):
        self.should_clear = True
        self.reference_data = None
        self.accept()

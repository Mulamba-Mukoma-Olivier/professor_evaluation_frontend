from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from logic.frameless_windows import install_drag_handle, install_size_grip
from api.evaluations_api import EvaluationsAPI
from api.criteria_api import CriteriaAPI


class EvaluationsDialog(QDialog):
    """Fenêtre de gestion des évaluations."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Évaluations")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setMinimumSize(480, 260)
        self.resize(620, 320)
        install_size_grip(self)
        layout = QVBoxLayout(self)
        title_row = QHBoxLayout()
        title = QLabel("Évaluations")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #123b66;")
        close = QPushButton("×")
        close.setFixedSize(30, 30)
        close.clicked.connect(self.close)
        title_row.addWidget(title)
        title_row.addStretch(1)
        title_row.addWidget(close)
        layout.addLayout(title_row)
        self.status_label = QLabel("Chargement des évaluations...")
        self.status_label.setStyleSheet("color: #123b66;")
        layout.addWidget(self.status_label)
        install_drag_handle(self, [title, self.status_label])
        self.load_evaluations()
    
    def load_evaluations(self):
        try:
            evaluations = EvaluationsAPI.get_all() or []
            self.status_label.setText(f"{len(evaluations)} évaluations enregistrées dans l'API.")
            return evaluations
        except Exception as e:
            self.status_label.setText(f"Erreur API: {e}")
            return []


__all__ = ["EvaluationsDialog"]


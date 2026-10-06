from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from api.evaluations_api import EvaluationsAPI
from api.criteria_api import CriteriaAPI


class EvaluationsDialog(QDialog):
    """Fenêtre de gestion des évaluations."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Évaluations")
        layout = QVBoxLayout(self)
        self.status_label = QLabel("Chargement des évaluations...")
        layout.addWidget(self.status_label)
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


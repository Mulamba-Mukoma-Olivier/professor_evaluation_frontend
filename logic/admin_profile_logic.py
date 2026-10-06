from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox, QWidget


class AdminProfile(QWidget):

    def __init__(self):
        super().__init__()

        ui_path = Path(__file__).resolve().parent.parent / "ui" / "admin_profile.ui"
        uic.loadUi(str(ui_path), self)

        self.pushButton.clicked.connect(self.save_profile)
        self.pushButton_2.clicked.connect(self.go_back)

    def save_profile(self):
        matricule = self.lineEdit.text().strip()
        name = self.lineEdit_2.text().strip()
        email = self.lineEdit_3.text().strip()
        role = self.lineEdit_4.text().strip()

        if not matricule or not name or not email or not role:
            QMessageBox.warning(
                self,
                "Erreur",
                "Tous les champs du profil administrateur doivent être remplis."
            )
            return

        QMessageBox.information(
            self,
            "Profil admin",
            "Profil administrateur enregistré avec succès."
        )

    def go_back(self):
        QMessageBox.information(
            self,
            "Retour",
            "Retour à l’écran précédent."
        )

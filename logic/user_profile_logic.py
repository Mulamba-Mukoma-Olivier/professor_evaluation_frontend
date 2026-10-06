from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox, QWidget


class UserProfile(QWidget):

    def __init__(self):
        super().__init__()

        ui_path = Path(__file__).resolve().parent.parent / "ui" / "user_profile.ui"
        uic.loadUi(str(ui_path), self)

        self.pushButton.clicked.connect(self.previous)
        self.pushButton_2.clicked.connect(self.update_profile)

    def update_profile(self):
        matricule = self.lineEdit.text().strip()
        name = self.lineEdit_2.text().strip()
        email = self.lineEdit_3.text().strip()
        role = self.lineEdit_4.text().strip()

        if not matricule or not name or not email or not role:
            QMessageBox.warning(
                self,
                "Erreur",
                "Veuillez remplir tous les champs avant de modifier le profil."
            )
            return

        if "@" not in email or "." not in email:
            QMessageBox.warning(
                self,
                "Erreur",
                "Veuillez saisir une adresse e-mail valide."
            )
            return

        QMessageBox.information(
            self,
            "Profil",
            "Profil mis à jour avec succès."
        )

    def previous(self):
        QMessageBox.information(
            self,
            "Précédent",
            "Retour à la page précédente."
        )

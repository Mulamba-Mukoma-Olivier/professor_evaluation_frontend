from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox, QWidget


class Signup(QWidget):

    def __init__(self):
        super().__init__()

        ui_path = Path(__file__).resolve().parent.parent / "ui" / "signup.ui"
        uic.loadUi(str(ui_path), self)

        self.pushButton.clicked.connect(self.register_user)
        self.pushButton_2.clicked.connect(self.open_login)

    def register_user(self):
        matricule = self.lineEdit.text().strip()
        name = self.lineEdit_2.text().strip()
        email = self.lineEdit_3.text().strip()
        password = self.lineEdit_4.text().strip()
        role = self.comboBox.currentText().strip() if self.comboBox.count() else ""

        if not matricule or not name or not email or not password:
            QMessageBox.warning(
                self,
                "Erreur",
                "Veuillez remplir tous les champs obligatoires."
            )
            return

        if "@" not in email or "." not in email:
            QMessageBox.warning(
                self,
                "Erreur",
                "Veuillez saisir une adresse e-mail valide."
            )
            return

        if len(password) < 4:
            QMessageBox.warning(
                self,
                "Erreur",
                "Le mot de passe doit contenir au moins 4 caractères."
            )
            return

        QMessageBox.information(
            self,
            "Inscription",
            f"Compte créé avec succès pour {name} ({role})."
        )

    def open_login(self):
        QMessageBox.information(
            self,
            "Connexion",
            "Ouverture du formulaire de connexion."
        )

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox

from api.auth_api import AuthAPI
from logic.main_section_logic import MainSection


class Login(QMainWindow):

    def __init__(self):
        super().__init__()

        uic.loadUi("ui/login.ui", self)

        self.login_button.clicked.connect(self.login)
        self.main_section = None
        self.login_password_input.setEchoMode(self.login_password_input.Password)

    def login(self):
        email = self.login_email_input.text().strip()
        password = self.login_password_input.text().strip()

        if not email or not password:
            QMessageBox.warning(
                self,
                "Erreur",
                "Veuillez remplir tous les champs."
            )
            return

        try:
            response = AuthAPI.login(email, password)
            if response is None:
                QMessageBox.warning(
                    self,
                    "Erreur",
                    "Identifiants invalides ou API indisponible."
                )
                return

            self.hide()
            self.main_section = MainSection(login_window=self, user_data=response.get("user"))
            self.main_section.show()

        except Exception as exc:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Impossible de se connecter : {exc}"
            )


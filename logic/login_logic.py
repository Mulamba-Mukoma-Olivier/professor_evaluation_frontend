from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QPalette, QPixmap
from pathlib import Path
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QVBoxLayout, QWidget

from api.auth_api import AuthAPI
from logic.main_section_logic import MainSection
from logic.signup_logic import Signup
from logic.frameless_windows import install_frameless_chrome


class Login(QMainWindow):

    def __init__(self):
        super().__init__()

        ui_path = Path(__file__).resolve().parent.parent / "ui" / "login.ui"
        uic.loadUi(str(ui_path), self)
        logo_path = Path(__file__).resolve().parent.parent / "assets" / "logo.png"
        self.setWindowIcon(QIcon(str(logo_path)))
        install_frameless_chrome(self, "EduRate", self.centralWidget())
        self._style_login(logo_path)

        self.login_button.clicked.connect(self.login)
        self.main_section = None
        self.signup_window = None
        self.login_password_input.setEchoMode(self.login_password_input.Password)
        self.register_link_from_login.clicked.connect(self.open_signup)

    def restore_session(self):
        """Rouvre la session précédente si son JWT est encore valide."""
        from logic.session_store import SessionStore
        user = SessionStore.restore()
        if not user:
            return False
        try:
            self.main_section = MainSection(login_window=self, user_data=user)
            self.main_section.showMaximized()
            self.main_section.raise_()
            self.main_section.activateWindow()
            self.hide()
            return True
        except Exception as exc:
            SessionStore.clear()
            QMessageBox.warning(self, "Session", f"La session précédente n’a pas pu être restaurée : {exc}")
            return False

    def _style_login(self, logo_path):
        self.setWindowTitle("Connexion | EduRate")
        self.setMinimumSize(720, 560)
        self.resize(1080, 700)
        self.centralWidget().setStyleSheet("background: #f1f5f9; color: #123b66;")
        self.widget.setMinimumWidth(430)
        self.widget.setMaximumWidth(470)
        self.widget.setStyleSheet(
            "QWidget#widget { background: #ffffff; border: 1px solid #dbe4f0; border-radius: 18px; }"
        )
        if self.widget.layout():
            self.widget.layout().setContentsMargins(32, 28, 32, 28)
            self.widget.layout().setVerticalSpacing(12)

        root_layout = self.horizontalLayout_7
        existing_content = root_layout.takeAt(0).layout()
        brand_panel = QFrame()
        brand_panel.setObjectName("authBrandPanel")
        brand_panel.setMinimumWidth(300)
        brand_panel.setStyleSheet(
            "QFrame#authBrandPanel { border-radius: 0px; background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
            "stop:0 #eff6ff, stop:0.58 #dbeafe, stop:1 #bfdbfe); }"
        )
        brand_layout = QVBoxLayout(brand_panel)
        brand_layout.setContentsMargins(42, 52, 42, 42)
        brand_layout.setSpacing(18)
        brand_layout.addStretch(1)
        brand_logo = QLabel()
        brand_logo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        brand_logo.setFixedSize(116, 116)
        brand_logo.setPixmap(QPixmap(str(logo_path)).scaled(
            116, 116, Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        brand_layout.addWidget(brand_logo)
        brand_name = QLabel("Professor\nEvaluation")
        brand_name.setStyleSheet("color: #123b66; font-size: 31px; font-weight: 800; background: transparent;")
        brand_layout.addWidget(brand_name)
        brand_copy = QLabel("Une plateforme claire pour recueillir et consulter les évaluations académiques.")
        brand_copy.setWordWrap(True)
        brand_copy.setStyleSheet("color: #1e4f7a; font-size: 14px; line-height: 1.5; background: transparent;")
        brand_layout.addWidget(brand_copy)
        brand_layout.addStretch(2)
        brand_footer = QLabel("QUALITÉ  ·  TRANSPARENCE  ·  PROGRESSION")
        brand_footer.setStyleSheet("color: #2563eb; font-size: 10px; font-weight: 700; letter-spacing: 1px; background: transparent;")
        brand_layout.addWidget(brand_footer)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(brand_panel, 4)
        root_layout.addLayout(existing_content, 6)

        heading = self.horizontalLayout_3
        while heading.count():
            heading.takeAt(0)
        logo = QLabel()
        logo.setFixedSize(66, 66)
        logo.setPixmap(QPixmap(str(logo_path)).scaled(
            66, 66, Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        text_box = QWidget()
        text_layout = QVBoxLayout(text_box)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        title = QLabel("EduRate")
        title.setStyleSheet("color: #123b66; font-size: 22px; font-weight: 800; background: transparent;")
        subtitle = QLabel("Connectez-vous à votre espace")
        subtitle.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)
        heading.addStretch(1)
        heading.addWidget(logo)
        heading.addWidget(text_box)
        heading.addStretch(1)
        self.label_3.hide()
        self.label_4.hide()

        for field in (self.login_email_input, self.login_password_input):
            field.setMinimumHeight(46)
            palette = field.palette()
            palette.setColor(QPalette.Text, QColor("#123b66"))
            palette.setColor(QPalette.PlaceholderText, QColor("#4f73a1"))
            field.setPalette(palette)
            field.setStyleSheet(
                "QLineEdit { background: #f8fafc; color: #123b66; border: 1px solid #cbd5e1; "
                "border-radius: 9px; padding: 0 14px; selection-background-color: #2563eb; }"
                "QLineEdit:focus { background: #ffffff; border: 1px solid #2563eb; }"
            )
        for label in (self.label, self.label_2, self.label_5):
            label.setStyleSheet("color: #123b66; background: transparent; font-size: 13px; font-weight: 600;")
        self.login_button.setMinimumHeight(46)
        self.login_button.setStyleSheet(
            "QPushButton { background: #dbeafe; color: #123b66; border: 1px solid #bfdbfe; border-radius: 9px; "
            "font-size: 14px; font-weight: 700; } QPushButton:hover { background: #bfdbfe; }"
        )
        self.register_link_from_login.setStyleSheet(
            "QPushButton { background: transparent; color: #1d4ed8; border: none; font-weight: 700; }"
            "QPushButton:hover { color: #1e40af; text-decoration: underline; }"
        )

    def open_signup(self):
        self.signup_window = Signup(login_window=self)
        self.hide()
        self.signup_window.showMaximized()
        self.signup_window.raise_()
        self.signup_window.activateWindow()

    def login(self):
        email = self.login_email_input.text().strip()
        password = self.login_password_input.text()

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
                    AuthAPI.last_error or "Identifiants invalides ou API indisponible."
                )
                return

            self.main_section = MainSection(login_window=self, user_data=response.get("user"))
            self.main_section.showMaximized()
            self.main_section.raise_()
            self.main_section.activateWindow()
            self.hide()

        except Exception as exc:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Impossible de se connecter : {exc}"
            )


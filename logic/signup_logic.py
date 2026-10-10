from pathlib import Path

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QPalette, QPixmap
from PyQt5.QtWidgets import QDialog, QFrame, QLabel, QMessageBox, QVBoxLayout
from api.auth_api import AuthAPI
from logic.frameless_windows import install_frameless_chrome


class Signup(QDialog):

    def __init__(self, login_window=None):
        super().__init__()
        self.login_window = login_window

        ui_path = Path(__file__).resolve().parent.parent / "ui" / "signup.ui"
        uic.loadUi(str(ui_path), self)
        logo_path = Path(__file__).resolve().parent.parent / "assets" / "logo.png"
        self.setWindowIcon(QIcon(str(logo_path)))
        install_frameless_chrome(self, "EduRate", self)

        heading_layout = getattr(self, "horizontalLayout", None)
        if heading_layout is not None:
            while heading_layout.count():
                heading_layout.takeAt(0)
            heading_layout.addWidget(self.label, 0, Qt.AlignVCenter)
            heading_layout.addStretch(1)
            heading_layout.setContentsMargins(0, 0, 0, 0)
            heading_layout.setSpacing(8)

        self.setWindowTitle("Créer un compte | EduRate")
        self.setMinimumSize(980, 680)
        self.resize(1100, 740)
        self.setStyleSheet("QDialog { background: #f1f5f9; color: #123b66; }")
        self.widget_2.setStyleSheet(
            "QWidget#widget_2 { background: #ffffff; border: 1px solid #dbe4f0; border-radius: 18px; }"
        )
        if self.verticalLayout_7:
            self.verticalLayout_7.setContentsMargins(32, 24, 32, 28)
            self.verticalLayout_7.setSpacing(14)
        self.label.setStyleSheet("color: #123b66; font-size: 22px; font-weight: 800; background: transparent;")
        self.label.setText("Créer votre compte")
        self.label_3.setText("Quelques informations pour commencer")
        self.label_3.setStyleSheet("color: #2563eb; font-size: 12px; background: transparent;")

        for field in (self.lineEdit, self.lineEdit_2, self.lineEdit_3, self.lineEdit_4):
            field.setMinimumHeight(44)
            palette = field.palette()
            palette.setColor(QPalette.Text, QColor("#123b66"))
            palette.setColor(QPalette.PlaceholderText, QColor("#4f73a1"))
            field.setPalette(palette)
            field.setStyleSheet(
                "QLineEdit { background: #f8fafc; color: #123b66; border: 1px solid #cbd5e1; "
                "border-radius: 8px; padding: 0 12px; }"
                "QLineEdit:focus { background: #ffffff; border: 1px solid #2563eb; }"
            )
        self.comboBox.setMinimumHeight(44)
        self.comboBox.setStyleSheet(
            "QComboBox { background: #f8fafc; color: #123b66; border: 1px solid #cbd5e1; "
            "border-radius: 8px; padding: 0 12px; } QComboBox:focus { border: 1px solid #2563eb; }"
        )
        for label in (self.label_4, self.label_5, self.label_6, self.label_7, self.label_8, self.label_9):
            label.setStyleSheet("color: #123b66; font-size: 12px; font-weight: 600; background: transparent;")
        self.pushButton.setMinimumHeight(44)
        self.pushButton.setStyleSheet(
            "QPushButton { background: #dbeafe; color: #123b66; border: 1px solid #bfdbfe; border-radius: 9px; "
            "font-size: 14px; font-weight: 700; } QPushButton:hover { background: #bfdbfe; }"
        )
        self.pushButton_2.setStyleSheet(
            "QPushButton { background: transparent; color: #1d4ed8; border: none; font-weight: 700; }"
            "QPushButton:hover { color: #1e40af; text-decoration: underline; }"
        )

        root_layout = self.horizontalLayout_11
        existing_content = root_layout.takeAt(0).layout()
        brand_panel = QFrame()
        brand_panel.setObjectName("authBrandPanel")
        brand_panel.setMinimumWidth(320)
        brand_panel.setStyleSheet(
            "QFrame#authBrandPanel { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
            "stop:0 #eff6ff, stop:0.58 #dbeafe, stop:1 #bfdbfe); }"
        )
        brand_layout = QVBoxLayout(brand_panel)
        brand_layout.setContentsMargins(42, 52, 42, 42)
        brand_layout.setSpacing(18)
        brand_layout.addStretch(1)
        brand_logo = QLabel()
        brand_logo.setFixedSize(116, 116)
        brand_logo.setPixmap(QPixmap(str(logo_path)).scaled(
            116, 116, Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        brand_layout.addWidget(brand_logo)
        brand_name = QLabel("Professor\nEvaluation")
        brand_name.setStyleSheet("color: #123b66; font-size: 31px; font-weight: 800; background: transparent;")
        brand_layout.addWidget(brand_name)
        brand_copy = QLabel("Rejoignez votre espace académique et participez à l’amélioration des enseignements.")
        brand_copy.setWordWrap(True)
        brand_copy.setStyleSheet("color: #1e4f7a; font-size: 14px; background: transparent;")
        brand_layout.addWidget(brand_copy)
        brand_layout.addStretch(2)
        brand_footer = QLabel("VOTRE ESPACE ACADÉMIQUE")
        brand_footer.setStyleSheet("color: #2563eb; font-size: 10px; font-weight: 700; letter-spacing: 1px; background: transparent;")
        brand_layout.addWidget(brand_footer)
        root_layout.setContentsMargins(0, 42, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(brand_panel, 4)
        root_layout.addLayout(existing_content, 6)

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

        if len(password) < 8:
            QMessageBox.warning(
                self,
                "Erreur",
                "Le mot de passe doit contenir au moins 8 caractères."
            )
            return
        response = AuthAPI.register(matricule, name, email, password, role)
        if response is None:
            QMessageBox.warning(self, "Inscription impossible", AuthAPI.last_error or "L’API n’a pas accepté l’inscription.")
            return
        QMessageBox.information(self, "Inscription", "Votre compte a été créé. Vous pouvez maintenant vous connecter.")
        self.close()
        if self.login_window is not None:
            self.login_window.showMaximized()
            self.login_window.login_email_input.setText(email)

    def open_login(self):
        self.close()
        if self.login_window is not None:
            self.login_window.showMaximized()

    def closeEvent(self, event):
        if self.login_window is not None:
            self.login_window.showMaximized()
            self.login_window.raise_()
            self.login_window.activateWindow()
        event.accept()

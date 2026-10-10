import sys
from pathlib import Path

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QIcon, QLinearGradient, QPainter, QPixmap
from PyQt5.QtWidgets import QApplication, QSplashScreen
from logic.login_logic import Login


def create_splash_pixmap(logo_path):
    pixmap = QPixmap(720, 420)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    gradient = QLinearGradient(0, 0, 720, 420)
    gradient.setColorAt(0, QColor("#ffffff"))
    gradient.setColorAt(1, QColor("#eff6ff"))
    painter.setBrush(gradient)
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(0, 0, 720, 420, 24, 24)

    logo = QPixmap(str(logo_path))
    if not logo.isNull():
        painter.drawPixmap(270, 38, 180, 180, logo)

    painter.setPen(QColor("#123b66"))
    painter.setFont(QFont("Arial", 25, QFont.Bold))
    painter.drawText(0, 252, 720, 42, Qt.AlignCenter, "EduRate")
    painter.setPen(QColor("#64748b"))
    painter.setFont(QFont("Arial", 11))
    painter.drawText(0, 296, 720, 28, Qt.AlignCenter, "Plateforme d’évaluation académique")

    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor("#dbeafe"))
    painter.drawRoundedRect(270, 365, 180, 5, 3, 3)
    painter.setBrush(QColor("#2563eb"))
    painter.drawRoundedRect(270, 365, 90, 5, 3, 3)
    painter.end()
    return pixmap


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("EduRate")
    logo_path = Path(__file__).resolve().parent / "assets" / "logo.png"
    app.setWindowIcon(QIcon(str(logo_path)))

    splash = QSplashScreen(create_splash_pixmap(logo_path), Qt.WindowStaysOnTopHint)
    splash.setWindowFlag(Qt.FramelessWindowHint)
    splash.show()
    app.processEvents()

    window = Login()
    window.setWindowIcon(QIcon(str(logo_path)))

    def show_login():
        splash.close()
        if not window.restore_session():
            window.showMaximized()
            window.raise_()
            window.activateWindow()

    # Laisser le splash lisible pendant le chargement, puis afficher la connexion.
    QTimer.singleShot(3000, show_login)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

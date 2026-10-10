"""
dialogs.py
──────────
Modales administratives professionnelles (Professeur, Cours, Critère, Éligibilité)
Thème Dark Slate Corporate — FramelessWindowHint avec coins arrondis et déplacement fluide.
"""
from typing import Optional, Dict, Any
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QComboBox, QSpinBox, QTextEdit,
    QPushButton, QLabel, QMessageBox, QCheckBox, QFrame
)
from api.professors_api import ProfessorsAPI
from api.courses_api import CoursesAPI
from api.criteria_api import CriteriaAPI
from api.eligibility_api import EligibilityAPI
from logic.frameless_windows import install_drag_handle

# ─── Palette claire et cohérente avec l'interface principale ──────────────────
BG       = "#f4f8fc"
CARD     = "#ffffff"
BORDER   = "#dbe5f0"
BLUE     = "#2563eb"
BLUE_DIM = "#eff6ff"
PURPLE   = "#7c3aed"
PURPLE_D = "#ede9fe"
AMBER    = "#d97706"
AMBER_D  = "#fffbeb"
GREEN    = "#059669"
GREEN_D  = "#ecfdf5"
TEXT_HI  = "#123b66"
TEXT_MID = "#456b8f"
TEXT_LO  = "#647b94"

DIALOG_STYLE = f"""
QDialog {{
    background-color: transparent;
}}
QLabel {{
    border: none;
    background: transparent;
    color: {TEXT_HI};
    padding: 0px;
}}
QLineEdit, QComboBox, QSpinBox, QTextEdit {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    color: {TEXT_HI};
    font-size: 13px;
    selection-background-color: #bfdbfe;
    selection-color: {TEXT_HI};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {{
    border: 1px solid {BLUE};
}}
QComboBox QAbstractItemView {{
    background-color: {CARD};
    color: {TEXT_HI};
    selection-background-color: {BLUE};
    border: 1px solid {BORDER};
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {CARD};
    border: none;
    border-radius: 3px;
}}
QCheckBox {{
    color: {TEXT_HI};
    font-size: 13px;
    font-weight: 600;
    spacing: 10px;
}}
QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 5px;
    border: 2px solid {BORDER};
    background-color: {BG};
}}
QCheckBox::indicator:checked {{
    background-color: {BLUE};
    border-color: {BLUE};
}}
"""


class _FramelessBaseDialog(QDialog):
    """Classe de base pour toutes les modales Frameless avec gestion du déplacement."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_pos = None
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setModal(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def _setup_container(self, fixed_width: int = 540) -> tuple[QVBoxLayout, QFrame]:
        self.setFixedWidth(fixed_width)
        root_lay = QVBoxLayout(self)
        root_lay.setContentsMargins(0, 0, 0, 0)

        container = QFrame()
        container.setObjectName("modalContainer")
        container.setStyleSheet(f"""
            QFrame#modalContainer {{
                background-color: {BG};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
        """)
        root_lay.addWidget(container)

        content_lay = QVBoxLayout(container)
        content_lay.setContentsMargins(28, 24, 28, 24)
        content_lay.setSpacing(18)
        return content_lay, container

    def _create_header(self, badge_txt: str, badge_bg: str, badge_border: str, title_txt: str, sub_txt: str) -> QFrame:
        header = QFrame()
        header.setObjectName("modalHeaderCard")
        header.setStyleSheet(f"""
            QFrame#modalHeaderCard {{
                background-color: {CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(16, 14, 16, 14)
        h_lay.setSpacing(14)

        icon = QLabel(badge_txt)
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(48, 48)
        icon.setStyleSheet(f"""
            background-color: {badge_bg};
            color: #ffffff;
            border: 2px solid {badge_border};
            border-radius: 24px;
            font-size: 15px;
            font-weight: 900;
        """)
        h_lay.addWidget(icon)

        t_box = QVBoxLayout()
        t_box.setSpacing(3)
        t = QLabel(title_txt)
        t.setStyleSheet(f"font-size: 17px; font-weight: 800; color: {TEXT_HI};")
        s = QLabel(sub_txt)
        s.setStyleSheet(f"font-size: 12px; color: {TEXT_LO};")
        t_box.addWidget(t)
        t_box.addWidget(s)
        h_lay.addLayout(t_box, stretch=1)

        close_x = QPushButton("✕")
        close_x.setCursor(QCursor(Qt.PointingHandCursor))
        close_x.setFixedSize(30, 30)
        close_x.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #94a3b8;
                border: none;
                border-radius: 6px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ef4444;
                color: #ffffff;
            }
        """)
        close_x.clicked.connect(self.reject)
        h_lay.addWidget(close_x)
        install_drag_handle(self, [header, icon, t, s])

        return header


# =============================================================================
# 1. MODALE PROFESSEUR
# =============================================================================
class ProfessorDialog(_FramelessBaseDialog):
    """Dialogue pour créer ou modifier un professeur (Frameless)."""

    def __init__(self, parent=None, professor: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.professor = professor
        self.is_edit = professor is not None
        self.setWindowTitle("Modifier le Professeur" if self.is_edit else "Ajouter un Professeur — EvalPro")
        self.setStyleSheet(DIALOG_STYLE)

        main_lay, _ = self._setup_container(fixed_width=540)

        t_title = "Modifier l'Enseignant" if self.is_edit else "Nouvel Enseignant"
        t_sub = "Mise à jour des coordonnées" if self.is_edit else "Enregistrez un nouveau professeur dans le corps professoral"
        header = self._create_header("PR", BLUE_DIM, BLUE, t_title, t_sub)
        main_lay.addWidget(header)

        # Formulaire
        card = QFrame()
        card.setObjectName("formCard")
        card.setStyleSheet(f"QFrame#formCard {{ background-color: {CARD}; border: 1px solid {BORDER}; border-radius: 12px; }}")
        f_lay = QGridLayout(card)
        f_lay.setContentsMargins(18, 18, 18, 18)
        f_lay.setHorizontalSpacing(16)
        f_lay.setVerticalSpacing(12)

        self.matricule_input = QLineEdit()
        self.matricule_input.setPlaceholderText("Ex: ENS001")

        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("Prénom")

        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Nom")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("exemple@univ.edu")

        self.department_input = QLineEdit()
        self.department_input.setPlaceholderText("Ex: Informatique")

        self.grade_input = QLineEdit()
        self.grade_input.setPlaceholderText("Ex: Professeur Ordinaire, Ph.D.")

        self.status_combo = QComboBox()
        self.status_combo.addItems(["active", "inactive", "on_leave", "retired"])

        fields = [
            ("Matricule *", self.matricule_input),
            ("Prénom *", self.first_name_input),
            ("Nom *", self.last_name_input),
            ("Email :", self.email_input),
            ("Département *", self.department_input),
            ("Grade :", self.grade_input),
            ("Statut *", self.status_combo),
        ]
        for row, (lbl_txt, widget) in enumerate(fields):
            l = QLabel(lbl_txt)
            l.setStyleSheet(f"color: {TEXT_LO}; font-size: 12px; font-weight: 600;")
            f_lay.addWidget(l, row, 0)
            f_lay.addWidget(widget, row, 1)

        main_lay.addWidget(card)

        # Boutons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch()

        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.cancel_btn.setFixedSize(110, 36)
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CARD};
                color: {TEXT_HI};
                border: 1px solid {BORDER};
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: {BG}; }}
        """)
        self.cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Enregistrer")
        self.save_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.save_btn.setFixedSize(120, 36)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BLUE};
                color: #ffffff;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: #2563eb; }}
        """)
        self.save_btn.clicked.connect(self.save)
        btn_row.addWidget(self.save_btn)
        main_lay.addLayout(btn_row)

        if self.is_edit and self.professor:
            self.matricule_input.setText(str(self.professor.get("matricule", "")))
            self.first_name_input.setText(str(self.professor.get("first_name", "")))
            self.last_name_input.setText(str(self.professor.get("last_name", "")))
            self.email_input.setText(str(self.professor.get("email", "")))
            self.department_input.setText(str(self.professor.get("department", "")))
            self.grade_input.setText(str(self.professor.get("grade", "")))
            current_status = self.professor.get("status", "active")
            idx = self.status_combo.findText(current_status)
            if idx >= 0:
                self.status_combo.setCurrentIndex(idx)

    def save(self):
        matricule = self.matricule_input.text().strip()
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        email = self.email_input.text().strip()
        department = self.department_input.text().strip()
        grade = self.grade_input.text().strip()
        status = self.status_combo.currentText()

        if not matricule or not first_name or not last_name or not department:
            QMessageBox.warning(self, "Champs obligatoires", "Veuillez remplir le matricule, le prénom, le nom et le département.")
            return

        if self.is_edit and self.professor:
            prof_id = self.professor.get("id")
            res = ProfessorsAPI.update(
                prof_id,
                matricule=matricule,
                first_name=first_name,
                last_name=last_name,
                email=email,
                department=department,
                grade=grade,
                active=(status == "active"),
                status=status
            )
            if res:
                QMessageBox.information(self, "Succès", "Professeur mis à jour avec succès.")
                self.accept()
            else:
                QMessageBox.warning(self, "Erreur", f"Échec de mise à jour: {ProfessorsAPI.last_error or 'Erreur inconnue'}")
        else:
            res = ProfessorsAPI.create(
                matricule=matricule,
                first_name=first_name,
                last_name=last_name,
                email=email,
                department=department,
                grade=grade,
                status=status
            )
            if res:
                QMessageBox.information(self, "Succès", "Professeur créé avec succès.")
                self.accept()
            else:
                QMessageBox.warning(self, "Erreur", f"Échec de création: {ProfessorsAPI.last_error or 'Erreur inconnue'}")


# =============================================================================
# 2. MODALE COURS
# =============================================================================
class CourseDialog(_FramelessBaseDialog):
    """Dialogue pour créer ou modifier un cours (Frameless)."""

    def __init__(self, parent=None, course: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.course = course
        self.is_edit = course is not None
        self.setWindowTitle("Modifier le Cours" if self.is_edit else "Ajouter un Cours — EvalPro")
        self.setStyleSheet(DIALOG_STYLE)

        main_lay, _ = self._setup_container(fixed_width=540)

        t_title = "Modifier le Cours" if self.is_edit else "Nouveau Cours"
        t_sub = "Mise à jour des paramètres du cours" if self.is_edit else "Ajoutez un nouvel enseignement au catalogue universitaire"
        header = self._create_header("CO", PURPLE_D, PURPLE, t_title, t_sub)
        main_lay.addWidget(header)

        card = QFrame()
        card.setObjectName("formCard")
        card.setStyleSheet(f"QFrame#formCard {{ background-color: {CARD}; border: 1px solid {BORDER}; border-radius: 12px; }}")
        f_lay = QGridLayout(card)
        f_lay.setContentsMargins(18, 18, 18, 18)
        f_lay.setHorizontalSpacing(16)
        f_lay.setVerticalSpacing(12)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Ex: INF304")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Intitulé du cours")

        self.department_input = QLineEdit()
        self.department_input.setPlaceholderText("Ex: Informatique")

        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("Ex. 2026-2027")

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Description sommaire des objectifs du cours")
        self.description_input.setFixedHeight(75)

        fields = [
            ("Code cours *", self.code_input),
            ("Intitulé *", self.name_input),
            ("Département *", self.department_input),
            ("Année académique *", self.year_input),
            ("Description :", self.description_input),
        ]
        for row, (lbl_txt, widget) in enumerate(fields):
            l = QLabel(lbl_txt)
            l.setStyleSheet(f"color: {TEXT_LO}; font-size: 12px; font-weight: 600;")
            f_lay.addWidget(l, row, 0)
            f_lay.addWidget(widget, row, 1)

        main_lay.addWidget(card)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch()

        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.cancel_btn.setFixedSize(110, 36)
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CARD};
                color: {TEXT_HI};
                border: 1px solid {BORDER};
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: {BG}; }}
        """)
        self.cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Enregistrer")
        self.save_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.save_btn.setFixedSize(120, 36)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PURPLE};
                color: #ffffff;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: #7c3aed; }}
        """)
        self.save_btn.clicked.connect(self.save)
        btn_row.addWidget(self.save_btn)
        main_lay.addLayout(btn_row)

        if self.is_edit and self.course:
            self.code_input.setText(str(self.course.get("code", "")))
            self.name_input.setText(str(self.course.get("name", "")))
            self.department_input.setText(str(self.course.get("department", "")))
            self.year_input.setText(str(self.course.get("academic_year", "")))
            self.description_input.setPlainText(str(self.course.get("description", "")))

    def save(self):
        code = self.code_input.text().strip()
        name = self.name_input.text().strip()
        department = self.department_input.text().strip()
        year = self.year_input.text().strip()
        description = self.description_input.toPlainText().strip()

        if not code or not name or not department or not year:
            QMessageBox.warning(self, "Champs obligatoires", "Veuillez remplir le code, le nom, le département et l'année académique.")
            return

        if self.is_edit and self.course:
            course_id = self.course.get("id")
            res = CoursesAPI.update(
                course_id,
                code=code,
                name=name,
                description=description,
                department=department,
                academic_year=year
            )
            if res:
                QMessageBox.information(self, "Succès", "Cours mis à jour avec succès.")
                self.accept()
            else:
                QMessageBox.warning(self, "Erreur", f"Échec de mise à jour: {CoursesAPI.last_error or 'Erreur inconnue'}")
        else:
            res = CoursesAPI.create(
                code=code,
                name=name,
                description=description,
                department=department,
                academic_year=year
            )
            if res:
                QMessageBox.information(self, "Succès", "Cours créé avec succès.")
                self.accept()
            else:
                QMessageBox.warning(self, "Erreur", f"Échec de création: {CoursesAPI.last_error or 'Erreur inconnue'}")


# =============================================================================
# 3. MODALE CRITÈRE
# =============================================================================
class CriterionDialog(_FramelessBaseDialog):
    """Dialogue pour créer ou modifier un critère d'évaluation (Frameless)."""

    def __init__(self, parent=None, criterion: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.criterion = criterion
        self.is_edit = criterion is not None
        self.setWindowTitle("Modifier le Critère" if self.is_edit else "Ajouter un Critère — EvalPro")
        self.setStyleSheet(DIALOG_STYLE)

        main_lay, _ = self._setup_container(fixed_width=640)

        t_title = "Modifier le Critère" if self.is_edit else "Nouveau Critère"
        t_sub = (
            "Ajustez les informations utilisées dans les évaluations."
            if self.is_edit else
            "Créez un repère clair pour guider l'évaluation des cours."
        )
        header = self._create_header("CR", AMBER_D, AMBER, t_title, t_sub)
        main_lay.addWidget(header)

        card = QFrame()
        card.setObjectName("formCard")
        card.setStyleSheet(f"QFrame#formCard {{ background-color: {CARD}; border: 1px solid {BORDER}; border-radius: 14px; }}")
        f_lay = QVBoxLayout(card)
        f_lay.setContentsMargins(22, 20, 22, 20)
        f_lay.setSpacing(8)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex. : Clarté des explications")
        self.name_input.setMinimumHeight(44)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Précisez ce que l'étudiant doit observer pour noter ce critère.")
        self.description_input.setFixedHeight(92)

        self.max_score_spin = QSpinBox()
        self.max_score_spin.setRange(1, 5)
        self.max_score_spin.setValue(5)
        self.max_score_spin.setFixedSize(100, 42)

        self.active_check = QCheckBox("Activer ce critère dans les formulaires étudiants")
        self.active_check.setChecked(True)

        def add_field(label_text, widget, help_text=None):
            label = QLabel(label_text)
            label.setStyleSheet(f"color: {TEXT_HI}; font-size: 13px; font-weight: 700;")
            f_lay.addWidget(label)
            f_lay.addWidget(widget)
            if help_text:
                hint = QLabel(help_text)
                hint.setWordWrap(True)
                hint.setStyleSheet(f"color: {TEXT_LO}; font-size: 11px;")
                f_lay.addWidget(hint)

        add_field("Nom du critère *", self.name_input)
        add_field(
            "Description",
            self.description_input,
            "Cette description aide les étudiants à comprendre ce qu'ils évaluent.",
        )

        options = QFrame()
        options.setStyleSheet(f"QFrame {{ background: {BG}; border: 1px solid {BORDER}; border-radius: 10px; }}")
        options_lay = QHBoxLayout(options)
        options_lay.setContentsMargins(14, 12, 14, 12)
        options_lay.setSpacing(14)
        score_box = QVBoxLayout()
        score_label = QLabel("NOTE MAXIMALE")
        score_label.setStyleSheet(f"color: {TEXT_LO}; font-size: 10px; font-weight: 800; letter-spacing: 0.5px;")
        score_box.addWidget(score_label)
        score_box.addWidget(self.max_score_spin)
        score_hint = QLabel("Échelle utilisée par les étudiants : 1 à la note maximale.")
        score_hint.setWordWrap(True)
        score_hint.setStyleSheet(f"color: {TEXT_LO}; font-size: 10px;")
        score_box.addWidget(score_hint)
        options_lay.addLayout(score_box, 1)

        status_box = QFrame()
        status_box.setStyleSheet(f"QFrame {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 9px; }}")
        status_lay = QVBoxLayout(status_box)
        status_lay.setContentsMargins(12, 12, 12, 12)
        status_lay.addWidget(self.active_check)
        status_hint = QLabel("Un critère désactivé n'apparaît plus dans les formulaires.")
        status_hint.setWordWrap(True)
        status_hint.setStyleSheet(f"color: {TEXT_LO}; font-size: 10px; border: none;")
        status_lay.addWidget(status_hint)
        options_lay.addWidget(status_box, 1)
        f_lay.addSpacing(6)
        f_lay.addWidget(options)

        main_lay.addWidget(card)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch()

        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.cancel_btn.setFixedSize(116, 40)
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CARD};
                color: {TEXT_HI};
                border: 1px solid {BORDER};
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: {BG}; }}
        """)
        self.cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Enregistrer")
        self.save_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.save_btn.setFixedSize(170, 40)
        self.save_btn.setText("Enregistrer les changements" if self.is_edit else "Créer le critère")
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BLUE};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: #1d4ed8; }}
        """)
        self.save_btn.clicked.connect(self.save)
        btn_row.addWidget(self.save_btn)
        main_lay.addLayout(btn_row)

        if self.is_edit and self.criterion:
            self.name_input.setText(str(self.criterion.get("name", "")))
            self.description_input.setPlainText(str(self.criterion.get("description", "")))
            self.max_score_spin.setValue(int(self.criterion.get("max_score", 5)))
            self.active_check.setChecked(bool(self.criterion.get("active", True)))

    def save(self):
        name = self.name_input.text().strip()
        description = self.description_input.toPlainText().strip()
        max_score = self.max_score_spin.value()
        active = self.active_check.isChecked()

        if not name:
            QMessageBox.warning(self, "Champs obligatoires", "Veuillez renseigner le nom du critère.")
            return

        if self.is_edit and self.criterion:
            crit_id = self.criterion.get("id")
            res = CriteriaAPI.update(
                crit_id,
                name=name,
                description=description,
                max_score=max_score,
                active=active
            )
            if res:
                QMessageBox.information(self, "Succès", "Critère mis à jour avec succès.")
                self.accept()
            else:
                QMessageBox.warning(self, "Erreur", f"Échec de mise à jour: {CriteriaAPI.last_error or 'Erreur inconnue'}")
        else:
            res = CriteriaAPI.create(
                name=name,
                description=description,
                max_score=max_score
            )
            if res:
                QMessageBox.information(self, "Succès", "Critère créé avec succès.")
                self.accept()
            else:
                QMessageBox.warning(self, "Erreur", f"Échec de création: {CriteriaAPI.last_error or 'Erreur inconnue'}")


# =============================================================================
# 4. MODALE ÉLIGIBILITÉ ADMIN
# =============================================================================
class EligibilityAdminDialog(_FramelessBaseDialog):
    """Dialogue moderne pour qu'un administrateur gère l'éligibilité d'un étudiant (Frameless)."""

    def __init__(self, parent=None, student_id: int = 1):
        super().__init__(parent)
        self.student_id = student_id
        self.has_record = False
        self.lookup_failed = False
        self.setWindowTitle(f"Gestion de l'Éligibilité — Étudiant #{student_id}")
        self.setStyleSheet(DIALOG_STYLE)

        main_lay, _ = self._setup_container(fixed_width=520)

        header = self._create_header(
            "EL", GREEN_D, GREEN,
            f"Éligibilité Étudiant #{student_id}",
            "Cochez les critères validés pour activer les droits d'évaluation"
        )
        main_lay.addWidget(header)

        card = QFrame()
        card.setObjectName("formCard")
        card.setStyleSheet(f"QFrame#formCard {{ background-color: {CARD}; border: 1px solid {BORDER}; border-radius: 12px; }}")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(18, 16, 18, 16)
        card_lay.setSpacing(12)

        self.enrollment_cb = QCheckBox("Inscription universitaire en règle")
        self.academic_fees_cb = QCheckBox("Frais académiques réglés")
        self.lab_fees_cb = QCheckBox("Frais de laboratoire réglés")
        self.access_fees_cb = QCheckBox("Frais d'accès réseau réglés")

        for cb in (self.enrollment_cb, self.academic_fees_cb, self.lab_fees_cb, self.access_fees_cb):
            cb.stateChanged.connect(self._on_criteria_changed)
            card_lay.addWidget(cb)

        main_lay.addWidget(card)

        self.status_lbl = QLabel("Vérification en cours...")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 700;
            padding: 10px;
            border-radius: 8px;
            background-color: {CARD};
            color: {TEXT_LO};
            border: 1px solid {BORDER};
        """)
        main_lay.addWidget(self.status_lbl)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        self.delete_btn = QPushButton("Supprimer la fiche")
        self.delete_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.delete_btn.setStyleSheet("QPushButton { background: #7f1d1d; color: white; border: none; border-radius: 6px; padding: 8px 12px; font-weight: bold; }")
        self.delete_btn.setVisible(False)
        self.delete_btn.clicked.connect(self.delete_record)
        btn_row.addWidget(self.delete_btn)
        btn_row.addStretch()

        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.cancel_btn.setFixedSize(110, 36)
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CARD};
                color: {TEXT_HI};
                border: 1px solid {BORDER};
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: {BG}; }}
        """)
        self.cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Enregistrer")
        self.save_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.save_btn.setFixedSize(120, 36)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {GREEN};
                color: #ffffff;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: #059669; }}
        """)
        self.save_btn.clicked.connect(self.save)
        btn_row.addWidget(self.save_btn)
        main_lay.addLayout(btn_row)

        self.load_data()

    def _on_criteria_changed(self):
        all_ok = (
            self.enrollment_cb.isChecked()
            and self.academic_fees_cb.isChecked()
            and self.lab_fees_cb.isChecked()
            and self.access_fees_cb.isChecked()
        )
        if all_ok:
            self.status_lbl.setText("✓ Statut résultant : ÉLIGIBLE AUX ÉVALUATIONS")
            self.status_lbl.setStyleSheet("""
                font-size: 12px;
                font-weight: 700;
                padding: 10px;
                border-radius: 8px;
                background-color: #064e3b;
                color: #6ee7b7;
                border: 1px solid #10b981;
            """)
        else:
            self.status_lbl.setText("✗ Statut résultant : NON ÉLIGIBLE (Critères manquants)")
            self.status_lbl.setStyleSheet("""
                font-size: 12px;
                font-weight: 700;
                padding: 10px;
                border-radius: 8px;
                background-color: #450a0a;
                color: #fca5a5;
                border: 1px solid #ef4444;
            """)

    def load_data(self):
        data = EligibilityAPI.check(self.student_id)
        if data:
            self.has_record = True
            self.delete_btn.setVisible(True)
            self.enrollment_cb.blockSignals(True)
            self.academic_fees_cb.blockSignals(True)
            self.lab_fees_cb.blockSignals(True)
            self.access_fees_cb.blockSignals(True)

            self.enrollment_cb.setChecked(bool(data.get("enrollment", False)))
            self.academic_fees_cb.setChecked(bool(data.get("academic_fees", False)))
            self.lab_fees_cb.setChecked(bool(data.get("laboratory_fees", False)))
            self.access_fees_cb.setChecked(bool(data.get("access_fees", False)))

            self.enrollment_cb.blockSignals(False)
            self.academic_fees_cb.blockSignals(False)
            self.lab_fees_cb.blockSignals(False)
            self.access_fees_cb.blockSignals(False)

            self._on_criteria_changed()
        elif "not found" in (EligibilityAPI.last_error or "").lower():
            self.status_lbl.setText("ℹ️ Aucune fiche existante (sera initialisée à l'enregistrement).")
            self.status_lbl.setStyleSheet(f"""
                font-size: 12px;
                font-weight: 600;
                padding: 10px;
                border-radius: 8px;
                background-color: {CARD};
                color: {TEXT_LO};
                border: 1px solid {BORDER};
            """)
        else:
            self.lookup_failed = True
            self.save_btn.setEnabled(False)
            self.status_lbl.setText("Impossible de vérifier la fiche via l’API : " + (EligibilityAPI.last_error or "erreur inconnue"))

    def delete_record(self):
        answer = QMessageBox.question(
            self,
            "Supprimer la fiche",
            f"Supprimer la fiche d’éligibilité de l’étudiant #{self.student_id} ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        if EligibilityAPI.delete(self.student_id):
            QMessageBox.information(self, "Fiche supprimée", "La fiche d’éligibilité a été supprimée.")
            self.accept()
        else:
            QMessageBox.warning(self, "Erreur", EligibilityAPI.last_error or "Suppression impossible.")

    def save(self):
        enrollment = self.enrollment_cb.isChecked()
        academic_fees = self.academic_fees_cb.isChecked()
        lab_fees = self.lab_fees_cb.isChecked()
        access_fees = self.access_fees_cb.isChecked()

        if self.has_record:
            res = EligibilityAPI.update(
                self.student_id,
                enrollment=enrollment,
                academic_fees=academic_fees,
                laboratory_fees=lab_fees,
                access_fees=access_fees
            )
        else:
            res = EligibilityAPI.create(
                self.student_id,
                enrollment=enrollment,
                academic_fees=academic_fees,
                laboratory_fees=lab_fees,
                access_fees=access_fees
            )

        if res:
            is_elig = res.get("eligible", False)
            msg = f"Statut de l'étudiant #{self.student_id} mis à jour :\n" + (
                "✅ Éligible pour évaluer ses enseignants." if is_elig
                else "⚠️ Non éligible (évaluation verrouillée)."
            )
            QMessageBox.information(self, "Succès", msg)
            self.accept()
        else:
            QMessageBox.warning(self, "Erreur", f"Impossible d'enregistrer: {EligibilityAPI.last_error or 'Erreur serveur'}")


# Alias pour compatibilité
CriteriaDialog = CriterionDialog

__all__ = [
    "ProfessorDialog",
    "CourseDialog",
    "CriterionDialog",
    "CriteriaDialog",
    "EligibilityAdminDialog",
]

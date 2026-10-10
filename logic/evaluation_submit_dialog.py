"""Formulaire de soumission d'une évaluation via l'API Go."""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from api.criteria_api import CriteriaAPI
from api.courses_api import CoursesAPI
from api.evaluations_api import EvaluationsAPI
from api.eligibility_api import EligibilityAPI
from api.professors_api import ProfessorsAPI
from logic.frameless_windows import install_drag_handle, install_size_grip


class EvaluationSubmitDialog(QDialog):
    evaluationSubmitted = pyqtSignal(dict)
    requestEligibility = pyqtSignal()

    def __init__(self, parent=None, embedded=False):
        super().__init__(parent)
        self.embedded = embedded
        self.setWindowTitle("Évaluer un professeur")
        if embedded:
            self.setWindowFlags(Qt.Widget)
            self.setModal(False)
        else:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
            screen = parent.screen() if parent is not None else QGuiApplication.primaryScreen()
            available = screen.availableGeometry() if screen is not None else None
            dialog_width = min(980, available.width() - 48) if available else 980
            dialog_height = min(780, available.height() - 48) if available else 780
            self.setMinimumSize(min(820, dialog_width), min(620, dialog_height))
            self.resize(dialog_width, dialog_height)
            install_size_grip(self)
        self.setStyleSheet("""
            QDialog { background: #ffffff; border: 1px solid #dbeafe; border-radius: 14px; }
            QLabel { color: #123b66; background: transparent; }
            QComboBox, QLineEdit, QSpinBox {
                background: white; color: #123b66; border: 1px solid #cbd5e1;
                border-radius: 9px; padding: 9px 11px; min-height: 22px; font-size: 13px;
            }
            QComboBox:focus, QLineEdit:focus, QSpinBox:focus { border: 1px solid #2563eb; }
            QComboBox QAbstractItemView { background: white; color: #123b66; selection-background-color: #dbeafe; }
            QScrollArea { border: none; background: white; }
        """)

        self.criteria = []
        self.available = False
        self.created_evaluation = None
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        root.addWidget(self._build_header())
        user = getattr(parent, "user_data", {}) or {}
        eligibility = EligibilityAPI.check(user.get("id", 0))
        if not eligibility or not eligibility.get("eligible"):
            self._build_unavailable_state(root, eligibility)
            return

        self.available = True
        criteria = CriteriaAPI.get_active()
        professors = ProfessorsAPI.get_active()
        courses = CoursesAPI.get_all()
        self.load_errors = [
            error for error in (
                CriteriaAPI.last_error if criteria is None else None,
                ProfessorsAPI.last_error if professors is None else None,
                CoursesAPI.last_error if courses is None else None,
            ) if error
        ]

        root.addWidget(self._build_selection_card(professors or [], courses or []))

        criteria_heading = QHBoxLayout()
        title = QLabel("Critères d’évaluation")
        title.setStyleSheet("font-size: 16px; font-weight: 700;")
        criteria_heading.addWidget(title)
        criteria_heading.addStretch(1)
        count = QLabel(f"{len(criteria or [])} critères")
        count.setStyleSheet("color: #456b8f; font-size: 12px;")
        criteria_heading.addWidget(count)
        root.addLayout(criteria_heading)

        self.criteria_scroll = QScrollArea()
        self.criteria_scroll.setWidgetResizable(True)
        self.criteria_scroll.setMinimumHeight(190)
        self.criteria_scroll.setStyleSheet("QScrollArea { background: white; }")
        criteria_content = QWidget()
        criteria_content.setStyleSheet("background: white;")
        criteria_layout = QVBoxLayout(criteria_content)
        criteria_layout.setContentsMargins(2, 2, 6, 2)
        criteria_layout.setSpacing(9)
        for index, criterion in enumerate(criteria or [], 1):
            criteria_layout.addWidget(self._build_criterion_card(index, criterion))
        criteria_layout.addStretch(1)
        self.criteria_scroll.setWidget(criteria_content)
        root.addWidget(self.criteria_scroll, 1)

        self.status = QLabel()
        self.status.setWordWrap(True)
        self.status.hide()
        root.addWidget(self.status)
        messages = list(self.load_errors)
        missing = []
        if criteria is not None and not criteria:
            missing.append("aucun critère actif")
        if professors is not None and not professors:
            missing.append("aucun professeur actif")
        if courses is not None and not courses:
            missing.append("aucun cours disponible")
        if messages:
            self._show_status("Connexion aux données impossible : " + "\n".join(messages), error=True)
        elif missing:
            self._show_status("Soumission indisponible : " + ", ".join(missing) + ".", error=True)

        footer = QHBoxLayout()
        footer.addStretch(1)
        cancel = QPushButton("Réinitialiser" if self.embedded else "Annuler")
        cancel.setObjectName("cancelButton")
        submit = QPushButton("Envoyer l’évaluation")
        submit.setObjectName("submitButton")
        submit.setDefault(True)
        submit.setEnabled(not self.load_errors and bool(criteria) and bool(professors) and bool(courses))
        footer.addWidget(cancel)
        footer.addWidget(submit)
        root.addLayout(footer)

        self.setStyleSheet(self.styleSheet() + """
            QPushButton { border: none; border-radius: 9px; padding: 11px 18px; font-size: 13px; font-weight: 700; }
            QPushButton#cancelButton { background: #eaf2ff; color: #123b66; }
            QPushButton#cancelButton:hover { background: #dbeafe; }
            QPushButton#submitButton { background: #dbeafe; color: #123b66; }
            QPushButton#submitButton:hover { background: #bfdbfe; }
            QPushButton#submitButton:disabled { background: #e2e8f0; color: #64748b; }
        """)
        cancel.clicked.connect(self.reset_form if self.embedded else self.reject)
        submit.clicked.connect(self.submit)

    def _build_header(self):
        card = QFrame()
        card.setObjectName("evaluationHeader")
        card.setStyleSheet("QFrame#evaluationHeader { background: #ffffff; border: 1px solid #dbeafe; border-radius: 14px; }")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)

        icon = QLabel("★")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(44, 44)
        icon.setStyleSheet("background: #dbeafe; color: #1d4ed8; border: 1px solid #bfdbfe; border-radius: 22px; font-size: 20px;")
        layout.addWidget(icon)
        text = QVBoxLayout()
        text.setSpacing(3)
        title = QLabel("Votre avis compte")
        title.setStyleSheet("font-size: 19px; font-weight: 800; color: #123b66;")
        subtitle = QLabel("Évaluez votre expérience avec un professeur")
        subtitle.setStyleSheet("font-size: 12px; color: #315b82;")
        text.addWidget(title)
        text.addWidget(subtitle)
        layout.addLayout(text, 1)
        close = QPushButton("×")
        close.setToolTip("Fermer")
        close.setFixedSize(32, 32)
        close.setStyleSheet("QPushButton { color: #315b82; background: #eff6ff; border: none; border-radius: 16px; font-size: 18px; font-weight: 700; } QPushButton:hover { background: #dbeafe; }")
        close.setVisible(not self.embedded)
        close.clicked.connect(self.reject)
        layout.addWidget(close)
        if not self.embedded:
            install_drag_handle(self, [card, icon, title, subtitle])
        return card

    def _build_selection_card(self, professors, courses):
        card = QFrame()
        card.setObjectName("selectionCard")
        card.setStyleSheet("QFrame#selectionCard { background: white; border: 1px solid #e2e8f0; border-radius: 12px; }")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        heading = QLabel("Contexte de l’évaluation")
        heading.setStyleSheet("font-size: 15px; font-weight: 700; color: #123b66;")
        layout.addWidget(heading)
        form = QFormLayout()
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(10)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.professor = QComboBox()
        self.professor.setMinimumHeight(42)
        self.professor.addItem("Choisir un professeur", None)
        for item in professors:
            name = f"{item.get('first_name', '')} {item.get('last_name', '')}".strip()
            self.professor.addItem(name or item.get("matricule", "Professeur"), item.get("id"))

        self.course = QComboBox()
        self.course.setMinimumHeight(42)
        self.course.addItem("Choisir un cours", None)
        for item in courses:
            label = f"{item.get('code', '')} — {item.get('name', '')}".strip(" —")
            self.course.addItem(label, (item.get("id"), item.get("academic_year", "")))

        self.year = QLineEdit()
        self.year.setReadOnly(True)
        self.year.setPlaceholderText("Sélectionnez un cours")
        self.year.setMinimumHeight(42)
        self.period = QComboBox()
        self.period.setMinimumHeight(42)
        self.period.addItems(["Semestre 1", "Semestre 2", "Annuel"])

        form.addRow(self._field_label("Professeur"), self.professor)
        form.addRow(self._field_label("Cours"), self.course)
        form.addRow(self._field_label("Année académique"), self.year)
        form.addRow(self._field_label("Période"), self.period)
        layout.addLayout(form)
        self.course.currentIndexChanged.connect(self._course_changed)
        self._course_changed()
        return card

    @staticmethod
    def _field_label(text):
        label = QLabel(text)
        label.setStyleSheet("font-size: 12px; font-weight: 600; color: #315b82;")
        return label

    def _build_criterion_card(self, index, criterion):
        card = QFrame()
        card.setObjectName("criterionCard")
        card.setStyleSheet("QFrame#criterionCard { background: white; border: 1px solid #e2e8f0; border-radius: 10px; }")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 11, 14, 11)
        layout.setSpacing(12)

        number = QLabel(f"{index:02d}")
        number.setAlignment(Qt.AlignCenter)
        number.setFixedSize(34, 34)
        number.setStyleSheet("background: #eff6ff; color: #2563eb; border-radius: 17px; font-weight: 700;")
        layout.addWidget(number)

        details = QVBoxLayout()
        details.setSpacing(3)
        title = QLabel(criterion.get("name", "Critère"))
        title.setStyleSheet("font-size: 13px; font-weight: 700; color: #123b66;")
        details.addWidget(title)
        description = criterion.get("description")
        if description:
            note = QLabel(description)
            note.setWordWrap(True)
            note.setStyleSheet("font-size: 11px; color: #456b8f;")
            details.addWidget(note)
        layout.addLayout(details, 1)

        maximum = min(5, max(1, int(criterion.get("max_score", 5))))
        score = QSpinBox()
        score.setRange(0, maximum)
        score.setValue(0)
        score.setFixedWidth(82)
        score.setAlignment(Qt.AlignCenter)
        score.setToolTip(f"0 = à renseigner ; choisissez une note de 1 à {maximum}")
        layout.addWidget(score)
        scale = QLabel(f"/ {maximum}")
        scale.setStyleSheet("font-size: 12px; color: #456b8f;")
        layout.addWidget(scale)
        self.criteria.append((criterion, score))
        return card

    def _build_unavailable_state(self, root, eligibility):
        if eligibility is None and "not found" not in (EligibilityAPI.last_error or "").lower():
            message = "Impossible de vérifier votre éligibilité. Réessayez dans quelques instants."
        else:
            message = "Votre compte ne possède pas de fiche d’éligibilité active. Contactez l’administration."
        reasons = (eligibility or {}).get("reasons", [])
        reason = EligibilityAPI.last_error or ", ".join(reasons)
        panel = QLabel(message + (f"\n\n{reason}" if reason else ""))
        panel.setWordWrap(True)
        panel.setStyleSheet("background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; padding: 18px; color: #123b66;")
        root.addWidget(panel)
        root.addStretch(1)
        if self.embedded:
            eligibility_btn = QPushButton("Consulter mon éligibilité")
            eligibility_btn.clicked.connect(self.requestEligibility.emit)
            eligibility_btn.setStyleSheet("background: #dbeafe; color: #123b66; border: none; border-radius: 9px; padding: 11px 18px; font-weight: 700;")
            root.addWidget(eligibility_btn, 0, Qt.AlignRight)
        else:
            close = QPushButton("Fermer")
            close.clicked.connect(self.reject)
            close.setStyleSheet("background: #dbeafe; color: #123b66; border: none; border-radius: 9px; padding: 11px 18px; font-weight: 700;")
            root.addWidget(close, 0, Qt.AlignRight)

    def _show_status(self, text, error=False):
        self.status.setText(text)
        color = "#123b66"
        background = "#eff6ff"
        self.status.setStyleSheet(f"background: {background}; color: {color}; border-radius: 8px; padding: 10px 12px;")
        self.status.show()

    def submit(self):
        if not self.available:
            return
        professor_id = self.professor.currentData()
        course_data = self.course.currentData()
        course_id = course_data[0] if course_data else None
        year = self.year.text().strip()
        if not professor_id or not course_id or not year or not self.criteria:
            QMessageBox.warning(self, "Formulaire incomplet", "Choisissez un professeur, un cours et renseignez les critères actifs.")
            return
        if any(score.value() < 1 for _, score in self.criteria):
            QMessageBox.warning(
                self,
                "Critères incomplets",
                "Chaque critère doit recevoir une note de 1 ou plus. Le 0 indique qu’il reste à renseigner.",
            )
            return
        answers = [{"criterion_id": int(item["id"]), "score": score.value()} for item, score in self.criteria]
        result = EvaluationsAPI.create(professor_id, course_id, year, self.period.currentText(), answers)
        if result:
            result["professor_name"] = self.professor.currentText()
            result["course_name"] = self.course.currentText()
            self.created_evaluation = result
            if self.embedded:
                self._show_status("Évaluation envoyée avec succès. Votre réponse a été enregistrée.")
                self.status.setStyleSheet(
                    "background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; "
                    "border-radius: 8px; padding: 10px 12px;"
                )
                self.evaluationSubmitted.emit(result)
                self.reset_scores()
            else:
                QMessageBox.information(self, "Évaluation envoyée", "Votre évaluation a été enregistrée.")
                self.accept()
        else:
            QMessageBox.warning(self, "Échec", EvaluationsAPI.last_error or "L’API n’a pas accepté l’évaluation.")

    def _course_changed(self):
        course_data = self.course.currentData() if hasattr(self, "course") else None
        self.year.setText(course_data[1] if course_data else "")

    def reset_scores(self):
        for _, score in self.criteria:
            score.setValue(0)

    def reset_form(self):
        if hasattr(self, "professor"):
            self.professor.setCurrentIndex(0)
            self.course.setCurrentIndex(0)
            self.period.setCurrentIndex(0)
            self.reset_scores()
        if hasattr(self, "status"):
            self.status.hide()


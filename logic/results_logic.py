"""
results_logic.py
────────────────
Modale de consultation des résultats d'évaluation — Thème Dark Slate Corporate.
FramelessWindowHint avec coins arrondis, bouton de fermeture intégré et déplacement fluide.
"""
from typing import Optional, Dict, Any, List
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QColor
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QFrame, QWidget
)
from api.results_api import ResultsAPI
from api.professors_api import ProfessorsAPI
from api.courses_api import CoursesAPI
from api.criteria_api import CriteriaAPI
from api.evaluations_api import EvaluationsAPI
from logic.frameless_windows import install_drag_handle

# ─── Palette claire, cohérente avec le reste de l'application ─────────────────
BG       = "#f4f8fc"
CARD     = "#ffffff"
BORDER   = "#dbe5f0"
BLUE     = "#2563eb"
BLUE_DIM = "#eff6ff"
GREEN    = "#059669"
LIME     = "#65a30d"
AMBER    = "#d97706"
RED      = "#dc2626"
TEXT_HI  = "#123b66"
TEXT_MID = "#456b8f"
TEXT_LO  = "#647b94"


def get_score_color(avg: float) -> str:
    if avg >= 4.5: return GREEN
    if avg >= 4.0: return LIME
    if avg >= 3.0: return BLUE
    if avg >= 2.0: return AMBER
    return RED


def get_score_label(avg: float) -> str:
    if avg >= 4.5: return "Excellent"
    if avg >= 4.0: return "Très satisfaisant"
    if avg >= 3.0: return "Satisfaisant"
    if avg >= 2.0: return "À améliorer"
    return "Insuffisant"


class ResultsDialog(QDialog):
    """Fenêtre modale d'affichage interactif des résultats d'évaluation (Frameless)."""

    def __init__(self, parent=None, professor_id: Optional[int] = None, course_id: Optional[int] = None,
                 academic_year: str = "", period: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Résultats d'Évaluation — EvalPro")
        self.setFixedWidth(920)
        self.setModal(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: transparent;
            }}
            QLabel {{
                border: none;
                background: transparent;
                color: {TEXT_HI};
                padding: 0px;
            }}
        """)

        self.initial_prof_id = professor_id
        self.initial_course_id = course_id
        self.initial_year = academic_year
        self.initial_period = period
        self._drag_pos = None

        self.criteria_names: Dict[int, str] = {}

        self._setup_ui()
        self._load_filters_and_data()

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

    def _setup_ui(self):
        root_lay = QVBoxLayout(self)
        root_lay.setContentsMargins(0, 0, 0, 0)

        container = QFrame()
        container.setObjectName("resultsContainer")
        container.setStyleSheet(f"""
            QFrame#resultsContainer {{
                background-color: {BG};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
        """)
        root_lay.addWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # ── 1. En-tête (+ Close [✕]) ──────────────────────────────────────────
        header = QFrame()
        header.setObjectName("resultsHeader")
        header.setStyleSheet(f"""
            QFrame#resultsHeader {{
                background-color: {CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(18, 14, 18, 14)
        h_lay.setSpacing(16)

        icon_lbl = QLabel("📈")
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFixedSize(50, 50)
        icon_lbl.setStyleSheet(f"""
            background-color: {BLUE_DIM};
            border: 2px solid {BLUE};
            border-radius: 25px;
            font-size: 24px;
        """)
        h_lay.addWidget(icon_lbl)

        t_box = QVBoxLayout()
        t_box.setSpacing(4)
        title = QLabel("Résultats des évaluations")
        title.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {TEXT_HI};")
        subtitle = QLabel("Consultez la moyenne générale et le détail des notes par critère.")
        subtitle.setStyleSheet(f"font-size: 12px; color: {TEXT_LO};")
        t_box.addWidget(title)
        t_box.addWidget(subtitle)
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
        install_drag_handle(self, [header, icon_lbl, title, subtitle])

        layout.addWidget(header)

        # ── 2. Filtres Card ───────────────────────────────────────────────────
        f_card = QFrame()
        f_card.setObjectName("resultsFilters")
        f_card.setStyleSheet(f"""
            QFrame#resultsFilters {{
                background-color: {CARD};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
            QComboBox {{
                background-color: {BG};
                color: {TEXT_HI};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
            }}
            QComboBox:hover {{
                border-color: {BLUE};
            }}
            QComboBox QAbstractItemView {{
                background-color: {CARD};
                color: {TEXT_HI};
                selection-background-color: {BLUE};
                border: 1px solid {BORDER};
            }}
        """)
        f_lay = QVBoxLayout(f_card)
        f_lay.setContentsMargins(16, 12, 16, 12)
        f_lay.setSpacing(10)

        filter_title = QLabel("Choisir les résultats à consulter")
        filter_title.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {TEXT_HI};")
        f_lay.addWidget(filter_title)

        # Ligne 1 : Professeur et Cours
        f_row1 = QHBoxLayout()
        f_row1.setSpacing(12)

        p_lbl = QLabel("Professeur")
        p_lbl.setStyleSheet(f"color: {TEXT_LO}; font-size: 12px; font-weight: 600;")
        self.prof_combo = QComboBox()
        self.prof_combo.setMinimumWidth(240)
        self.prof_combo.currentIndexChanged.connect(self._sync_year_with_course)
        f_row1.addWidget(p_lbl)
        f_row1.addWidget(self.prof_combo, stretch=2)

        c_lbl = QLabel("Cours")
        c_lbl.setStyleSheet(f"color: {TEXT_LO}; font-size: 12px; font-weight: 600;")
        self.course_combo = QComboBox()
        self.course_combo.setMinimumWidth(200)
        self.course_combo.currentIndexChanged.connect(self._sync_year_with_course)
        f_row1.addWidget(c_lbl)
        f_row1.addWidget(self.course_combo, stretch=2)
        f_lay.addLayout(f_row1)

        # Ligne 2 : Période, Année, Bouton
        f_row2 = QHBoxLayout()
        f_row2.setSpacing(12)

        per_lbl = QLabel("Période")
        per_lbl.setStyleSheet(f"color: {TEXT_LO}; font-size: 12px; font-weight: 600;")
        self.period_combo = QComboBox()
        self.period_combo.setEditable(True)
        self.period_combo.lineEdit().setPlaceholderText("Période enregistrée dans l’évaluation")
        self.period_combo.currentIndexChanged.connect(self.load_results)
        f_row2.addWidget(per_lbl)
        f_row2.addWidget(self.period_combo, stretch=1)

        y_lbl = QLabel("Année académique")
        y_lbl.setStyleSheet(f"color: {TEXT_LO}; font-size: 12px; font-weight: 600;")
        self.year_combo = QComboBox()
        self.year_combo.setEditable(True)
        self.year_combo.lineEdit().setPlaceholderText("Année académique du cours")
        self.year_combo.currentIndexChanged.connect(self.load_results)
        f_row2.addWidget(y_lbl)
        f_row2.addWidget(self.year_combo, stretch=1)

        self.refresh_btn = QPushButton("Actualiser ⟳")
        self.refresh_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.refresh_btn.setFixedSize(120, 34)
        self.refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BLUE};
                color: #ffffff;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: #2563eb;
            }}
        """)
        self.refresh_btn.clicked.connect(self.load_results)
        f_row2.addWidget(self.refresh_btn)
        f_lay.addLayout(f_row2)

        layout.addWidget(f_card)

        # ── 3. Synthèse globale Score Card ────────────────────────────────────
        self.score_card = QFrame()
        self.score_card.setObjectName("scoreCard")
        self.score_card.setStyleSheet(f"""
            QFrame#scoreCard {{
                background-color: {CARD};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
        """)
        s_lay = QVBoxLayout(self.score_card)
        s_lay.setContentsMargins(18, 14, 18, 14)
        s_lay.setSpacing(10)

        s_top = QHBoxLayout()
        s_top.setSpacing(18)

        self.score_val_lbl = QLabel("—")
        self.score_val_lbl.setStyleSheet(f"font-size: 32px; font-weight: 900; color: {TEXT_LO};")
        s_top.addWidget(self.score_val_lbl)

        s_mid = QVBoxLayout()
        s_mid.setSpacing(6)
        self.score_label = QLabel("Moyenne générale · Nombre d’évaluations")
        self.score_label.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {TEXT_HI};")
        s_mid.addWidget(self.score_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {BG};
                border-radius: 4px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {BLUE};
                border-radius: 4px;
            }}
        """)
        s_mid.addWidget(self.progress_bar)
        s_top.addLayout(s_mid, stretch=1)

        self.badge_lbl = QLabel("  AUCUNE DONNÉE  ")
        self.badge_lbl.setStyleSheet(f"""
            background-color: {BG};
            color: {TEXT_LO};
            border: 1px solid {BORDER};
            border-radius: 6px;
            font-size: 11px;
            font-weight: bold;
            padding: 4px 8px;
        """)
        s_top.addWidget(self.badge_lbl)
        s_lay.addLayout(s_top)
        layout.addWidget(self.score_card)

        # ── 4. Tableau des critères ───────────────────────────────────────────
        criteria_title = QLabel("Détail par critère")
        criteria_title.setStyleSheet(f"font-size: 16px; font-weight: 800; color: {TEXT_HI};")
        layout.addWidget(criteria_title)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Critère évalué", "Moyenne / 5", "Nombre de réponses"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setFixedHeight(180)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {CARD};
                border: 1px solid {BORDER};
                border-radius: 10px;
                color: {TEXT_HI};
                gridline-color: {BORDER};
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 8px 12px;
                border-bottom: 1px solid {BORDER};
            }}
            QHeaderView::section {{
                background-color: {BG};
                color: {TEXT_LO};
                font-weight: 700;
                font-size: 12px;
                padding: 8px 12px;
                border: none;
                border-bottom: 1px solid {BORDER};
            }}
        """)
        layout.addWidget(self.table)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(self.table.styleSheet() + f"""
            QTableWidget {{ alternate-background-color: #f8fbff; }}
            QTableWidget::item:selected {{ background-color: #dbeafe; color: {TEXT_HI}; }}
        """)

        # ── 5. Bannière d'état ────────────────────────────────────────────────
        self.status_banner = QLabel("Chargement des résultats...")
        self.status_banner.setStyleSheet(f"""
            background-color: {CARD};
            color: {TEXT_LO};
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 10px 14px;
            font-size: 12px;
            font-weight: 500;
        """)
        layout.addWidget(self.status_banner)

        # ── 6. Bouton Fermer ──────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton("Fermer")
        close_btn.setCursor(QCursor(Qt.PointingHandCursor))
        close_btn.setFixedSize(130, 38)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BORDER};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #475569;
            }}
        """)
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _load_filters_and_data(self):
        """Remplit les listes déroulantes et charge le résultat initial."""
        criteria = CriteriaAPI.get_all()
        criteria = criteria or []
        self.criteria_names = {c.get("id"): c.get("name") for c in criteria if c.get("id")}
        parent = self.parent()
        evaluations = []
        if str(getattr(parent, "user_role", "")).upper() in {"ADMIN", "SUPER_ADMIN"}:
            evaluations = EvaluationsAPI.get_all() or []
        self._evaluations = evaluations

        self.prof_combo.blockSignals(True)
        self.prof_combo.clear()
        # Les résultats historiques peuvent concerner un professeur désormais inactif.
        profs = ProfessorsAPI.get_all() or []
        def _get_id(x):
            try:
                return int(x.get("id", 0))
            except (ValueError, TypeError):
                return 0
        if profs and any(_get_id(x) > 0 for x in profs):
            profs.sort(key=_get_id, reverse=True)
        for p in profs:
            label = f"{p.get('first_name', '')} {p.get('last_name', '')} ({p.get('department', '')})"
            self.prof_combo.addItem(label, userData=p.get("id"))
        professor_ids = {p.get("id") for p in profs}
        for professor_id in sorted({e.get("professor_id") for e in evaluations} - professor_ids):
            if professor_id:
                self.prof_combo.addItem(f"Professeur #{professor_id} (historique)", userData=professor_id)
        if self.initial_prof_id:
            idx = self.prof_combo.findData(self.initial_prof_id)
            if idx >= 0:
                self.prof_combo.setCurrentIndex(idx)
        self.prof_combo.blockSignals(False)

        self.course_combo.blockSignals(True)
        self.course_combo.clear()
        courses = CoursesAPI.get_all() or []
        self._courses = courses
        if courses and any(_get_id(x) > 0 for x in courses):
            courses.sort(key=_get_id, reverse=True)
        years = set()
        for c in courses:
            label = f"{c.get('code')} — {c.get('name')}"
            self.course_combo.addItem(label, userData=c.get("id"))
            if c.get("academic_year"):
                years.add(str(c["academic_year"]))
        course_ids = {c.get("id") for c in courses}
        for course_id in sorted({e.get("course_id") for e in evaluations} - course_ids):
            if course_id:
                self.course_combo.addItem(f"Cours #{course_id} (historique)", userData=course_id)
        if self.initial_course_id:
            idx = self.course_combo.findData(self.initial_course_id)
            if idx >= 0:
                self.course_combo.setCurrentIndex(idx)
        self.course_combo.blockSignals(False)

        # Le backend ne fournit pas de route de découverte des périodes.
        # Les comptes administrateurs peuvent les charger depuis les vraies évaluations.
        periods = sorted({str(e["period"]) for e in evaluations if e.get("period")})
        years.update(str(e["academic_year"]) for e in evaluations if e.get("academic_year"))

        self.year_combo.blockSignals(True)
        self.year_combo.clear()
        self.year_combo.addItems(sorted(years, reverse=True))
        current_course = next((c for c in courses if c.get("id") == self.course_combo.currentData()), {})
        selected_year = self.initial_year or current_course.get("academic_year", "")
        if selected_year:
            self.year_combo.setEditText(str(selected_year))
        self.year_combo.blockSignals(False)

        self.period_combo.blockSignals(True)
        self.period_combo.clear()
        period_options = sorted(set(periods) | {"Semestre 1", "Semestre 2", "Annuel"})
        self.period_combo.addItems(period_options)
        if self.initial_period:
            self.period_combo.setEditText(self.initial_period)
        elif periods:
            self.period_combo.setCurrentText(periods[0])
        else:
            self.period_combo.setCurrentText("Semestre 1")
        self.period_combo.blockSignals(False)

        errors = [
            error for error in (
                CriteriaAPI.last_error,
                ProfessorsAPI.last_error,
                CoursesAPI.last_error,
                EvaluationsAPI.last_error if str(getattr(parent, "user_role", "")).upper() in {"ADMIN", "SUPER_ADMIN"} else None,
            ) if error
        ]
        if errors:
            self.status_banner.setText("API indisponible : " + " • ".join(errors))
        elif not profs or not courses:
            self.status_banner.setText("L’API ne renvoie aucun professeur ou cours consultable.")

        self.load_results()

    def _sync_year_with_course(self):
        selected_course = self.course_combo.currentData()
        course = next(
            (item for item in self._courses if item.get("id") == selected_course),
            None,
        )
        if course and course.get("academic_year"):
            self.year_combo.setEditText(str(course["academic_year"]))
        else:
            matching = [
                item for item in self._evaluations
                if item.get("course_id") == selected_course
                and item.get("professor_id") == self.prof_combo.currentData()
            ]
            if matching:
                self.year_combo.setEditText(str(matching[0].get("academic_year", "")))
                self.period_combo.setEditText(str(matching[0].get("period", "")))
        self.load_results()

    def load_results(self):
        prof_id = self.prof_combo.currentData()
        course_id = self.course_combo.currentData()
        period = self.period_combo.currentText()
        academic_year = self.year_combo.currentText()

        if not prof_id or not course_id or not academic_year.strip() or not period.strip():
            return

        res = None
        try:
            res = ResultsAPI.get_professor_result(
                professor_id=int(prof_id),
                course_id=int(course_id),
                academic_year=academic_year,
                period=period
            )
        except Exception as e:
            print(f"[ResultsDialog] Erreur API : {e}")

        self.table.setRowCount(0)

        if res and res.get("total_reviews", 0) > 0:
            avg = float(res.get("global_average", 0.0))
            tot = int(res.get("total_reviews", 0))
            pct = int((avg / 5.0) * 100)
            col = get_score_color(avg)
            qual = get_score_label(avg).upper()

            self.score_val_lbl.setText(f"{avg:.2f} / 5")
            self.score_val_lbl.setStyleSheet(f"color: {col}; font-size: 32px; font-weight: 900;")

            self.score_label.setText(
                f"Moyenne générale · {tot} {'évaluation' if tot == 1 else 'évaluations'}"
            )
            self.badge_lbl.setText(f"  {qual}  ")
            self.badge_lbl.setStyleSheet(f"""
                background-color: {col}22;
                color: {col};
                border: 1px solid {col};
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 8px;
            """)

            self.progress_bar.setValue(pct)
            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: {BG};
                    border-radius: 4px;
                    border: none;
                }}
                QProgressBar::chunk {{
                    background-color: {col};
                    border-radius: 4px;
                }}
            """)

            self.status_banner.setText(
                f"Résultats chargés · {tot} "
                f"{'évaluation enregistrée' if tot == 1 else 'évaluations enregistrées'} pour la sélection."
            )
            self.status_banner.setStyleSheet("""
                background-color: #ecfdf5;
                color: #047857;
                border: 1px solid #a7f3d0;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 12px;
                font-weight: 600;
            """)

            crit_list = res.get("criteria", [])
            self.table.setRowCount(len(crit_list))
            for row, item in enumerate(crit_list):
                cid = item.get("criterion_id")
                c_name = self.criteria_names.get(cid) or item.get("criterion_name") or "Critère sans nom"
                c_avg = float(item.get("average", 0.0))
                c_resp = int(item.get("responses", 0))
                c_col = get_score_color(c_avg)

                it0 = QTableWidgetItem(f"  {c_name}")
                it1 = QTableWidgetItem(f"{c_avg:.2f} / 5.0")
                it1.setTextAlignment(Qt.AlignCenter)
                it1.setForeground(QColor(c_col))
                it2 = QTableWidgetItem(str(c_resp))
                it2.setTextAlignment(Qt.AlignCenter)
                it2.setForeground(QColor(TEXT_MID))

                self.table.setItem(row, 0, it0)
                self.table.setItem(row, 1, it1)
                self.table.setItem(row, 2, it2)
        else:
            self.score_val_lbl.setText("—")
            self.score_val_lbl.setStyleSheet(f"color: {TEXT_LO}; font-size: 32px; font-weight: 900;")

            self.score_label.setText("Aucune réponse pour ces filtres")
            self.badge_lbl.setText("  AUCUN AVIS  ")
            self.badge_lbl.setStyleSheet(f"""
                background-color: {BG};
                color: {TEXT_LO};
                border: 1px solid {BORDER};
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 8px;
            """)

            self.progress_bar.setValue(0)
            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: {BG};
                    border-radius: 4px;
                    border: none;
                }}
                QProgressBar::chunk {{
                    background-color: {BORDER};
                    border-radius: 4px;
                }}
            """)

            api_error = ResultsAPI.last_error or ""
            no_data = "no evaluations found" in api_error.lower() or "no answers" in api_error.lower()
            self.status_banner.setText(
                "ℹ Aucune évaluation enregistrée pour ce cours et cette période."
                if no_data or not api_error
                else f"Impossible de charger les résultats : {api_error}"
            )
            self.status_banner.setStyleSheet(f"""
                background-color: {'#fffbeb' if no_data or not api_error else '#fef2f2'};
                color: {'#92400e' if no_data or not api_error else '#b91c1c'};
                border: 1px solid {'#fcd34d' if no_data or not api_error else '#fecaca'};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 12px;
                font-weight: 500;
            """)


__all__ = ["ResultsDialog"]

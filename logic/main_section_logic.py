from pathlib import Path
import tempfile
from datetime import datetime, timezone

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QInputDialog,
    QMenu,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    from PyQt5.QtCore import QUrl
except ImportError:
    QWebEngineView = None
    QUrl = None

from api.client import api_client
from api.courses_api import CoursesAPI
from api.criteria_api import CriteriaAPI
from api.eligibility_api import EligibilityAPI
from api.evaluations_api import EvaluationsAPI
from api.professors_api import ProfessorsAPI
from logic.dialogs import ProfessorDialog, CourseDialog, CriterionDialog, EligibilityAdminDialog
from logic.results_logic import ResultsDialog
from logic.evaluation_submit_dialog import EvaluationSubmitDialog
from logic.dashboard_plotly import (
    professors_figure,
    score_distribution_figure,
    timeline_figure,
)
from logic.frameless_windows import install_drag_handle, install_size_grip
from plotly.offline import get_plotlyjs


class MainSection(QDialog):

    def __init__(self, login_window=None, user_data=None):
        super().__init__()

        ui_path = Path(__file__).resolve().parent.parent / "ui" / "main_section.ui"
        uic.loadUi(str(ui_path), self)
        self.setStyleSheet("QDialog { background: #f8fafc; color: #123b66; }")
        logo_path = Path(__file__).resolve().parent.parent / "assets" / "logo.png"
        self.setWindowIcon(QIcon(str(logo_path)))
        self.label.setPixmap(QPixmap(str(logo_path)).scaled(
            34, 34, Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        self.label.setFixedSize(38, 38)
        self.label.setToolTip("EduRate")
        # A QDialog without minimize/maximize hints can ignore window-state
        # requests on some window managers. Keep it as a normal top-level window.
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.Window
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint
        )
        self.setMinimumSize(800, 500)
        install_size_grip(self)
        self._setup_frameless_titlebar()

        self.login_window = login_window
        self.user_data = user_data or {}
        self.user_role = str(self.user_data.get("role", "")).upper()
        self.is_admin = self.user_role in {"ADMIN", "SUPER_ADMIN"}
        self.is_student = self.user_role == "STUDENT"
        self.student_allowed_pages = {
            "accueil", "professeurs", "cours", "evaluations", "eligibilites"
        }
        # La page Administration reste accessible par ses outils internes, mais
        # son bouton n'a pas sa place dans la navigation latérale.
        self.pushButton_8.hide()
        self.stack_pages = {}
        self.section_state = {}
        self.student_eligibility = None
        self.my_evaluations = []
        self.cached_professors = []
        self.cached_courses = []

        self.accueil.clicked.connect(self.open_home)
        self.pushButton_2.clicked.connect(self.open_teachers)
        self.pushButton_3.clicked.connect(self.open_courses)
        self.pushButton_4.clicked.connect(self.open_evaluations)
        self.pushButton_5.clicked.connect(self.open_results)
        self.pushButton_6.clicked.connect(self.open_eligibilities)
        self.pushButton_22.clicked.connect(self.open_criteria)
        self.pushButton_7.clicked.connect(self.open_profile)
        self.pushButton_9.clicked.connect(self.logout)

        self.sidebar_map = {
            self.accueil: "accueil",
            self.pushButton_2: "professeurs",
            self.pushButton_3: "cours",
            self.pushButton_4: "evaluations",
            self.pushButton_5: "resultats",
            self.pushButton_6: "eligibilites",
            self.pushButton_22: "criteres",
            self.pushButton_7: "profil",
        }
        self._style_sidebar()
        if self.is_student:
            self.accueil.setText("◉     Mon profil")
            for button in (
                self.pushButton_5,
                self.pushButton_7, self.pushButton_22,
            ):
                button.hide()
        self._setup_stack_pages()
        self.show_page("accueil")

        self.recent_items_model = self.eval_recentes.model()
        if self.recent_items_model is None:
            self.recent_items_model = QStandardItemModel(self.eval_recentes)
            self.eval_recentes.setModel(self.recent_items_model)

        self._display_user_name()
        self._style_dashboard()
        if self.is_student:
            self._setup_student_dashboard()
        self._setup_dashboard_charts()
        self.load_dashboard_data()

    def _setup_frameless_titlebar(self):
        self.widget_2.setStyleSheet(
            "QWidget#widget_2 { background: transparent; border: none; border-bottom: 1px solid #e2e8f0; }"
        )
        self.widget_2.layout().setContentsMargins(18, 4, 14, 4)
        self.widget_2.layout().setSpacing(12)
        self.label_2.setStyleSheet(
            "QLabel { color: #123b66; background: #eff6ff; border: 1px solid #dbeafe; "
            "border-radius: 14px; padding: 5px 12px; font-size: 12px; font-weight: 700; }"
        )
        controls = (
            (self.pushButton_12, "−", "Réduire", self._minimize_window),
            (self.pushButton_11, "□", "Agrandir / restaurer", self._toggle_maximized),
            (self.pushButton_10, "×", "Fermer", self.close),
        )
        for button, text, tooltip, callback in controls:
            button.setText(text)
            button.setToolTip(tooltip)
            button.setFixedSize(32, 30)
            button.setStyleSheet(
                "QPushButton { color: #315b82; background: transparent; border: none; "
                "border-radius: 6px; font-size: 16px; font-weight: 700; }"
                "QPushButton:hover { color: #123b66; background: #e8f1ff; }"
            )
            button.clicked.connect(callback)
        self.pushButton_10.setStyleSheet(
            self.pushButton_10.styleSheet() + "QPushButton:hover { background: #fee2e2; color: #b91c1c; }"
        )
        install_drag_handle(self, [self.widget_2, self.label, self.label_2])

    def _style_sidebar(self):
        self.widget_3.setStyleSheet("QWidget#widget_3 { background: #f8fafc; }")
        self.widget_4.setMinimumWidth(224)
        self.widget_4.setMaximumWidth(248)
        self.widget_4.setStyleSheet(
            "QWidget#widget_4 { background: #ffffff; border-right: 1px solid #e2e8f0; }"
        )
        sidebar_layout = self.widget_4.layout()
        if sidebar_layout is not None:
            sidebar_layout.setContentsMargins(14, 18, 14, 16)
            sidebar_layout.setSpacing(8)
        for layout_name in ("verticalLayout_2", "verticalLayout_3"):
            layout = getattr(self, layout_name, None)
            if layout is not None:
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(6)

        button_names = {
            "accueil": ("⌂", "Tableau de bord"),
            "pushButton_2": ("♙", "Enseignants"),
            "pushButton_3": ("▤", "Cours"),
            "pushButton_22": ("◇", "Critères"),
            "pushButton_6": ("✓", "Éligibilité"),
            "pushButton_4": ("▧", "Évaluations"),
            "pushButton_5": ("↗", "Résultats"),
            "pushButton_7": ("◉", "Mon profil"),
        }
        nav_style = (
            "QPushButton { background: transparent; color: #47627d; border: none; "
            "border-left: 3px solid transparent; border-radius: 9px; text-align: left; "
            "padding: 0 12px; font-size: 13px; font-weight: 600; }"
            "QPushButton:hover { background: #f1f6fc; color: #123b66; }"
            "QPushButton:checked { background: #eaf2ff; color: #164f91; "
            "border-left: 3px solid #3478d4; font-weight: 700; }"
            "QPushButton:pressed { background: #dbeafe; color: #123b66; }"
        )
        for name, (icon, title) in button_names.items():
            button = getattr(self, name, None)
            if button is None:
                continue
            button.setText(f"{icon}     {title}")
            button.setCheckable(True)
            button.setMinimumHeight(44)
            button.setMaximumHeight(48)
            button.setStyleSheet(nav_style)

        self.pushButton_9.setText("↪     Déconnexion")
        self.pushButton_9.setMinimumHeight(44)
        self.pushButton_9.setStyleSheet(
            "QPushButton { background: #fff7f7; color: #a33c48; border: 1px solid #fee2e2; "
            "border-radius: 9px; text-align: left; padding: 0 12px; font-size: 13px; font-weight: 700; }"
            "QPushButton:hover { background: #fee2e2; color: #8f2634; }"
        )

    def _make_brand_header(self, compact=False):
        brand = QWidget()
        layout = QHBoxLayout(brand)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(10)
        logo = QLabel()
        size = 34 if compact else 38
        logo.setFixedSize(size, size)
        logo_path = Path(__file__).resolve().parent.parent / "assets" / "logo.png"
        logo.setPixmap(QPixmap(str(logo_path)).scaled(
            size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        title = QLabel("EduRate")
        title.setStyleSheet("color: #123b66; font-size: 14px; font-weight: 800; background: transparent;")
        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addStretch(1)
        brand.setStyleSheet("background: transparent; border: none;")
        brand.setMaximumHeight(48)
        return brand

    def _toggle_maximized(self):
        if self.isMaximized() or self.isFullScreen():
            self.showNormal()
        else:
            self.showMaximized()
        self.raise_()
        self.activateWindow()

    def _minimize_window(self):
        self.showMinimized()

    def _setup_student_dashboard(self):
        """Build a personal, task-focused home screen for students."""
        for widget in (
            self.widget_7, self.widget_8, self.widget_9, self.widget_10,
            self.widget_11, self.widget_12, self.widget_13, self.widget_15, self.widget_14,
            self.label_13, self.label_14, self.label_12,
        ):
            widget.hide()
        # Remove the now-empty section headers and their spacers from the home layout.
        for index in reversed(range(self.verticalLayout_10.count())):
            item = self.verticalLayout_10.itemAt(index)
            section = item.layout()
            if section and section.objectName() in {
                "horizontalLayout_11", "horizontalLayout_14", "horizontalLayout_16", "horizontalLayout_13"
            }:
                self.verticalLayout_10.takeAt(index)

        self.label_3.setText("Mon profil")
        self.label_3.setStyleSheet("font-size: 28px; font-weight: 800; color: #123b66; background: transparent;")
        self.dashboard_subtitle.setText("Vos informations personnelles et votre espace d’évaluation.")
        name = self.user_data.get("name") or "Étudiant"
        if not self.user_data.get("name"):
            name = " ".join(part for part in (
                self.user_data.get("first_name"), self.user_data.get("last_name")
            ) if part) or name
        first_name = self.user_data.get("first_name") or name.split()[0]

        hero = QFrame(self.scrollAreaWidgetContents)
        hero.setObjectName("studentWelcomeCard")
        hero.setStyleSheet(
            "QFrame#studentWelcomeCard { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
            "stop:0 #102a56, stop:0.65 #174ea6, stop:1 #2563eb); border: none; border-radius: 18px; }"
        )
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(26, 24, 26, 24)
        hero_layout.setSpacing(18)
        welcome = QVBoxLayout()
        welcome.setSpacing(6)
        eyebrow = QLabel("PROFIL ÉTUDIANT")
        eyebrow.setStyleSheet(
            "font-size: 10px; font-weight: 800; letter-spacing: 1px; "
            "color: #93c5fd; background: transparent; border: none;"
        )
        greeting = QLabel(f"Bonjour, {first_name}")
        greeting.setWordWrap(True)
        greeting.setStyleSheet(
            "font-size: 26px; font-weight: 800; color: white; "
            "background: transparent; border: none;"
        )
        description = QLabel("Consultez vos informations et partagez votre expérience pédagogique.")
        description.setWordWrap(True)
        description.setStyleSheet(
            "font-size: 13px; color: #dbeafe; background: transparent; border: none;"
        )
        welcome.addWidget(eyebrow)
        welcome.addWidget(greeting)
        welcome.addWidget(description)
        hero_layout.addLayout(welcome, 1)

        action = QPushButton("Commencer une évaluation  ›")
        action.setCursor(Qt.PointingHandCursor)
        action.setMinimumHeight(48)
        action.setStyleSheet(
            "QPushButton { background: white; color: #164f91; border: none; border-radius: 10px; "
            "padding: 0 18px; font-size: 13px; font-weight: 700; }"
            "QPushButton:hover { background: #dbeafe; }"
        )
        action.clicked.connect(self._start_student_evaluation)
        hero_layout.addWidget(action, 0, Qt.AlignVCenter)
        self.verticalLayout_10.insertWidget(2, hero)
        self.student_welcome_card = hero
        self.student_evaluate_button = action

        info = QFrame(self.scrollAreaWidgetContents)
        info.setObjectName("studentInfoCard")
        info.setStyleSheet("QFrame#studentInfoCard { background: white; border: 1px solid #e2e8f0; border-radius: 14px; }")
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(22, 20, 22, 22)
        info_layout.setSpacing(14)
        heading = QLabel("Mes informations")
        heading.setStyleSheet("font-size: 17px; font-weight: 700; color: #123b66;")
        info_layout.addWidget(heading)
        fields = QGridLayout()
        fields.setHorizontalSpacing(12)
        fields.setVerticalSpacing(10)
        details = [
            ("Adresse e-mail", self.user_data.get("email")),
            ("Matricule", self.user_data.get("matricule")),
            ("Faculté", self.user_data.get("faculty") or self.user_data.get("department")),
            ("Programme", self.user_data.get("program") or self.user_data.get("study_program")),
        ]
        visible_details = [(label, value) for label, value in details if value]
        if not visible_details:
            visible_details = [("Nom du compte", name)]
        for index, (label, value) in enumerate(visible_details):
            cell = QFrame()
            cell.setStyleSheet("QFrame { background: #f8fafc; border: 1px solid #edf2f7; border-radius: 9px; }")
            cell_layout = QVBoxLayout(cell)
            cell_layout.setContentsMargins(13, 10, 13, 10)
            cell_layout.setSpacing(4)
            caption = QLabel(label.upper())
            caption.setStyleSheet("font-size: 10px; font-weight: 700; color: #64748b; background: transparent; border: none;")
            value_label = QLabel(str(value))
            value_label.setWordWrap(True)
            value_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #123b66; background: transparent; border: none;")
            cell_layout.addWidget(caption)
            cell_layout.addWidget(value_label)
            fields.addWidget(cell, index // 2, index % 2)
        info_layout.addLayout(fields)
        self.verticalLayout_10.insertWidget(3, info)
        self.student_info_card = info

        steps = QFrame(self.scrollAreaWidgetContents)
        steps.setObjectName("studentStepsCard")
        steps.setStyleSheet("QFrame#studentStepsCard { background: white; border: 1px solid #e2e8f0; border-radius: 14px; }")
        steps_layout = QVBoxLayout(steps)
        steps_layout.setContentsMargins(22, 18, 22, 18)
        steps_layout.setSpacing(10)
        steps_title = QLabel("Comment participer")
        steps_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #123b66;")
        steps_layout.addWidget(steps_title)
        guidance = QLabel("1. Choisissez un professeur et un cours     ·     2. Notez chaque critère     ·     3. Envoyez votre avis")
        guidance.setWordWrap(True)
        guidance.setStyleSheet("font-size: 12px; color: #456b8f; background: transparent;")
        steps_layout.addWidget(guidance)

        shortcuts = QFrame(self.scrollAreaWidgetContents)
        shortcuts.setObjectName("studentShortcutsCard")
        shortcuts.setStyleSheet("QFrame#studentShortcutsCard { background: white; border: 1px solid #e2e8f0; border-radius: 14px; }")
        shortcuts_layout = QVBoxLayout(shortcuts)
        shortcuts_layout.setContentsMargins(22, 18, 22, 18)
        shortcuts_layout.setSpacing(12)
        shortcuts_title = QLabel("Mon espace étudiant")
        shortcuts_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #123b66;")
        shortcuts_layout.addWidget(shortcuts_title)
        shortcuts_row = QHBoxLayout()
        shortcuts_row.setSpacing(10)
        for label, callback in (
            ("Consulter les professeurs", self.open_teachers),
            ("Parcourir les cours", self.open_courses),
            ("Vérifier mon éligibilité", self.open_eligibilities),
        ):
            button = QPushButton(label)
            button.setCursor(Qt.PointingHandCursor)
            button.setMinimumHeight(42)
            button.setStyleSheet(
                "QPushButton { background: #f8fbff; color: #123b66; border: 1px solid #dbe5f0; "
                "border-radius: 9px; padding: 0 14px; font-size: 12px; font-weight: 700; }"
                "QPushButton:hover { background: #eff6ff; border-color: #93c5fd; }"
            )
            button.clicked.connect(callback)
            shortcuts_row.addWidget(button)
        shortcuts_layout.addLayout(shortcuts_row)
        self.verticalLayout_10.insertWidget(4, shortcuts)
        self.student_shortcuts_card = shortcuts
        self.verticalLayout_10.insertWidget(5, steps)

    def _style_dashboard(self):
        """Build a distinct, spacious analytics dashboard from the real API data."""
        self.widget_6.setStyleSheet("background: #f3f6fb; color: #123b66;")
        self.scrollArea.setStyleSheet(
            "QScrollArea { border: none; background: #f3f6fb; }"
            "QScrollArea > QWidget > QWidget { background: #f3f6fb; }"
        )
        self.scrollAreaWidgetContents.setStyleSheet("background: #f3f6fb;")
        content_layout = self.verticalLayout_10
        content_layout.setContentsMargins(28, 22, 28, 32)
        content_layout.setSpacing(20)

        header_layout = self.horizontalLayout_9
        while header_layout.count():
            header_layout.takeAt(0)
        header_layout.setContentsMargins(0, 0, 0, 0)
        if not self.is_student:
            for index in reversed(range(content_layout.count())):
                if content_layout.itemAt(index).layout() is header_layout:
                    content_layout.takeAt(index)

            hero = QFrame(self.scrollAreaWidgetContents)
            hero.setObjectName("dashboardHero")
            hero.setStyleSheet(
                "QFrame#dashboardHero { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
                "stop:0 #102a56, stop:0.65 #174ea6, stop:1 #2563eb); border: none; border-radius: 18px; }"
            )
            hero_layout = QHBoxLayout(hero)
            hero_layout.setContentsMargins(26, 20, 24, 20)
            hero_layout.setSpacing(18)
            hero_copy = QVBoxLayout()
            hero_copy.setSpacing(6)
            eyebrow = QLabel("VUE D’ENSEMBLE")
            eyebrow.setStyleSheet("color: #93c5fd; font-size: 10px; font-weight: 800; letter-spacing: 1px; background: transparent;")
            self.label_3.setText("Pilotage des évaluations")
            self.label_3.setStyleSheet("font-size: 28px; font-weight: 800; color: white; background: transparent;")
            subtitle = QLabel("Suivez les retours et l’activité académique depuis un seul espace.")
            subtitle.setStyleSheet("font-size: 13px; color: #dbeafe; background: transparent;")
            self.dashboard_subtitle = subtitle
            hero_copy.addWidget(eyebrow)
            hero_copy.addWidget(self.label_3)
            hero_copy.addWidget(subtitle)
            hero_layout.addLayout(hero_copy, 1)

            badge = QFrame()
            badge.setStyleSheet("QFrame { background: rgba(255,255,255,24); border: 1px solid rgba(255,255,255,55); border-radius: 14px; }")
            badge_layout = QVBoxLayout(badge)
            badge_layout.setContentsMargins(18, 12, 18, 12)
            badge_layout.setSpacing(3)
            badge_value = QLabel("API")
            badge_value.setStyleSheet("color: white; font-size: 20px; font-weight: 900; background: transparent;")
            badge_caption = QLabel("SOURCE DES DONNÉES")
            badge_caption.setStyleSheet("color: #dbeafe; font-size: 9px; font-weight: 800; letter-spacing: 1px; background: transparent;")
            badge_layout.addWidget(badge_value, 0, Qt.AlignCenter)
            badge_layout.addWidget(badge_caption, 0, Qt.AlignCenter)
            hero_layout.addWidget(badge, 0, Qt.AlignVCenter)
            content_layout.insertWidget(0, hero)
        else:
            self.label_3.setText("Mon profil")
            self.label_3.setStyleSheet("font-size: 28px; font-weight: 800; color: #123b66; background: transparent;")
            header_layout.addWidget(self.label_3)
            header_layout.addStretch(1)
            subtitle = QLabel("Vos informations personnelles et votre espace d’évaluation.")
            subtitle.setStyleSheet("font-size: 13px; color: #426789; background: transparent;")
            self.dashboard_subtitle = subtitle
            content_layout.insertWidget(1, subtitle)

        self.horizontalLayout_10.setSpacing(14)
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.label_11.setText("Note moyenne / 5")
        card_colors = {
            "widget_7": "#3478d4",
            "widget_8": "#21a6a1",
            "widget_9": "#7279d8",
            "widget_10": "#e19a45",
        }
        for name, accent in card_colors.items():
            card = getattr(self, name)
            card.setMinimumHeight(124)
            card.setMaximumHeight(124)
            if card.layout() is not None:
                card.layout().setContentsMargins(18, 14, 18, 14)
                card.layout().setSpacing(6)
            card.setStyleSheet(
                f"QWidget#{name} {{ background: white; border: 1px solid #e2e8f0; "
                f"border-top: 4px solid {accent}; border-radius: 15px; }}"
            )
            value_label, title_label = card.findChildren(QLabel)
            value_label.setStyleSheet("font-size: 33px; font-weight: 800; color: #123b66; background: transparent; border: none;")
            title_label.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {accent}; background: transparent; border: none;")
            title_label.setText(title_label.text().upper())

        self.label_13.setText("Analyse des résultats")
        self.label_14.setText("Activité dans le temps")
        self.label_12.setText("Dernières évaluations")
        for heading in (self.label_13, self.label_14, self.label_12):
            heading.setStyleSheet("font-size: 16px; font-weight: 800; color: #123b66; background: transparent;")
        self.widget_11.setMinimumHeight(360)
        self.widget_15.setMinimumHeight(350)
        self.widget_15.setMaximumHeight(350)
        self.widget_14.setStyleSheet("QWidget#widget_14 { background: white; border: 1px solid #e1e8f1; border-radius: 15px; }")
        self.widget_14.setMinimumHeight(210)
        self.widget_14.setMaximumHeight(250)
        self.eval_recentes.setMinimumHeight(190)
        self.eval_recentes.setStyleSheet(
            "QListView { background: transparent; border: none; padding: 8px; color: #315b82; font-size: 13px; }"
            "QListView::item { padding: 10px 8px; border-bottom: 1px solid #edf2f7; }"
            "QListView::item:selected { background: #eaf2ff; color: #164f91; }"
        )

    def _setup_dashboard_charts(self):
        # setHtml() embeds its content in a data URL, which is too large for
        # Plotly's bundled JavaScript. Serve each chart from a local HTML file.
        self.dashboard_html_dir = tempfile.TemporaryDirectory(prefix="professor-evaluation-charts-")
        self.dashboard_html_path = Path(self.dashboard_html_dir.name)
        (self.dashboard_html_path / "plotly.min.js").write_text(get_plotlyjs(), encoding="utf-8")
        self.dashboard_chart_views = []
        self.dashboard_chart_notices = []
        self.dashboard_chart_containers = [self.widget_12, self.widget_13, self.widget_15]
        for container in self.dashboard_chart_containers:
            container.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 12px;")
            if container.layout() is None:
                layout = QVBoxLayout(container)
                layout.setContentsMargins(4, 4, 4, 4)
            else:
                layout = container.layout()
            layout.setContentsMargins(6, 6, 6, 6)
            if QWebEngineView is None:
                notice = QLabel("Installez PyQtWebEngine pour afficher les graphiques Plotly.")
                notice.setAlignment(Qt.AlignCenter)
                notice.setStyleSheet("color: #64748b; padding: 16px; background: white; border: none;")
                layout.addWidget(notice)
                self.dashboard_chart_notices.append(notice)
                self.dashboard_chart_views.append(None)
                continue
            view = QWebEngineView(container)
            view.setMinimumHeight(280)
            layout.addWidget(view)
            self.dashboard_chart_notices.append(None)
            self.dashboard_chart_views.append(view)

    def _render_dashboard_charts(self, evaluations, professors):
        if not self.is_admin:
            for view, notice in zip(self.dashboard_chart_views, self.dashboard_chart_notices):
                if view is not None:
                    view.setHtml("<html><body style='font:16px Arial;color:#64748b;text-align:center;padding:40px'>Statistiques accessibles aux administrateurs uniquement.</body></html>")
                elif notice is not None:
                    notice.setText("Statistiques accessibles aux administrateurs uniquement.")
            return
        if evaluations is None:
            message = "Impossible de récupérer les évaluations depuis l’API."
            for view, notice in zip(self.dashboard_chart_views, self.dashboard_chart_notices):
                if view is not None:
                    view.setHtml(f"<html><body style='font:16px Arial;color:#64748b;text-align:center;padding:40px'>{message}</body></html>")
                elif notice is not None:
                    notice.setText(message)
            return
        for notice in self.dashboard_chart_notices:
            if notice is not None:
                notice.setText("Installez PyQtWebEngine pour afficher les graphiques Plotly.")
        figures = [
            professors_figure(evaluations, professors or []),
            score_distribution_figure(evaluations),
            timeline_figure(evaluations),
        ]
        if QWebEngineView is None:
            return
        for view, figure in zip(self.dashboard_chart_views, figures):
            if view is None:
                continue
            html = figure.to_html(
                full_html=True, include_plotlyjs="directory",
                config={"responsive": True, "displayModeBar": False},
            )
            chart_path = self.dashboard_html_path / f"dashboard_chart_{self.dashboard_chart_views.index(view)}.html"
            chart_path.write_text(html, encoding="utf-8")
            view.load(QUrl.fromLocalFile(str(chart_path)))

    def _build_table_page(self, name, title, subtitle, columns, add_label):
        page = QWidget()
        page.setObjectName(name)
        page.setStyleSheet("background-color: rgb(248, 250, 252);")

        root_layout = QVBoxLayout(page)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(16)
        root_layout.addWidget(self._make_brand_header())

        header = QLabel(title)
        header.setStyleSheet("font-size: 30px; font-weight: bold; color: rgb(15, 23, 42);")
        root_layout.addWidget(header)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("font-size: 13px; color: rgb(71, 85, 105);")
        root_layout.addWidget(subtitle_label)

        has_crud_actions = self.is_admin and name in {"professeurs", "cours", "criteres"}

        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        search_input = QLineEdit()
        search_input.setPlaceholderText("Rechercher...")
        search_input.setStyleSheet(
            "QLineEdit { border: 1px solid #cbd5e1; border-radius: 10px; padding: 10px 12px; background: white; color: #0f172a; }"
        )
        search_input.textChanged.connect(lambda query, page_name=name: self._on_search(page_name, query))
        top_bar.addWidget(search_input, 1)

        add_button = QPushButton(f"+ {add_label}")
        add_button.setStyleSheet(
            "QPushButton { background-color: #2563eb; color: white; border: none; border-radius: 10px; padding: 10px 16px; font-weight: bold; }"
        )
        add_button.clicked.connect(lambda: self._on_add_clicked(name))
        top_bar.addWidget(add_button)

        root_layout.addLayout(top_bar)

        table = QTableWidget()
        display_columns = list(columns) + (["Actions"] if has_crud_actions else [])
        table.setColumnCount(len(display_columns))
        table.setHorizontalHeaderLabels(display_columns)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(table.SelectRows)
        table.setEditTriggers(table.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(60 if has_crud_actions else 40)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        if has_crud_actions:
            actions_column = len(display_columns) - 1
            table.horizontalHeader().setSectionResizeMode(actions_column, QHeaderView.Fixed)
            table.setColumnWidth(actions_column, 104)
        table.setStyleSheet(
            "QTableWidget { background: white; border: 1px solid #e2e8f0; border-radius: 12px; color: #0f172a; }"
            "QHeaderView::section { background: #e2e8f0; color: #0f172a; padding: 8px; border: none; font-weight: bold; }"
            "QTableWidget::item { padding: 10px; border-bottom: 1px solid #e2e8f0; }"
        )
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(lambda pos, page_name=name: self._table_menu(page_name, pos))
        root_layout.addWidget(table)

        nav_layout = QHBoxLayout()
        nav_layout.addStretch()

        prev_btn = QPushButton("Précédent")
        prev_btn.setStyleSheet("QPushButton { background-color: #e2e8f0; color: #0f172a; border-radius: 8px; padding: 8px 14px; }")
        prev_btn.clicked.connect(lambda: self._change_page(name, -1))
        nav_layout.addWidget(prev_btn)

        page_label = QLabel("Page 1")
        page_label.setAlignment(Qt.AlignCenter)
        page_label.setStyleSheet("color: #0f172a; font-weight: bold;")
        nav_layout.addWidget(page_label)

        next_btn = QPushButton("Suivant")
        next_btn.setStyleSheet("QPushButton { background-color: #0f172a; color: white; border-radius: 8px; padding: 8px 14px; }")
        next_btn.clicked.connect(lambda: self._change_page(name, 1))
        nav_layout.addWidget(next_btn)
        nav_layout.addStretch()
        root_layout.addLayout(nav_layout)

        self.section_state[name] = {
            "page": 1,
            "page_size": 8,
            "query": "",
            "table": table,
            "page_label": page_label,
            "search_input": search_input,
            "add_button": add_button,
            "columns": display_columns,
            "data_columns": columns,
            "has_crud_actions": has_crud_actions,
            "fetch_data": None,
            "row_mapper": None,
        }

        return page

    def _register_page(self, name, title, subtitle, columns, add_label, fetch_data, row_mapper):
        if self.is_student and name == "evaluations":
            page = self._build_student_evaluation_page()
            self.stackedWidget.addWidget(page)
            self.stack_pages[name] = page
            return

        page = self._build_table_page(name, title, subtitle, columns, add_label)
        self.stackedWidget.addWidget(page)
        self.stack_pages[name] = page
        self.section_state[name]["fetch_data"] = fetch_data
        self.section_state[name]["row_mapper"] = row_mapper
        add_button = self.section_state[name]["add_button"]
        add_button.setVisible(
            (self.is_admin and name in {"professeurs", "cours", "criteres", "eligibilites"})
            or (self.user_role == "STUDENT" and name == "evaluations")
        )
        if self.is_student and name == "evaluations":
            add_button.setText("＋ Évaluer un professeur")
        elif self.is_admin and name == "eligibilites":
            add_button.setText("＋ Gérer une fiche étudiant")
        if not self.is_student or name in self.student_allowed_pages:
            self._refresh_table_data(name)

    def _build_student_evaluation_page(self):
        page = QWidget()
        page.setObjectName("studentEvaluationPage")
        page.setStyleSheet("QWidget#studentEvaluationPage { background: #f4f7fb; }")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.addWidget(self._make_brand_header())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(6, 6, 6, 6)
        content_layout.setSpacing(0)

        self.student_evaluation_form = EvaluationSubmitDialog(self, embedded=True)
        self.student_evaluation_form.evaluationSubmitted.connect(self._on_student_evaluation_submitted)
        self.student_evaluation_form.requestEligibility.connect(self.open_eligibilities)
        content_layout.addWidget(self.student_evaluation_form)

        history_card = QFrame()
        history_card.setObjectName("studentEvaluationHistory")
        history_card.setStyleSheet(
            "QFrame#studentEvaluationHistory { background: white; border: 1px solid #dbe5f0; border-radius: 14px; }"
        )
        history_layout = QVBoxLayout(history_card)
        history_layout.setContentsMargins(18, 16, 18, 18)
        history_layout.setSpacing(8)
        history_title = QLabel("Mes évaluations envoyées")
        history_title.setStyleSheet("font-size: 16px; font-weight: 800; color: #123b66;")
        history_note = QLabel(
            "Cette liste affiche les envois effectués depuis votre connexion actuelle. "
            "L’API ne permet pas de récupérer l’historique étudiant des sessions précédentes."
        )
        history_note.setWordWrap(True)
        history_note.setStyleSheet("font-size: 11px; color: #647b94;")
        history_layout.addWidget(history_title)
        history_layout.addWidget(history_note)

        self.student_session_table = QTableWidget(0, 5)
        self.student_session_table.setHorizontalHeaderLabels(
            ["Professeur", "Cours", "Année", "Période", "Envoyée le"]
        )
        self.student_session_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.student_session_table.verticalHeader().setVisible(False)
        self.student_session_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.student_session_table.setMinimumHeight(150)
        self.student_session_table.setStyleSheet(
            "QTableWidget { background: #fff; border: 1px solid #e2e8f0; border-radius: 9px; color: #123b66; }"
            "QHeaderView::section { background: #f4f8fc; color: #456b8f; padding: 8px; border: none; font-weight: 700; }"
            "QTableWidget::item { padding: 8px; border-bottom: 1px solid #edf2f7; }"
        )
        history_layout.addWidget(self.student_session_table)
        content_layout.addWidget(history_card)
        self._refresh_student_session_history()

        content_layout.addStretch(1)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
        return page

    def _on_student_evaluation_submitted(self, evaluation):
        self.my_evaluations.append(evaluation)
        self._refresh_student_session_history()
        self.load_dashboard_data()

    def _refresh_student_session_history(self):
        table = getattr(self, "student_session_table", None)
        if table is None:
            return
        evaluations = self._newest_evaluations_first(self.my_evaluations)
        table.setRowCount(max(1, len(evaluations)))
        if not evaluations:
            table.setItem(0, 0, QTableWidgetItem("Aucune évaluation envoyée pendant cette connexion."))
            for column in range(1, table.columnCount()):
                table.setItem(0, column, QTableWidgetItem(""))
            return
        for row, evaluation in enumerate(evaluations):
            submitted = evaluation.get("submitted_at") or evaluation.get("created_at") or "À l’instant"
            if isinstance(submitted, str) and len(submitted) >= 10:
                submitted = submitted[:10]
            values = (
                evaluation.get("professor_name") or self._evaluation_professor_name(evaluation),
                evaluation.get("course_name") or self._evaluation_course_name(evaluation),
                evaluation.get("academic_year", "—"),
                evaluation.get("period", "—"),
                submitted,
            )
            for column, value in enumerate(values):
                table.setItem(row, column, QTableWidgetItem(str(value)))

    def _on_search(self, name, query):
        if name in self.section_state:
            self.section_state[name]["query"] = query
            self.section_state[name]["page"] = 1
            self._refresh_table_data(name)

    def _change_page(self, name, delta):
        if name not in self.section_state:
            return
        state = self.section_state[name]
        total_pages = state.get("total_pages", 1)
        state["page"] = max(1, min(total_pages, state["page"] + delta))
        self._refresh_table_data(name)

    def _on_add_clicked(self, name):
        if name == "evaluations" and self.user_role == "STUDENT":
            self.show_page("evaluations")
            return
        if not self.is_admin:
            QMessageBox.warning(self, "Accès refusé", "Cette action est réservée aux administrateurs.")
            return
        dialogs = {"professeurs": ProfessorDialog, "cours": CourseDialog, "criteres": CriterionDialog}
        dialog_type = dialogs.get(name)
        if dialog_type:
            if dialog_type(self).exec_() == QDialog.Accepted:
                self._refresh_table_data(name)
                self.load_dashboard_data()
        elif name == "eligibilites":
            student_id, ok = QInputDialog.getInt(self, "Éligibilité étudiant", "ID de l’étudiant :", 1, 1)
            if ok:
                EligibilityAdminDialog(self, student_id=student_id).exec_()

    def _refresh_table_data(self, name):
        if name not in self.section_state:
            return
        if self.is_student and name not in self.student_allowed_pages:
            return

        state = self.section_state[name]
        table = state["table"]
        fetch_data = state.get("fetch_data")
        row_mapper = state.get("row_mapper")
        query = state.get("query", "").strip().lower()

        items = fetch_data() if fetch_data else []
        if items is None:
            message = getattr(self, "_last_data_message", None)
            if not message:
                for api in (ProfessorsAPI, CoursesAPI, CriteriaAPI, EvaluationsAPI, EligibilityAPI):
                    if api.last_error:
                        message = api.last_error
                        break
            table.setRowCount(1)
            table.setColumnCount(len(state["columns"]))
            for col in range(len(state["columns"])):
                table.setItem(0, col, QTableWidgetItem((message or "Données indisponibles.") if col == 0 else ""))
            state["total_pages"] = 1
            state["page_label"].setText("Données indisponibles")
            return
        items = self._newest_records_first(items)
        filtered = []

        for item in items:
            text = " ".join(str(value) for value in row_mapper(item)).lower()
            if query in text:
                filtered.append(item)

        state["total_pages"] = max(1, (len(filtered) + state["page_size"] - 1) // state["page_size"])
        page = max(1, min(state["page"], state["total_pages"]))
        state["page"] = page

        start = (page - 1) * state["page_size"]
        end = start + state["page_size"]
        visible_items = filtered[start:end]
        state["visible_items"] = visible_items

        table.setRowCount(len(visible_items))
        table.setColumnCount(len(state["columns"]))
        if not visible_items:
            table.setRowCount(1)
            if query:
                empty_text = "Aucun résultat pour cette recherche."
            elif self.is_student and name == "evaluations":
                empty_text = "L’API ne fournit pas l’historique des anciennes évaluations. Vos nouvelles soumissions apparaîtront ici."
            elif self.is_admin and name == "eligibilites":
                empty_text = "Aucune liste disponible. Utilisez « Gérer une fiche étudiant » pour ouvrir une fiche par ID."
            else:
                empty_text = "Aucune donnée disponible dans l’API."
            table.setItem(0, 0, QTableWidgetItem(empty_text))
            for col in range(1, table.columnCount()):
                table.setItem(0, col, QTableWidgetItem(""))
            state["page_label"].setText(f"Page {page} / {state['total_pages']}")
            return
        for row_index, item in enumerate(visible_items):
            values = row_mapper(item)
            for col_index, value in enumerate(values):
                table.setItem(row_index, col_index, QTableWidgetItem(str(value)))
            if state.get("has_crud_actions"):
                table.setCellWidget(
                    row_index,
                    len(state["data_columns"]),
                    self._make_crud_actions(name, item),
                )

        state["page_label"].setText(f"Page {page} / {state['total_pages']}")

    def _setup_stack_pages(self):
        self.stack_pages.clear()

        home_page = self.stackedWidget.widget(0)
        home_page.setObjectName("accueil")
        # Garder le profil étudiant dans le même thème clair bleu que ses cartes
        # et le contenu du dashboard (l'ancien beige créait une rupture visible).
        home_page.setStyleSheet("background-color: #f3f6fb; color: #123b66;")
        if home_page.layout() is not None:
            home_page.layout().insertWidget(0, self._make_brand_header())
        self.stack_pages["accueil"] = home_page

        self._register_page(
            "professeurs",
            "Professeurs",
            "Consultez les professeurs disponibles avant de choisir qui évaluer."
            if self.is_student else "Gestion des professeurs et leur suivi.",
            ["Nom", "Département", "Grade", "Statut"],
            "Professeur",
            self._get_professors_for_table,
            lambda item: [
                f"{item.get('first_name', '')} {item.get('last_name', '')}".strip() or item.get("name", "-"),
                item.get("department", "-"),
                item.get("grade", "-"),
                item.get("status", item.get("active", "-")),
            ],
        )

        self._register_page(
            "cours",
            "Cours",
            "Parcourez les cours pour sélectionner celui de votre évaluation."
            if self.is_student else "Catalogue des cours et modules universitaires.",
            ["Code", "Nom", "Département", "Année"],
            "Cours",
            self._get_courses_for_table,
            lambda item: [
                item.get("code", "-"),
                item.get("name", "-"),
                item.get("department", "-"),
                item.get("academic_year", "-"),
            ],
        )

        self._register_page(
            "evaluations",
            "Évaluations" if self.is_admin else "Soumettre une évaluation",
            "Consultation des évaluations soumises." if self.is_admin else "Vos évaluations soumises pendant cette session.",
            ["Professeur", "Cours", "Année", "Période", "Soumise le"],
            "Évaluation",
            self._get_evaluations,
            lambda item: [
                self._evaluation_professor_name(item),
                self._evaluation_course_name(item),
                item.get("academic_year", "-"),
                item.get("period", "-"),
                str(item.get("submitted_at") or item.get("created_at") or "-")[:10],
            ],
        )

        self._register_page(
            "resultats",
            "Résultats",
            "Synthèse des moyennes et résultats.",
            ["Professeur", "Cours", "Année", "Période", "Moyenne"],
            "Résultat",
            lambda: [],
            lambda item: [
                item.get("professor_id", "-"),
                item.get("course_id", "-"),
                item.get("academic_year", "-"),
                item.get("period", "-"),
                item.get("global_average", "-"),
            ],
        )

        self._register_page(
            "eligibilites",
            "Éligibilités",
            "Gérez une fiche d’étudiant depuis le bouton dédié. L’API ne fournit pas la liste des fiches."
            if self.is_admin else "Consultez votre statut et les conditions nécessaires pour évaluer.",
            ["Étudiant", "Inscription", "Frais académiques", "Frais de laboratoire", "Frais d’accès"],
            "Éligibilité",
            lambda: [] if self.is_admin else self._get_my_eligibility(),
            lambda item: [
                self._eligibility_student_name(item),
                "Oui" if item.get("enrollment") else "Non",
                "Oui" if item.get("academic_fees") else "Non",
                "Oui" if item.get("laboratory_fees") else "Non",
                "Oui" if item.get("access_fees") else "Non",
            ],
        )

        self._register_page(
            "criteres",
            "Critères",
            "Paramétrage des critères d’évaluation.",
            ["Nom", "Description", "Score max", "Actif"],
            "Critère",
            lambda: self._fetch_api(CriteriaAPI, CriteriaAPI.get_all),
            lambda item: [
                item.get("name", "-"),
                item.get("description", "-"),
                item.get("max_score", "-"),
                "Oui" if item.get("active") else "Non",
            ],
        )

        self._register_page(
            "profil",
            "Profil",
            "Informations et préférences du compte.",
            ["Champ", "Valeur"],
            "Profil",
            lambda: [
                {"field": "Nom", "value": self.user_data.get("name", "Utilisateur")},
                {"field": "Email", "value": self.user_data.get("email", "-")},
                {"field": "Rôle", "value": self.user_data.get("role", "-")},
                {"field": "Matricule", "value": self.user_data.get("matricule", "-")},
            ],
            lambda item: [item.get("field", "-"), item.get("value", "-")],
        )

        self._register_page(
            "admin",
            "Administration",
            "L’API ne fournit pas de route de gestion des comptes utilisateurs.",
            ["Nom", "Email", "Rôle", "Statut"],
            "Utilisateur",
            lambda: [],
            lambda item: [
                item.get("name", "-"),
                item.get("email", "-"),
                item.get("role", "-"),
                item.get("status", "-"),
            ],
        )
        admin_table = self.section_state["admin"]["table"]
        admin_table.setRowCount(1)
        admin_table.setItem(0, 0, QTableWidgetItem("Gestion des comptes absente de l’API"))
        for col in range(1, admin_table.columnCount()):
            admin_table.setItem(0, col, QTableWidgetItem("—"))

    def show_page(self, page_name: str):
        if self.is_student and page_name not in self.student_allowed_pages:
            return
        if page_name in self.stack_pages:
            self.stackedWidget.setCurrentWidget(self.stack_pages[page_name])
            for button, mapped_page in self.sidebar_map.items():
                button.setChecked(mapped_page == page_name)
            if page_name in {"professeurs", "cours", "evaluations", "eligibilites", "criteres"}:
                self._refresh_table_data(page_name)

    def _display_user_name(self):
        user_name = self.user_data.get("name") or self.user_data.get("email") or "Utilisateur"
        if hasattr(self, "label_2"):
            self.label_2.setText(user_name)

    def _set_label_text(self, label_name: str, value: str):
        label = getattr(self, label_name, None)
        if label is not None:
            label.setText(value)

    def load_dashboard_data(self):
        try:
            if self.is_admin:
                professors = ProfessorsAPI.get_active()
                courses = CoursesAPI.get_all()
                evaluations = EvaluationsAPI.get_all()
            else:
                professors, courses, evaluations = [], [], []

            self._render_dashboard_charts(evaluations, professors)

            self._set_label_text("label_4", str(len(professors)) if professors is not None else "—")
            self._set_label_text("label_6", str(len(courses)) if courses is not None else "—")
            self._set_label_text("label_8", str(len(evaluations)) if evaluations is not None else "—")
            professors = professors or []
            courses = courses or []
            evaluations = evaluations or []
            scores = [
                int(answer["score"])
                for evaluation in evaluations
                for answer in evaluation.get("answers", [])
                if isinstance(answer, dict) and answer.get("score") is not None
            ]
            if scores:
                self._set_label_text("label_10", f"{sum(scores) / len(scores):.2f}")
            else:
                self._set_label_text("label_10", "—")

            if self.is_admin and EvaluationsAPI.last_error and not evaluations:
                self.recent_items_model.clear()
                self.recent_items_model.appendRow(QStandardItem(f"API indisponible : {EvaluationsAPI.last_error}"))
            elif evaluations:
                model = self.recent_items_model
                model.clear()
                professor_names = {
                    item.get("id"): f"{item.get('first_name', '')} {item.get('last_name', '')}".strip()
                    for item in professors
                }
                course_names = {item.get("id"): item.get("name", "") for item in courses}
                for evaluation in self._newest_evaluations_first(evaluations)[:8]:
                    professor_id = evaluation.get("professor_id", "?")
                    course_id = evaluation.get("course_id", "?")
                    submitted_at = evaluation.get("submitted_at", "")
                    date_value = submitted_at[:10] if isinstance(submitted_at, str) and len(submitted_at) >= 10 else submitted_at
                    professor_name = professor_names.get(professor_id) or f"Professeur #{professor_id}"
                    course_name = course_names.get(course_id) or f"Cours #{course_id}"
                    item_text = f"{professor_name} • {course_name} • {date_value}"
                    item = QStandardItem(item_text)
                    item.setEditable(False)
                    item.setToolTip(item_text)
                    model.appendRow(item)
            elif self.is_student:
                self.recent_items_model.clear()
                self.recent_items_model.appendRow(QStandardItem("Vos informations sont affichées dans l’accueil et le profil."))
            else:
                self.recent_items_model.clear()
                self.recent_items_model.appendRow(QStandardItem("Aucune évaluation récente."))

        except Exception as exc:
            print(f"Erreur de chargement du dashboard: {exc}")
            QMessageBox.warning(
                self,
                "Dashboard",
                "Impossible de charger les statistiques depuis l'API."
            )

    def open_home(self):
        self.show_page("accueil")

    def open_teachers(self):
        self.show_page("professeurs")

    def open_courses(self):
        self.show_page("cours")

    def open_evaluations(self):
        self.show_page("evaluations")

    def open_results(self):
        if self.is_student:
            return
        ResultsDialog(self).exec_()

    def _start_student_evaluation(self):
        self.show_page("evaluations")
        if hasattr(self, "student_evaluation_form"):
            self.student_evaluation_form.professor.setFocus()

    def open_eligibilities(self):
        self.show_page("eligibilites")

    def open_criteria(self):
        self.show_page("criteres")

    def open_profile(self):
        self.show_page("accueil" if self.is_student else "profil")

    def open_admin(self):
        if self.is_admin:
            self.show_page("admin")

    def logout(self):
        response = QMessageBox.question(
            self,
            "Déconnexion",
            "Voulez-vous vraiment vous déconnecter ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if response == QMessageBox.Yes:
            api_client.clear_token()
            QMessageBox.information(self, "Déconnexion", "Déconnexion réussie.")
            self.close()

            if self.login_window is not None:
                self.login_window.login_email_input.setText("")
                self.login_window.login_password_input.setText("")
                self.login_window.showMaximized()
                self.login_window.raise_()
                self.login_window.activateWindow()

    def _get_my_eligibility(self):
        student_id = self.user_data.get("id")
        if not student_id:
            self._last_data_message = "L’identifiant étudiant manque dans la session de connexion."
            return None
        result = EligibilityAPI.check(student_id)
        if result:
            self._last_data_message = None
            return [result]
        if "not found" in (EligibilityAPI.last_error or "").lower():
            self._last_data_message = "Aucune fiche d’éligibilité enregistrée. Contactez l’administration."
        else:
            self._last_data_message = EligibilityAPI.last_error or "Impossible de charger l’éligibilité."
        return None

    def _get_evaluations(self):
        if self.is_student:
            self._last_data_message = None
            return self._newest_evaluations_first(self.my_evaluations)
        if not self.is_admin:
            self._last_data_message = "Consultation réservée à l’administration."
            return None
        evaluations = self._fetch_api(EvaluationsAPI, EvaluationsAPI.get_all)
        return self._newest_evaluations_first(evaluations) if evaluations is not None else None

    @staticmethod
    def _newest_evaluations_first(evaluations):
        """Sort submitted evaluations by their real submission timestamp."""
        return MainSection._newest_records_first(evaluations)

    @staticmethod
    def _newest_records_first(records):
        """Sort all API-backed tables newest-first, falling back to descending IDs."""
        def sort_key(record):
            if not isinstance(record, dict):
                return (0, float("-inf"), float("-inf"))
            value = next((record.get(field) for field in (
                "submitted_at", "created_at", "updated_at", "date"
            ) if record.get(field)), None)
            if isinstance(value, datetime):
                parsed = value
            elif isinstance(value, (int, float)):
                return (1, float(value), MainSection._numeric_id(record.get("id")))
            elif isinstance(value, str) and value.strip():
                try:
                    parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
                except ValueError:
                    parsed = None
            else:
                parsed = None
            if parsed is not None:
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                return (1, parsed.timestamp(), MainSection._numeric_id(record.get("id")))
            return (0, float("-inf"), MainSection._numeric_id(record.get("id")))

        return sorted(records, key=sort_key, reverse=True)

    @staticmethod
    def _numeric_id(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return float("-inf")

    def _get_professors_for_table(self):
        request = ProfessorsAPI.get_active if self.is_student else ProfessorsAPI.get_all
        professors = self._fetch_api(ProfessorsAPI, request)
        if professors is not None:
            self.cached_professors = professors
        return professors

    def _get_courses_for_table(self):
        courses = self._fetch_api(CoursesAPI, CoursesAPI.get_all)
        if courses is not None:
            self.cached_courses = courses
        return courses

    @staticmethod
    def _related_name(record, relation, name_keys, fallback):
        related = record.get(relation)
        if isinstance(related, str) and related.strip():
            return related.strip()
        if isinstance(related, dict):
            label = " ".join(str(related.get(key, "")).strip() for key in name_keys if related.get(key))
            if label:
                return label
        direct = record.get(f"{relation}_name")
        return direct.strip() if isinstance(direct, str) and direct.strip() else fallback

    def _evaluation_professor_name(self, evaluation):
        fallback = self._related_name(evaluation, "professor", ("first_name", "last_name", "name"), "—")
        if fallback != "—":
            return fallback
        professor_id = evaluation.get("professor_id")
        professor = next((item for item in self.cached_professors if self._same_id(item.get("id"), professor_id)), None)
        if professor:
            return " ".join(part for part in (professor.get("first_name"), professor.get("last_name")) if part) or professor.get("name", "—")
        return "—"

    def _evaluation_course_name(self, evaluation):
        fallback = self._related_name(evaluation, "course", ("code", "name"), "—")
        if fallback != "—":
            return fallback
        course_id = evaluation.get("course_id")
        course = next((item for item in self.cached_courses if self._same_id(item.get("id"), course_id)), None)
        return f"{course.get('code', '')} — {course.get('name', '')}".strip(" —") if course else "—"

    @staticmethod
    def _same_id(left, right):
        return left is not None and right is not None and str(left) == str(right)

    def _eligibility_student_name(self, eligibility):
        student = eligibility.get("student")
        if isinstance(student, dict):
            name = " ".join(part for part in (student.get("first_name"), student.get("last_name")) if part)
            if name:
                return name
            if student.get("name"):
                return student["name"]
        if eligibility.get("student_name"):
            return eligibility["student_name"]
        if self._same_id(eligibility.get("student_id"), self.user_data.get("id")):
            return self.user_data.get("name") or " ".join(
                part for part in (self.user_data.get("first_name"), self.user_data.get("last_name")) if part
            ) or "Mon profil"
        return "—"

    def _fetch_api(self, api, request):
        result = request()
        self._last_data_message = api.last_error if result is None else None
        return result

    def _make_crud_actions(self, page_name, entry):
        actions = QWidget()
        layout = QHBoxLayout(actions)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)
        edit = QPushButton("✎")
        edit.setToolTip("Modifier cet élément")
        edit.setAccessibleName("Modifier")
        edit.setStyleSheet(
            "QPushButton { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; "
            "border-radius: 16px; padding: 0; font-size: 17px; font-weight: 700; }"
            "QPushButton:hover { background: #dbeafe; border-color: #93c5fd; }"
        )
        edit.setFixedSize(32, 32)
        delete = QPushButton("×")
        delete.setToolTip("Supprimer cet élément")
        delete.setAccessibleName("Supprimer")
        delete.setStyleSheet(
            "QPushButton { background: #fff1f2; color: #be123c; border: 1px solid #fecdd3; "
            "border-radius: 16px; padding: 0; font-size: 21px; font-weight: 500; }"
            "QPushButton:hover { background: #ffe4e6; border-color: #fda4af; }"
        )
        delete.setFixedSize(32, 32)
        edit.clicked.connect(lambda _checked=False, name=page_name, record=entry: self._edit_record(name, record))
        delete.clicked.connect(lambda _checked=False, name=page_name, record=entry: self._delete_record(name, record))
        layout.addWidget(edit)
        layout.addWidget(delete)
        return actions

    def _edit_record(self, page_name, entry):
        if not self.is_admin:
            return
        dialog_type = {
            "professeurs": ProfessorDialog,
            "cours": CourseDialog,
            "criteres": CriterionDialog,
        }.get(page_name)
        if dialog_type and dialog_type(self, entry).exec_() == QDialog.Accepted:
            self._refresh_table_data(page_name)
            self.load_dashboard_data()

    def _delete_record(self, page_name, entry):
        if not self.is_admin:
            return
        api, label = {
            "professeurs": (ProfessorsAPI, "ce professeur"),
            "cours": (CoursesAPI, "ce cours"),
            "criteres": (CriteriaAPI, "ce critère"),
        }.get(page_name, (None, None))
        if api is None:
            return
        answer = QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"Voulez-vous vraiment supprimer {label} ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        if api.delete(entry.get("id")):
            self._refresh_table_data(page_name)
            self.load_dashboard_data()
        else:
            QMessageBox.warning(self, "Erreur", api.last_error or "Suppression impossible.")

    def _table_menu(self, page_name, position):
        state = self.section_state.get(page_name)
        if not state or not self.is_admin or page_name not in {"professeurs", "cours", "criteres"}:
            return
        table = state["table"]
        row = table.rowAt(position.y())
        if row < 0:
            return
        visible_items = state.get("visible_items", [])
        if row >= len(visible_items):
            return
        entry = visible_items[row]
        menu = QMenu(self)
        edit_action = menu.addAction("Modifier")
        delete_action = menu.addAction("Supprimer")
        selected = menu.exec_(table.viewport().mapToGlobal(position))
        if selected == edit_action:
            self._edit_record(page_name, entry)
        elif selected == delete_action:
            self._delete_record(page_name, entry)

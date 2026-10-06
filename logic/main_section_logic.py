from pathlib import Path

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
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
    QVBoxLayout,
    QWidget,
)

from api.client import api_client
from api.courses_api import CoursesAPI
from api.criteria_api import CriteriaAPI
from api.eligibility_api import EligibilityAPI
from api.evaluations_api import EvaluationsAPI, ResultsAPI
from api.professors_api import ProfessorsAPI


class MainSection(QDialog):

    def __init__(self, login_window=None, user_data=None):
        super().__init__()

        ui_path = Path(__file__).resolve().parent.parent / "ui" / "main_section.ui"
        uic.loadUi(str(ui_path), self)

        self.login_window = login_window
        self.user_data = user_data or {}
        self.stack_pages = {}
        self.section_state = {}

        self.accueil.clicked.connect(self.open_home)
        self.pushButton_2.clicked.connect(self.open_teachers)
        self.pushButton_3.clicked.connect(self.open_courses)
        self.pushButton_4.clicked.connect(self.open_evaluations)
        self.pushButton_5.clicked.connect(self.open_results)
        self.pushButton_6.clicked.connect(self.open_eligibilities)
        self.pushButton_22.clicked.connect(self.open_criteria)
        self.pushButton_7.clicked.connect(self.open_profile)
        self.pushButton_8.clicked.connect(self.open_admin)
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
            self.pushButton_8: "admin",
        }
        self._bind_sidebar_actions()

        self._setup_stack_pages()
        self.show_page("accueil")

        self.recent_items_model = self.eval_recentes.model()
        if self.recent_items_model is None:
            self.recent_items_model = QStandardItemModel(self.eval_recentes)
            self.eval_recentes.setModel(self.recent_items_model)

        self._display_user_name()
        self.load_dashboard_data()

    def _build_table_page(self, name, title, subtitle, columns, add_label):
        page = QWidget()
        page.setObjectName(name)
        page.setStyleSheet("background-color: rgb(248, 250, 252);")

        root_layout = QVBoxLayout(page)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(16)

        header = QLabel(title)
        header.setStyleSheet("font-size: 30px; font-weight: bold; color: rgb(15, 23, 42);")
        root_layout.addWidget(header)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("font-size: 13px; color: rgb(71, 85, 105);")
        root_layout.addWidget(subtitle_label)

        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        search_input = QLineEdit()
        search_input.setPlaceholderText("Rechercher...")
        search_input.setStyleSheet(
            "QLineEdit { border: 1px solid #cbd5e1; border-radius: 10px; padding: 10px 12px; background: white; color: #0f172a; }"
        )
        search_input.textChanged.connect(lambda query, page_name=name: self._on_search(page_name, query))
        top_bar.addWidget(search_input)

        add_button = QPushButton(f"+ {add_label}")
        add_button.setStyleSheet(
            "QPushButton { background-color: #2563eb; color: white; border: none; border-radius: 10px; padding: 10px 16px; font-weight: bold; }"
        )
        add_button.clicked.connect(lambda: self._on_add_clicked(name))
        top_bar.addWidget(add_button)

        root_layout.addLayout(top_bar)

        table = QTableWidget()
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(table.SelectRows)
        table.setEditTriggers(table.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setStyleSheet(
            "QTableWidget { background: white; border: 1px solid #e2e8f0; border-radius: 12px; color: #0f172a; }"
            "QHeaderView::section { background: #e2e8f0; color: #0f172a; padding: 8px; border: none; font-weight: bold; }"
            "QTableWidget::item { padding: 10px; border-bottom: 1px solid #e2e8f0; }"
        )
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
            "columns": columns,
            "fetch_data": None,
            "row_mapper": None,
        }

        return page

    def _register_page(self, name, title, subtitle, columns, add_label, fetch_data, row_mapper):
        page = self._build_table_page(name, title, subtitle, columns, add_label)
        self.stack_pages[name] = page
        self.section_state[name]["fetch_data"] = fetch_data
        self.section_state[name]["row_mapper"] = row_mapper
        self._refresh_table_data(name)

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
        QMessageBox.information(self, "Ajouter", f"Ajout dans {name} à venir.")

    def _refresh_table_data(self, name):
        if name not in self.section_state:
            return

        state = self.section_state[name]
        table = state["table"]
        fetch_data = state.get("fetch_data")
        row_mapper = state.get("row_mapper")
        query = state.get("query", "").strip().lower()

        items = fetch_data() if fetch_data else []
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

        table.setRowCount(len(visible_items))
        table.setColumnCount(len(state["columns"]))
        for row_index, item in enumerate(visible_items):
            values = row_mapper(item)
            for col_index, value in enumerate(values):
                table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

        state["page_label"].setText(f"Page {page} / {state['total_pages']}")

    def _setup_stack_pages(self):
        self.stack_pages.clear()

        home_page = self.stackedWidget.widget(0)
        home_page.setObjectName("accueil")
        home_page.setStyleSheet("background-color: rgb(246, 245, 244);")
        self.stack_pages["accueil"] = home_page

        self._register_page(
            "professeurs",
            "Professeurs",
            "Gestion des professeurs et leur suivi.",
            ["ID", "Nom", "Département", "Grade", "Statut"],
            "Professeur",
            lambda: ProfessorsAPI.get_all() or [],
            lambda item: [
                item.get("id", "-"),
                f"{item.get('first_name', '')} {item.get('last_name', '')}".strip() or item.get("name", "-"),
                item.get("department", "-"),
                item.get("grade", "-"),
                item.get("status", item.get("active", "-")),
            ],
        )

        self._register_page(
            "cours",
            "Cours",
            "Catalogue des cours et modules universitaires.",
            ["ID", "Code", "Nom", "Département", "Année"],
            "Cours",
            lambda: CoursesAPI.get_all() or [],
            lambda item: [
                item.get("id", "-"),
                item.get("code", "-"),
                item.get("name", "-"),
                item.get("department", "-"),
                item.get("academic_year", "-"),
            ],
        )

        self._register_page(
            "evaluations",
            "Évaluations",
            "Liste des évaluations soumises et suivies.",
            ["ID", "Professeur", "Cours", "Année", "Période"],
            "Évaluation",
            lambda: EvaluationsAPI.get_all() or [],
            lambda item: [
                item.get("id", "-"),
                item.get("professor_id", "-"),
                item.get("course_id", "-"),
                item.get("academic_year", "-"),
                item.get("period", "-"),
            ],
        )

        self._register_page(
            "resultats",
            "Résultats",
            "Synthèse des moyennes et résultats.",
            ["Professeur", "Cours", "Année", "Période", "Moyenne"],
            "Résultat",
            lambda: [
                {"professor_id": 1, "course_id": 1, "academic_year": "2024-2025", "period": "semester", "global_average": 4.5},
                {"professor_id": 2, "course_id": 2, "academic_year": "2024-2025", "period": "semester", "global_average": 4.1},
            ],
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
            "Vérification et suivi d’éligibilité des étudiants.",
            ["Étudiant", "Inscription", "Frais acad.", "Lab.", "Accès"],
            "Éligibilité",
            lambda: [
                {"student_id": 101, "enrollment": True, "academic_fees": True, "laboratory_fees": False, "access_fees": True},
                {"student_id": 102, "enrollment": False, "academic_fees": True, "laboratory_fees": True, "access_fees": False},
            ],
            lambda item: [
                item.get("student_id", "-"),
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
            ["ID", "Nom", "Description", "Score max", "Actif"],
            "Critère",
            lambda: CriteriaAPI.get_all() or [],
            lambda item: [
                item.get("id", "-"),
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
            "Supervision globale du système et des utilisateurs.",
            ["Nom", "Email", "Rôle", "Statut"],
            "Utilisateur",
            lambda: [
                {"name": "Admin principal", "email": "admin@school.com", "role": "ADMIN", "status": "Actif"},
                {"name": "Équipe evaluation", "email": "eval@school.com", "role": "SUPER_ADMIN", "status": "Actif"},
            ],
            lambda item: [
                item.get("name", "-"),
                item.get("email", "-"),
                item.get("role", "-"),
                item.get("status", "-"),
            ],
        )

    def show_page(self, page_name: str):
        if page_name in self.stack_pages:
            self.stackedWidget.setCurrentWidget(self.stack_pages[page_name])

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
            professors = ProfessorsAPI.get_all() or []
            courses = CoursesAPI.get_all() or []
            evaluations = EvaluationsAPI.get_all() or []

            self._set_label_text("label_4", str(len(professors)))
            self._set_label_text("label_6", str(len(courses)))
            self._set_label_text("label_8", str(len(evaluations)))

            if evaluations:
                model = self.recent_items_model
                model.clear()
                for evaluation in sorted(evaluations, key=lambda item: item.get("submitted_at", ""), reverse=True)[:8]:
                    professor_id = evaluation.get("professor_id", "?")
                    course_id = evaluation.get("course_id", "?")
                    submitted_at = evaluation.get("submitted_at", "")
                    date_value = submitted_at[:10] if isinstance(submitted_at, str) and len(submitted_at) >= 10 else submitted_at
                    item_text = f"Prof {professor_id} • Cours {course_id} • {date_value}"
                    item = QStandardItem(item_text)
                    item.setEditable(False)
                    item.setToolTip(item_text)
                    model.appendRow(item)
            else:
                self.recent_items_model.clear()
                self.recent_items_model.appendRow(QStandardItem("Aucune évaluation récente."))

            if professors:
                first_professor = professors[0]
                professor_id = first_professor.get("id")
                if professor_id is not None:
                    result = ResultsAPI.get_professor_result(
                        professor_id=professor_id,
                        course_id=first_professor.get("course_id", 1),
                        academic_year="2024-2025",
                        period="semester",
                    )
                    if result:
                        avg = result.get("global_average", 0)
                        self._set_label_text("label_10", f"{avg:.2f}")

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
        self.show_page("resultats")

    def open_eligibilities(self):
        self.show_page("eligibilites")

    def open_criteria(self):
        self.show_page("criteres")

    def open_profile(self):
        self.show_page("profil")

    def open_admin(self):
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
                self.login_window.show()
                self.login_window.raise_()
                self.login_window.activateWindow()

    def _bind_sidebar_actions(self):
        for button, page_name in self.sidebar_map.items():
            if button is not None:
                button.clicked.connect(lambda checked=False, target=page_name: self.show_page(target))

"""
Design sobre, corporate et adaptatif des pages de gestion CRUD.
- Page 1 : Gestion des Professeurs (page_2)
- Page 2 : Catalogue des Cours (page_3)
- Page 3 : Critères d'Évaluation (page_4)

Thème Dark Slate unifié (#0f172a, #1e293b, #334155).
Adaptation dynamique à toute résolution d'écran sans troncature.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QTableView,
    QHeaderView, QFrame, QSizePolicy, QHBoxLayout
)

# ─── Palette Sobre & Épurée ───────────────────────────────────────────────────
BG         = "#0f172a"
CARD       = "#1e293b"
CARD_ALT   = "#162032"
BORDER     = "#334155"
BORDER_ROW = "#243247"
BLUE       = "#3b82f6"
BLUE_HOVER = "#2563eb"
BLUE_PRESS = "#1d4ed8"
GREEN      = "#34d399"
RED        = "#f87171"
TEXT_HI    = "#f8fafc"
TEXT_MID   = "#cbd5e1"
TEXT_LO    = "#94a3b8"
TEXT_MUTED = "#64748b"

TABLE_STYLE = f"""
QTableView {{
    background-color: {CARD};
    alternate-background-color: {CARD_ALT};
    color: {TEXT_HI};
    gridline-color: {BORDER_ROW};
    border: 1px solid {BORDER};
    border-radius: 8px;
    selection-background-color: {BLUE_PRESS};
    selection-color: #ffffff;
    font-size: 13px;
    outline: none;
}}
QTableView::item {{
    padding: 6px 12px;
    border-bottom: 1px solid {BORDER_ROW};
}}
QTableView::item:selected {{
    background-color: {BLUE_PRESS};
    color: #ffffff;
}}
QHeaderView::section {{
    background-color: {BG};
    color: {TEXT_LO};
    padding: 10px 12px;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border: none;
    border-bottom: 2px solid {BORDER};
    border-right: 1px solid {BORDER_ROW};
}}
QScrollBar:vertical {{
    border: none;
    background: {BG};
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: #475569;
    min-height: 24px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical:hover {{
    background: #64748b;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    border: none;
    background: {BG};
    height: 8px;
    margin: 0px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: #475569;
    min-width: 24px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal:hover {{
    background: #64748b;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}
"""

INPUT_STYLE = f"""
QLineEdit {{
    background-color: {CARD};
    color: {TEXT_HI};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 13px;
    selection-background-color: {BLUE};
}}
QLineEdit:focus {{
    border: 1px solid {BLUE};
    background-color: {CARD};
}}
QLineEdit::placeholder {{
    color: {TEXT_MUTED};
}}
"""

PRIMARY_BTN_STYLE = f"""
QPushButton {{
    background-color: {BLUE};
    color: #ffffff;
    font-weight: 600;
    font-size: 13px;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
}}
QPushButton:hover {{
    background-color: {BLUE_HOVER};
}}
QPushButton:pressed {{
    background-color: {BLUE_PRESS};
}}
"""

PAGINATION_BTN_STYLE = f"""
QPushButton {{
    background-color: {CARD};
    color: {TEXT_HI};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 500;
}}
QPushButton:hover:enabled {{
    background-color: {BORDER};
    border-color: #475569;
}}
QPushButton:pressed:enabled {{
    background-color: #273549;
}}
QPushButton:disabled {{
    background-color: {BG};
    color: {TEXT_MUTED};
    border-color: {CARD};
}}
"""

MENU_STYLE = f"""
QMenu {{
    background-color: {CARD};
    color: {TEXT_HI};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 4px;
}}
QMenu::item {{
    padding: 8px 24px;
    border-radius: 4px;
    font-size: 13px;
}}
QMenu::item:selected {{
    background-color: {BLUE};
    color: #ffffff;
}}
QMenu::separator {{
    height: 1px;
    background-color: {BORDER};
    margin: 4px 0px;
}}
"""


class CRUDPagesDesigner:
    """
    Configure et modernise l'affichage des 3 pages de gestion :
    Professeurs, Cours et Critères.
    """

    def __init__(self, main_window):
        self.mw = main_window

    def setup(self):
        """Initialise le design complet des 3 pages CRUD."""
        self._setup_professors_page()
        self._setup_courses_page()
        self._setup_criteria_page()

    def _setup_professors_page(self):
        """Page 1 : Gestion des Professeurs (page_2)"""
        mw = self.mw

        # Conteneurs et fonds
        if hasattr(mw, "page_2"):
            mw.page_2.setStyleSheet(f"background-color: {BG};")
        if hasattr(mw, "widget_16"):
            mw.widget_16.setStyleSheet(f"background-color: {BG}; border: none;")
        if hasattr(mw, "scrollArea_2"):
            mw.scrollArea_2.setStyleSheet("background-color: transparent; border: none;")
            mw.scrollArea_2.setFrameShape(QFrame.NoFrame)
            mw.scrollArea_2.setWidgetResizable(True)
        if hasattr(mw, "scrollAreaWidgetContents_2"):
            mw.scrollAreaWidgetContents_2.setStyleSheet(f"background-color: {BG};")

        # Marges de layout
        if hasattr(mw, "verticalLayout_11"):
            mw.verticalLayout_11.setContentsMargins(28, 20, 28, 16)
            mw.verticalLayout_11.setSpacing(14)

        # Header
        if hasattr(mw, "horizontalSpacer_11"):
            mw.horizontalSpacer_11.changeSize(0, 0, QSizePolicy.Fixed, QSizePolicy.Fixed)
        if hasattr(mw, "label_15"):
            mw.label_15.setText("Gestion des Enseignants")
            mw.label_15.setStyleSheet(
                f"color: {TEXT_HI}; font-size: 20px; font-weight: 700; letter-spacing: -0.3px;"
            )

        # Barre de recherche & Action
        if hasattr(mw, "lineEdit"):
            mw.lineEdit.setStyleSheet(INPUT_STYLE)
            mw.lineEdit.setPlaceholderText("Rechercher par nom, matricule, département, grade...")
            mw.lineEdit.setMinimumHeight(38)
            mw.lineEdit.setMinimumWidth(320)
            mw.lineEdit.setMaximumWidth(450)

        if hasattr(mw, "pushButton"):
            mw.pushButton.setText("+ Nouveau professeur")
            mw.pushButton.setStyleSheet(PRIMARY_BTN_STYLE)
            mw.pushButton.setMinimumHeight(38)
            mw.pushButton.setCursor(Qt.PointingHandCursor)

        # Tableau
        if hasattr(mw, "widget_17"):
            mw.widget_17.setStyleSheet("background-color: transparent; border: none;")
            mw.widget_17.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            mw.widget_17.setMinimumHeight(240)
            mw.widget_17.setMaximumHeight(16777215)
            if mw.widget_17.layout():
                mw.widget_17.layout().setContentsMargins(0, 0, 0, 0)

        if hasattr(mw, "tableView"):
            self._configure_table(mw.tableView)

        # Barre de pagination
        if hasattr(mw, "widget_18"):
            mw.widget_18.setStyleSheet("background-color: transparent; border: none;")
            mw.widget_18.setMaximumHeight(50)

        # Boutons pagination
        if hasattr(mw, "pushButton_14"):
            mw.pushButton_14.setText("← Précédent")
            mw.pushButton_14.setStyleSheet(PAGINATION_BTN_STYLE)
            mw.pushButton_14.setMinimumHeight(34)
            mw.pushButton_14.setCursor(Qt.PointingHandCursor)

        if hasattr(mw, "pushButton_13"):
            mw.pushButton_13.setText("Suivant →")
            mw.pushButton_13.setStyleSheet(PAGINATION_BTN_STYLE)
            mw.pushButton_13.setMinimumHeight(34)
            mw.pushButton_13.setCursor(Qt.PointingHandCursor)

        # Label d'information de pagination
        if hasattr(mw, "horizontalLayout_22") and not hasattr(mw, "prof_page_label"):
            mw.prof_page_label = QLabel("Page 1 sur 1", mw.widget_18)
            mw.prof_page_label.setStyleSheet(
                f"color: {TEXT_LO}; font-size: 13px; font-weight: 500; padding: 0 10px;"
            )
            # Insérer avant le bouton Précédent
            idx = mw.horizontalLayout_22.indexOf(mw.pushButton_14)
            if idx >= 0:
                mw.horizontalLayout_22.insertWidget(idx, mw.prof_page_label)
            else:
                mw.horizontalLayout_22.addWidget(mw.prof_page_label)

    def _setup_courses_page(self):
        """Page 2 : Catalogue des Cours (page_3)"""
        mw = self.mw

        # Conteneurs et fonds
        if hasattr(mw, "page_3"):
            mw.page_3.setStyleSheet(f"background-color: {BG};")
        if hasattr(mw, "widget_19"):
            mw.widget_19.setStyleSheet(f"background-color: {BG}; border: none;")
        if hasattr(mw, "scrollArea_3"):
            mw.scrollArea_3.setStyleSheet("background-color: transparent; border: none;")
            mw.scrollArea_3.setFrameShape(QFrame.NoFrame)
            mw.scrollArea_3.setWidgetResizable(True)
        if hasattr(mw, "scrollAreaWidgetContents_3"):
            mw.scrollAreaWidgetContents_3.setStyleSheet(f"background-color: {BG};")

        # Marges de layout
        if hasattr(mw, "verticalLayout_12"):
            mw.verticalLayout_12.setContentsMargins(28, 20, 28, 16)
            mw.verticalLayout_12.setSpacing(14)

        # Header
        if hasattr(mw, "horizontalSpacer_15"):
            mw.horizontalSpacer_15.changeSize(0, 0, QSizePolicy.Fixed, QSizePolicy.Fixed)
        if hasattr(mw, "label_16"):
            mw.label_16.setText("Catalogue des Cours")
            mw.label_16.setStyleSheet(
                f"color: {TEXT_HI}; font-size: 20px; font-weight: 700; letter-spacing: -0.3px;"
            )

        # Barre de recherche & Action
        if hasattr(mw, "lineEdit_2"):
            mw.lineEdit_2.setStyleSheet(INPUT_STYLE)
            mw.lineEdit_2.setPlaceholderText("Rechercher par code, intitulé, département...")
            mw.lineEdit_2.setMinimumHeight(38)
            mw.lineEdit_2.setMinimumWidth(320)
            mw.lineEdit_2.setMaximumWidth(450)

        if hasattr(mw, "pushButton_15"):
            mw.pushButton_15.setText("+ Nouveau cours")
            mw.pushButton_15.setStyleSheet(PRIMARY_BTN_STYLE)
            mw.pushButton_15.setMinimumHeight(38)
            mw.pushButton_15.setCursor(Qt.PointingHandCursor)

        # Tableau
        if hasattr(mw, "widget_20"):
            mw.widget_20.setStyleSheet("background-color: transparent; border: none;")
            mw.widget_20.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            mw.widget_20.setMinimumHeight(240)
            mw.widget_20.setMaximumHeight(16777215)
            if mw.widget_20.layout():
                mw.widget_20.layout().setContentsMargins(0, 0, 0, 0)

        if hasattr(mw, "tableView_2"):
            self._configure_table(mw.tableView_2)

        # Barre de pagination
        if hasattr(mw, "widget_21"):
            mw.widget_21.setStyleSheet("background-color: transparent; border: none;")
            mw.widget_21.setMaximumHeight(50)

        if hasattr(mw, "pushButton_16"):
            mw.pushButton_16.setText("← Précédent")
            mw.pushButton_16.setStyleSheet(PAGINATION_BTN_STYLE)
            mw.pushButton_16.setMinimumHeight(34)
            mw.pushButton_16.setCursor(Qt.PointingHandCursor)

        if hasattr(mw, "pushButton_17"):
            mw.pushButton_17.setText("Suivant →")
            mw.pushButton_17.setStyleSheet(PAGINATION_BTN_STYLE)
            mw.pushButton_17.setMinimumHeight(34)
            mw.pushButton_17.setCursor(Qt.PointingHandCursor)

        if hasattr(mw, "horizontalLayout_29") and not hasattr(mw, "course_page_label"):
            mw.course_page_label = QLabel("Page 1 sur 1", mw.widget_21)
            mw.course_page_label.setStyleSheet(
                f"color: {TEXT_LO}; font-size: 13px; font-weight: 500; padding: 0 10px;"
            )
            idx = mw.horizontalLayout_29.indexOf(mw.pushButton_16)
            if idx >= 0:
                mw.horizontalLayout_29.insertWidget(idx, mw.course_page_label)
            else:
                mw.horizontalLayout_29.addWidget(mw.course_page_label)

    def _setup_criteria_page(self):
        """Page 3 : Critères d'Évaluation (page_4)"""
        mw = self.mw

        # Conteneurs et fonds
        if hasattr(mw, "page_4"):
            mw.page_4.setStyleSheet(f"background-color: {BG};")
        if hasattr(mw, "widget_22"):
            mw.widget_22.setStyleSheet(f"background-color: {BG}; border: none;")
        if hasattr(mw, "scrollArea_4"):
            mw.scrollArea_4.setStyleSheet("background-color: transparent; border: none;")
            mw.scrollArea_4.setFrameShape(QFrame.NoFrame)
            mw.scrollArea_4.setWidgetResizable(True)
        if hasattr(mw, "scrollAreaWidgetContents_4"):
            mw.scrollAreaWidgetContents_4.setStyleSheet(f"background-color: {BG};")

        # Marges de layout
        if hasattr(mw, "verticalLayout_13"):
            mw.verticalLayout_13.setContentsMargins(28, 20, 28, 16)
            mw.verticalLayout_13.setSpacing(14)

        # Header
        if hasattr(mw, "horizontalSpacer_19"):
            mw.horizontalSpacer_19.changeSize(0, 0, QSizePolicy.Fixed, QSizePolicy.Fixed)
        if hasattr(mw, "label_17"):
            mw.label_17.setText("Critères d'Évaluation")
            mw.label_17.setStyleSheet(
                f"color: {TEXT_HI}; font-size: 20px; font-weight: 700; letter-spacing: -0.3px;"
            )

        # Barre de recherche & Action
        if hasattr(mw, "lineEdit_3"):
            mw.lineEdit_3.setStyleSheet(INPUT_STYLE)
            mw.lineEdit_3.setPlaceholderText("Rechercher par nom de critère, description...")
            mw.lineEdit_3.setMinimumHeight(38)
            mw.lineEdit_3.setMinimumWidth(320)
            mw.lineEdit_3.setMaximumWidth(450)

        if hasattr(mw, "pushButton_18"):
            mw.pushButton_18.setText("+ Nouveau critère")
            mw.pushButton_18.setStyleSheet(PRIMARY_BTN_STYLE)
            mw.pushButton_18.setMinimumHeight(38)
            mw.pushButton_18.setCursor(Qt.PointingHandCursor)

        # Tableau
        if hasattr(mw, "widget_23"):
            mw.widget_23.setStyleSheet("background-color: transparent; border: none;")
            mw.widget_23.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            mw.widget_23.setMinimumHeight(240)
            mw.widget_23.setMaximumHeight(16777215)
            if mw.widget_23.layout():
                mw.widget_23.layout().setContentsMargins(0, 0, 0, 0)

        if hasattr(mw, "tableView_3"):
            self._configure_table(mw.tableView_3)

        # Barre de pagination
        if hasattr(mw, "widget_24"):
            mw.widget_24.setStyleSheet("background-color: transparent; border: none;")
            mw.widget_24.setMaximumHeight(50)

        if hasattr(mw, "pushButton_19"):
            mw.pushButton_19.setText("← Précédent")
            mw.pushButton_19.setStyleSheet(PAGINATION_BTN_STYLE)
            mw.pushButton_19.setMinimumHeight(34)
            mw.pushButton_19.setCursor(Qt.PointingHandCursor)

        if hasattr(mw, "pushButton_20"):
            mw.pushButton_20.setText("Suivant →")
            mw.pushButton_20.setStyleSheet(PAGINATION_BTN_STYLE)
            mw.pushButton_20.setMinimumHeight(34)
            mw.pushButton_20.setCursor(Qt.PointingHandCursor)

        if hasattr(mw, "horizontalLayout_35") and not hasattr(mw, "criteria_page_label"):
            mw.criteria_page_label = QLabel("Page 1 sur 1", mw.widget_24)
            mw.criteria_page_label.setStyleSheet(
                f"color: {TEXT_LO}; font-size: 13px; font-weight: 500; padding: 0 10px;"
            )
            idx = mw.horizontalLayout_35.indexOf(mw.pushButton_19)
            if idx >= 0:
                mw.horizontalLayout_35.insertWidget(idx, mw.criteria_page_label)
            else:
                mw.horizontalLayout_35.addWidget(mw.criteria_page_label)

    def _configure_table(self, table_view: QTableView):
        """Applique les styles et comportements unifiés à un QTableView."""
        table_view.setStyleSheet(TABLE_STYLE)
        table_view.setSelectionBehavior(QTableView.SelectRows)
        table_view.setSelectionMode(QTableView.SingleSelection)
        table_view.setEditTriggers(QTableView.NoEditTriggers)
        table_view.setAlternatingRowColors(True)
        table_view.setShowGrid(False)
        table_view.setWordWrap(False)
        table_view.setMinimumHeight(240)
        table_view.setMaximumHeight(16777215)
        table_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        table_view.verticalHeader().setVisible(False)
        table_view.verticalHeader().setDefaultSectionSize(40)

        header = table_view.horizontalHeader()
        header.setStretchLastSection(True)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def setup_prof_header_columns(self, table_view: QTableView):
        """Définit les largeurs et modes de redimensionnement des colonnes professeurs."""
        header = table_view.horizontalHeader()
        if header is None or header.count() < 7:
            return
        try:
            header.setSectionResizeMode(QHeaderView.Interactive)
            header.resizeSection(0, 50)   # ID
            header.resizeSection(1, 110)  # Matricule
            header.resizeSection(2, 220)  # Nom complet
            header.resizeSection(3, 220)  # Email
            header.resizeSection(4, 160)  # Département
            header.resizeSection(5, 130)  # Grade
            header.resizeSection(6, 100)  # Statut
            header.setSectionResizeMode(2, QHeaderView.Stretch)
            header.setSectionResizeMode(3, QHeaderView.Stretch)
        except Exception:
            pass

    def setup_course_header_columns(self, table_view: QTableView):
        """Définit les largeurs et modes de redimensionnement des colonnes cours."""
        header = table_view.horizontalHeader()
        if header is None or header.count() < 6:
            return
        try:
            header.setSectionResizeMode(QHeaderView.Interactive)
            header.resizeSection(0, 50)   # ID
            header.resizeSection(1, 100)  # Code
            header.resizeSection(2, 240)  # Nom
            header.resizeSection(3, 160)  # Département
            header.resizeSection(4, 130)  # Année
            header.resizeSection(5, 200)  # Description
            header.setSectionResizeMode(2, QHeaderView.Stretch)
            header.setSectionResizeMode(5, QHeaderView.Stretch)
        except Exception:
            pass

    def setup_criteria_header_columns(self, table_view: QTableView):
        """Définit les largeurs et modes de redimensionnement des colonnes critères."""
        header = table_view.horizontalHeader()
        if header is None or header.count() < 5:
            return
        try:
            header.setSectionResizeMode(QHeaderView.Interactive)
            header.resizeSection(0, 50)   # ID
            header.resizeSection(1, 240)  # Nom
            header.resizeSection(2, 260)  # Description
            header.resizeSection(3, 110)  # Barème
            header.resizeSection(4, 100)  # Statut
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.Stretch)
        except Exception:
            pass

"""
navbar_sidebar.py
─────────────────
Design professionnel pour la barre de titre (navbar) et la sidebar
de navigation — thème Dark Slate Corporate.

Structure UI :
  widget_2   → navbar / barre de titre (logo + nom utilisateur + contrôles fenêtre)
  widget_3   → zone latérale gauche (contient widget_4 + widget_5)
  widget_4   → sidebar de navigation (boutons de menu)
  accueil    → Dashboard
  pushButton_2 … pushButton_9 → items de navigation
  pushButton_9 → Déconnexion (en bas)
  pushButton_10/11/12 → Fermer / Max / Réduire (dans navbar)
"""
from __future__ import annotations
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QLabel, QSizePolicy

# ─── Palette ──────────────────────────────────────────────────────────────────
BG      = "#0f172a"
SIDEBAR = "#111827"      # légèrement plus foncé que le fond
NAVBAR  = "#0f172a"
CARD    = "#1e293b"
BORDER  = "#1e293b"
BLUE    = "#3b82f6"
BLUE_DIM= "#1d4ed8"
TEXT_HI = "#f8fafc"
TEXT_MID= "#cbd5e1"
TEXT_LO = "#94a3b8"
DANGER  = "#ef4444"
DANGER2 = "#dc2626"

# ─── Navigation items config ──────────────────────────────────────────────────
# (widget_name, label, icon, section_break_before)
NAV_ITEMS = [
    # ADMIN only
    ("accueil",       "Tableau de Bord",  "⊞",  False),
    # Gestion
    ("pushButton_2",  "Enseignants",      "👤",  True),
    ("pushButton_3",  "Cours",            "📚",  False),
    ("pushButton_22", "Critères",         "⚖",   False),
    # Workflow étudiants
    ("pushButton_6",  "Éligibilité",      "✓",   True),
    ("pushButton_4",  "Évaluations",      "📊",  False),
    ("pushButton_5",  "Résultats",        "📈",  False),
    # Compte
    ("pushButton_7",  "Mon Profil",       "🎓",  True),
    ("pushButton_8",  "Administration",   "🛡",   False),
]

# Bouton déconnexion (traitement séparé)
LOGOUT_BTN = "pushButton_9"

# Boutons fenêtre
WIN_BTNS = [
    ("pushButton_12", "─",  "Réduire",          "#334155", "#475569"),
    ("pushButton_11", "⬜", "Agrandir/Restaurer","#334155", "#475569"),
    ("pushButton_10", "✕",  "Fermer",            "#7f1d1d", DANGER),
]


class NavbarSidebarDesigner:
    """
    Applique un design professionnel à la navbar et à la sidebar.
    Appeler .build() après uic.loadUi().
    Appeler .set_active(widget_name) pour marquer le bouton actif.
    """

    def __init__(self, main_window):
        self.mw = main_window
        self._nav_buttons: dict[str, QPushButton] = {}

    # ─────────────────────────────────────────────────────────────────────────
    def build(self):
        self._style_navbar()
        self._style_sidebar_container()
        self._style_nav_buttons()
        self._style_logout_button()

    # ─────────────────────────────────────────────────────────────────────────
    # 1. NAVBAR (barre de titre)
    # ─────────────────────────────────────────────────────────────────────────
    def _style_navbar(self):
        mw = self.mw

        # Fond de la barre
        if w := getattr(mw, "widget_2", None):
            w.setStyleSheet(f"""
                QWidget {{
                    background-color: {CARD};
                    border-bottom: 1px solid {BORDER};
                }}
            """)
            w.setMinimumHeight(48)
            w.setMaximumHeight(52)

        # Logo / icône application  (label)
        if lbl := getattr(mw, "label", None):
            lbl.setStyleSheet(
                f"color: {BLUE}; font-size: 18px; font-weight: 800;"
                f" background: transparent; border: none; padding-left: 6px;"
            )

        # Nom de l'application / version (label_2 = nom utilisateur)
        if lbl := getattr(mw, "label_2", None):
            lbl.setStyleSheet(
                f"color: {TEXT_MID}; font-size: 12px; font-weight: 500;"
                f" background: transparent; border: none;"
            )

        # Boutons de fenêtre (Réduire / Agrandir / Fermer)
        for btn_name, icon_text, tooltip, bg_normal, bg_hover in WIN_BTNS:
            btn = getattr(mw, btn_name, None)
            if btn is None:
                continue
            btn.setText(icon_text)
            btn.setToolTip(tooltip)
            btn.setFixedSize(32, 28)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {TEXT_LO};
                    border: none;
                    border-radius: 4px;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background-color: {bg_hover};
                    color: {TEXT_HI};
                }}
                QPushButton:pressed {{
                    background-color: {bg_normal};
                }}
            """)

    # ─────────────────────────────────────────────────────────────────────────
    # 2. Conteneur de la sidebar
    # ─────────────────────────────────────────────────────────────────────────
    def _style_sidebar_container(self):
        mw = self.mw

        # widget_3 : zone latérale globale (sidebar + contenu)
        if w := getattr(mw, "widget_3", None):
            w.setStyleSheet(f"background-color: {BG};")

        # widget_4 : le panneau de navigation lui-même
        if w := getattr(mw, "widget_4", None):
            w.setMinimumWidth(190)
            w.setMaximumWidth(220)
            w.setStyleSheet(f"""
                QWidget {{
                    background-color: {SIDEBAR};
                    border-right: 1px solid {BORDER};
                }}
            """)
            if lay := w.layout():
                lay.setContentsMargins(8, 12, 8, 12)
                lay.setSpacing(2)

        # Layout imbriqué (verticalLayout_2 / 3 / 4)
        for vl_name in ("verticalLayout_2", "verticalLayout_3", "verticalLayout_4"):
            if vl := getattr(mw, vl_name, None):
                vl.setSpacing(2)
                vl.setContentsMargins(0, 0, 0, 0)

        # Titre de l'application dans la sidebar (s'il y en a un)
        for lbl_name in ("label_sidebar", "label_app"):
            if lbl := getattr(mw, lbl_name, None):
                lbl.setText("EvalPro")
                lbl.setStyleSheet(
                    f"color: {BLUE}; font-size: 16px; font-weight: 800;"
                    f" padding: 8px 12px 16px 12px; background: transparent; border: none;"
                )

    # ─────────────────────────────────────────────────────────────────────────
    # 3. Boutons de navigation
    # ─────────────────────────────────────────────────────────────────────────
    def _style_nav_buttons(self):
        mw = self.mw

        for widget_name, label, icon, _ in NAV_ITEMS:
            btn = getattr(mw, widget_name, None)
            if btn is None:
                continue

            # Mettre à jour le texte avec l'icône
            btn.setText(f"  {icon}  {label}")
            btn.setMinimumHeight(40)
            btn.setMaximumHeight(44)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setCheckable(True)
            btn.setStyleSheet(self._nav_btn_style())

            self._nav_buttons[widget_name] = btn

    def _nav_btn_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_LO};
                border: none;
                border-radius: 7px;
                text-align: left;
                padding: 0px 12px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {CARD};
                color: {TEXT_HI};
            }}
            QPushButton:checked {{
                background-color: {BLUE_DIM};
                color: {TEXT_HI};
                font-weight: 600;
                border-left: 3px solid {BLUE};
            }}
            QPushButton:pressed {{
                background-color: {BLUE};
                color: {TEXT_HI};
            }}
        """

    def _active_btn_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: {BLUE_DIM};
                color: {TEXT_HI};
                border: none;
                border-left: 3px solid {BLUE};
                border-radius: 7px;
                text-align: left;
                padding: 0px 12px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {BLUE};
                color: {TEXT_HI};
            }}
        """

    # ─────────────────────────────────────────────────────────────────────────
    # 4. Bouton Déconnexion
    # ─────────────────────────────────────────────────────────────────────────
    def _style_logout_button(self):
        mw = self.mw
        btn = getattr(mw, LOGOUT_BTN, None)
        if btn is None:
            return

        btn.setText("  ⏻  Déconnexion")
        btn.setMinimumHeight(40)
        btn.setMaximumHeight(44)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_LO};
                border: 1px solid #374151;
                border-radius: 7px;
                text-align: left;
                padding: 0px 12px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #7f1d1d;
                color: #fca5a5;
                border-color: {DANGER};
            }}
            QPushButton:pressed {{
                background-color: {DANGER2};
                color: white;
            }}
        """)

    # ─────────────────────────────────────────────────────────────────────────
    # 5. Marquer le bouton actif
    # ─────────────────────────────────────────────────────────────────────────
    def set_active(self, widget_name: str):
        """Applique l'état actif au bouton correspondant, désactive les autres."""
        for name, btn in self._nav_buttons.items():
            if name == widget_name:
                btn.setChecked(True)
            else:
                btn.setChecked(False)

    # ─────────────────────────────────────────────────────────────────────────
    # 6. Mapping PAGE_INDEX → widget_name de navigation
    # ─────────────────────────────────────────────────────────────────────────
    PAGE_TO_NAV = {
        0: "accueil",
        1: "pushButton_2",   # Professeurs
        2: "pushButton_3",   # Cours
        3: "pushButton_22",  # Critères
        4: "pushButton_6",   # Éligibilité
        5: "pushButton_4",   # Évaluations
        6: "pushButton_5",   # Résultats
    }

    def on_page_changed(self, page_index: int):
        """À appeler dans go_to_page() pour synchroniser l'état actif."""
        widget_name = self.PAGE_TO_NAV.get(page_index)
        if widget_name:
            self.set_active(widget_name)

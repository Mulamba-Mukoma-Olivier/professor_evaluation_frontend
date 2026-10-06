"""
dashboard_page.py
─────────────────
Dashboard professionnel — Système d'Évaluation des Professeurs Universitaires.

KPI cards adaptées au métier :
  1. Enseignants actifs
  2. Cours enregistrés
  3. Évaluations soumises
  4. Note globale moyenne /5

Sections graphiques :
  Ligne 1 : Classement profs (barres H) | Distribution des notes (histo)
  Ligne 2 : Activité mensuelle (timeline pleine largeur)
  Ligne 3 : Variabilité (boxplot) | Départements (barres groupées)
  Ligne 4 : Heatmap prof×critère | Niveaux par prof (stacked)
  Section : Évaluations récentes (liste)
"""
from __future__ import annotations
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy
)

# ─── Palette ──────────────────────────────────────────────────────────────────
BG      = "#0f172a"
CARD    = "#1e293b"
CARD2   = "#162032"
BORDER  = "#1e293b"
BORDER2 = "#334155"
BLUE    = "#3b82f6"
GREEN   = "#10b981"
AMBER   = "#f59e0b"
VIOLET  = "#8b5cf6"
TEAL    = "#14b8a6"
TEXT_HI  = "#f8fafc"
TEXT_MID = "#cbd5e1"
TEXT_LO  = "#94a3b8"

KPI_CARDS = [
    {"widget": "widget_7",  "value": "label_4",  "title": "label_5",
     "label": "Enseignants actifs", "accent": BLUE,   "sub": "Total inscrits"},
    {"widget": "widget_8",  "value": "label_6",  "title": "label_7",
     "label": "Cours",              "accent": GREEN,  "sub": "Dans le catalogue"},
    {"widget": "widget_9",  "value": "label_8",  "title": "label_9",
     "label": "Évaluations",        "accent": AMBER,  "sub": "Soumissions totales"},
    {"widget": "widget_10", "value": "label_10", "title": "label_11",
     "label": "Note Globale /5",    "accent": VIOLET, "sub": "Moyenne toutes évals"},
]


class DashboardPageDesigner:
    """
    Construit l'interface du dashboard adapté au système d'évaluation des profs.
    Appeler .build() une seule fois dans __init__.

    Conteneurs de graphiques dynamiques (créés et stockés ici) :
      .boxplot_w      → Variabilité notes par prof
      .scatter_w      → Barres groupées par département
      .heatmap_w      → Heatmap prof × critère
      .stacked_w      → Niveaux empilés par prof
    """

    def __init__(self, main_window):
        self.mw = main_window
        self.boxplot_w: QWidget | None = None
        self.scatter_w: QWidget | None = None
        self.heatmap_w: QWidget | None = None
        self.stacked_w: QWidget | None = None

    def build(self):
        self._style_page()
        self._style_header()
        self._style_kpi_cards()
        self._style_chart_containers()
        self._rename_section_headers()
        self._inject_advanced_rows()
        self._style_recent_evals()

    # ─────────────────────────────────────────────────────────────────────────
    def _style_page(self):
        mw = self.mw
        for name in ("page", "widget_6"):
            if w := getattr(mw, name, None):
                w.setStyleSheet(f"background-color: {BG}; border: none;")
        if sa := getattr(mw, "scrollArea", None):
            sa.setStyleSheet("background: transparent; border: none;")
            sa.setFrameShape(QFrame.NoFrame)
            sa.setWidgetResizable(True)
        if sc := getattr(mw, "scrollAreaWidgetContents", None):
            sc.setStyleSheet(f"background-color: {BG};")
        if vl := getattr(mw, "verticalLayout_10", None):
            vl.setContentsMargins(24, 10, 24, 24)
            vl.setSpacing(14)

    # ─────────────────────────────────────────────────────────────────────────
    def _style_header(self):
        mw = self.mw
        if lbl := getattr(mw, "label_3", None):
            lbl.setText("Tableau de Bord")
            lbl.setStyleSheet(
                f"color: {TEXT_HI}; font-size: 22px; font-weight: 700;"
                f" letter-spacing: -0.5px; background: transparent; border: none;"
            )

        # Sous-titre (si label secondaire dans horizontalLayout_9)
        if hl := getattr(mw, "horizontalLayout_9", None):
            hl.setContentsMargins(0, 4, 0, 8)

    # ─────────────────────────────────────────────────────────────────────────
    def _style_kpi_cards(self):
        mw = self.mw
        if hl := getattr(mw, "horizontalLayout_10", None):
            hl.setSpacing(12)

        for cfg in KPI_CARDS:
            card = getattr(mw, cfg["widget"], None)
            if card is None:
                continue
            card.setMinimumSize(130, 95)
            card.setMaximumHeight(140)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            card.setStyleSheet(f"""
                QWidget {{
                    background-color: {CARD};
                    border: 1px solid {BORDER2};
                    border-left: 4px solid {cfg['accent']};
                    border-radius: 10px;
                }}
            """)
            if lay := card.layout():
                lay.setContentsMargins(16, 10, 12, 10)
                lay.setSpacing(3)

            if val_lbl := getattr(mw, cfg["value"], None):
                val_lbl.setStyleSheet(
                    f"color: {TEXT_HI}; font-size: 30px; font-weight: 800;"
                    f" letter-spacing: -1px; background: transparent; border: none;"
                )
                val_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            if ttl_lbl := getattr(mw, cfg["title"], None):
                ttl_lbl.setText(cfg["label"])
                ttl_lbl.setStyleSheet(
                    f"color: {TEXT_LO}; font-size: 11px; font-weight: 600;"
                    f" letter-spacing: 0.3px; background: transparent; border: none;"
                )
                ttl_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    # ─────────────────────────────────────────────────────────────────────────
    def _style_chart_containers(self):
        mw = self.mw
        # widget_11 = conteneur côte-à-côte (widget_12 + widget_13)
        if w := getattr(mw, "widget_11", None):
            w.setStyleSheet("background: transparent; border: none;")
            w.setMinimumHeight(280)
            w.setMaximumHeight(340)
            w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            if lay := w.layout():
                lay.setContentsMargins(0, 0, 0, 0)
                lay.setSpacing(12)

        for name in ("widget_12", "widget_13"):
            if w := getattr(mw, name, None):
                w.setStyleSheet(
                    f"background: {CARD}; border: 1px solid {BORDER2}; border-radius: 10px;"
                )
                w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # widget_15 = timeline pleine largeur
        if w := getattr(mw, "widget_15", None):
            w.setStyleSheet(
                f"background: {CARD}; border: 1px solid {BORDER2}; border-radius: 10px;"
            )
            w.setMinimumHeight(185)
            w.setMaximumHeight(225)
            w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    # ─────────────────────────────────────────────────────────────────────────
    def _rename_section_headers(self):
        mw = self.mw
        sec = (
            f"color: {TEXT_HI}; font-size: 14px; font-weight: 700;"
            f" background: transparent; border: none;"
        )
        renames = {
            "label_13": "Performances des Enseignants",
            "label_14": "Activité des Évaluations",
            "label_12": "Évaluations Récentes",
        }
        for name, text in renames.items():
            if lbl := getattr(mw, name, None):
                lbl.setText(text)
                lbl.setStyleSheet(sec)

    # ─────────────────────────────────────────────────────────────────────────
    def _inject_advanced_rows(self):
        mw = self.mw
        vl = getattr(mw, "verticalLayout_10", None)
        if vl is None:
            return

        # Trouver la position de widget_14 (liste évals récentes)
        w14 = getattr(mw, "widget_14", None)
        insert_at = vl.count()
        if w14 is not None:
            for i in range(vl.count()):
                item = vl.itemAt(i)
                if item and item.widget() is w14:
                    insert_at = max(0, i - 1)  # avant le header "Évals récentes"
                    break

        # En-tête "Analyse Approfondie"
        hdr = self._make_section_label("Analyse Approfondie")
        vl.insertWidget(insert_at, hdr)
        insert_at += 1

        # Ligne : Barres par département (pleine largeur, boxplot retiré)
        self.boxplot_w = None
        self.scatter_w = self._card(280)
        vl.insertWidget(insert_at, self.scatter_w)
        insert_at += 1

        # Ligne : Heatmap | Barres empilées
        self.heatmap_w = self._card(280)
        self.stacked_w = self._card(280)
        vl.insertWidget(insert_at, self._row(self.heatmap_w, self.stacked_w))

    # ─────────────────────────────────────────────────────────────────────────
    def _style_recent_evals(self):
        mw = self.mw
        if w := getattr(mw, "widget_14", None):
            w.setStyleSheet(
                f"background: {CARD}; border: 1px solid {BORDER2}; border-radius: 10px;"
            )
            w.setMinimumHeight(155)
            w.setMaximumHeight(235)
            w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            if lay := w.layout():
                lay.setContentsMargins(10, 10, 10, 10)

        if ev := getattr(mw, "eval_recentes", None):
            ev.setStyleSheet(f"""
                QListView {{
                    background: transparent; border: none;
                    color: {TEXT_MID}; font-size: 12px; outline: none;
                }}
                QListView::item {{
                    padding: 6px 10px;
                    border-bottom: 1px solid {BORDER2};
                    border-radius: 4px;
                }}
                QListView::item:selected {{
                    background: #1d4ed8; color: {TEXT_HI};
                }}
                QListView::item:hover {{
                    background: {CARD2}; color: {TEXT_HI};
                }}
                QScrollBar:vertical {{
                    border: none; background: {BG};
                    width: 5px; border-radius: 2px;
                }}
                QScrollBar::handle:vertical {{
                    background: #475569; border-radius: 2px; min-height: 20px;
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
            """)

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────
    def _make_section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {TEXT_HI}; font-size: 14px; font-weight: 700;"
            f" background: transparent; border: none; padding-top: 4px;"
        )
        return lbl

    def _card(self, min_h: int = 270) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {CARD}; border: 1px solid {BORDER2}; border-radius: 10px;")
        w.setMinimumHeight(min_h)
        w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return w

    def _row(self, w1: QWidget, w2: QWidget) -> QWidget:
        row = QWidget()
        row.setStyleSheet("background: transparent; border: none;")
        lay = QHBoxLayout(row)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)
        lay.addWidget(w1)
        lay.addWidget(w2)
        return row

"""
Design sobre et adaptatif de la page Résultats — thème dark minimaliste.
Optimisé pour s'adapter à toutes les résolutions d'écran (notamment 1366x768 et plein écran).
Palette sobre : nuances de slate (#0f172a, #1e293b, #334155) et bleu professionnel.
"""
from typing import List, Optional, Dict, Any
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QProgressBar, QFrame, QSizePolicy, QScrollArea, QComboBox, QPushButton
)

# ─── Palette Sobre & Épurée (Slate Corporate) ──────────────────────────────────
BG         = "#0f172a"
CARD       = "#1e293b"
CARD_INNER = "#0f172a"
CARD_HOVER = "#273549"
BORDER     = "#334155"
BORDER_SUB = "#1e293b"
BLUE       = "#3b82f6"
BLUE_HOVER = "#2563eb"
TEXT_HI    = "#f8fafc"
TEXT_MID   = "#cbd5e1"
TEXT_LO    = "#94a3b8"
TEXT_MUTED = "#64748b"

COMBO_STYLE = f"""
QComboBox {{
    background-color: {CARD_INNER};
    color: {TEXT_HI};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 5px 10px;
    font-size: 12px;
}}
QComboBox:hover {{
    border-color: {BLUE};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {TEXT_LO};
    margin-right: 6px;
}}
QComboBox QAbstractItemView {{
    background-color: {CARD};
    color: {TEXT_HI};
    selection-background-color: {BLUE};
    selection-color: #ffffff;
    border: 1px solid {BORDER};
    border-radius: 6px;
    outline: none;
    padding: 2px;
}}
"""

BTN_STYLE = f"""
QPushButton {{
    background-color: {BLUE};
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: {BLUE_HOVER};
}}
QPushButton:pressed {{
    background-color: #1d4ed8;
}}
"""


def score_badge_text(avg: float) -> str:
    if avg >= 4.5: return "Excellent"
    if avg >= 4.0: return "Très satisfaisant"
    if avg >= 3.0: return "Satisfaisant"
    if avg >= 2.0: return "À améliorer"
    return "Insuffisant"


def _clear_layout_safely(layout):
    """Vide récursivement un layout Qt."""
    if layout is None:
        return
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w is not None:
            w.setParent(None)
            w.deleteLater()
        else:
            sub = item.layout()
            if sub is not None:
                _clear_layout_safely(sub)


class ResultsPageDesigner:
    """
    Gestionnaire sobre et responsive de la page Résultats.
    Grille 2 colonnes pour afficher l'ensemble des 10 critères sans défilement excessif.
    """

    def __init__(self, main_window):
        self.mw = main_window
        self._stat_widgets: Dict[str, Any] = {}
        self._grid_container: Optional[QWidget] = None
        self._grid_layout: Optional[QGridLayout] = None

    def build(self):
        """Construit l'interface complète de la page résultats."""
        container: QWidget = getattr(self.mw, "scrollAreaWidgetContents_6", None)
        if container is None:
            return

        scroll_area: QScrollArea = getattr(self.mw, "scrollArea_6", None)
        if scroll_area:
            scroll_area.setStyleSheet(f"QScrollArea {{ background: {BG}; border: none; }}")
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        page_7 = getattr(self.mw, "page_7", None)
        if page_7:
            page_7.setStyleSheet(f"QWidget#page_7 {{ background: {BG}; }}")

        layout: QVBoxLayout = container.layout()
        if layout is None:
            layout = QVBoxLayout(container)
        else:
            _clear_layout_safely(layout)

        container.setStyleSheet(f"background: {BG}; border: none;")
        # Marges compactes et adaptatives
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(10)

        # 1. En-tête compact
        layout.addWidget(self._make_header())

        # 2. Barre d'outils / Filtres
        layout.addWidget(self._make_filters_card())

        # 3. Carte de synthèse globale KPI (compacte et horizontale)
        layout.addWidget(self._make_global_card())

        # 4. Message d'état informatif discret
        layout.addWidget(self._make_status_banner())

        # 5. Titre de la section critères
        crit_header = self._make_section_header("Critères d'évaluation (10)")
        layout.addWidget(crit_header)

        # 6. Grille adaptative 2 colonnes (5 critères à gauche, 5 à droite)
        self._grid_container = QWidget()
        self._grid_container.setStyleSheet("background: transparent; border: none;")
        self._grid_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        self._grid_layout.setSpacing(8)

        layout.addWidget(self._grid_container)
        layout.addStretch(1)

        # État initial vide
        self._show_empty_state()

    # ──────────────────────────────────────────────────────────────────────────
    # 1. EN-TÊTE COMPACT
    # ──────────────────────────────────────────────────────────────────────────
    def _make_header(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(
            f"QWidget {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 8px; }}"
        )
        row = QHBoxLayout(w)
        row.setContentsMargins(14, 8, 14, 8)
        row.setSpacing(12)

        col = QVBoxLayout()
        col.setSpacing(1)
        title = QLabel("Résultats des évaluations")
        title.setStyleSheet(f"color: {TEXT_HI}; font-size: 15px; font-weight: 700; background: transparent; border: none;")

        self._stat_widgets["header_sub"] = QLabel("Synthèse globale et analytique par critère")
        self._stat_widgets["header_sub"].setStyleSheet(f"color: {TEXT_LO}; font-size: 11px; background: transparent; border: none;")
        col.addWidget(title)
        col.addWidget(self._stat_widgets["header_sub"])
        row.addLayout(col, stretch=1)

        # Badge total avis discret
        self._stat_widgets["reviews_badge"] = QLabel("0 avis")
        self._stat_widgets["reviews_badge"].setAlignment(Qt.AlignCenter)
        self._stat_widgets["reviews_badge"].setFixedHeight(26)
        self._stat_widgets["reviews_badge"].setStyleSheet(
            f"background: {CARD_INNER}; color: {TEXT_MID}; border: 1px solid {BORDER};"
            " border-radius: 13px; padding: 0 12px; font-size: 11px; font-weight: 600;"
        )
        row.addWidget(self._stat_widgets["reviews_badge"])

        return w

    # ──────────────────────────────────────────────────────────────────────────
    # 2. BARRE DE FILTRES RESPONSIVE
    # ──────────────────────────────────────────────────────────────────────────
    def _make_filters_card(self) -> QWidget:
        card = QWidget()
        card.setStyleSheet(
            f"QWidget {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 8px; }}"
        )
        row = QHBoxLayout(card)
        row.setContentsMargins(12, 8, 12, 8)
        row.setSpacing(10)

        # Professeur
        p_lbl = QLabel("Professeur :")
        p_lbl.setStyleSheet(f"color: {TEXT_MID}; font-size: 11px; font-weight: 600; background: transparent; border: none;")
        self.mw.comboBox_3 = QComboBox()
        self.mw.comboBox_3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.mw.comboBox_3.setStyleSheet(COMBO_STYLE)
        row.addWidget(p_lbl)
        row.addWidget(self.mw.comboBox_3, stretch=3)

        # Cours
        c_lbl = QLabel("Cours :")
        c_lbl.setStyleSheet(f"color: {TEXT_MID}; font-size: 11px; font-weight: 600; background: transparent; border: none;")
        self.mw.results_course_combo = QComboBox()
        self.mw.results_course_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.mw.results_course_combo.setStyleSheet(COMBO_STYLE)
        row.addWidget(c_lbl)
        row.addWidget(self.mw.results_course_combo, stretch=3)

        # Période
        per_lbl = QLabel("Période :")
        per_lbl.setStyleSheet(f"color: {TEXT_MID}; font-size: 11px; font-weight: 600; background: transparent; border: none;")
        self.mw.results_period_combo = QComboBox()
        self.mw.results_period_combo.setMinimumWidth(100)
        self.mw.results_period_combo.addItems(["Semestre 1", "Semestre 2", "Annuel", "E2E"])
        self.mw.results_period_combo.setStyleSheet(COMBO_STYLE)
        row.addWidget(per_lbl)
        row.addWidget(self.mw.results_period_combo, stretch=1)

        # Année
        y_lbl = QLabel("Année :")
        y_lbl.setStyleSheet(f"color: {TEXT_MID}; font-size: 11px; font-weight: 600; background: transparent; border: none;")
        self.mw.results_year_combo = QComboBox()
        self.mw.results_year_combo.setMinimumWidth(95)
        self.mw.results_year_combo.addItems(["2025-2026", "2024-2025", "2023-2024"])
        self.mw.results_year_combo.setStyleSheet(COMBO_STYLE)
        row.addWidget(y_lbl)
        row.addWidget(self.mw.results_year_combo, stretch=1)

        # Bouton
        self.mw.results_refresh_btn = QPushButton("Actualiser")
        self.mw.results_refresh_btn.setCursor(Qt.PointingHandCursor)
        self.mw.results_refresh_btn.setStyleSheet(BTN_STYLE)
        row.addWidget(self.mw.results_refresh_btn)

        # Connexions
        self.mw.comboBox_3.currentIndexChanged.connect(self.mw._on_results_prof_changed)
        self.mw.results_course_combo.currentIndexChanged.connect(self.mw._fetch_and_display_results)
        self.mw.results_period_combo.currentIndexChanged.connect(self.mw._fetch_and_display_results)
        self.mw.results_year_combo.currentIndexChanged.connect(self.mw._fetch_and_display_results)
        self.mw.results_refresh_btn.clicked.connect(self.mw._fetch_and_display_results)

        return card

    # ──────────────────────────────────────────────────────────────────────────
    # 3. CARTE SYNTHÈSE GLOBALE (SOBRE & COMPACTE)
    # ──────────────────────────────────────────────────────────────────────────
    def _make_global_card(self) -> QWidget:
        card = QWidget()
        card.setFixedHeight(68)
        card.setStyleSheet(
            f"QWidget {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 8px; }}"
        )
        row = QHBoxLayout(card)
        row.setContentsMargins(16, 8, 16, 8)
        row.setSpacing(20)

        # ── Score principal ──
        score_box = QHBoxLayout()
        score_box.setSpacing(8)

        self._stat_widgets["global_score"] = QLabel("—")
        self._stat_widgets["global_score"].setStyleSheet(
            f"color: {TEXT_HI}; font-size: 26px; font-weight: 800; background: transparent; border: none;"
        )
        score_box.addWidget(self._stat_widgets["global_score"])

        score_sub = QVBoxLayout()
        score_sub.setSpacing(1)
        score_sub_lbl = QLabel("/ 5.0")
        score_sub_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; font-weight: 600; background: transparent; border: none;")
        self._stat_widgets["score_badge"] = QLabel("Aucune donnée")
        self._stat_widgets["score_badge"].setStyleSheet(
            f"color: {TEXT_LO}; font-size: 11px; font-weight: 600; background: transparent; border: none;"
        )
        score_sub.addWidget(score_sub_lbl)
        score_sub.addWidget(self._stat_widgets["score_badge"])
        score_box.addLayout(score_sub)

        row.addLayout(score_box)

        # Séparateur
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.VLine)
        sep1.setStyleSheet(f"background: {BORDER};")
        sep1.setFixedWidth(1)
        row.addWidget(sep1)

        # ── Barre de progression globale ──
        bar_box = QVBoxLayout()
        bar_box.setSpacing(3)
        bar_info = QHBoxLayout()
        bar_title = QLabel("Moyenne générale")
        bar_title.setStyleSheet(f"color: {TEXT_MID}; font-size: 11px; font-weight: 600; background: transparent; border: none;")
        self._stat_widgets["bar_ratio"] = QLabel("0.00 / 5.0 (0%)")
        self._stat_widgets["bar_ratio"].setStyleSheet(f"color: {TEXT_HI}; font-size: 11px; font-weight: 600; background: transparent; border: none;")
        bar_info.addWidget(bar_title)
        bar_info.addStretch()
        bar_info.addWidget(self._stat_widgets["bar_ratio"])
        bar_box.addLayout(bar_info)

        self._stat_widgets["global_bar"] = QProgressBar()
        self._stat_widgets["global_bar"].setRange(0, 100)
        self._stat_widgets["global_bar"].setValue(0)
        self._stat_widgets["global_bar"].setFixedHeight(6)
        self._stat_widgets["global_bar"].setTextVisible(False)
        self._stat_widgets["global_bar"].setStyleSheet(
            f"QProgressBar {{ background: {CARD_INNER}; border-radius: 3px; border: none; }}"
            f"QProgressBar::chunk {{ background: {BLUE}; border-radius: 3px; }}"
        )
        bar_box.addWidget(self._stat_widgets["global_bar"])
        row.addLayout(bar_box, stretch=2)

        # Séparateur
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.VLine)
        sep2.setStyleSheet(f"background: {BORDER};")
        sep2.setFixedWidth(1)
        row.addWidget(sep2)

        # ── Résumé forces / axes (sobre) ──
        kpi_col = QVBoxLayout()
        kpi_col.setSpacing(2)

        best_row = QHBoxLayout()
        best_row.setSpacing(6)
        b_tag = QLabel("Point fort :")
        b_tag.setStyleSheet(f"color: {TEXT_LO}; font-size: 11px; font-weight: 600; background: transparent; border: none;")
        self._stat_widgets["best_crit"] = QLabel("—")
        self._stat_widgets["best_crit"].setStyleSheet(f"color: {TEXT_HI}; font-size: 11px; font-weight: 600; background: transparent; border: none;")
        best_row.addWidget(b_tag)
        best_row.addWidget(self._stat_widgets["best_crit"], stretch=1)
        kpi_col.addLayout(best_row)

        worst_row = QHBoxLayout()
        worst_row.setSpacing(6)
        w_tag = QLabel("À améliorer :")
        w_tag.setStyleSheet(f"color: {TEXT_LO}; font-size: 11px; font-weight: 600; background: transparent; border: none;")
        self._stat_widgets["worst_crit"] = QLabel("—")
        self._stat_widgets["worst_crit"].setStyleSheet(f"color: {TEXT_HI}; font-size: 11px; font-weight: 600; background: transparent; border: none;")
        worst_row.addWidget(w_tag)
        worst_row.addWidget(self._stat_widgets["worst_crit"], stretch=1)
        kpi_col.addLayout(worst_row)

        row.addLayout(kpi_col, stretch=2)

        return card

    # ──────────────────────────────────────────────────────────────────────────
    # 4. BANNIÈRE DISCRÈTE
    # ──────────────────────────────────────────────────────────────────────────
    def _make_status_banner(self) -> QWidget:
        self.mw.results_status_banner = QLabel("Sélectionnez un professeur et un cours pour charger les résultats.")
        self.mw.results_status_banner.setStyleSheet(
            f"background: {CARD_INNER}; color: {TEXT_LO}; border: 1px solid {BORDER};"
            " border-radius: 6px; padding: 6px 12px; font-size: 11px; font-weight: 500;"
        )
        return self.mw.results_status_banner

    # ──────────────────────────────────────────────────────────────────────────
    # 5. TITRE DE SECTION
    # ──────────────────────────────────────────────────────────────────────────
    def _make_section_header(self, title: str) -> QWidget:
        t = QLabel(title)
        t.setStyleSheet(f"color: {TEXT_LO}; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; background: transparent; border: none; padding-top: 4px;")
        return t

    # ──────────────────────────────────────────────────────────────────────────
    # 6. CRÉATION D'UNE CARTE CRITÈRE (COMPACTE, 1 LIGNE)
    # ──────────────────────────────────────────────────────────────────────────
    def _make_crit_card(self, index: int, name: str, avg: float, responses: int) -> QWidget:
        pct = int(avg / 5.0 * 100) if avg > 0 else 0

        card = QWidget()
        card.setFixedHeight(44)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setStyleSheet(
            f"QWidget {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 6px; }}"
            f"QWidget:hover {{ background: {CARD_HOVER}; border-color: {BLUE}; }}"
        )

        row = QHBoxLayout(card)
        row.setContentsMargins(10, 4, 10, 4)
        row.setSpacing(10)

        # Numéro discret
        num = QLabel(f"{index+1:02d}")
        num.setFixedSize(24, 24)
        num.setAlignment(Qt.AlignCenter)
        num.setStyleSheet(
            f"background: {CARD_INNER}; color: {TEXT_LO}; border: 1px solid {BORDER};"
            " border-radius: 12px; font-weight: 700; font-size: 10px;"
        )
        row.addWidget(num)

        # Nom du critère
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(f"color: {TEXT_HI}; font-size: 12px; font-weight: 600; background: transparent; border: none;")
        row.addWidget(name_lbl, stretch=1)

        # Barre de progression fine
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(pct)
        bar.setFixedWidth(75)
        bar.setFixedHeight(4)
        bar.setTextVisible(False)
        bar.setStyleSheet(
            f"QProgressBar {{ background: {CARD_INNER}; border-radius: 2px; border: none; }}"
            f"QProgressBar::chunk {{ background: {BLUE}; border-radius: 2px; }}"
        )
        row.addWidget(bar)

        # Note / 5
        sc_val = QLabel(f"{avg:.2f}" if avg > 0 else "—")
        sc_val.setFixedWidth(36)
        sc_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        sc_val.setStyleSheet(f"color: {TEXT_HI}; font-size: 13px; font-weight: 700; background: transparent; border: none;")
        row.addWidget(sc_val)

        sc_unit = QLabel("/ 5.0")
        sc_unit.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; background: transparent; border: none;")
        row.addWidget(sc_unit)

        # Compteur d'avis
        resp_badge = QLabel(f"({responses} avis)" if responses > 0 else "(0)")
        resp_badge.setFixedWidth(56)
        resp_badge.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        resp_badge.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; background: transparent; border: none;")
        row.addWidget(resp_badge)

        return card

    # ──────────────────────────────────────────────────────────────────────────
    # 7. MISE À JOUR DES DONNÉES EN TEMPS RÉEL
    # ──────────────────────────────────────────────────────────────────────────
    def update_display(self, result: Optional[Dict[str, Any]],
                       prof_name: str = "", course_name: str = "",
                       period: str = "", academic_year: str = "",
                       criteria: Optional[List[Dict]] = None):
        """Met à jour l'affichage avec les données réelles de l'API Go."""
        if result is None or result.get("total_reviews", 0) == 0:
            self._show_empty_state(prof_name, course_name, period, academic_year, criteria)
            return

        avg_global = float(result.get("global_average", 0.0))
        total_rev  = int(result.get("total_reviews", 0))
        pct_global = int(avg_global / 5.0 * 100)

        # ── Header ──
        if self._stat_widgets.get("header_sub"):
            self._stat_widgets["header_sub"].setText(
                f"{prof_name}  •  {course_name}  •  {period} {academic_year}"
            )
        if self._stat_widgets.get("reviews_badge"):
            self._stat_widgets["reviews_badge"].setText(f"{total_rev} avis")

        # ── Score Global ──
        if self._stat_widgets.get("global_score"):
            self._stat_widgets["global_score"].setText(f"{avg_global:.2f}")

        if self._stat_widgets.get("score_badge"):
            self._stat_widgets["score_badge"].setText(score_badge_text(avg_global))

        if self._stat_widgets.get("bar_ratio"):
            self._stat_widgets["bar_ratio"].setText(f"{avg_global:.2f} / 5.0 ({pct_global}%)")

        if self._stat_widgets.get("global_bar"):
            self._stat_widgets["global_bar"].setValue(pct_global)

        # ── Bannière d'état ──
        if hasattr(self.mw, "results_status_banner"):
            self.mw.results_status_banner.setText(
                f"✓ {total_rev} évaluation(s) enregistrée(s) pour {prof_name} sur {course_name} ({period} {academic_year})."
            )
            self.mw.results_status_banner.setStyleSheet(
                f"background: {CARD_INNER}; color: {TEXT_MID}; border: 1px solid {BORDER};"
                " border-radius: 6px; padding: 6px 12px; font-size: 11px; font-weight: 500;"
            )

        # ── Critères dans la grille 2 colonnes ──
        crit_results = {cr.get("criterion_id"): cr for cr in result.get("criteria", [])}
        active_crit = [c for c in (criteria or []) if c.get("active", True)]
        if not active_crit:
            active_crit = [{"id": i+1, "name": f"Critère {i+1}"} for i in range(10)]

        best_name, best_avg   = "—", -1.0
        worst_name, worst_avg = "—", 99.0

        if self._grid_layout is not None:
            _clear_layout_safely(self._grid_layout)
            self._grid_layout.setColumnStretch(0, 1)
            self._grid_layout.setColumnStretch(1, 1)

            # Placer 5 critères par colonne (colonne 0 = 0-4, colonne 1 = 5-9)
            items_per_col = (len(active_crit) + 1) // 2
            for i, crit in enumerate(active_crit):
                cid      = crit.get("id")
                c_name   = crit.get("name", f"Critère {i+1}")
                cr_data  = crit_results.get(cid, {})
                c_avg    = float(cr_data.get("average", 0.0))
                c_resp   = int(cr_data.get("responses", 0))

                if c_resp > 0:
                    if c_avg > best_avg:
                        best_avg, best_name = c_avg, c_name
                    if c_avg < worst_avg:
                        worst_avg, worst_name = c_avg, c_name

                card_widget = self._make_crit_card(i, c_name, c_avg, c_resp)
                row_idx = i % items_per_col
                col_idx = i // items_per_col
                self._grid_layout.addWidget(card_widget, row_idx, col_idx)

        # ── Meilleur / pire critère ──
        if self._stat_widgets.get("best_crit"):
            self._stat_widgets["best_crit"].setText(
                f"{best_name} ({best_avg:.2f}/5)" if best_avg >= 0 else "—"
            )

        if self._stat_widgets.get("worst_crit"):
            self._stat_widgets["worst_crit"].setText(
                f"{worst_name} ({worst_avg:.2f}/5)" if (worst_avg <= 5.0 and worst_avg != 99.0) else "—"
            )

    # ──────────────────────────────────────────────────────────────────────────
    # 8. ÉTAT VIDE (AUCUNE ÉVALUATION)
    # ──────────────────────────────────────────────────────────────────────────
    def _show_empty_state(self, prof_name: str = "", course_name: str = "",
                          period: str = "", academic_year: str = "",
                          criteria: Optional[List[Dict]] = None):
        """Affiche un état vide soigné lorsqu'aucune évaluation n'est disponible."""
        if self._stat_widgets.get("header_sub"):
            if prof_name and course_name:
                self._stat_widgets["header_sub"].setText(
                    f"{prof_name}  •  {course_name}  •  {period} {academic_year}"
                )
            else:
                self._stat_widgets["header_sub"].setText(
                    "Synthèse globale et analytique par critère"
                )

        if self._stat_widgets.get("reviews_badge"):
            self._stat_widgets["reviews_badge"].setText("0 avis")

        if self._stat_widgets.get("global_score"):
            self._stat_widgets["global_score"].setText("—")

        if self._stat_widgets.get("score_badge"):
            self._stat_widgets["score_badge"].setText("Aucune évaluation")

        if self._stat_widgets.get("bar_ratio"):
            self._stat_widgets["bar_ratio"].setText("0.00 / 5.0 (0%)")

        if self._stat_widgets.get("global_bar"):
            self._stat_widgets["global_bar"].setValue(0)

        if self._stat_widgets.get("best_crit"):
            self._stat_widgets["best_crit"].setText("—")
        if self._stat_widgets.get("worst_crit"):
            self._stat_widgets["worst_crit"].setText("—")

        if hasattr(self.mw, "results_status_banner"):
            if prof_name and course_name:
                self.mw.results_status_banner.setText(
                    f"ℹ Aucune évaluation pour {prof_name} sur {course_name} ({period} {academic_year})."
                )
            else:
                self.mw.results_status_banner.setText(
                    "Sélectionnez un professeur et un cours pour charger les résultats."
                )
            self.mw.results_status_banner.setStyleSheet(
                f"background: {CARD_INNER}; color: {TEXT_LO}; border: 1px solid {BORDER};"
                " border-radius: 6px; padding: 6px 12px; font-size: 11px; font-weight: 500;"
            )

        active_crit = [c for c in (criteria or []) if c.get("active", True)]
        if not active_crit:
            active_crit = [{"id": i+1, "name": f"Critère {i+1}"} for i in range(10)]

        if self._grid_layout is not None:
            _clear_layout_safely(self._grid_layout)
            self._grid_layout.setColumnStretch(0, 1)
            self._grid_layout.setColumnStretch(1, 1)
            items_per_col = (len(active_crit) + 1) // 2
            for i, crit in enumerate(active_crit):
                c_name = crit.get("name", f"Critère {i+1}")
                row_idx = i % items_per_col
                col_idx = i // items_per_col
                self._grid_layout.addWidget(self._make_crit_card(i, c_name, 0.0, 0), row_idx, col_idx)


__all__ = ["ResultsPageDesigner"]

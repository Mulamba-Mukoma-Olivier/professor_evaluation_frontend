"""
Design premium de la page d'évaluation — cohérent avec le thème dark #0f172a.
Injecté dans widget_28/verticalLayout_30 existants du .ui.
"""
from typing import List, Optional
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QSizePolicy,
)

# ─── Palette ─────────────────────────────────────────────────────────────────
BG_DEEP    = "#0f172a"
BG_CARD    = "#1e293b"
BG_HOVER   = "#243448"
BORDER     = "#334155"
BLUE       = "#3b82f6"
GREEN      = "#10b981"
AMBER      = "#f59e0b"
RED        = "#ef4444"
ORANGE     = "#f97316"
LIME       = "#84cc16"
TEXT_HI    = "#f1f5f9"
TEXT_LO    = "#94a3b8"

SCORE_COLOR = {1: RED, 2: ORANGE, 3: AMBER, 4: LIME, 5: GREEN}
SCORE_LABEL = {1: "Insuffisant", 2: "Médiocre", 3: "Passable", 4: "Bien", 5: "Excellent"}

STAR_CSS = """
QPushButton {{
    background: {bg};
    color: {fg};
    border: 2px solid {border};
    border-radius: 10px;
    font-size: 20px;
    font-weight: bold;
    padding: 0;
}}
QPushButton:hover {{
    background: {hover_bg};
    border-color: {fg};
}}
"""


class CriterionCard(QFrame):
    """Carte d'évaluation d'un critère — étoiles cliquables sur fond card."""
    scoreChanged = pyqtSignal(int, int)   # (index, score)

    def __init__(self, index: int, name: str, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.index = index
        self._score = 1
        self._build(name)

    def _build(self, name: str):
        self.setFixedHeight(90)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(
            f"QFrame {{ background: {BG_CARD}; border: 1px solid {BORDER};"
            f" border-radius: 14px; }}"
        )

        root = QHBoxLayout(self)
        root.setContentsMargins(16, 10, 16, 10)
        root.setSpacing(14)

        # ── Badge numéro ──
        num = QLabel(f"{self.index + 1:02d}")
        num.setFixedSize(36, 36)
        num.setAlignment(Qt.AlignCenter)
        num.setStyleSheet(
            f"background: {BLUE}; color: white; border-radius: 18px;"
            " font-weight: 900; font-size: 14px; border: none;"
        )
        root.addWidget(num)

        # ── Colonne nom + qualificatif ──
        info = QVBoxLayout()
        info.setSpacing(2)
        self.name_lbl = QLabel(name)
        self.name_lbl.setStyleSheet(
            f"color: {TEXT_HI}; font-size: 13px; font-weight: 700; background: transparent; border: none;"
        )
        self.name_lbl.setWordWrap(True)
        self.qual_lbl = QLabel(SCORE_LABEL[1])
        self.qual_lbl.setStyleSheet(
            f"color: {RED}; font-size: 11px; font-weight: 600; background: transparent; border: none;"
        )
        info.addWidget(self.name_lbl)
        info.addWidget(self.qual_lbl)
        root.addLayout(info, stretch=1)

        # ── Étoiles ──
        stars = QHBoxLayout()
        stars.setSpacing(5)
        self._btns: List[QPushButton] = []
        for s in range(1, 6):
            btn = QPushButton("★")
            btn.setFixedSize(40, 40)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(f"{SCORE_LABEL[s]}")
            btn.setProperty("sv", s)
            btn.clicked.connect(lambda _, sc=s: self._on_click(sc))
            stars.addWidget(btn)
            self._btns.append(btn)
        root.addLayout(stars)

        # ── Score numérique ──
        self.score_num = QLabel("1")
        self.score_num.setFixedWidth(28)
        self.score_num.setAlignment(Qt.AlignCenter)
        self.score_num.setStyleSheet(
            f"color: {RED}; font-size: 20px; font-weight: 900;"
            " background: transparent; border: none;"
        )
        root.addWidget(self.score_num)

        self._refresh(1)

    def _on_click(self, score: int):
        self._score = score
        self._refresh(score)
        self.scoreChanged.emit(self.index, score)

    def _refresh(self, score: int):
        c = SCORE_COLOR.get(score, GREEN)
        for btn in self._btns:
            s = btn.property("sv")
            if s <= score:
                btn.setStyleSheet(STAR_CSS.format(
                    bg=f"{c}20", fg=c, border=c, hover_bg=f"{c}40"
                ))
            else:
                btn.setStyleSheet(STAR_CSS.format(
                    bg="transparent", fg=BORDER, border=BORDER, hover_bg=f"{c}20"
                ))
        self.qual_lbl.setText(SCORE_LABEL[score])
        self.qual_lbl.setStyleSheet(
            f"color: {c}; font-size: 11px; font-weight: 600; background: transparent; border: none;"
        )
        self.score_num.setText(str(score))
        self.score_num.setStyleSheet(
            f"color: {c}; font-size: 20px; font-weight: 900;"
            " background: transparent; border: none;"
        )
        # Mettre en évidence la carte sélectionnée
        self.setStyleSheet(
            f"QFrame {{ background: {BG_CARD}; border: 1px solid {c}4a;"
            f" border-radius: 14px; }}"
        )

    def get_score(self) -> int:
        return self._score

    def set_name(self, name: str):
        self.name_lbl.setText(name)


class EvaluationPageDesigner:
    """
    Injecte le design premium dans verticalLayout_30 de widget_28.
    N'essaie JAMAIS de remplacer le layout Qt (impossible après loadUi).
    Vide l'existant et remplace le contenu dans le même layout.
    """

    def __init__(self, main_window):
        self.mw = main_window
        self.cards: List[CriterionCard] = []
        self._scores: List[int] = [1] * 10
        self._avg_lbl = None
        self._bar = None
        self._pct_lbl = None

    # ──────────────────────────────────────────────────────────────────────────
    def build(self, criteria_names: Optional[List[str]] = None):
        names = criteria_names or [
            "Ponctualité", "Organisation du cours", "Disponibilité",
            "Interaction avec les étudiants", "Utilisation des exemples",
            "Respect du programme", "Qualité des supports",
            "Évaluation des étudiants", "Respect des étudiants",
            "Pertinence du contenu",
        ]

        container: QWidget = getattr(self.mw, "widget_28", None)
        if container is None:
            return

        # ── Récupérer le layout existant (jamais en créer un nouveau) ──────
        layout: QVBoxLayout = container.layout()
        if layout is None:
            layout = QVBoxLayout(container)

        # Nettoyer et détruire TOUS les enfants existants dans container (anciens labels .ui, radios, etc.)
        for child in container.findChildren(QWidget):
            child.hide()
            child.setParent(None)
            child.deleteLater()

        # Vider récursivement le layout
        def _clear_layout(l):
            if l is None:
                return
            while l.count():
                item = l.takeAt(0)
                w = item.widget()
                if w:
                    w.hide()
                    w.setParent(None)
                    w.deleteLater()
                sub = item.layout()
                if sub:
                    _clear_layout(sub)

        _clear_layout(layout)

        container.setStyleSheet(
            f"QWidget {{ background: {BG_DEEP}; border: none; }}"
        )
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(8)

        # ── 1. Bandeau score global ──────────────────────────────────────────
        layout.addWidget(self._make_banner(container))

        # ── 2. Cartes critères directement dans le layout (pas de scroll imbriquée) ──
        self.cards = []
        self._scores = [1] * len(names)

        for i, name in enumerate(names):
            card = CriterionCard(i, name, container)
            card.scoreChanged.connect(self._on_score_changed)
            layout.addWidget(card)
            self.cards.append(card)

        layout.addStretch(1)

        self._update_banner()

    # ──────────────────────────────────────────────────────────────────────────
    def _make_banner(self, parent) -> QWidget:
        banner = QFrame(parent)
        banner.setAttribute(Qt.WA_StyledBackground, True)
        banner.setFixedHeight(64)
        banner.setStyleSheet(
            f"QFrame {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 #1a3a5c, stop:1 {BG_DEEP}); "
            f"border: 1px solid {BORDER}; border-radius: 12px; }}"
        )

        row = QHBoxLayout(banner)
        row.setContentsMargins(18, 0, 18, 0)
        row.setSpacing(10)

        ico = QLabel("📊")
        ico.setStyleSheet("font-size: 22px; background: transparent; border: none;")
        row.addWidget(ico)

        col = QVBoxLayout()
        col.setSpacing(1)
        sub = QLabel("Score global")
        sub.setStyleSheet(f"color: {TEXT_LO}; font-size: 11px; background: transparent; border: none;")
        self._avg_lbl = QLabel("5.0 / 5.0")
        self._avg_lbl.setStyleSheet(
            f"color: {GREEN}; font-size: 19px; font-weight: 900; background: transparent; border: none;"
        )
        col.addWidget(sub)
        col.addWidget(self._avg_lbl)
        row.addLayout(col)
        row.addStretch()

        bar_col = QVBoxLayout()
        bar_col.setSpacing(3)
        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(100)
        self._bar.setFixedSize(180, 8)
        self._bar.setTextVisible(False)
        self._bar.setStyleSheet(
            f"QProgressBar {{ background: {BORDER}; border-radius: 4px; border: none; }}"
            f"QProgressBar::chunk {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {BLUE}, stop:1 {GREEN}); border-radius: 4px; }}"
        )
        self._pct_lbl = QLabel("100%")
        self._pct_lbl.setAlignment(Qt.AlignRight)
        self._pct_lbl.setStyleSheet(
            f"color: {TEXT_LO}; font-size: 10px; background: transparent; border: none;"
        )
        bar_col.addWidget(self._bar)
        bar_col.addWidget(self._pct_lbl)
        row.addLayout(bar_col)

        return banner

    # ──────────────────────────────────────────────────────────────────────────
    def _on_score_changed(self, idx: int, score: int):
        if idx < len(self._scores):
            self._scores[idx] = score
        self._update_banner()

    def _update_banner(self):
        if not self._scores:
            return
        avg = sum(self._scores) / len(self._scores)
        pct = int(avg / 5 * 100)
        c = GREEN if avg >= 4 else (BLUE if avg >= 3 else (AMBER if avg >= 2 else RED))
        if self._avg_lbl:
            self._avg_lbl.setText(f"{avg:.1f} / 5.0")
            self._avg_lbl.setStyleSheet(
                f"color: {c}; font-size: 19px; font-weight: 900; background: transparent; border: none;"
            )
        if self._bar:
            self._bar.setValue(pct)
        if self._pct_lbl:
            self._pct_lbl.setText(f"{pct}%")

    # ──────────────────────────────────────────────────────────────────────────
    def get_scores(self) -> List[int]:
        return [c.get_score() for c in self.cards]

    def update_criteria_names(self, names: List[str]):
        for i, card in enumerate(self.cards):
            if i < len(names):
                card.set_name(names[i])

    def reset(self):
        """Remet toutes les cartes à 1 étoile et réinitialise le bandeau."""
        self._scores = [1] * len(self.cards)
        for card in self.cards:
            card._score = 1
            card._refresh(1)
        self._update_banner()
        # Vider les combos professeur et cours
        for attr in ("comboBox", "comboBox_2"):
            combo = getattr(self.mw, attr, None)
            if combo:
                combo.setCurrentIndex(0)


__all__ = ["EvaluationPageDesigner", "CriterionCard"]

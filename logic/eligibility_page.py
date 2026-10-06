"""
Design sobre, corporate et adaptatif de la page d'Éligibilité.
Thème dark minimaliste (#0f172a, #1e293b, #334155).
Affichage en grille 2x2 des 4 critères administratifs pour un ajustement parfait à l'écran.
"""
from typing import Optional, Dict, Any
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QFrame, QSizePolicy, QInputDialog
)

# ─── Palette Sobre & Épurée ───────────────────────────────────────────────────
BG         = "#0f172a"
CARD       = "#1e293b"
CARD_INNER = "#0f172a"
CARD_HOVER = "#273549"
BORDER     = "#334155"
BLUE       = "#3b82f6"
BLUE_HOVER = "#2563eb"
GREEN      = "#10b981"
AMBER      = "#f59e0b"
RED        = "#ef4444"
TEXT_HI    = "#f8fafc"
TEXT_MID   = "#cbd5e1"
TEXT_LO    = "#94a3b8"
TEXT_MUTED = "#64748b"

CRITERIA_META = [
    {
        "key": "enrollment",
        "num": "01",
        "title": "Inscription Universitaire",
        "desc": "Validation administrative du dossier d'inscription",
    },
    {
        "key": "academic_fees",
        "num": "02",
        "title": "Frais Académiques",
        "desc": "Régularisation des tranches de scolarité",
    },
    {
        "key": "laboratory_fees",
        "num": "03",
        "title": "Frais de Laboratoire",
        "desc": "Accès aux travaux pratiques et plateformes scientifiques",
    },
    {
        "key": "access_fees",
        "num": "04",
        "title": "Frais d'Accès & Bibliothèque",
        "desc": "Droits d'accès aux infrastructures et ressources numériques",
    },
]


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


class EligibilityPageDesigner:
    """
    Gestionnaire et constructeur du design de la page Éligibilité.
    """

    def __init__(self, main_window):
        self.mw = main_window
        self._stat_widgets: Dict[str, Any] = {}
        self._card_widgets: Dict[str, Dict[str, QLabel]] = {}
        self._action_btn: Optional[QPushButton] = None
        self._admin_btn: Optional[QPushButton] = None

    def build(self):
        """Construit l'interface complète de la page éligibilité."""
        page_5: QWidget = getattr(self.mw, "page_5", None)
        if page_5:
            page_5.setStyleSheet(f"QWidget#page_5 {{ background: {BG}; }}")

        container: QWidget = getattr(self.mw, "widget_25", None)
        if container is None:
            return

        container.setStyleSheet(f"background: {BG}; border: none;")

        layout: QVBoxLayout = container.layout()
        if layout is None:
            layout = QVBoxLayout(container)
        else:
            _clear_layout_safely(layout)

        # Marges équilibrées et compactes (s'adaptent à toutes les résolutions)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(12)

        # 1. En-tête
        layout.addWidget(self._make_header())

        # 2. Carte Principale d'État (Hero Card)
        layout.addWidget(self._make_status_card())

        # 3. Grille 2x2 des 4 critères
        grid_title = QLabel("CONDITIONS D'ÉLIGIBILITÉ REQUISES")
        grid_title.setStyleSheet(
            f"color: {TEXT_MUTED}; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;"
            " background: transparent; border: none; padding-top: 4px;"
        )
        layout.addWidget(grid_title)

        grid_w = QWidget()
        grid_w.setStyleSheet("background: transparent; border: none;")
        grid_layout = QGridLayout(grid_w)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(10)
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)

        for i, meta in enumerate(CRITERIA_META):
            row = i // 2
            col = i % 2
            card = self._make_criterion_card(meta)
            grid_layout.addWidget(card, row, col)

        layout.addWidget(grid_w)

        # 4. Pied de page / Actions
        layout.addWidget(self._make_footer_actions())
        layout.addStretch(1)

        # État initial
        self._show_initial_state()

    # ──────────────────────────────────────────────────────────────────────────
    # 1. EN-TÊTE
    # ──────────────────────────────────────────────────────────────────────────
    def _make_header(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(
            f"QWidget {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 8px; }}"
        )
        row = QHBoxLayout(w)
        row.setContentsMargins(16, 10, 16, 10)
        row.setSpacing(14)

        col = QVBoxLayout()
        col.setSpacing(1)
        title = QLabel("Contrôle d'Éligibilité aux Évaluations")
        title.setStyleSheet(f"color: {TEXT_HI}; font-size: 16px; font-weight: 700; background: transparent; border: none;")

        self._stat_widgets["header_sub"] = QLabel("Vérification en temps réel des prérequis académiques et administratifs")
        self._stat_widgets["header_sub"].setStyleSheet(f"color: {TEXT_LO}; font-size: 12px; background: transparent; border: none;")
        col.addWidget(title)
        col.addWidget(self._stat_widgets["header_sub"])
        row.addLayout(col, stretch=1)

        # Bouton d'administration (pour superviseur / admin)
        self._admin_btn = QPushButton("Gestion administrative ⚙")
        self._admin_btn.setCursor(Qt.PointingHandCursor)
        self._admin_btn.setStyleSheet(f"""
            QPushButton {{
                background: {CARD_INNER}; color: {TEXT_MID}; border: 1px solid {BORDER};
                border-radius: 6px; padding: 6px 14px; font-size: 12px; font-weight: 600;
            }}
            QPushButton:hover {{
                border-color: {BLUE}; color: {TEXT_HI};
            }}
        """)
        self._admin_btn.clicked.connect(self._on_admin_click)
        row.addWidget(self._admin_btn)

        return w

    # ──────────────────────────────────────────────────────────────────────────
    # 2. CARTE D'ÉTAT PRINCIPALE (HERO)
    # ──────────────────────────────────────────────────────────────────────────
    def _make_status_card(self) -> QWidget:
        card = QWidget()
        card.setFixedHeight(80)
        card.setStyleSheet(
            f"QWidget {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 8px; }}"
        )
        row = QHBoxLayout(card)
        row.setContentsMargins(18, 12, 18, 12)
        row.setSpacing(16)

        # Badge indicateur circulaire / statut
        self._stat_widgets["status_icon"] = QLabel("✓")
        self._stat_widgets["status_icon"].setFixedSize(44, 44)
        self._stat_widgets["status_icon"].setAlignment(Qt.AlignCenter)
        self._stat_widgets["status_icon"].setStyleSheet(
            f"background: {CARD_INNER}; color: {TEXT_LO}; border: 1px solid {BORDER};"
            " border-radius: 22px; font-size: 18px; font-weight: 800;"
        )
        row.addWidget(self._stat_widgets["status_icon"])

        # Texte principal
        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        self._stat_widgets["status_title"] = QLabel("Vérification de votre dossier...")
        self._stat_widgets["status_title"].setStyleSheet(
            f"color: {TEXT_HI}; font-size: 15px; font-weight: 700; background: transparent; border: none;"
        )

        self._stat_widgets["status_desc"] = QLabel("Chargement des critères depuis l'API universitaire...")
        self._stat_widgets["status_desc"].setStyleSheet(
            f"color: {TEXT_LO}; font-size: 12px; background: transparent; border: none;"
        )

        text_col.addWidget(self._stat_widgets["status_title"])
        text_col.addWidget(self._stat_widgets["status_desc"])
        row.addLayout(text_col, stretch=1)

        # Badge pill à droite
        self._stat_widgets["status_badge"] = QLabel("En attente")
        self._stat_widgets["status_badge"].setFixedHeight(28)
        self._stat_widgets["status_badge"].setAlignment(Qt.AlignCenter)
        self._stat_widgets["status_badge"].setStyleSheet(
            f"background: {CARD_INNER}; color: {TEXT_LO}; border: 1px solid {BORDER};"
            " border-radius: 14px; padding: 0 14px; font-size: 12px; font-weight: 600;"
        )
        row.addWidget(self._stat_widgets["status_badge"])

        return card

    # ──────────────────────────────────────────────────────────────────────────
    # 3. CARTE CRITÈRE INDIVIDUELLE (GRILLE 2x2)
    # ──────────────────────────────────────────────────────────────────────────
    def _make_criterion_card(self, meta: Dict[str, str]) -> QWidget:
        key = meta["key"]

        card = QWidget()
        card.setFixedHeight(64)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setStyleSheet(
            f"QWidget {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 8px; }}"
            f"QWidget:hover {{ background: {CARD_HOVER}; border-color: {BLUE}; }}"
        )

        row = QHBoxLayout(card)
        row.setContentsMargins(14, 8, 14, 8)
        row.setSpacing(12)

        # Numéro discret
        num_lbl = QLabel(meta["num"])
        num_lbl.setFixedSize(28, 28)
        num_lbl.setAlignment(Qt.AlignCenter)
        num_lbl.setStyleSheet(
            f"background: {CARD_INNER}; color: {TEXT_LO}; border: 1px solid {BORDER};"
            " border-radius: 14px; font-size: 11px; font-weight: 700;"
        )
        row.addWidget(num_lbl)

        # Textes
        col = QVBoxLayout()
        col.setSpacing(1)
        tit = QLabel(meta["title"])
        tit.setStyleSheet(f"color: {TEXT_HI}; font-size: 13px; font-weight: 600; background: transparent; border: none;")
        desc = QLabel(meta["desc"])
        desc.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; background: transparent; border: none;")
        col.addWidget(tit)
        col.addWidget(desc)
        row.addLayout(col, stretch=1)

        # Badge statut du critère
        badge = QLabel("—")
        badge.setFixedHeight(24)
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(
            f"background: {CARD_INNER}; color: {TEXT_LO}; border: 1px solid {BORDER};"
            " border-radius: 12px; padding: 0 10px; font-size: 11px; font-weight: 600;"
        )
        row.addWidget(badge)

        self._card_widgets[key] = {
            "card": card,
            "badge": badge,
            "num": num_lbl,
        }

        return card

    # ──────────────────────────────────────────────────────────────────────────
    # 4. PIED DE PAGE / ACTIONS
    # ──────────────────────────────────────────────────────────────────────────
    def _make_footer_actions(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 4, 0, 0)
        row.setSpacing(12)

        self._stat_widgets["footer_hint"] = QLabel(
            "L'éligibilité est requise pour pouvoir accéder aux formulaires d'évaluation des enseignants."
        )
        self._stat_widgets["footer_hint"].setStyleSheet(
            f"color: {TEXT_MUTED}; font-size: 11px; background: transparent; border: none;"
        )
        row.addWidget(self._stat_widgets["footer_hint"], stretch=1)

        # Bouton d'action directe vers les évaluations
        self._action_btn = QPushButton("Accéder aux Évaluations →")
        self._action_btn.setCursor(Qt.PointingHandCursor)
        self._action_btn.setFixedHeight(34)
        self._action_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BLUE}; color: white; border: none;
                border-radius: 6px; padding: 0 18px; font-size: 12px; font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {BLUE_HOVER};
            }}
            QPushButton:disabled {{
                background-color: {CARD}; color: {TEXT_MUTED}; border: 1px solid {BORDER};
            }}
        """)
        self._action_btn.clicked.connect(self._go_to_evaluations)
        row.addWidget(self._action_btn)

        return w

    # ──────────────────────────────────────────────────────────────────────────
    # 5. MISE À JOUR EN TEMPS RÉEL (APPELÉE PAR load_eligibility)
    # ──────────────────────────────────────────────────────────────────────────
    def update_display(self, elig: Optional[Dict[str, Any]], user_data: Optional[Dict[str, Any]] = None):
        """Met à jour l'ensemble des éléments avec les données de l'API."""
        role = (user_data or {}).get("role", "STUDENT").upper()
        name = (user_data or {}).get("name") or (user_data or {}).get("email") or "Étudiant"

        # Mode superviseur / admin
        if role in ["ADMIN", "SUPER_ADMIN", "PROFESSOR"]:
            if self._admin_btn:
                self._admin_btn.setVisible(True)

            self._stat_widgets["header_sub"].setText(f"Session {role} : {name} — Supervision des prérequis étudiants")
            self._stat_widgets["status_icon"].setText("⚙")
            self._stat_widgets["status_icon"].setStyleSheet(
                f"background: {CARD_INNER}; color: {BLUE}; border: 1px solid {BLUE};"
                " border-radius: 22px; font-size: 18px; font-weight: 800;"
            )
            self._stat_widgets["status_title"].setText("Mode Supervision Administrative")
            self._stat_widgets["status_desc"].setText(
                "Vous pouvez vérifier ou régulariser l'éligibilité de n'importe quel étudiant via le bouton ci-dessus."
            )
            self._stat_widgets["status_badge"].setText("Supervision")
            self._stat_widgets["status_badge"].setStyleSheet(
                f"background: {CARD_INNER}; color: {BLUE}; border: 1px solid {BLUE};"
                " border-radius: 14px; padding: 0 14px; font-size: 12px; font-weight: 600;"
            )

            # Activer les 4 critères en aperçu neutre
            for meta in CRITERIA_META:
                key = meta["key"]
                if key in self._card_widgets:
                    self._card_widgets[key]["badge"].setText("Supervisé")
                    self._card_widgets[key]["badge"].setStyleSheet(
                        f"background: {CARD_INNER}; color: {TEXT_MID}; border: 1px solid {BORDER};"
                        " border-radius: 12px; padding: 0 10px; font-size: 11px; font-weight: 600;"
                    )

            if self._action_btn:
                self._action_btn.setEnabled(True)
                self._action_btn.setText("Voir les Évaluations →")
            return

        # Mode Étudiant
        if self._admin_btn:
            self._admin_btn.setVisible(False)

        self._stat_widgets["header_sub"].setText(f"Dossier de {name} — Année académique en cours")

        if elig is None:
            # Dossier non trouvé
            self._stat_widgets["status_icon"].setText("⏳")
            self._stat_widgets["status_icon"].setStyleSheet(
                f"background: {CARD_INNER}; color: {AMBER}; border: 1px solid {AMBER};"
                " border-radius: 22px; font-size: 18px; font-weight: 800;"
            )
            self._stat_widgets["status_title"].setText("Dossier en cours de traitement")
            self._stat_widgets["status_desc"].setText(
                "Votre dossier d'éligibilité n'est pas encore finalisé par l'administration académique."
            )
            self._stat_widgets["status_badge"].setText("En attente")
            self._stat_widgets["status_badge"].setStyleSheet(
                f"background: {CARD_INNER}; color: {AMBER}; border: 1px solid {AMBER};"
                " border-radius: 14px; padding: 0 14px; font-size: 12px; font-weight: 600;"
            )
            for meta in CRITERIA_META:
                key = meta["key"]
                if key in self._card_widgets:
                    self._card_widgets[key]["badge"].setText("En attente")
                    self._card_widgets[key]["badge"].setStyleSheet(
                        f"background: {CARD_INNER}; color: {TEXT_MUTED}; border: 1px solid {BORDER};"
                        " border-radius: 12px; padding: 0 10px; font-size: 11px; font-weight: 600;"
                    )
            if self._action_btn:
                self._action_btn.setEnabled(False)
            return

        # Étudiant avec dossier
        is_eligible = bool(elig.get("eligible", False))

        criteria_vals = {
            "enrollment": bool(elig.get("enrollment", False)),
            "academic_fees": bool(elig.get("academic_fees", False)),
            "laboratory_fees": bool(elig.get("laboratory_fees", False)),
            "access_fees": bool(elig.get("access_fees", False)),
        }

        # Mise à jour des 4 cartes
        for meta in CRITERIA_META:
            key = meta["key"]
            ok = criteria_vals.get(key, False)
            if key in self._card_widgets:
                badge = self._card_widgets[key]["badge"]
                card = self._card_widgets[key]["card"]
                num = self._card_widgets[key]["num"]

                if ok:
                    badge.setText("Validé ✓")
                    badge.setStyleSheet(
                        f"background: {CARD_INNER}; color: {GREEN}; border: 1px solid {GREEN};"
                        " border-radius: 12px; padding: 0 10px; font-size: 11px; font-weight: 700;"
                    )
                    card.setStyleSheet(
                        f"QWidget {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 8px; }}"
                        f"QWidget:hover {{ background: {CARD_HOVER}; border-color: {GREEN}; }}"
                    )
                    num.setStyleSheet(
                        f"background: {CARD_INNER}; color: {GREEN}; border: 1px solid {GREEN};"
                        " border-radius: 14px; font-size: 11px; font-weight: 700;"
                    )
                else:
                    badge.setText("Non régularisé ✗")
                    badge.setStyleSheet(
                        f"background: {CARD_INNER}; color: {AMBER}; border: 1px solid {AMBER};"
                        " border-radius: 12px; padding: 0 10px; font-size: 11px; font-weight: 600;"
                    )
                    card.setStyleSheet(
                        f"QWidget {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 8px; }}"
                        f"QWidget:hover {{ background: {CARD_HOVER}; border-color: {AMBER}; }}"
                    )
                    num.setStyleSheet(
                        f"background: {CARD_INNER}; color: {AMBER}; border: 1px solid {AMBER};"
                        " border-radius: 14px; font-size: 11px; font-weight: 700;"
                    )

        # Carte d'état générale
        if is_eligible:
            self._stat_widgets["status_icon"].setText("✓")
            self._stat_widgets["status_icon"].setStyleSheet(
                f"background: {CARD_INNER}; color: {GREEN}; border: 1px solid {GREEN};"
                " border-radius: 22px; font-size: 20px; font-weight: 800;"
            )
            self._stat_widgets["status_title"].setText("Dossier Validé — Vous êtes éligible")
            self._stat_widgets["status_desc"].setText(
                "Tous vos prérequis académiques et financiers sont en règle. Vous pouvez évaluer vos professeurs."
            )
            self._stat_widgets["status_badge"].setText("Éligible")
            self._stat_widgets["status_badge"].setStyleSheet(
                f"background: {CARD_INNER}; color: {GREEN}; border: 1px solid {GREEN};"
                " border-radius: 14px; padding: 0 14px; font-size: 12px; font-weight: 700;"
            )
            if self._action_btn:
                self._action_btn.setEnabled(True)
                self._action_btn.setText("Accéder aux Évaluations →")
            self._stat_widgets["footer_hint"].setText(
                "Vos droits d'évaluation sont actifs pour l'ensemble des cours auxquels vous êtes inscrit."
            )
        else:
            reasons = elig.get("reasons") or ["Certains frais universitaires restent à régulariser."]
            reasons_txt = ", ".join(reasons) if isinstance(reasons, list) else str(reasons)

            self._stat_widgets["status_icon"].setText("!")
            self._stat_widgets["status_icon"].setStyleSheet(
                f"background: {CARD_INNER}; color: {AMBER}; border: 1px solid {AMBER};"
                " border-radius: 22px; font-size: 20px; font-weight: 800;"
            )
            self._stat_widgets["status_title"].setText("Dossier Incomplet — Non éligible")
            self._stat_widgets["status_desc"].setText(f"Motif(s) : {reasons_txt}")
            self._stat_widgets["status_badge"].setText("Non éligible")
            self._stat_widgets["status_badge"].setStyleSheet(
                f"background: {CARD_INNER}; color: {AMBER}; border: 1px solid {AMBER};"
                " border-radius: 14px; padding: 0 14px; font-size: 12px; font-weight: 700;"
            )
            if self._action_btn:
                self._action_btn.setEnabled(False)
                self._action_btn.setText("Évaluation bloquée")
            self._stat_widgets["footer_hint"].setText(
                "Veuillez régulariser votre dossier auprès des services académiques pour débloquer les évaluations."
            )

    def _show_initial_state(self):
        """État par défaut avant le chargement des données."""
        for meta in CRITERIA_META:
            key = meta["key"]
            if key in self._card_widgets:
                self._card_widgets[key]["badge"].setText("Vérification...")

    def _on_admin_click(self):
        """Déclenche le dialogue admin si disponible sur la fenêtre principale."""
        if hasattr(self.mw, "_open_admin_eligibility_dialog"):
            self.mw._open_admin_eligibility_dialog()

    def _go_to_evaluations(self):
        """Navigation rapide vers la page d'évaluation."""
        if hasattr(self.mw, "go_to_page") and hasattr(self.mw, "PAGE_EVALUATIONS"):
            self.mw.go_to_page(self.mw.PAGE_EVALUATIONS)


__all__ = ["EligibilityPageDesigner"]

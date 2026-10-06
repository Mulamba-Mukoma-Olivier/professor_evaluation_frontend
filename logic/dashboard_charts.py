"""
dashboard_charts.py
────────────────────
Graphiques matplotlib du dashboard — Système d'Évaluation des Professeurs.
Thème Dark Slate Corporate.

7 graphiques :
  1. render_top_professors_chart  — Top professeurs par note moyenne (barres H)
  2. render_score_distribution    — Distribution des notes 1→5 (histogramme)
  3. render_timeline_chart        — Évolution mensuelle des évaluations (courbe)
  4. render_boxplot               — Dispersion par professeur (boxplot)
  5. render_department_radar      — Radar / comparaison par département (barres groupées)
  6. render_heatmap               — Heatmap prof × critère
  7. render_stacked_bars          — Proportion note/niveau par professeur
"""
from __future__ import annotations
from collections import defaultdict, Counter
from typing import List, Dict, Any

import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.ticker import MaxNLocator
from PyQt5.QtWidgets import QVBoxLayout, QWidget

# ─── Palette Dark Slate ────────────────────────────────────────────────────────
SURFACE    = "#1e293b"
CARD_ALT   = "#162032"
BORDER     = "#334155"
BLUE       = "#3b82f6"
BLUE_LIGHT = "#60a5fa"
GREEN      = "#10b981"
AMBER      = "#f59e0b"
ORANGE     = "#f97316"
YELLOW     = "#facc15"
VIOLET     = "#8b5cf6"
RED        = "#f87171"
TEAL       = "#14b8a6"
TEXT_HI    = "#f8fafc"
TEXT_MID   = "#cbd5e1"
TEXT_LO    = "#94a3b8"
TEXT_MUTED = "#64748b"
PALETTE    = [BLUE, GREEN, AMBER, VIOLET, TEAL, ORANGE, RED, BLUE_LIGHT]

plt.rcParams.update({"font.family": "sans-serif", "font.size": 9})


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _dark(fig: Figure, ax, title: str = "") -> None:
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=TEXT_LO, labelsize=8, length=0)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_edgecolor(BORDER)
    ax.spines["bottom"].set_edgecolor(BORDER)
    if title:
        ax.set_title(title, color=TEXT_HI, fontsize=9.5, fontweight="bold",
                     pad=10, loc="left")


def _embed(container: QWidget, fig: Figure) -> None:
    canvas = FigureCanvas(fig)
    canvas.setStyleSheet("background: transparent;")
    lay = container.layout()
    if lay is None:
        lay = QVBoxLayout(container)
        lay.setContentsMargins(4, 4, 4, 4)
        container.setLayout(lay)
    else:
        while lay.count():
            item = lay.takeAt(0)
            w = item.widget()
            if w:
                w.hide()
                w.deleteLater()
    lay.addWidget(canvas)
    canvas.draw()


def _avg(ev: dict) -> float | None:
    t = ev.get("total_score")
    if t is not None:
        return float(t)
    ans = ev.get("answers", [])
    s = [a["score"] for a in ans if a.get("score") is not None]
    return sum(s) / len(s) if s else None


def _empty(container: QWidget, msg: str) -> None:
    fig = Figure(figsize=(5, 3), tight_layout=True)
    ax = fig.add_subplot(111)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    ax.text(.5, .52, "— — —", transform=ax.transAxes,
            ha="center", va="center", fontsize=16, color=TEXT_MUTED, alpha=0.3)
    ax.text(.5, .30, msg, transform=ax.transAxes,
            ha="center", va="center", color=TEXT_MUTED, fontsize=9, linespacing=1.7)
    _embed(container, fig)


# ─────────────────────────────────────────────────────────────────────────────
# 1. TOP PROFESSEURS — Barres horizontales avec note moyenne
# ─────────────────────────────────────────────────────────────────────────────
def render_top_professors_chart(
    container: QWidget, evaluations: List[dict], professors: List[dict]
) -> None:
    prof_name = {
        p["id"]: f"{p.get('last_name','')}, {p.get('first_name','')[0]}."
        if p.get("first_name") else p.get("last_name", f"#{p['id']}")
        for p in professors
    }
    prof_dept = {p["id"]: p.get("department", "") for p in professors}

    scores: Dict[int, list] = defaultdict(list)
    for ev in evaluations:
        pid = ev.get("professor_id")
        s = _avg(ev)
        if pid and s is not None:
            scores[pid].append(s)

    if not scores:
        _empty(container, "Aucune donnée d'évaluation.\nEn attente des premières soumissions.")
        return

    avg = {pid: sum(v) / len(v) for pid, v in scores.items()}
    items = sorted(avg.items(), key=lambda x: x[1], reverse=True)[:8]
    labels = [prof_name.get(pid, f"#{pid}") for pid, _ in items]
    values = [v for _, v in items]
    nb_ev  = [len(scores[pid]) for pid, _ in items]
    max_v  = max(values) if values else 5

    bar_colors = [
        GREEN if v >= 4.0 else (BLUE if v >= 3.0 else (AMBER if v >= 2.0 else RED))
        for v in values
    ]

    fig = Figure(figsize=(5.5, 3.5), tight_layout=True)
    ax = fig.add_subplot(111)
    _dark(fig, ax, "Classement des enseignants")

    for i in range(len(labels)):
        ax.barh(i, max_v * 1.1, color=CARD_ALT, height=0.55, zorder=0, edgecolor="none")
    bars = ax.barh(labels, values, color=bar_colors, height=0.55, edgecolor="none", zorder=2)

    ax.set_xlim(0, max_v * 1.28)
    ax.invert_yaxis()
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, color=TEXT_MID, fontsize=8)
    ax.xaxis.set_major_locator(MaxNLocator(integer=False, nbins=4))
    ax.tick_params(axis="x", colors=TEXT_MUTED)
    ax.grid(axis="x", color=BORDER, linestyle="--", linewidth=0.5, alpha=0.5, zorder=1)
    ax.spines["left"].set_visible(False)

    for bar, val, n in zip(bars, values, nb_ev):
        ax.text(val + max_v * 0.02, bar.get_y() + bar.get_height() / 2,
                f"{val:.2f} /5  ({n} éval.)",
                va="center", color=TEXT_HI, fontsize=7.5, fontweight="bold")

    _embed(container, fig)


# ─────────────────────────────────────────────────────────────────────────────
# 2. DISTRIBUTION DES NOTES — Histogramme 1→5 pour toutes les réponses
# ─────────────────────────────────────────────────────────────────────────────
def render_score_distribution(
    container: QWidget, evaluations: List[dict], professors: List[dict]
) -> None:
    all_scores: list = []
    for ev in evaluations:
        for ans in ev.get("answers", []):
            s = ans.get("score")
            if s is not None:
                all_scores.append(int(s))

    if not all_scores:
        # Fallback: utiliser total_score
        for ev in evaluations:
            s = ev.get("total_score")
            if s is not None:
                all_scores.append(round(float(s)))
    if not all_scores:
        _empty(container, "Pas de données de notation\ndisponibles.")
        return

    counts = Counter(all_scores)
    levels = [1, 2, 3, 4, 5]
    level_labels = ["Médiocre", "Insuffisant", "Moyen", "Bien", "Excellent"]
    vals = [counts.get(l, 0) for l in levels]
    bar_colors = [RED, ORANGE, AMBER, BLUE, GREEN]
    total = sum(vals)

    fig = Figure(figsize=(4.2, 3.5), tight_layout=True)
    ax = fig.add_subplot(111)
    _dark(fig, ax, "Distribution des notes")

    bars = ax.bar(level_labels, vals, color=bar_colors, edgecolor=SURFACE,
                  linewidth=0.8, zorder=2, width=0.6)

    ax.grid(axis="y", color=BORDER, linestyle="--", linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)
    ax.set_ylabel("Nb de réponses", color=TEXT_LO, fontsize=8.5)
    ax.tick_params(axis="x", colors=TEXT_MID, rotation=15)
    ax.tick_params(axis="y", colors=TEXT_MUTED)
    ax.spines["left"].set_edgecolor(BORDER)

    for bar, val in zip(bars, vals):
        if val > 0:
            pct = val / total * 100
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(vals) * 0.02,
                    f"{pct:.0f}%", ha="center", color=TEXT_HI,
                    fontsize=7.5, fontweight="bold")

    _embed(container, fig)


# ─────────────────────────────────────────────────────────────────────────────
# 3. TIMELINE — Évaluations soumises par mois (courbe area)
# ─────────────────────────────────────────────────────────────────────────────
def render_timeline_chart(container: QWidget, evaluations: List[dict]) -> None:
    monthly: Dict[str, int] = Counter()
    for ev in evaluations:
        d = str(ev.get("submitted_at", ""))[:7]
        if len(d) == 7:
            monthly[d] += 1

    if not monthly:
        _empty(container, "Aucune donnée temporelle.\nLes évaluations soumises apparaîtront ici.")
        return

    months = sorted(monthly)
    counts = [monthly[m] for m in months]
    xlbls  = [f"{m[5:]}/{m[2:4]}" for m in months]
    x      = list(range(len(counts)))
    step   = max(1, len(xlbls) // 8)

    fig = Figure(figsize=(8, 2.8), tight_layout=True)
    ax = fig.add_subplot(111)
    _dark(fig, ax, "Activité mensuelle — Évaluations soumises")

    ax.fill_between(x, counts, alpha=0.13, color=BLUE, zorder=1)
    ax.plot(x, counts, color=BLUE, linewidth=2.5, zorder=3)
    ax.scatter(x, counts, color=BLUE, s=42, zorder=4,
               edgecolors=SURFACE, linewidths=1.5)

    for i, v in enumerate(counts):
        ax.annotate(str(v), (i, v), textcoords="offset points", xytext=(0, 8),
                    ha="center", color=TEXT_HI, fontsize=8, fontweight="bold")

    vis = list(range(0, len(xlbls), step))
    ax.set_xticks(vis)
    ax.set_xticklabels([xlbls[i] for i in vis], color=TEXT_LO, fontsize=8,
                       rotation=25, ha="right")
    ax.set_yticks([])
    ax.set_xlim(-0.4, len(x) - 0.6)
    ax.set_ylim(0, max(counts) * 1.42 if counts else 5)
    ax.grid(axis="y", color=BORDER, linestyle="--", linewidth=0.5, alpha=0.4)
    ax.spines["left"].set_visible(False)

    _embed(container, fig)


# ─────────────────────────────────────────────────────────────────────────────
# 4. BOXPLOT — Dispersion des notes par professeur
# ─────────────────────────────────────────────────────────────────────────────
def render_boxplot(
    container: QWidget, evaluations: List[dict], professors: List[dict]
) -> None:
    prof_name = {p["id"]: p.get("last_name", f"#{p['id']}")[:10] for p in professors}
    scores: Dict[int, list] = defaultdict(list)
    for ev in evaluations:
        pid = ev.get("professor_id")
        s = _avg(ev)
        if pid and s is not None:
            scores[pid].append(s)

    eligible = {pid: v for pid, v in scores.items() if len(v) >= 2}
    if not eligible:
        _empty(container, "Données insuffisantes.\n(≥2 évaluations par enseignant requises)")
        return

    items = sorted(eligible.items(), key=lambda x: sum(x[1]) / len(x[1]), reverse=True)[:8]
    labels = [prof_name.get(pid, f"#{pid}") for pid, _ in items]
    data   = [v for _, v in items]

    fig = Figure(figsize=(5.5, 3.5), tight_layout=True)
    ax = fig.add_subplot(111)
    _dark(fig, ax, "Variabilité des notes par enseignant")

    ax.boxplot(
        data, vert=True, patch_artist=True, labels=labels,
        medianprops=dict(color=AMBER, linewidth=2.5),
        boxprops=dict(facecolor=BLUE + "33", edgecolor=BLUE, linewidth=1.5),
        whiskerprops=dict(color=TEXT_LO, linewidth=1.5, linestyle="--"),
        capprops=dict(color=TEXT_LO, linewidth=1.5),
        flierprops=dict(marker="o", markerfacecolor=RED, markersize=4,
                        alpha=0.7, markeredgewidth=0),
    )

    ax.set_ylim(0, 5.5)
    ax.set_ylabel("Score (/5)", color=TEXT_LO, fontsize=8.5)
    ax.tick_params(axis="x", colors=TEXT_MID, labelsize=8, rotation=25)
    ax.tick_params(axis="y", colors=TEXT_MUTED, labelsize=8)
    ax.grid(axis="y", color=BORDER, linestyle="--", linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)

    # Ligne de référence à 3.0 (seuil satisfaisant)
    ax.axhline(3.0, color=AMBER, linewidth=1, linestyle=":", alpha=0.7)
    ax.text(len(data) - 0.1, 3.05, "Seuil 3.0", color=AMBER, fontsize=7, ha="right")

    _embed(container, fig)


# ─────────────────────────────────────────────────────────────────────────────
# 5. BARRES GROUPÉES — Comparaison moyenne par département
# ─────────────────────────────────────────────────────────────────────────────
def render_department_bars(
    container: QWidget, evaluations: List[dict], professors: List[dict]
) -> None:
    prof_dept = {p["id"]: p.get("department", "Autre") or "Autre" for p in professors}

    dept_scores: Dict[str, list] = defaultdict(list)
    for ev in evaluations:
        pid = ev.get("professor_id")
        s = _avg(ev)
        if pid and s is not None:
            dept = prof_dept.get(pid, "Autre")
            dept_scores[dept].append(s)

    if not dept_scores:
        _empty(container, "Aucune donnée\nde département disponible.")
        return

    # Afficher jusqu'à 10 départements sur la pleine largeur
    sorted_depts = sorted(dept_scores.items(),
                          key=lambda x: sum(x[1]) / len(x[1]), reverse=True)[:10]
    depts  = [d for d, _ in sorted_depts]
    avgs   = [sum(v) / len(v) for _, v in sorted_depts]
    counts = [len(v) for _, v in sorted_depts]
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(depts))]

    fig = Figure(figsize=(8.5, 3.2), tight_layout=True)
    ax = fig.add_subplot(111)
    _dark(fig, ax, "Moyenne par département")

    x = range(len(depts))
    bar_w = 0.45 if len(depts) > 4 else 0.35
    bars = ax.bar(x, avgs, color=colors, edgecolor=SURFACE, linewidth=0.5, width=bar_w, zorder=2)

    ax.set_xticks(list(x))
    rot = 15 if len(depts) > 5 else 0
    align = "right" if rot > 0 else "center"
    ax.set_xticklabels(depts, color=TEXT_MID, fontsize=8.5, rotation=rot, ha=align)
    ax.set_ylim(0, 5.5)
    ax.set_ylabel("Note moy. (/5)", color=TEXT_LO, fontsize=8.5)
    ax.tick_params(axis="y", colors=TEXT_MUTED, labelsize=8)
    ax.axhline(3.0, color=AMBER, linewidth=1, linestyle=":", alpha=0.6)
    ax.grid(axis="y", color=BORDER, linestyle="--", linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)

    for bar, val, n in zip(bars, avgs, counts):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.08,
                f"{val:.2f}\n({n})", ha="center", color=TEXT_HI,
                fontsize=7.5, fontweight="bold", linespacing=1.3)

    _embed(container, fig)


# ─────────────────────────────────────────────────────────────────────────────
# 6. HEATMAP — Notes prof × critère (ou prof × mois en fallback)
# ─────────────────────────────────────────────────────────────────────────────
def render_heatmap(
    container: QWidget, evaluations: List[dict], professors: List[dict]
) -> None:
    prof_map = {p["id"]: p.get("last_name", f"#{p['id']}")[:12] for p in professors}

    crit_data: Dict[tuple, list] = defaultdict(list)
    crit_ids: set = set()
    for ev in evaluations:
        pid = ev.get("professor_id")
        if pid is None:
            continue
        for ans in ev.get("answers", []):
            cid = ans.get("criterion_id")
            s   = ans.get("score")
            if cid is not None and s is not None:
                crit_data[(pid, cid)].append(float(s))
                crit_ids.add(cid)

    if len(crit_ids) >= 2 and crit_data:
        prof_ids = sorted({pid for (pid, _) in crit_data})[:8]
        col_ids  = sorted(crit_ids)[:10]
        row_lbl  = [prof_map.get(p, f"#{p}") for p in prof_ids]
        col_lbl  = [f"Critère {c}" for c in col_ids]
        matrix   = np.full((len(prof_ids), len(col_ids)), np.nan)
        for i, pid in enumerate(prof_ids):
            for j, cid in enumerate(col_ids):
                vs = crit_data.get((pid, cid), [])
                if vs:
                    matrix[i, j] = sum(vs) / len(vs)
        title = "Performance par critère d'évaluation"
    else:
        monthly: Dict[tuple, list] = defaultdict(list)
        for ev in evaluations:
            pid = ev.get("professor_id")
            s   = _avg(ev)
            d   = str(ev.get("submitted_at", ""))[:7]
            if pid and s is not None and len(d) == 7:
                monthly[(pid, d)].append(s)
        if not monthly:
            _empty(container, "Données insuffisantes\npour la heatmap.")
            return
        all_months = sorted({m for (_, m) in monthly})
        prof_ids   = sorted({pid for (pid, _) in monthly})[:8]
        row_lbl    = [prof_map.get(p, f"#{p}") for p in prof_ids]
        col_lbl    = [m[5:] for m in all_months]
        matrix     = np.full((len(prof_ids), len(all_months)), np.nan)
        for i, pid in enumerate(prof_ids):
            for j, m in enumerate(all_months):
                vs = monthly.get((pid, m), [])
                if vs:
                    matrix[i, j] = sum(vs) / len(vs)
        title = "Notes des enseignants par période"

    fig = Figure(figsize=(6, 3.5), tight_layout=True)
    ax = fig.add_subplot(111)
    _dark(fig, ax, title)

    im = ax.imshow(matrix, cmap=plt.cm.RdYlGn, aspect="auto", vmin=0, vmax=5, alpha=0.9)
    ax.set_xticks(range(len(col_lbl)))
    ax.set_xticklabels(col_lbl, fontsize=7.5, color=TEXT_LO, rotation=30, ha="right")
    ax.set_yticks(range(len(row_lbl)))
    ax.set_yticklabels(row_lbl, fontsize=8, color=TEXT_MID)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            v = matrix[i, j]
            if not np.isnan(v):
                tc = "white" if v < 2.0 or v > 4.2 else "#0f172a"
                ax.text(j, i, f"{v:.1f}", ha="center", va="center",
                        fontsize=7, color=tc, fontweight="bold")

    cb = fig.colorbar(im, ax=ax, shrink=0.75, pad=0.02)
    cb.ax.tick_params(colors=TEXT_LO, labelsize=7)
    _embed(container, fig)


# ─────────────────────────────────────────────────────────────────────────────
# 7. BARRES EMPILÉES — Répartition des niveaux de réponse par professeur
# ─────────────────────────────────────────────────────────────────────────────
def render_stacked_bars(
    container: QWidget, evaluations: List[dict], professors: List[dict]
) -> None:
    prof_map = {p["id"]: p.get("last_name", f"#{p['id']}")[:10] for p in professors}
    level_counts: Dict[int, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
    has_ans = False

    for ev in evaluations:
        pid = ev.get("professor_id")
        if pid is None:
            continue
        for ans in ev.get("answers", []):
            s = ans.get("score")
            if s is not None:
                level_counts[pid][int(min(5, max(1, round(float(s)))))] += 1
                has_ans = True

    if not has_ans:
        for ev in evaluations:
            pid = ev.get("professor_id")
            s   = _avg(ev)
            if pid and s is not None:
                level_counts[pid][int(min(5, max(1, round(s))))] += 1

    if not level_counts:
        _empty(container, "Aucune donnée de réponse.")
        return

    def _wavg(d): t = sum(d.values()); return sum(k * v for k, v in d.items()) / max(1, t)
    prof_ids = sorted(level_counts.keys(), key=lambda p: _wavg(level_counts[p]), reverse=True)[:8]
    labels = [prof_map.get(pid, f"#{pid}") for pid in prof_ids]
    levels  = [1, 2, 3, 4, 5]
    lcolors = [RED, ORANGE, AMBER, BLUE, GREEN]
    llabels = ["Médiocre", "Insuffisant", "Moyen", "Bien", "Excellent"]

    fig = Figure(figsize=(5.5, 3.5), tight_layout=True)
    ax = fig.add_subplot(111)
    _dark(fig, ax, "Répartition des niveaux par enseignant")

    bottom = [0] * len(prof_ids)
    for lv, col, lbl in zip(levels, lcolors, llabels):
        vals = [level_counts[pid].get(lv, 0) for pid in prof_ids]
        ax.bar(labels, vals, bottom=bottom, color=col,
               edgecolor=SURFACE, linewidth=0.4, label=lbl, zorder=2)
        bottom = [b + v for b, v in zip(bottom, vals)]

    ax.set_ylabel("Réponses", color=TEXT_LO, fontsize=8.5)
    ax.tick_params(axis="x", colors=TEXT_MID, labelsize=8, rotation=25)
    ax.tick_params(axis="y", colors=TEXT_MUTED, labelsize=8)
    ax.grid(axis="y", color=BORDER, linestyle="--", linewidth=0.5, alpha=0.4)
    ax.set_axisbelow(True)
    ax.legend(fontsize=7, frameon=True, framealpha=0.12, edgecolor=BORDER,
              labelcolor=TEXT_MID, loc="upper right", ncol=2)
    _embed(container, fig)

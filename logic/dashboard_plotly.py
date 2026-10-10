"""Graphiques Plotly interactifs du tableau de bord."""

from collections import Counter, defaultdict

import plotly.graph_objects as go


COLORS = ["#3478d4", "#21a6a1", "#7279d8", "#e19a45", "#5c88b2"]


def _layout(figure, title):
    figure.update_layout(
        title={"text": title, "x": 0.04, "xanchor": "left", "font": {"size": 16}},
        paper_bgcolor="white",
        plot_bgcolor="white",
        font={"family": "Arial, sans-serif", "color": "#315b82", "size": 12},
        margin={"l": 58, "r": 28, "t": 62, "b": 52},
        hoverlabel={"bgcolor": "#0f172a", "font_color": "white"},
        autosize=True,
    )
    figure.update_xaxes(showgrid=False, zeroline=False, tickfont={"color": "#617d99"})
    figure.update_yaxes(gridcolor="#e9eff6", zeroline=False, tickfont={"color": "#617d99"})
    return figure


def _evaluation_scores(evaluation):
    return [
        float(answer["score"])
        for answer in evaluation.get("answers", [])
        if isinstance(answer, dict) and answer.get("score") is not None
    ]


def professors_figure(evaluations, professors):
    scores_by_professor = defaultdict(list)
    for evaluation in evaluations:
        professor_id = evaluation.get("professor_id")
        if professor_id is not None:
            scores_by_professor[professor_id].extend(_evaluation_scores(evaluation))

    names = {
        item.get("id"): " ".join(
            part for part in (item.get("first_name"), item.get("last_name")) if part
        ) or f"Professeur #{item.get('id')}"
        for item in professors
    }
    ranked = sorted(
        ((names.get(pid, f"Professeur #{pid}"), sum(scores) / len(scores), len(scores))
         for pid, scores in scores_by_professor.items() if scores),
        key=lambda row: row[1], reverse=True,
    )[:8]
    figure = go.Figure()
    figure.add_trace(go.Bar(
        x=[row[1] for row in ranked], y=[row[0] for row in ranked], orientation="h",
        marker_color=COLORS[0], text=[f"{row[1]:.2f} · {row[2]} notes" for row in ranked],
        textposition="auto", hovertemplate="%{y}<br>Moyenne : %{x:.2f}/5<extra></extra>",
    ))
    figure.update_layout(showlegend=False, height=320, yaxis={"autorange": "reversed"}, xaxis={"range": [0, 5], "title": "Moyenne / 5"})
    return _layout(figure, "Professeurs les mieux évalués")


def score_distribution_figure(evaluations):
    counts = Counter(
        int(score)
        for evaluation in evaluations
        for score in _evaluation_scores(evaluation)
    )
    labels = [str(score) for score in range(1, 6)]
    figure = go.Figure(go.Bar(
        x=labels, y=[counts.get(score, 0) for score in range(1, 6)],
        marker_color=COLORS, text=[counts.get(score, 0) for score in range(1, 6)],
        textposition="outside", hovertemplate="Note %{x}/5<br>%{y} réponse(s)<extra></extra>",
    ))
    figure.update_layout(showlegend=False, height=320, xaxis_title="Note attribuée", yaxis_title="Nombre de réponses")
    return _layout(figure, "Distribution des notes")


def timeline_figure(evaluations):
    counts = Counter()
    for evaluation in evaluations:
        submitted = evaluation.get("submitted_at")
        if isinstance(submitted, str) and len(submitted) >= 7:
            counts[submitted[:7]] += 1
    months = sorted(counts)
    figure = go.Figure(go.Scatter(
        x=months, y=[counts[month] for month in months], mode="lines+markers",
        line={"color": COLORS[1], "width": 3}, marker={"size": 8},
        fill="tozeroy", fillcolor="rgba(6, 182, 212, 0.12)",
        hovertemplate="%{x}<br>%{y} évaluation(s)<extra></extra>",
    ))
    figure.update_layout(showlegend=False, height=320, xaxis_title="Mois", yaxis_title="Évaluations reçues")
    return _layout(figure, "Évolution des évaluations")


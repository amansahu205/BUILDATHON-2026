"""
PDF report generator for VERDICT deposition analysis.

Produces a multi-page, branded PDF with:
  - Cover header with case metadata
  - Radar / spider chart for the 5 scoring dimensions
  - Per-dimension deep-dive with score bars and rationale
  - Critical vulnerability callout
  - Coaching suggestions checklist
  - Lawyer's executive brief with trial-readiness assessment
"""

import io
import math
import textwrap
from datetime import datetime, timezone

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    HRFlowable,
    KeepTogether,
    PageBreak,
)

WIDTH, HEIGHT = A4

# ── Brand colours ────────────────────────────────────────────────
NAVY = colors.HexColor("#0F1B2D")
GOLD = colors.HexColor("#C9A84C")
SLATE = colors.HexColor("#1E293B")
LIGHT_BG = colors.HexColor("#F8FAFC")
RED = colors.HexColor("#DC2626")
AMBER = colors.HexColor("#D97706")
GREEN = colors.HexColor("#16A34A")
WHITE = colors.white
GRAY = colors.HexColor("#64748B")
LIGHT_GRAY = colors.HexColor("#E2E8F0")

DIMENSION_LABELS = [
    "Composure",
    "Tactical\nDiscipline",
    "Professionalism",
    "Directness",
    "Consistency",
]


def _score_colour(score: int) -> colors.HexColor:
    if score >= 70:
        return GREEN
    if score >= 45:
        return AMBER
    return RED


def _rating_colour(rating: str) -> colors.HexColor:
    r = rating.lower()
    if "strong" in r:
        return GREEN
    if "moderate" in r:
        return AMBER
    return RED


def _build_radar_chart(scores: dict) -> io.BytesIO:
    """Render a radar / spider chart and return it as a PNG buffer."""
    categories = list(DIMENSION_LABELS)
    values = [
        scores.get("composure", 0),
        scores.get("tactical_discipline", 0),
        scores.get("professionalism", 0),
        scores.get("directness", 0),
        scores.get("consistency", 0),
    ]

    n = len(categories)
    angles = [i / n * 2 * math.pi for i in range(n)]
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4.2, 4.2), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#0F1B2D")
    ax.set_facecolor("#0F1B2D")

    for ring in [20, 40, 60, 80, 100]:
        ring_vals = [ring] * (n + 1)
        ax.plot(angles, ring_vals, color="#334155", linewidth=0.5, linestyle="--")

    ax.fill(angles, values, color="#C9A84C", alpha=0.25)
    ax.plot(angles, values, color="#C9A84C", linewidth=2.5)

    for i in range(n):
        ax.plot(angles[i], values[i], "o", color="#C9A84C", markersize=7, zorder=5)
        ax.annotate(
            f"{values[i]}",
            xy=(angles[i], values[i]),
            xytext=(0, 12),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            fontweight="bold",
            color="white",
        )

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=9, color="white", fontweight="bold")
    ax.set_yticklabels([])
    ax.set_ylim(0, 100)
    ax.spines["polar"].set_color("#334155")
    ax.grid(color="#334155", linewidth=0.5)

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=180, bbox_inches="tight",
                facecolor="#0F1B2D", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return buf


def _styles():
    """Build all paragraph styles used in the report."""
    ss = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "VTitle", parent=ss["Title"], fontName="Helvetica-Bold",
            fontSize=22, textColor=WHITE, alignment=TA_CENTER, spaceAfter=2 * mm,
        ),
        "subtitle": ParagraphStyle(
            "VSub", parent=ss["Normal"], fontName="Helvetica",
            fontSize=11, textColor=GOLD, alignment=TA_CENTER, spaceAfter=6 * mm,
        ),
        "h2": ParagraphStyle(
            "VH2", parent=ss["Heading2"], fontName="Helvetica-Bold",
            fontSize=14, textColor=NAVY, spaceBefore=8 * mm, spaceAfter=3 * mm,
        ),
        "h3": ParagraphStyle(
            "VH3", parent=ss["Heading3"], fontName="Helvetica-Bold",
            fontSize=11, textColor=SLATE, spaceBefore=4 * mm, spaceAfter=2 * mm,
        ),
        "body": ParagraphStyle(
            "VBody", parent=ss["Normal"], fontName="Helvetica",
            fontSize=10, textColor=SLATE, leading=14, alignment=TA_JUSTIFY,
            spaceAfter=2 * mm,
        ),
        "body_sm": ParagraphStyle(
            "VBodySm", parent=ss["Normal"], fontName="Helvetica",
            fontSize=9, textColor=GRAY, leading=12, spaceAfter=1 * mm,
        ),
        "callout": ParagraphStyle(
            "VCallout", parent=ss["Normal"], fontName="Helvetica-Bold",
            fontSize=10, textColor=RED, leading=14, spaceAfter=2 * mm,
        ),
        "coaching": ParagraphStyle(
            "VCoach", parent=ss["Normal"], fontName="Helvetica",
            fontSize=10, textColor=SLATE, leading=14, leftIndent=8 * mm,
            spaceAfter=2 * mm,
        ),
        "meta_label": ParagraphStyle(
            "VMetaL", fontName="Helvetica-Bold", fontSize=9,
            textColor=GRAY, spaceAfter=0,
        ),
        "meta_value": ParagraphStyle(
            "VMetaV", fontName="Helvetica", fontSize=10,
            textColor=SLATE, spaceAfter=2 * mm,
        ),
        "footer": ParagraphStyle(
            "VFooter", fontName="Helvetica", fontSize=7,
            textColor=GRAY, alignment=TA_CENTER,
        ),
        "big_score": ParagraphStyle(
            "VBigScore", fontName="Helvetica-Bold", fontSize=36,
            textColor=NAVY, alignment=TA_CENTER, spaceAfter=1 * mm,
        ),
        "rating_label": ParagraphStyle(
            "VRating", fontName="Helvetica-Bold", fontSize=12,
            alignment=TA_CENTER, spaceAfter=1 * mm,
        ),
    }


def _header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, HEIGHT - 28 * mm, WIDTH, 28 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(15 * mm, HEIGHT - 12 * mm, "VERDICT")
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(15 * mm, HEIGHT - 18 * mm, "Deposition Analysis Report")
    canvas.setFont("Helvetica", 7)
    canvas.drawRightString(WIDTH - 15 * mm, HEIGHT - 18 * mm, f"Page {doc.page}")
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(2)
    canvas.line(0, HEIGHT - 28 * mm, WIDTH, HEIGHT - 28 * mm)
    canvas.setFillColor(GRAY)
    canvas.setFont("Helvetica", 6)
    canvas.drawCentredString(WIDTH / 2, 8 * mm,
        "PRIVILEGED & CONFIDENTIAL — Attorney Work Product — Do Not Distribute")
    canvas.restoreState()


def generate_pdf(report: dict) -> io.BytesIO:
    """Build a full PDF report and return it as a BytesIO buffer."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        topMargin=34 * mm, bottomMargin=18 * mm,
        leftMargin=15 * mm, rightMargin=15 * mm,
    )

    s = _styles()
    story = []

    scores = report.get("spider_chart_scores", {})
    rationale = report.get("analysis_rationale", {})
    vulnerability = report.get("critical_vulnerability", {})
    coaching = report.get("coaching_suggestions", [])
    brief = report.get("lawyer_brief", {})
    case_name = report.get("case_name", "Unknown Case")
    witness = report.get("witness_name", "Unknown Witness")
    aggression = report.get("aggression_level", "N/A")
    method = report.get("analysis_method", "rule_based")
    gen_at = report.get("generated_at", datetime.now(timezone.utc).isoformat())

    # ── 1. Cover / Metadata ──────────────────────────────────────
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(f"Deposition Analysis Report", s["h2"]))
    story.append(HRFlowable(width="100%", thickness=1, color=GOLD, spaceAfter=4 * mm))

    meta_data = [
        ["Case", case_name, "Witness", witness],
        ["Aggression Level", aggression, "Analysis Method",
         "AI (Claude)" if "llm" in method else "Rule-Based Engine"],
        ["Generated", gen_at[:19].replace("T", " ") + " UTC", "", ""],
    ]
    meta_table = Table(meta_data, colWidths=[28 * mm, 62 * mm, 32 * mm, 58 * mm])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), GRAY),
        ("TEXTCOLOR", (2, 0), (2, -1), GRAY),
        ("TEXTCOLOR", (1, 0), (1, -1), SLATE),
        ("TEXTCOLOR", (3, 0), (3, -1), SLATE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6 * mm))

    # ── 2. Overall Score Card ────────────────────────────────────
    overall_score = brief.get("overall_score", 0)
    overall_rating = brief.get("overall_rating", "N/A")
    trial_readiness = brief.get("trial_readiness", "")

    score_color = _rating_colour(overall_rating)
    score_hex = score_color.hexval() if hasattr(score_color, 'hexval') else str(score_color)

    score_card_data = [[
        Paragraph(f'<font size="36" color="{score_hex}">{overall_score}</font>', s["big_score"]),
        Paragraph(f'<font size="14" color="{score_hex}"><b>{overall_rating.upper()}</b></font>', s["rating_label"]),
        Paragraph(trial_readiness, s["body"]),
    ]]
    score_table = Table(score_card_data, colWidths=[30 * mm, 40 * mm, 110 * mm])
    score_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
        ("BOX", (0, 0), (-1, -1), 1, LIGHT_GRAY),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 6 * mm))

    # ── 3. Radar Chart ───────────────────────────────────────────
    story.append(Paragraph("Performance Radar", s["h2"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GRAY, spaceAfter=3 * mm))

    chart_buf = _build_radar_chart(scores)
    chart_img = Image(chart_buf, width=90 * mm, height=90 * mm)
    chart_img.hAlign = "CENTER"
    story.append(chart_img)
    story.append(Spacer(1, 4 * mm))

    # Score summary row
    dim_names = ["Composure", "Tactical Discipline", "Professionalism", "Directness", "Consistency"]
    dim_keys = ["composure", "tactical_discipline", "professionalism", "directness", "consistency"]
    score_row_header = [Paragraph(f'<b>{n}</b>', s["body_sm"]) for n in dim_names]
    score_row_values = []
    for k in dim_keys:
        v = scores.get(k, 0)
        c = _score_colour(v)
        ch = c.hexval() if hasattr(c, "hexval") else str(c)
        score_row_values.append(
            Paragraph(f'<font color="{ch}"><b>{v}/100</b></font>', s["body_sm"])
        )
    summary_table = Table(
        [score_row_header, score_row_values],
        colWidths=[36 * mm] * 5,
    )
    summary_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    summary_table.hAlign = "CENTER"
    story.append(summary_table)

    # ── 4. Dimension Deep-Dives ──────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Detailed Dimension Analysis", s["h2"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GRAY, spaceAfter=3 * mm))

    rationale_map = {
        "Composure": rationale.get("composure_reasoning", ""),
        "Tactical Discipline": rationale.get("tactical_discipline_reasoning", ""),
        "Professionalism": rationale.get("professionalism_reasoning", ""),
        "Directness": rationale.get("directness_reasoning", ""),
        "Consistency": rationale.get("consistency_reasoning", ""),
    }

    for name, key in zip(dim_names, dim_keys):
        v = scores.get(key, 0)
        sc = _score_colour(v)
        sc_hex = sc.hexval() if hasattr(sc, "hexval") else str(sc)
        reasoning = rationale_map.get(name, "No analysis available.")

        block = []
        block.append(Paragraph(
            f'{name} — <font color="{sc_hex}"><b>{v}/100</b></font>', s["h3"]
        ))

        bar_filled = max(1, int(v * 1.5))
        bar_empty = 150 - bar_filled
        bar_data = [["", ""]]
        bar_table = Table(bar_data, colWidths=[bar_filled * mm, bar_empty * mm], rowHeights=[4 * mm])
        bar_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), sc),
            ("BACKGROUND", (1, 0), (1, 0), LIGHT_GRAY),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        block.append(bar_table)
        block.append(Spacer(1, 2 * mm))
        block.append(Paragraph(reasoning, s["body"]))
        block.append(Spacer(1, 3 * mm))
        story.append(KeepTogether(block))

    # ── 5. Critical Vulnerability ────────────────────────────────
    story.append(Paragraph("Critical Vulnerability", s["h2"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=RED, spaceAfter=3 * mm))

    vuln_data = [
        [Paragraph("<b>Interrogator Tactic</b>", s["body_sm"]),
         Paragraph(vulnerability.get("interrogator_tactic_used", "N/A"), s["body"])],
        [Paragraph("<b>Witness Reaction</b>", s["body_sm"]),
         Paragraph(vulnerability.get("witness_reaction", "N/A"), s["body"])],
        [Paragraph("<b>Trial Risk</b>", s["body_sm"]),
         Paragraph(f'<font color="#DC2626">{vulnerability.get("trial_risk", "N/A")}</font>', s["body"])],
    ]
    vuln_table = Table(vuln_data, colWidths=[40 * mm, 140 * mm])
    vuln_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF2F2")),
        ("BOX", (0, 0), (-1, -1), 1, RED),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor("#FECACA")),
    ]))
    story.append(vuln_table)

    # ── 6. Coaching & Improvement Suggestions ────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Coaching & Improvement Plan", s["h2"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GOLD, spaceAfter=3 * mm))

    if not coaching:
        coaching = [report.get("coaching_directive", "No coaching available.")]

    for idx, item in enumerate(coaching, 1):
        story.append(Paragraph(
            f'<font color="#C9A84C"><b>#{idx}</b></font>  {item}', s["coaching"]
        ))
        story.append(Spacer(1, 2 * mm))

    # ── 7. Lawyer's Executive Brief ──────────────────────────────
    story.append(Paragraph("Lawyer's Executive Brief", s["h2"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=NAVY, spaceAfter=3 * mm))

    brief_items = [
        ("Overall Rating", f'{brief.get("overall_rating", "N/A")} ({brief.get("overall_score", 0)}/100)'),
        ("Trial Readiness", brief.get("trial_readiness", "N/A")),
        ("Interrogation Intensity", brief.get("interrogation_intensity", "N/A")),
        ("Strongest Dimension", brief.get("strongest_dimension", "N/A")),
        ("Weakest Dimension", brief.get("weakest_dimension", "N/A")),
        ("Primary Risk", brief.get("primary_risk", "N/A")),
        ("Total Exchanges", str(brief.get("total_exchanges", 0))),
        ("Witness Responses", str(brief.get("witness_responses", 0))),
    ]
    brief_data = [
        [Paragraph(f"<b>{label}</b>", s["body_sm"]), Paragraph(value, s["body"])]
        for label, value in brief_items
    ]
    brief_table = Table(brief_data, colWidths=[45 * mm, 135 * mm])
    brief_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
        ("BOX", (0, 0), (-1, -1), 1, LIGHT_GRAY),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, LIGHT_GRAY),
    ]))
    story.append(brief_table)
    story.append(Spacer(1, 6 * mm))

    # ── 8. Recommended Next Steps ────────────────────────────────
    story.append(Paragraph("Recommended Next Steps", s["h3"]))
    next_steps = brief.get("recommended_next_steps", [])
    for idx, step in enumerate(next_steps, 1):
        story.append(Paragraph(
            f'<font color="#0F1B2D"><b>{idx}.</b></font>  {step}', s["body"]
        ))

    story.append(Spacer(1, 10 * mm))
    story.append(HRFlowable(width="60%", thickness=0.5, color=GRAY, spaceAfter=4 * mm))
    story.append(Paragraph(
        f"Report generated by VERDICT Analysis Engine  •  {gen_at[:10]}  •  Confidential",
        s["footer"],
    ))

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    buf.seek(0)
    return buf

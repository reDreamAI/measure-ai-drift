"""Generate evaluation methods diagram — Three-Level Stability Framework.

Source references:
    src/evaluation/metrics.py      — metric computation functions
    src/evaluation/experiment.py   — experiment orchestration
    src/stacks/evaluation_stack.py — trial generation
    data/prompts/evaluation/       — taxonomy, judge prompt, fused prompt
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ── colours ──────────────────────────────────────────────────────────────────
C = {
    "trial":      "#E67E22",   # orange — matches pipeline eval section
    "plan":       "#F0B27A",   # light orange — matches pipeline trial
    "resp":       "#E59866",   # medium orange
    "extract":    "#78909C",   # blue-grey — neutral processing
    "taxonomy":   "#17A589",   # teal — reference data
    "l31":        "#6C5CE7",   # indigo — unique to eval levels
    "l32":        "#00B894",   # emerald — unique to eval levels
    "l33":        "#E84393",   # hot pink — unique to eval levels
    "output":     "#34495E",   # dark slate
    "bg":         "#FAFBFC",
    "text":       "#2C3E50",
    "arrow":      "#4A4A4A",
    "label":      "#566573",
}

fig, ax = plt.subplots(figsize=(18, 12))
fig.patch.set_facecolor(C["bg"])
ax.set_facecolor(C["bg"])
ax.set_xlim(0, 18)
ax.set_ylim(0, 12)
ax.axis("off")

# ── helpers ──────────────────────────────────────────────────────────────────

def box(x, y, w, h, color, label, sublabel=None, fontsize=10, alpha=0.92,
        bold=True, radius=0.3):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.15,rounding_size={radius}",
        facecolor=color, edgecolor="white", linewidth=2, alpha=alpha,
        zorder=3,
    )
    ax.add_patch(patch)
    weight = "bold" if bold else "normal"
    ax.text(x + w / 2, y + h / 2 + (0.12 if sublabel else 0),
            label, ha="center", va="center", fontsize=fontsize,
            color="white", fontweight=weight, zorder=4)
    if sublabel:
        ax.text(x + w / 2, y + h / 2 - 0.22,
                sublabel, ha="center", va="center", fontsize=fontsize - 2,
                color="white", fontstyle="italic", alpha=0.9, zorder=4)


def file_box(x, y, w, h, color, label, fontsize=8):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.08,rounding_size=0.15",
        facecolor=color, edgecolor="white", linewidth=1.5, alpha=0.85,
        zorder=3,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
            fontsize=fontsize, color="white", fontweight="bold", zorder=4,
            family="monospace")


def arrow(x1, y1, x2, y2, color=C["arrow"], lw=2, style="->", rad=0.08):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle=style, color=color, lw=lw,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=4, shrinkB=4,
        ),
        zorder=2,
    )


def section_bg(x, y, w, h, color, alpha=0.06):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.2,rounding_size=0.4",
        facecolor=color, edgecolor=color, linewidth=1.5, alpha=alpha,
        linestyle="--", zorder=1,
    )
    ax.add_patch(patch)


def section_label(x, y, text, color, fontsize=11):
    ax.text(x, y, text, fontsize=fontsize, color=color,
            fontweight="bold", va="center", zorder=5)


# ═══════════════════════════════════════════════════════════════════════════════
# TITLE
# ═══════════════════════════════════════════════════════════════════════════════

ax.text(9.0, 11.7, "Evaluation Methods — Three-Level Stability Framework",
        fontsize=16, color=C["text"], ha="center", fontweight="bold", zorder=10)

# ═══════════════════════════════════════════════════════════════════════════════
# TOP: Trial Output + Extraction + Taxonomy
# ═══════════════════════════════════════════════════════════════════════════════

# --- Trial output ---
section_bg(0.3, 9.2, 5.0, 2.0, C["trial"])
section_label(0.6, 11.0, "TRIAL OUTPUT (x10)", C["trial"])

box(0.6, 9.5, 2.1, 1.3, C["plan"], "<plan>",
    sublabel="cat1 / cat2", fontsize=9)
box(2.9, 9.5, 2.1, 1.3, C["resp"], "Response",
    sublabel="1-3 sentences", fontsize=9)

ax.text(2.65, 9.3, "evaluation_stack.py:run_trial()",
        fontsize=6.5, color=C["label"], ha="center", family="monospace",
        style="italic")

# --- Extraction ---
section_bg(5.6, 9.2, 5.8, 2.0, C["extract"])
section_label(5.9, 11.0, "PLAN PARSING", C["extract"])

box(5.9, 10.0, 5.2, 0.75, C["extract"],
    "extract_plan_strategies()", fontsize=9)

box(5.9, 9.4, 2.4, 0.5, C["extract"],
    "10 strategy sets", fontsize=8, alpha=0.6)

box(8.5, 9.4, 2.6, 0.5, C["extract"],
    "Validity Rate (1-2?)", fontsize=8, alpha=0.6)

# (plan → extraction connection implied by layout)

# --- Strategy Taxonomy ---
section_bg(11.7, 9.2, 5.8, 2.0, C["taxonomy"])
section_label(12.0, 11.0, "STRATEGY TAXONOMY", C["taxonomy"])

strategies = [
    "confrontation", "self_empowerment", "safety",
    "cognitive_reframe", "emotional_regulation",
    "social_support", "sensory_modulation",
]
for i, s in enumerate(strategies):
    col = i % 3
    row = i // 3
    fx = 12.0 + col * 1.9
    fy = 10.2 - row * 0.45
    if i == 6:
        fx = 12.0
        fy = 10.2 - 2 * 0.45
    file_box(fx, fy, 1.75, 0.35, C["taxonomy"], s, fontsize=6)

ax.text(14.6, 9.3, "strategy_taxonomy.yaml",
        fontsize=6.5, color=C["label"], ha="center", family="monospace",
        style="italic")

# ═══════════════════════════════════════════════════════════════════════════════
# THREE METRIC COLUMNS
# ═══════════════════════════════════════════════════════════════════════════════

# --- Level 3.1: Cognitive Stability ---
c1x, c1w = 0.3, 5.3
section_bg(c1x, 2.3, c1w, 6.5, C["l31"])
section_label(c1x + 0.3, 8.5, "LEVEL 3.1", C["l31"], fontsize=13)

box(c1x + 0.3, 7.4, c1w - 0.6, 0.85, C["l31"],
    "Cognitive Stability",
    sublabel="Are strategy choices consistent?", fontsize=11)

ax.text(c1x + c1w / 2, 7.1, "input: strategy sets",
        fontsize=8.5, color=C["l31"], ha="center", style="italic")

box(c1x + 0.5, 6.1, c1w - 1.0, 0.75, C["l31"],
    "Pairwise Jaccard Similarity", fontsize=9.5, alpha=0.7)

ax.text(c1x + c1w / 2, 5.55,
        "J(A, B) = |A ∩ B| / |A ∪ B|",
        fontsize=10, color=C["l31"], ha="center", fontweight="bold",
        family="monospace")

ax.text(c1x + c1w / 2, 5.1,
        "mean over C(10,2) = 45 pairs",
        fontsize=8, color=C["label"], ha="center", style="italic")

# Example
box(c1x + 0.3, 4.0, c1w - 0.6, 0.8, C["l31"], "", bold=False, alpha=0.2)
ax.text(c1x + c1w / 2, 4.55,
        "{agency, safety} vs {agency}",
        fontsize=8, color=C["l31"], ha="center", family="monospace", zorder=5)
ax.text(c1x + c1w / 2, 4.2,
        "= 1/2 = 0.50",
        fontsize=8, color=C["l31"], ha="center", family="monospace",
        fontweight="bold", zorder=5)

# Output
box(c1x + 0.6, 3.1, c1w - 1.2, 0.6, C["l31"],
    "mean Jaccard (0.0 - 1.0)", fontsize=9, alpha=0.6)

ax.text(c1x + c1w / 2, 2.6,
        "compute_pairwise_jaccard()",
        fontsize=7.5, color=C["label"], ha="center", family="monospace",
        style="italic")

# --- Level 3.2: Output Consistency ---
c2x, c2w = 5.9, 5.6
section_bg(c2x, 2.3, c2w, 6.5, C["l32"])
section_label(c2x + 0.3, 8.5, "LEVEL 3.2", C["l32"], fontsize=13)

box(c2x + 0.3, 7.4, c2w - 0.6, 0.85, C["l32"],
    "Output Consistency",
    sublabel="Are responses semantically similar?", fontsize=11)

ax.text(c2x + c2w / 2, 7.1, "input: response texts",
        fontsize=8.5, color=C["l32"], ha="center", style="italic")

box(c2x + 0.5, 6.1, c2w - 1.0, 0.75, C["l32"],
    "Pairwise BERTScore", fontsize=9.5, alpha=0.7)

ax.text(c2x + c2w / 2, 5.55,
        "DeBERTa-XLarge-MNLI",
        fontsize=10, color=C["l32"], ha="center", fontweight="bold",
        family="monospace")

ax.text(c2x + c2w / 2, 5.1,
        "NLI-finetuned · token-level matching",
        fontsize=8, color=C["label"], ha="center", style="italic")

# Detail
box(c2x + 0.3, 4.0, c2w - 0.6, 0.8, C["l32"], "", bold=False, alpha=0.2)
ax.text(c2x + c2w / 2, 4.55,
        "precision / recall / F1",
        fontsize=8.5, color=C["l32"], ha="center", family="monospace", zorder=5)
ax.text(c2x + c2w / 2, 4.2,
        "45 pairwise comparisons",
        fontsize=8, color=C["l32"], ha="center", style="italic", zorder=5)

# Output
box(c2x + 0.6, 3.1, c2w - 1.2, 0.6, C["l32"],
    "mean F1 (0.0 - 1.0)", fontsize=9, alpha=0.6)

ax.text(c2x + c2w / 2, 2.6,
        "compute_pairwise_bertscore()",
        fontsize=7.5, color=C["label"], ha="center", family="monospace",
        style="italic")

# --- Level 3.3: Plan-Output Alignment ---
c3x, c3w = 11.8, 5.9
section_bg(c3x, 2.3, c3w, 6.5, C["l33"])
section_label(c3x + 0.3, 8.5, "LEVEL 3.3", C["l33"], fontsize=13)

box(c3x + 0.3, 7.4, c3w - 0.6, 0.85, C["l33"],
    "Plan-Output Alignment",
    sublabel="Does response implement the plan?", fontsize=11)

ax.text(c3x + c3w / 2, 7.1,
        "input: strategies + responses + taxonomy",
        fontsize=7.5, color=C["l33"], ha="center", style="italic")

box(c3x + 0.5, 6.1, c3w - 1.0, 0.75, C["l33"],
    "LLM Judge", sublabel="Gemini Flash · T=0.0", fontsize=9.5, alpha=0.7)

# Ternary scoring
ax.text(c3x + c3w / 2, 5.5,
        "Ternary scoring per strategy:",
        fontsize=9, color=C["l33"], ha="center", fontweight="bold")

score_labels = [
    ("0", "absent", "#F1948A"),
    ("1", "partial", "#F5B041"),
    ("2", "implemented", "#58D68D"),
]
for i, (score, label, color) in enumerate(score_labels):
    sx = c3x + 0.4 + i * 1.7
    file_box(sx, 4.9, 1.55, 0.4, color, f"{score} = {label}", fontsize=7)

# Formula
ax.text(c3x + c3w / 2, 4.5,
        "trial = mean(scores) / 2   (0.0 - 1.0)",
        fontsize=8, color=C["label"], ha="center", family="monospace")

# Detail
box(c3x + 0.3, 3.7, c3w - 0.6, 0.55, C["l33"], "", bold=False, alpha=0.2)
ax.text(c3x + c3w / 2, 3.95,
        "per-trial · per-strategy · raw judgments",
        fontsize=8, color=C["l33"], ha="center", family="monospace", zorder=5)

# Output
box(c3x + 0.6, 3.0, c3w - 1.2, 0.5, C["l33"],
    "mean alignment (0.0 - 1.0)", fontsize=9, alpha=0.6)

ax.text(c3x + c3w / 2, 2.55,
        "compute_alignment() · alignment_judge.yaml",
        fontsize=7, color=C["label"], ha="center", family="monospace",
        style="italic")

# ═══════════════════════════════════════════════════════════════════════════════
# BOTTOM: Output
# ═══════════════════════════════════════════════════════════════════════════════

section_bg(0.3, 0.3, 17.4, 1.7, C["output"])
section_label(0.6, 1.75, "OUTPUT", C["output"])

# metrics.json centered between L3.1 and L3.2
metrics_cx = (c1x + c1w / 2 + c2x + c2w / 2) / 2
file_box(metrics_cx - 1.4, 0.5, 2.8, 0.65, C["output"], "metrics.json", fontsize=9)

ax.text(metrics_cx, 0.3,
        "validity_rate · jaccard · bertscore_f1 · alignment_mean",
        fontsize=7, color=C["label"], ha="center", family="monospace",
        style="italic")

# judgments.json under L3.3
judgments_cx = c3x + c3w / 2
file_box(judgments_cx - 1.4, 0.5, 2.8, 0.65, C["output"], "judgments.json", fontsize=9)

ax.text(judgments_cx, 0.3,
        "raw LLM judge outputs",
        fontsize=7, color=C["label"], ha="center", family="monospace",
        style="italic")

ax.text(9.0, 1.75,
        "src/evaluation/metrics.py  ·  src/evaluation/experiment.py",
        fontsize=7, color=C["label"], ha="center", family="monospace",
        style="italic")

# Light arrows from L3.1 and L3.2 output boxes down to metrics.json
arrow(c1x + c1w / 2, 3.1, metrics_cx, 1.2, lw=1.5, color="#B0B0B0")
arrow(c2x + c2w / 2, 3.1, metrics_cx, 1.2, lw=1.5, color="#B0B0B0")

# ── Save ─────────────────────────────────────────────────────────────────────
plt.tight_layout(pad=0.5)
plt.savefig("visualizations/evaluation_methods.png", dpi=200, bbox_inches="tight",
            facecolor=C["bg"], edgecolor="none")
plt.savefig("visualizations/evaluation_methods.svg", bbox_inches="tight",
            facecolor=C["bg"], edgecolor="none")
print("Saved visualizations/evaluation_methods.png + .svg")

"""Generate a vivid pipeline diagram showing data flow from vignettes to results."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# ── colours ──────────────────────────────────────────────────────────────────
C = {
    "vignette":   "#5B8DEE",   # blue
    "gen":        "#6C5CE7",   # indigo — matches eval L3.1
    "frozen":     "#8E44AD",   # purple
    "slice":      "#AF7AC5",   # light purple
    "eval":       "#E67E22",   # orange
    "trial":      "#F0B27A",   # light orange
    "agg":        "#E74C3C",   # red
    "result":     "#F1948A",   # light red
    "bg":         "#FAFBFC",   # near-white
    "text":       "#2C3E50",   # dark slate
    "arrow":      "#4A4A4A",   # dark grey
    "label":      "#566573",   # medium gray
}

fig, ax = plt.subplots(figsize=(18, 11))
fig.patch.set_facecolor(C["bg"])
ax.set_facecolor(C["bg"])
ax.set_xlim(0, 18)
ax.set_ylim(0, 11)
ax.axis("off")

# ── helpers ──────────────────────────────────────────────────────────────────

def box(x, y, w, h, color, label, sublabel=None, fontsize=10, alpha=0.92,
        bold=True, radius=0.3):
    """Draw a rounded box with label."""
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
    """Draw a small file-style box."""
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


def arrow(x1, y1, x2, y2, color=C["arrow"], lw=2, style="->"):
    """Draw a curved arrow."""
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle=style, color=color, lw=lw,
            connectionstyle="arc3,rad=0.08",
            shrinkA=4, shrinkB=4,
        ),
        zorder=2,
    )


def section_bg(x, y, w, h, color, alpha=0.06):
    """Draw a subtle background region."""
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.2,rounding_size=0.4",
        facecolor=color, edgecolor=color, linewidth=1.5, alpha=alpha,
        linestyle="--", zorder=1,
    )
    ax.add_patch(patch)


def section_label(x, y, text, color, fontsize=11):
    """Section header label."""
    ax.text(x, y, text, fontsize=fontsize, color=color,
            fontweight="bold", va="center", zorder=5)


# ═══════════════════════════════════════════════════════════════════════════════
# LAYOUT
# ═══════════════════════════════════════════════════════════════════════════════

# ── Section 1: Vignettes ─────────────────────────────────────────────────────
section_bg(0.3, 8.0, 3.4, 2.6, C["vignette"])
section_label(0.6, 10.3, "1  VIGNETTES", C["vignette"])

vignettes = ["anxious", "avoidant", "cooperative", "resistant", "skeptic", "trauma"]
for i, v in enumerate(vignettes):
    col = i % 2
    row = i // 2
    file_box(0.6 + col * 1.55, 9.4 - row * 0.5, 1.4, 0.38, C["vignette"], f"{v}.json")

ax.text(2.0, 8.22, "data/prompts/patients/vignettes/",
        fontsize=7.5, color=C["label"], ha="center", family="monospace", style="italic")

# ── Section 2: Generation ────────────────────────────────────────────────────
section_bg(3.8, 8.0, 3.2, 2.6, C["gen"])
section_label(4.1, 10.3, "2  GENERATE", C["gen"])

box(4.3, 8.65, 2.5, 1.1, C["gen"], "Generation Stack",
    sublabel="Patient ↔ Router ↔ Therapist")

ax.text(5.4, 8.2, "python -m src generate --freeze",
        fontsize=7, color=C["label"], ha="center", family="monospace", style="italic")

arrow(3.7, 9.1, 4.15, 9.1, lw=2.5)

# ── Section 3: Frozen Histories ──────────────────────────────────────────────
section_bg(0.3, 3.8, 7.0, 3.8, C["frozen"])
section_label(0.6, 7.3, "3  FROZEN HISTORIES", C["frozen"])

# Show one folder expanded, others as compact
folders = [
    ("frozen_anxious_54cf714f", True),
    ("frozen_avoidant_c74a38c3", False),
    ("frozen_cooperative_7f1feef7", False),
    ("frozen_resistant_c6726724", False),
    ("frozen_skeptic_22438f9b", False),
    ("frozen_trauma_260c754c", False),
]

# Other folders (compact) — LEFT side
for i, (fname, _) in enumerate(folders[1:]):
    short = fname.split("_")[1]  # just the vignette name
    file_box(0.6, 6.55 - i * 0.45, 2.3, 0.35, C["frozen"],
             f"frozen_{short}_*/", fontsize=7.5)

# Expanded folder (anxious) — RIGHT side
box(3.2, 4.55, 3.8, 2.5, C["frozen"], "", bold=False, alpha=0.25)
ax.text(5.1, 6.82, "frozen_anxious_54cf714f/",
        fontsize=8.5, color=C["frozen"], ha="center", fontweight="bold",
        family="monospace", zorder=5)

slice_files = ["full.json", "slice_1.json", "slice_2.json", "slice_3.json"]
slice_colors = [C["frozen"], C["slice"], C["slice"], C["slice"]]
for i, (sf, sc) in enumerate(zip(slice_files, slice_colors)):
    file_box(3.45 + (i % 2) * 1.85, 5.85 - (i // 2) * 0.55, 1.65, 0.4, sc, sf, fontsize=8)

ax.text(3.65, 4.05, "data/synthetic/frozen_histories/",
        fontsize=7.5, color=C["label"], ha="center", family="monospace", style="italic")

# Arrow from generation to frozen (single arrow)
arrow(5.4, 8.55, 5.1, 7.1, lw=2.5)

# ── Section 4: Evaluation ────────────────────────────────────────────────────
section_bg(8.0, 3.8, 5.2, 6.8, C["eval"])
section_label(8.3, 10.3, "4  EVALUATE", C["eval"])

ax.text(10.65, 9.95, "python -m src evaluate -i slice_3.json --model X",
        fontsize=6.5, color=C["label"], ha="center", family="monospace", style="italic")

# Step 1: Rescripting prompt injected directly (no router needed)
box(8.5, 9.05, 4.3, 0.75, C["eval"], "Rescripting Prompt",
    sublabel="no router — stage is known", fontsize=9)

# Arrow down to Therapist LLM
arrow(10.65, 9.05, 10.65, 8.8, lw=2)

# Step 2: Therapist LLM produces one rescripting message per trial
box(8.5, 8.0, 4.3, 0.75, C["eval"], "Therapist LLM",
    sublabel="fused CoT · x10 trials · T=0.0 / 0.7", fontsize=9)

# Arrow down to experiment folder + annotation
arrow(10.65, 8.0, 10.65, 7.5, lw=2)
ax.text(12.15, 7.65, "plan + response",
        fontsize=7.5, color=C["eval"], ha="left", style="italic", zorder=5)

# Arrow from frozen slice to eval (enters the rescripting prompt box)
arrow(7.0, 5.5, 8.5, 9.4, lw=2.5, style="-|>")

# Experiment run folder
box(8.4, 4.2, 4.5, 3.15, C["eval"], "", bold=False, alpha=0.2)

# Run folder header
ax.text(10.65, 7.1, "20260217_152151_llama70b_anxious/",
        fontsize=8, color=C["eval"], ha="center", fontweight="bold",
        family="monospace", zorder=5)

# Files inside run
run_files = [
    ("config.yaml", 0),
    ("frozen_history.json", 1),
    ("metrics.json", 2),
    ("judgments.json", 3),
]
for fname, i in run_files:
    col = i % 2
    row = i // 2
    file_box(8.65 + col * 2.15, 6.3 - row * 0.5, 1.95, 0.38, C["eval"], fname, fontsize=7.5)

# Trials subfolder
box(8.65, 4.5, 4.0, 1.0, C["trial"], "", bold=False, alpha=0.5)
ax.text(10.65, 5.3, "trials/", fontsize=8.5, color="white",
        ha="center", fontweight="bold", family="monospace", zorder=5)
trial_names = ["trial_01", "trial_02", "trial_03", "...", "trial_10"]
for i, tn in enumerate(trial_names):
    file_box(8.8 + i * 0.78, 4.6, 0.7, 0.32, C["trial"], tn, fontsize=6)

ax.text(10.65, 4.0, "experiments/runs/{timestamp}_{model}_{vignette}/",
        fontsize=7, color=C["label"], ha="center", family="monospace", style="italic")

# ── Section 5: Aggregation ───────────────────────────────────────────────────
section_bg(13.8, 3.8, 3.9, 6.8, C["agg"])
section_label(14.1, 10.3, "5  AGGREGATE", C["agg"])

box(14.1, 8.75, 3.3, 1.1, C["agg"], "Aggregation",
    sublabel="across 36 experiment runs")

ax.text(15.75, 9.95, "python -m src aggregate",
        fontsize=7, color=C["label"], ha="center", family="monospace", style="italic")

# Arrow from eval to aggregate
arrow(12.9, 9.5, 14.1, 9.5, lw=2.5)

# Result files
result_files = ["stability.json", "semantic_consistency.json", "alignment.json"]
for i, rf in enumerate(result_files):
    file_box(14.3, 7.2 - i * 0.55, 3.0, 0.42, C["result"], rf, fontsize=8.5)

arrow(15.75, 9.0, 15.75, 7.7, lw=2)

ax.text(15.8, 5.55, "data/synthetic/results/",
        fontsize=7.5, color=C["label"], ha="center", family="monospace", style="italic")

# ── Section 6: Slicing detail (bottom) ───────────────────────────────────────
section_bg(0.3, 0.15, 17.4, 3.4, "#566573")
section_label(0.6, 3.25, "SLICING DETAIL  —  each slice is a prefix of the dialogue, cut after the Nth rewriting exchange", "#566573", fontsize=9)

# Draw message blocks as a horizontal timeline
msg_data = [
    ("P", "—", "#85C1E9"),
    ("T", "rec", "#85C1E9"),
    ("P", "—", "#85C1E9"),
    ("T", "rec", "#85C1E9"),
    ("P", "—", "#85C1E9"),
    ("T", "rew 1", "#58D68D"),
    ("P", "—", "#58D68D"),
    # slice_1 cut
    ("T", "rew 2", "#F9E79F"),
    ("P", "—", "#F9E79F"),
    # slice_2 cut
    ("T", "rew 3", "#F0B27A"),
    ("P", "—", "#F0B27A"),
    # slice_3 cut
    ("T", "sum", "#D5D8DC"),
    ("T", "reh", "#D5D8DC"),
    ("T", "fin", "#D5D8DC"),
]

bx, by, bw, bh = 0.7, 1.3, 1.15, 0.8
gap = 0.12
for i, (role, stage, color) in enumerate(msg_data):
    x = bx + i * (bw + gap)
    patch = FancyBboxPatch(
        (x, by), bw, bh,
        boxstyle="round,pad=0.05,rounding_size=0.12",
        facecolor=color, edgecolor="white", linewidth=1.5, alpha=0.9,
        zorder=3,
    )
    ax.add_patch(patch)
    ax.text(x + bw / 2, by + bh / 2 + 0.12, role,
            ha="center", va="center", fontsize=11, color=C["text"],
            fontweight="bold", zorder=4)
    ax.text(x + bw / 2, by + bh / 2 - 0.18, stage,
            ha="center", va="center", fontsize=8.5, color=C["text"],
            zorder=4, family="monospace")

# Slice cut lines + labels
cuts = [
    (7, "slice_1", C["slice"]),
    (9, "slice_2", C["slice"]),
    (11, "slice_3", C["slice"]),
]
for msg_idx, label, color in cuts:
    x = bx + msg_idx * (bw + gap) - gap / 2
    ax.plot([x, x], [1.05, 2.35], color=color, lw=3, ls="--", zorder=5)
    ax.text(x, 2.75, label, ha="center", va="bottom",
            fontsize=10, color=color, fontweight="bold", zorder=5)
    # small cut marker
    ax.plot(x, 2.5, marker="v", color=color, markersize=8, zorder=5)

# Bracket for "not included"
x_after = bx + 11 * (bw + gap)
ax.text((x_after + bx + 13 * (bw + gap) + bw) / 2, 1.05,
        "not in any slice", ha="center", va="top",
        fontsize=8.5, color=C["label"], style="italic")

# Legend for the timeline
ax.text(0.7, 0.6, "P = Patient (stage=None)      T = Therapist (carries stage tag)      "
        "rec = recording      rew = rewriting      sum/reh/fin = later stages",
        fontsize=8, color=C["label"], va="center")

# ── Title ────────────────────────────────────────────────────────────────────
ax.text(9.0, 10.75, "Measure-AI-Drift  —  Data Creation & Slicing Pipeline",
        fontsize=16, color=C["text"], ha="center", fontweight="bold", zorder=10)

plt.tight_layout(pad=0.5)
plt.savefig("visualizations/pipeline_data_flow.png", dpi=200, bbox_inches="tight",
            facecolor=C["bg"], edgecolor="none")
plt.savefig("visualizations/pipeline_data_flow.svg", bbox_inches="tight",
            facecolor=C["bg"], edgecolor="none")
print("Saved visualizations/pipeline_data_flow.png + .svg")

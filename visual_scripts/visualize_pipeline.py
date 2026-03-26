"""Generate pipeline diagram showing data flow from vignettes to results.

Matches current experiment design:
    10 models · 6 vignettes · 5 temperatures · 20 trials = 6,000 trials
    Evaluation at slice_2 (second rewriting-turn boundary)
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ── colours ──────────────────────────────────────────────────────────────────
C = {
    "vignette":   "#5B8DEE",   # blue
    "gen":        "#6C5CE7",   # indigo
    "frozen":     "#8E44AD",   # purple
    "slice":      "#AF7AC5",   # light purple
    "slice_used": "#8E44AD",   # darker purple — the chosen slice
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


def arrow(x1, y1, x2, y2, color=C["arrow"], lw=2, style="->"):
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
# LAYOUT
# ═══════════════════════════════════════════════════════════════════════════════

# ── Section 1: Vignettes ─────────────────────────────────────────────────────
section_bg(0.3, 8.0, 3.4, 2.6, C["vignette"])
section_label(0.6, 10.3, "1  VIGNETTES", C["vignette"])

vignettes = ["anxious", "avoidant", "cooperative", "resistant", "skeptic", "trauma"]
for i, v in enumerate(vignettes):
    col = i % 2
    row = i // 2
    file_box(0.6 + col * 1.55, 9.4 - row * 0.5, 1.4, 0.38, C["vignette"], v)

ax.text(2.0, 8.22, "6 patient profiles",
        fontsize=7.5, color=C["label"], ha="center", style="italic")

# ── Section 2: Generation ────────────────────────────────────────────────────
section_bg(3.8, 8.0, 3.2, 2.6, C["gen"])
section_label(4.1, 10.3, "2  GENERATE", C["gen"])

box(4.3, 8.65, 2.5, 1.1, C["gen"], "Generation Stack",
    sublabel="Patient \u2194 Router \u2194 Therapist")

ax.text(5.4, 8.22, "one IRT session per vignette",
        fontsize=7, color=C["label"], ha="center", style="italic")

arrow(3.7, 9.1, 4.15, 9.1, lw=2.5)

# ── Section 3: Frozen Histories ──────────────────────────────────────────────
section_bg(0.3, 3.8, 7.0, 3.8, C["frozen"])
section_label(0.6, 7.3, "3  FROZEN HISTORIES", C["frozen"])

# Other folders (compact) — LEFT side
for i, v in enumerate(["avoidant", "cooperative", "resistant", "skeptic", "trauma"]):
    file_box(0.6, 6.55 - i * 0.45, 2.3, 0.35, C["frozen"],
             f"frozen_{v}", fontsize=7.5)

# Expanded folder (anxious) — RIGHT side
box(3.2, 4.55, 3.8, 2.5, C["frozen"], "", bold=False, alpha=0.25)
ax.text(5.1, 6.82, "frozen_anxious/",
        fontsize=8.5, color=C["frozen"], ha="center", fontweight="bold",
        family="monospace", zorder=5)

slice_files = [
    ("full.json", C["frozen"]),
    ("slice_1.json", C["slice"]),
    ("slice_2.json", C["slice_used"]),
    ("slice_3.json", C["slice"]),
]
for i, (sf, sc) in enumerate(slice_files):
    x = 3.45 + (i % 2) * 1.85
    y = 5.85 - (i // 2) * 0.55
    file_box(x, y, 1.65, 0.4, sc, sf, fontsize=8)

# Highlight slice_2 as the chosen one
ax.text(5.1, 4.7, "\u2191 used for evaluation",
        fontsize=7, color=C["slice_used"], ha="center",
        fontweight="bold", zorder=5)

ax.text(3.65, 4.05, "sliced at rewriting-turn boundaries",
        fontsize=7.5, color=C["label"], ha="center", style="italic")

# Arrow from generation to frozen
arrow(5.4, 8.55, 5.1, 7.1, lw=2.5)

# ── Section 4: Evaluation ────────────────────────────────────────────────────
section_bg(8.0, 3.8, 5.2, 6.8, C["eval"])
section_label(8.3, 10.3, "4  EVALUATE", C["eval"])

ax.text(10.65, 9.95, "per model \u00d7 vignette \u00d7 temperature",
        fontsize=7, color=C["label"], ha="center", style="italic")

# Step 1: Rescripting prompt
box(8.5, 9.05, 4.3, 0.75, C["eval"], "Rescripting Prompt",
    sublabel="frozen context + fused CoT", fontsize=9)

# Arrow down to Therapist LLM
arrow(10.65, 9.05, 10.65, 8.8, lw=2)

# Step 2: Therapist LLM
box(8.5, 8.0, 4.3, 0.75, C["eval"], "Therapist LLM",
    sublabel="20 trials \u00b7 5 temperatures [0.0 \u2013 0.6]", fontsize=9)

# Arrow down to experiment folder
arrow(10.65, 8.0, 10.65, 7.5, lw=2)
ax.text(12.15, 7.65, "plan + response",
        fontsize=7.5, color=C["eval"], ha="left", style="italic", zorder=5)

# Arrow from frozen slice to eval
arrow(7.0, 5.5, 8.5, 9.4, lw=2.5, style="-|>")

# Experiment run folder
box(8.4, 4.2, 4.5, 3.15, C["eval"], "", bold=False, alpha=0.2)

# Run folder header
ax.text(10.65, 7.1, "run_{model}_{vignette}/",
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
trial_names = ["trial_01", "trial_02", "trial_03", "...", "trial_20"]
for i, tn in enumerate(trial_names):
    file_box(8.8 + i * 0.78, 4.6, 0.7, 0.32, C["trial"], tn, fontsize=6)

ax.text(10.65, 4.0, "300 runs (10 models \u00d7 6 vignettes \u00d7 5 temps)",
        fontsize=7, color=C["label"], ha="center", style="italic")

# ── Section 5: Aggregation ───────────────────────────────────────────────────
section_bg(13.8, 3.8, 3.9, 6.8, C["agg"])
section_label(14.1, 10.3, "5  AGGREGATE", C["agg"])

box(14.1, 8.75, 3.3, 1.1, C["agg"], "Aggregation",
    sublabel="across 300 experiment runs")

ax.text(15.75, 9.95, "cross-model comparison",
        fontsize=7, color=C["label"], ha="center", style="italic")

# Arrow from eval to aggregate
arrow(12.9, 9.5, 14.1, 9.5, lw=2.5)

# Result files
result_files = [
    "experiment_runs.csv",
    "per-model statistics",
    "result figures",
]
for i, rf in enumerate(result_files):
    file_box(14.3, 7.2 - i * 0.55, 3.0, 0.42, C["result"], rf, fontsize=8.5)

arrow(15.75, 9.0, 15.75, 7.7, lw=2)

ax.text(15.8, 5.55, "6,000 total trials",
        fontsize=8, color=C["label"], ha="center", fontweight="bold")

# ── Section 6: Slicing detail (bottom) ───────────────────────────────────────
section_bg(0.3, 0.15, 17.4, 3.4, "#566573")
section_label(0.6, 3.25,
              "SLICING DETAIL  \u2014  each slice is a prefix of the dialogue, "
              "cut after the Nth rewriting exchange",
              "#566573", fontsize=9)

# Draw message blocks as a horizontal timeline
msg_data = [
    ("P", "\u2014", "#85C1E9"),
    ("T", "rec", "#85C1E9"),
    ("P", "\u2014", "#85C1E9"),
    ("T", "rec", "#85C1E9"),
    ("P", "\u2014", "#85C1E9"),
    ("T", "rew 1", "#58D68D"),
    ("P", "\u2014", "#58D68D"),
    # slice_1 cut
    ("T", "rew 2", "#F9E79F"),
    ("P", "\u2014", "#F9E79F"),
    # slice_2 cut  <-- used for evaluation
    ("T", "rew 3", "#F0B27A"),
    ("P", "\u2014", "#F0B27A"),
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
    (7, "slice_1", C["slice"], 1.5),
    (9, "slice_2", C["slice_used"], 3.0),    # thicker — the chosen slice
    (11, "slice_3", C["slice"], 1.5),
]
for msg_idx, label, color, lw in cuts:
    x = bx + msg_idx * (bw + gap) - gap / 2
    ax.plot([x, x], [1.05, 2.35], color=color, lw=lw, ls="--", zorder=5)
    fs = 11 if label == "slice_2" else 10
    ax.text(x, 2.75, label, ha="center", va="bottom",
            fontsize=fs, color=color, fontweight="bold", zorder=5)
    ax.plot(x, 2.5, marker="v", color=color, markersize=8, zorder=5)

# Annotation for slice_2
s2_x = bx + 9 * (bw + gap) - gap / 2
ax.text(s2_x, 0.9, "\u2191 evaluation point",
        fontsize=8, color=C["slice_used"], ha="center",
        fontweight="bold", zorder=5)

# Bracket for "not included"
x_after = bx + 11 * (bw + gap)
ax.text((x_after + bx + 13 * (bw + gap) + bw) / 2, 1.05,
        "not in any slice", ha="center", va="top",
        fontsize=8.5, color=C["label"], style="italic")

# Legend for the timeline
ax.text(0.7, 0.6, "P = Patient      T = Therapist      "
        "rec = recording      rew = rewriting      sum/reh/fin = later stages",
        fontsize=8, color=C["label"], va="center")

# ── Title ────────────────────────────────────────────────────────────────────
ax.text(9.0, 10.75, "Experiment Pipeline",
        fontsize=16, color=C["text"], ha="center", fontweight="bold", zorder=10)

plt.tight_layout(pad=0.5)
plt.savefig("thesis/figures/pipeline_data_flow.png", dpi=200, bbox_inches="tight",
            facecolor=C["bg"], edgecolor="none")
plt.savefig("thesis/figures/pipeline_data_flow.svg", bbox_inches="tight",
            facecolor=C["bg"], edgecolor="none")
print("Saved thesis/figures/pipeline_data_flow.png + .svg")

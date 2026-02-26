"""Generate a model overview diagram showing all thesis LLM roles and evaluation targets."""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ── colours (shared palette from visualize_pipeline.py) ──────────────────────
C = {
    "gen":        "#6C5CE7",   # indigo
    "primary":    "#E67E22",   # orange (highlight)
    "small":      "#5B8DEE",   # blue
    "mid":        "#8E44AD",   # purple
    "ceiling":    "#E74C3C",   # red
    "judge":      "#27AE60",   # green
    "bg":         "#FAFBFC",   # near-white
    "text":       "#2C3E50",   # dark slate
    "arrow":      "#4A4A4A",   # dark grey
    "label":      "#566573",   # medium gray
    "section_bg": "#E8EAF0",   # light section fill
}

fig, ax = plt.subplots(figsize=(16, 12))
fig.patch.set_facecolor(C["bg"])
ax.set_facecolor(C["bg"])
ax.set_xlim(0, 16)
ax.set_ylim(0, 12)
ax.axis("off")


# ── helpers ──────────────────────────────────────────────────────────────────

def box(x, y, w, h, color, label, sublabel=None, fontsize=10, alpha=0.92,
        bold=True, radius=0.3):
    """Draw a rounded box with label and optional sublabel."""
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.15,rounding_size={radius}",
        facecolor=color, edgecolor="white", linewidth=2, alpha=alpha,
        zorder=3,
    )
    ax.add_patch(patch)
    weight = "bold" if bold else "normal"
    ty = y + h / 2 + (0.15 if sublabel else 0)
    ax.text(x + w / 2, ty, label, ha="center", va="center",
            fontsize=fontsize, color="white", fontweight=weight, zorder=4)
    if sublabel:
        ax.text(x + w / 2, y + h / 2 - 0.2, sublabel,
                ha="center", va="center", fontsize=fontsize - 2,
                color="white", fontstyle="italic", alpha=0.9, zorder=4)


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


def arrow(x1, y1, x2, y2, color=C["arrow"], lw=2):
    """Draw a curved arrow."""
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="->", color=color, lw=lw,
            connectionstyle="arc3,rad=0.05",
            shrinkA=4, shrinkB=4,
        ),
        zorder=2,
    )


# ═════════════════════════════════════════════════════════════════════════════
# LAYOUT
# ═════════════════════════════════════════════════════════════════════════════

# ── Title ────────────────────────────────────────────────────────────────────
ax.text(8.0, 11.55, "Measure-AI-Drift: Model Overview",
        fontsize=16, color=C["text"], ha="center", fontweight="bold", zorder=10)

# ── Generation Stack ─────────────────────────────────────────────────────────
section_bg(0.5, 9.3, 15.0, 1.9, C["gen"])
section_label(0.9, 10.95, "GENERATION STACK (supporting roles, not evaluated)", C["gen"])

box(1.0, 9.6, 3.8, 1.0, C["gen"], "Patient",
    sublabel="Venice 24B / OpenRouter / T=0.7")
box(6.1, 9.6, 3.8, 1.0, C["gen"], "Router",
    sublabel="Llama 70B / Groq / T=0.0")
box(11.2, 9.6, 3.8, 1.0, C["gen"], "Therapist",
    sublabel="Llama 70B / Groq / T=0.0")

# Bidirectional arrows between generation agents
ax.annotate("", xy=(5.8, 10.1), xytext=(5.0, 10.1),
            arrowprops=dict(arrowstyle="<->", color="white", lw=2))
ax.annotate("", xy=(10.9, 10.1), xytext=(10.1, 10.1),
            arrowprops=dict(arrowstyle="<->", color="white", lw=2))

# ── Arrow: Generation to Evaluation ─────────────────────────────────────────
ax.text(8.0, 9.0, "frozen histories", ha="center", va="center",
        fontsize=9, color=C["label"], fontstyle="italic", zorder=5)
arrow(8.0, 9.3, 8.0, 8.85, color=C["arrow"], lw=2.5)

# ── Evaluation Stack ─────────────────────────────────────────────────────────
section_bg(0.5, 0.5, 15.0, 8.1, C["primary"], alpha=0.04)
section_label(0.9, 8.35, "EVALUATION STACK (stability measurement)", C["primary"])

# ── Primary Subject (prominent center box) ───────────────────────────────────
box(4.0, 6.4, 8.0, 1.6, C["primary"], "Mistral Large 3 (Primary Subject)",
    sublabel="675B MoE (41B active) / Mistral API / Apache 2.0 / EU-sovereign",
    fontsize=13)

# ── Comparator models ────────────────────────────────────────────────────────

# Small class (left column)
section_label(0.9, 5.65, "SMALL (24-32B)", C["small"], fontsize=9)

box(0.7, 4.4, 4.3, 1.0, C["small"], "Mistral Small 3.2",
    sublabel="24B dense / Scaleway / Apache 2.0")
box(0.7, 3.1, 4.3, 1.0, C["small"], "Qwen 3 32B",
    sublabel="32B dense / Groq / Apache 2.0")
box(0.7, 1.8, 4.3, 1.0, C["small"], "OLMo 3.1 32B",
    sublabel="32B dense / OpenRouter / fully open")

# Mid class (center column)
section_label(5.75, 5.65, "MID (70B+)", C["mid"], fontsize=9)

box(5.5, 4.4, 4.6, 1.0, C["mid"], "Llama 3.3 70B",
    sublabel="70B dense / Groq / efficacy study")
box(5.5, 3.1, 4.6, 1.0, C["mid"], "Mistral Medium 3",
    sublabel="undisclosed / Mistral API / EU-origin")

# Proprietary ceiling (right column)
section_label(11.15, 5.65, "PROPRIETARY CEILING", C["ceiling"], fontsize=9)

box(11.0, 4.4, 4.3, 1.0, C["ceiling"], "Gemini 3 Pro",
    sublabel="Google AI Studio / free credits")
box(11.0, 3.1, 4.3, 1.0, C["ceiling"], "Gemini 2.5 Flash",
    sublabel="Google AI Studio / pipeline testing")

# ── Judge (bottom) ───────────────────────────────────────────────────────────
box(5.5, 0.8, 5.0, 0.9, C["judge"], "Judge: Gemini 2.5 Flash",
    sublabel="T=0.0 / scores plan-output alignment (Method 3)")

# ── Arrows from primary to judge ────────────────────────────────────────────
arrow(8.0, 6.4, 8.0, 1.75, color=C["judge"], lw=1.5)
ax.text(8.6, 4.0, "trials scored by judge", ha="left", va="center",
        fontsize=8, color=C["judge"], fontstyle="italic", zorder=5,
        rotation=90)

# ── Arrows from primary down to comparator columns ──────────────────────────
arrow(6.0, 6.4, 2.9, 5.55, color=C["small"], lw=1.5)
arrow(8.0, 6.4, 7.8, 5.55, color=C["mid"], lw=1.5)
arrow(10.0, 6.4, 13.1, 5.55, color=C["ceiling"], lw=1.5)

# ── Legend note ──────────────────────────────────────────────────────────────
ax.text(0.7, 0.2,
        "MoE note: 41B active params per token. Deterministic routing "
        "at inference adds no stochastic variance to stability measurements.",
        fontsize=8, color=C["label"], va="center", fontstyle="italic")

# ── Save ─────────────────────────────────────────────────────────────────────
plt.tight_layout(pad=0.5)
plt.savefig("visualizations/thesis_models.png", dpi=200, bbox_inches="tight",
            facecolor=C["bg"], edgecolor="none")
plt.savefig("visualizations/thesis_models.svg", bbox_inches="tight",
            facecolor=C["bg"], edgecolor="none")
print("Saved visualizations/thesis_models.png + .svg")

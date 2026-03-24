"""Figure 3.3: Evaluation stack detail.

Shows what happens in a single evaluation condition:
Frozen History → Model Under Test → N independent trials (plan + response).

Output: thesis/figures/fig_3_3_eval_stack.pdf
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

C_FROZEN = "#fff9c4"
C_MODEL = "#fadbd8"
C_TRIAL = "#d5f5e3"
C_PLAN = "#aed6f1"
C_RESP = "#d5f5e3"
C_BORDER = "#2c3e50"
C_ARROW = "#566573"


def rbox(ax, x, y, w, h, color="white", lw=1.2):
    b = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.08", facecolor=color,
        edgecolor=C_BORDER, linewidth=lw, zorder=3,
    )
    ax.add_patch(b)


def arrow(ax, x1, y1, x2, y2, color=C_ARROW, lw=1.5):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw), zorder=2,
    )


def main():
    fig, ax = plt.subplots(figsize=(15, 6.5))
    ax.set_xlim(-0.5, 15)
    ax.set_ylim(-0.8, 5.8)
    ax.set_aspect("equal")
    ax.axis("off")

    # ── Left: Frozen History ────────────────────────────────────────────
    fx, fy = 2.0, 2.5
    rbox(ax, fx, fy, 3.2, 3.8, C_FROZEN)
    ax.text(fx, 4.15, "Frozen History", ha="center", va="center",
            fontsize=12, fontweight="bold", zorder=4)

    turns = [
        ("P:", "I had this nightmare about..."),
        ("T:", "Can you describe what you saw?"),
        ("P:", "There was a dark figure and..."),
        ("T:", "Let's try to rescript this..."),
        ("P:", "I felt so trapped, I couldn't..."),
        ("T:", "What would you change?"),
    ]
    for i, (role, text) in enumerate(turns):
        yy = 3.55 - i * 0.38
        c = "#2471a3" if role == "P:" else "#c0392b"
        ax.text(0.7, yy, role, fontsize=8, fontweight="bold",
                color=c, zorder=4, family="monospace")
        ax.text(1.15, yy, text, fontsize=7.5, color="#444", zorder=4)

    ax.text(fx, 0.75, "Identical for every trial",
            ha="center", va="center", fontsize=8.5, color="#888",
            style="italic", zorder=4)

    # ── Center: Model Under Test ────────────────────────────────────────
    mx, my = 6.2, 2.5
    rbox(ax, mx, my, 2.6, 2.2, C_MODEL)
    ax.text(mx, 3.25, "Model", ha="center", va="center",
            fontsize=12, fontweight="bold", zorder=4)
    ax.text(mx, 2.85, "Under Test", ha="center", va="center",
            fontsize=12, fontweight="bold", zorder=4)
    ax.text(mx, 2.25, "e.g. Mistral Large 3", ha="center", va="center",
            fontsize=8.5, color="#555", zorder=4)
    ax.text(mx, 1.8, "Temperature = T", ha="center", va="center",
            fontsize=9.5, color="#c0392b", fontweight="bold", zorder=4)

    # Arrow: frozen -> model
    arrow(ax, 3.6, 2.5, 4.9, 2.5)
    ax.text(4.25, 2.85, "Same\ncontext", ha="center", va="bottom",
            fontsize=8, color="#666", zorder=4)

    # ── Right: Fan-out to trials ────────────────────────────────────────
    trial_data = [
        (4.5, "confrontation, cognitive_reframe",
              "In your new dream, you turn to face the figure..."),
        (3.5, "confrontation, self_empowerment",
              "Imagine you feel a surge of strength within..."),
        (2.5, "cognitive_reframe, social_support",
              "What if the dark figure was actually trying..."),
    ]
    ellipsis_y = 1.5
    last_y = 0.6

    # Fan-out arrows from model to each trial
    for ty, _, _ in trial_data:
        arrow(ax, 7.5, 2.5, 8.6, ty)
    arrow(ax, 7.5, 2.5, 8.6, ellipsis_y)
    arrow(ax, 7.5, 2.5, 8.6, last_y)

    # Trial boxes
    tw = 5.8
    for i, (ty, strategies, response) in enumerate(trial_data):
        rbox(ax, 11.5, ty, tw, 0.75, C_TRIAL, lw=0.9)

        # Trial label
        ax.text(8.8, ty + 0.05, f"Trial {i + 1}", ha="left", va="center",
                fontsize=8, color="#888", fontweight="bold", zorder=4)

        # Plan section
        ax.text(10.0, ty + 0.15, "<plan>", ha="left", va="center",
                fontsize=7.5, fontweight="bold", color="#2471a3",
                zorder=4, family="monospace")
        ax.text(10.7, ty + 0.15, strategies, ha="left", va="center",
                fontsize=7.5, color="#333", zorder=4)

        # Response preview
        ax.text(10.0, ty - 0.15, response[:45] + "...", ha="left", va="center",
                fontsize=7, color="#666", style="italic", zorder=4)

    # Ellipsis
    ax.text(11.5, ellipsis_y, "\u22ef", ha="center", va="center",
            fontsize=20, color="#aaa", zorder=4)

    # Last trial (N=20)
    rbox(ax, 11.5, last_y, tw, 0.65, "#eee", lw=0.8)
    ax.text(8.8, last_y + 0.05, "Trial 20", ha="left", va="center",
            fontsize=8, color="#888", fontweight="bold", zorder=4)
    ax.text(10.0, last_y + 0.12, "<plan>", ha="left", va="center",
            fontsize=7.5, fontweight="bold", color="#2471a3",
            zorder=4, family="monospace")
    ax.text(10.7, last_y + 0.12, "self_empowerment, safety", ha="left", va="center",
            fontsize=7.5, color="#333", zorder=4)
    ax.text(10.0, last_y - 0.15, "You find a shield of light forming...", ha="left",
            va="center", fontsize=7, color="#666", style="italic", zorder=4)

    # Top label
    ax.text(11.5, 5.2, "20 independent outputs",
            ha="center", va="center", fontsize=12, fontweight="bold", zorder=4)
    ax.text(11.5, 4.8, "Same input, different stochastic samples",
            ha="center", va="center", fontsize=9, color="#666",
            style="italic", zorder=4)

    # Bottom annotation
    ax.text(7.5, -0.5,
            "Strategy variation across trials = the instability this study measures",
            ha="center", va="center", fontsize=9.5, color="#888",
            style="italic", zorder=4)

    fig.tight_layout()
    fig.savefig("thesis/figures/fig_3_3_eval_stack.pdf", bbox_inches="tight")
    fig.savefig("thesis/figures/fig_3_3_eval_stack.png", bbox_inches="tight", dpi=150)
    print("Saved thesis/figures/fig_3_3_eval_stack")
    plt.close(fig)


if __name__ == "__main__":
    main()

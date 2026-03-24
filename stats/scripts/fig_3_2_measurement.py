"""Figure 3.2: Three-level measurement framework.

Shows the three evaluation methods, what clinical question each answers,
inputs and output metrics.

Output: thesis/figures/fig_3_2_measurement.pdf
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

FIG_W, FIG_H = 13, 7

C1 = "#aed6f1"   # blue  - plan consistency
C2 = "#a9dfbf"   # green - response similarity
C3 = "#f9e79f"   # yellow - alignment
C_BORDER = "#2c3e50"
C_ARROW = "#566573"


def rbox(ax, x, y, w, h, color="white"):
    b = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.08", facecolor=color,
        edgecolor=C_BORDER, linewidth=1.1, zorder=3,
    )
    ax.add_patch(b)


def arrow(ax, x1, y1, x2, y2):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=C_ARROW, lw=1.4), zorder=2,
    )


def draw_row(ax, y, color, num, title, question, input_text, metric, metric_detail):
    # Method box (wide center)
    cx = 6.5
    bw, bh = 5.0, 1.3
    rbox(ax, cx, y, bw, bh, color)
    ax.text(cx, y + 0.28, f"Method {num}: {title}",
            ha="center", va="center", fontsize=12, fontweight="bold", zorder=4)
    ax.text(cx, y - 0.22, question,
            ha="center", va="center", fontsize=9.5, color="#444",
            style="italic", zorder=4)

    # Input box (left)
    lx, lw, lh = 1.8, 2.8, 0.8
    rbox(ax, lx, y, lw, lh, "white")
    ax.text(lx, y, input_text, ha="center", va="center",
            fontsize=9, zorder=4)

    arrow(ax, lx + lw / 2, y, cx - bw / 2, y)

    # Output box (right)
    rx, rw, rh = 11.3, 2.2, 0.8
    rbox(ax, rx, y, rw, rh, "white")
    ax.text(rx, y + 0.13, metric, ha="center", va="center",
            fontsize=10, fontweight="bold", zorder=4)
    ax.text(rx, y - 0.17, metric_detail, ha="center", va="center",
            fontsize=7.5, color="#666", zorder=4)

    arrow(ax, cx + bw / 2, y, rx - rw / 2, y)


def main():
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    ax.set_xlim(-0.5, 13)
    ax.set_ylim(-0.5, 7.2)
    ax.set_aspect("equal")
    ax.axis("off")

    # Title
    ax.text(6.5, 6.7, "Three-Level Evaluation Framework",
            ha="center", va="center", fontsize=15, fontweight="bold")
    ax.text(6.5, 6.2, "Each method targets a distinct layer of the generation process",
            ha="center", va="center", fontsize=10, color="#666", style="italic")

    # Column headers
    ax.text(1.8, 5.55, "Input", ha="center", va="center",
            fontsize=10, fontweight="bold", color="#888")
    ax.text(6.5, 5.55, "Evaluation Method", ha="center", va="center",
            fontsize=10, fontweight="bold", color="#888")
    ax.text(11.3, 5.55, "Metric", ha="center", va="center",
            fontsize=10, fontweight="bold", color="#888")

    draw_row(ax, y=4.6, color=C1, num=1,
             title="Plan Consistency",
             question="Does the model select the same strategies?",
             input_text="Strategy sets\nfrom <plan> blocks",
             metric="Jaccard",
             metric_detail="Set similarity [0, 1]")

    draw_row(ax, y=2.8, color=C2, num=2,
             title="Response Similarity",
             question="Does the model produce equivalent responses?",
             input_text="Therapeutic\nresponse texts",
             metric="BERTScore F1",
             metric_detail="Semantic similarity [0, 1]")

    draw_row(ax, y=1.0, color=C3, num=3,
             title="Plan-Response Alignment",
             question="Does the model do what it declared?",
             input_text="Plan + Response\n(per trial)",
             metric="Alignment",
             metric_detail="LLM judge [0, 1, 2]")

    # Vertical connector showing same trials
    ax.plot([0.2, 0.2], [1.0, 4.6], color="#bbb", linewidth=2.0,
            linestyle=":", zorder=1)
    ax.text(0.2, 2.8, "Same 20 trials\nper condition",
            ha="center", va="center", fontsize=8, color="#999",
            rotation=90, zorder=4,
            bbox=dict(facecolor="white", edgecolor="none", pad=2))

    fig.tight_layout()
    fig.savefig("thesis/figures/fig_3_2_measurement.pdf", bbox_inches="tight")
    fig.savefig("thesis/figures/fig_3_2_measurement.png", bbox_inches="tight", dpi=150)
    print("Saved thesis/figures/fig_3_2_measurement")
    plt.close(fig)


if __name__ == "__main__":
    main()

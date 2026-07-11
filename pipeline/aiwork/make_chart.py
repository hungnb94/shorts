"""One-off asset generator for the data_viz_overlay value-add (render_aiwork_v1.py).

Real data transcribed directly off Alex Albert's on-screen slide at t=217-235s of
tP4MGcJ80Y0 ("Every model moves the ceiling" / SWE-bench Verified since Sonnet 3.7).
Styled in the channel's own indigo palette (brand_assets.txt) rather than reproducing
the source slide's orange/cream look, so this reads as our own transformative overlay,
not a screenshot of Anthropic's deck.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

MODELS = ["Sonnet 3.7", "Opus 4", "Opus 4.1", "Opus 4.5", "Opus 4.5", "Opus 4.6", "Opus 4.7"]
SCORES = [62.3, 72.5, 74.5, 77.2, 80.9, 80.8, 87.6]

INDIGO = "#4F46E5"
INDIGO_DARK = "#312E81"
BG = "none"

fig, ax = plt.subplots(figsize=(9.6, 5.4), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor("none")

x = range(len(MODELS))
ax.plot(x, SCORES, color=INDIGO, linewidth=5, zorder=3, solid_capstyle="round")
ax.scatter(x[:-1], SCORES[:-1], s=90, facecolors="white", edgecolors=INDIGO, linewidths=3, zorder=4)
ax.scatter([x[-1]], [SCORES[-1]], s=260, facecolors=INDIGO, edgecolors="white", linewidths=3, zorder=5)

ax.annotate("62.3%", (x[0], SCORES[0]), textcoords="offset points", xytext=(-4, -34),
            fontsize=26, fontweight="bold", color=INDIGO_DARK, ha="center")
ax.annotate("87.6%", (x[-1], SCORES[-1]), textcoords="offset points", xytext=(0, 22),
            fontsize=34, fontweight="bold", color=INDIGO_DARK, ha="center")
ax.annotate("+25.3 pts in ~1 year", xy=(3, 68), fontsize=20, color=INDIGO_DARK,
            ha="center", style="italic")

ax.set_ylim(50, 100)
ax.set_xlim(-0.4, len(MODELS) - 0.6)
ax.set_xticks(list(x))
ax.set_xticklabels([m if i in (0, len(MODELS) - 1) else "" for i, m in enumerate(MODELS)],
                    fontsize=18, color="#333333")
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(length=0)

plt.tight_layout()
out = "output/projects/aiwork/final/assets/capability_curve_chart.png"
plt.savefig(out, transparent=True)
print(f"Saved {out}")

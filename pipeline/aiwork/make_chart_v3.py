"""One-off asset generator for the data_viz_overlay value-add (render_aiwork_v3.py).

Real numbers transcribed directly from mWvtOHlZM-I's own narration (not shown on screen
in any footage we actually use): "system prompt had grown to become several hundred
lines long" plus the precise "400 lines long" figure named later at t=226.3s (a slide-only
moment we do NOT use as footage, per the audience-fit decision to avoid code/CLI-heavy
visuals), and "we simplified our system prompt to 15 lines long" at t=2506.3s (also
slide-adjacent, not used as footage). Styled in the channel's own indigo palette
(brand_assets.txt), same approach as make_chart.py (v1/v2), so this reads as our own
transformative overlay, not a screenshot of Anthropic's deck.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INDIGO = "#4F46E5"
INDIGO_LIGHT = "#A5B4FC"
INDIGO_DARK = "#312E81"

fig, ax = plt.subplots(figsize=(9.0, 6.0), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor("none")

labels = ["BEFORE", "AFTER"]
values = [400, 15]
colors = [INDIGO_LIGHT, INDIGO]

bars = ax.bar(labels, values, color=colors, width=0.55, zorder=3)

ax.annotate("400 lines", (0, 400), textcoords="offset points", xytext=(0, 14),
            fontsize=30, fontweight="bold", color=INDIGO_DARK, ha="center")
ax.annotate("15 lines", (1, 15), textcoords="offset points", xytext=(0, 14),
            fontsize=30, fontweight="bold", color=INDIGO_DARK, ha="center")

ax.set_ylim(0, 460)
ax.set_xticks([0, 1])
ax.set_xticklabels(labels, fontsize=24, fontweight="bold", color="#333333")
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(length=0)

plt.tight_layout()
out = "output/projects/aiwork/final/assets/prompt_bloat_chart_v3.png"
plt.savefig(out, transparent=True)
print(f"Saved {out}")

#!/usr/bin/env python3
"""Re-run only Mode B variants with longer commentary for 30-60s."""
import sys, asyncio
from pathlib import Path

sys.path.insert(0, str(Path("/Users/hung/code/ai/shorts/scripts")))
import importlib.util
spec = importlib.util.spec_from_file_location("v5", Path("/Users/hung/code/ai/shorts/scripts/render_explore_v5.py"))
assert spec and spec.loader, "Failed to load render_explore_v5.py"
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Override B narratives with longer content
for n in mod.NARRATIVES:
    if n["id"] == "b1_culture":
        n["commentary_tts"] = (
            "Andy Frisella built a billion dollar company by focusing on one thing. Culture. "
            "He says people spend most of their life at work. "
            "If you don't have a strong culture, you can't have a strong business. "
            "So he created a culture where everybody trains together, works together, "
            "and struggles together. That mutual suffering builds character. "
            "That character builds companies. "
            "It's not about the product. It's about the people. "
            "When you have the right people who share the same values, "
            "everything else falls into place. "
            "That's the secret. Culture. Not money. Not strategy. Culture."
        )
    elif n["id"] == "b2_fitness":
        n["commentary_tts"] = (
            "There's a huge correlation between physical fitness and financial success. "
            "Andy says it's not just about looking good. "
            "When everybody trains together and struggles together, "
            "something powerful happens. Mutual suffering. "
            "You see people who are dying on the gym floor, "
            "and the person next to them is their boss at work. "
            "But out here, they are equal. "
            "The same discipline it takes to show up at five AM for a workout "
            "is exactly the same discipline it takes to show up for your business. "
            "Your body and your bank account are built by the same habit. "
            "You cannot separate them. Work on both."
        )
    elif n["id"] == "b3_advice":
        n["commentary_tts"] = (
            "Andy Frisella has spent his whole life encouraging young entrepreneurs. "
            "He says this isn't just about Lamborghinis and balling out. "
            "This is hard. It's a grind. And just because it's hard "
            "doesn't mean you're doing it wrong. It means you're doing it right. "
            "Anybody can learn the skills. Anybody can learn to be resilient. "
            "But you have to be willing to pay the price. "
            "And that price is often left out of what you see on the internet. "
            "Every single person hearing this has the ability to be great. "
            "But greatness requires sacrifice. Are you willing to pay that price?"
        )

async def main():
    b_videos = [(i, n) for i, n in enumerate(mod.NARRATIVES) if n["mode"] == "B"]
    print(f"Re-rendering {len(b_videos)} Mode B videos...")
    for idx, narr in b_videos:
        print(f"\n{'='*60}")
        print(f"  [{idx+1}/6] {narr['id']} (mode B)")
        try:
            dur, mb = await mod.render_variant_b(narr, narr["hook"], idx + 1, mod.OUTDIR)
            print(f"  ✅ {dur:.1f}s, {mb:.1f}MB")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"  ❌ {e}")

asyncio.run(main())

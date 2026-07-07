// Character image generation via Pollinations (free, no auth)
// 7 protagonist states + 6 supporting visuals for B-AI-META storyboard
// Style: minimalist illustration, dark moody palette, cinematic

const POLLINATIONS = "https://image.pollinations.ai/prompt";

const characters = [
  // CH 1 — FALL: broken founder, alone in dark apartment
  {
    id: "ch1_founder",
    prompt: "minimalist portrait illustration, young Asian male founder 25 years old, sitting alone on floor in dark apartment, knees up, head down, single dim light from cracked laptop, blue-cyan cold color palette, painterly cinematic, Spider-Verse style, dramatic rim light, melancholic mood, vertical 9:16 composition",
    seed: 1001,
  },
  // CH 2 — HUMILIATION: empty chairs, demo rejection
  {
    id: "ch2_demo",
    prompt: "minimalist illustration, empty presentation chairs in dark co-working space, one chair tilted over, spotlight on broken laptop on stage, scattered rejection letters on floor, cold cyan-grey palette, painterly cinematic, vertical 9:16, lonely mood, Spider-Verse style",
    seed: 1002,
  },
  // CH 3 — FAKE HOPE: AI guru on phone screen (THE TELL: faint scan lines)
  {
    id: "ch3_guru",
    prompt: "minimalist portrait, charismatic Asian male guru 35 years old, slicked hair, designer jacket, gold chain, holding cash, fake smile, dark background with magenta neon glow, slight glitch scan-line artifacts on face, sinister charlatan vibe, painterly cinematic, vertical 9:16, Spider-Verse style",
    seed: 1003,
  },
  // CH 4 — FALSE VICTORY: holding fake check
  {
    id: "ch4_fake_win",
    prompt: "minimalist illustration, young Asian founder holding giant novelty check above head, but his face is conflicted, worried eyes, smile is fake, dark ballroom background with stage lights, gold-magenta palette, painterly cinematic, vertical 9:16, Spider-Verse style, hollow victory mood",
    seed: 1004,
  },
  // CH 5 — ABYSS: hospital + empty apartment
  {
    id: "ch5_abyss",
    prompt: "minimalist dramatic illustration, young Asian founder kneeling in dark empty apartment, hospital bracelet still on wrist, torn check on floor, cracked laptop showing balance zero dollars, single red webcam LED glowing ominously, cold blue-cyan with red accent, painterly cinematic, vertical 9:16, Spider-Verse style, devastating mood",
    seed: 1005,
  },
  // CH 6 — REAL RISE: coding alone at 3am
  {
    id: "ch6_rise",
    prompt: "minimalist illustration, young Asian founder alone at library desk at 3am, multiple laptop screens with green code, focused determined eyes, cuts on knuckles, dawn light coming through window, warm amber tones rising from cold blue, painterly cinematic, vertical 9:16, Spider-Verse style, heroic grind mood",
    seed: 1006,
  },
  // CH 7 — TOTAL DOMINANCE: NASDAQ bell ringing
  {
    id: "ch7_nasdaq",
    prompt: "minimalist illustration, young Asian founder in tailored jacket ringing NASDAQ bell, college hoodie underneath, triumphant but humble, golden warm light pouring from above, magenta accents, confetti particles, painterly cinematic, vertical 9:16, Spider-Verse style, victory mood, family lineage theme",
    seed: 1007,
  },
  // Supporting: father hospital
  {
    id: "father",
    prompt: "minimalist portrait, elderly Asian father 70 years old, hospital bed, gentle wise eyes, oxygen tube, fading but smiling, soft warm light, painterly cinematic, vertical 9:16, Spider-Verse style, emotional intimate mood",
    seed: 2001,
  },
  // Supporting: boy at library (loop callback)
  {
    id: "boy",
    prompt: "minimalist portrait, young Asian boy 10 years old, sitting at library desk with old laptop, curious bright eyes, hope, soft warm light, painterly cinematic, vertical 9:16, Spider-Verse style, innocent determined mood",
    seed: 2002,
  },
  // Supporting: mentor (old librarian)
  {
    id: "mentor",
    prompt: "minimalist portrait, grizzled elderly Asian man 75 years old, former CTO, now librarian, kind tired eyes, books in background, soft warm light, painterly cinematic, vertical 9:16, Spider-Verse style, mentor sage mood",
    seed: 2003,
  },
  // Supporting: co-founder walking away
  {
    id: "cofounder_leave",
    prompt: "minimalist illustration, back view of a person in business casual walking away through glass door, leaving a young founder alone in office, boxes being packed, cold cyan-grey palette, painterly cinematic, vertical 9:16, Spider-Verse style, betrayal mood",
    seed: 2004,
  },
  // Supporting: grave scene
  {
    id: "grave",
    prompt: "minimalist illustration, small gravestone in peaceful cemetery at golden hour, IPO lanyard placed on stone, fresh flowers, founder kneeling, soft warm sunset light, painterly cinematic, vertical 9:16, Spider-Verse style, emotional reconciliation mood",
    seed: 2005,
  },
  // Supporting: laptop with $0 balance (key prop)
  {
    id: "laptop_zero",
    prompt: "minimalist close-up illustration, cracked laptop screen showing account balance zero dollars in red text, dark room, single red webcam LED glowing, cold blue tones, painterly cinematic, vertical 9:16, Spider-Verse style, devastating final loss",
    seed: 2006,
  },
];

// Generate via Pollinations - free, no auth needed
async function generateAll() {
  const fs = await import('fs');
  const path = await import('path');

  const assetDir = path.join(process.cwd(), 'public', 'assets');
  fs.mkdirSync(assetDir, { recursive: true });

  for (const char of characters) {
    const url = `${POLLINATIONS}/${encodeURIComponent(char.prompt)}?width=1080&height=1920&seed=${char.seed}&nologo=true&model=flux`;
    console.log(`Generating ${char.id}...`);
    console.log(`  URL: ${url.substring(0, 100)}...`);

    const response = await fetch(url);
    if (!response.ok) {
      console.error(`  FAILED: ${response.status}`);
      continue;
    }
    const buffer = Buffer.from(await response.arrayBuffer());
    const outPath = path.join(assetDir, `${char.id}.jpg`);
    fs.writeFileSync(outPath, buffer);
    console.log(`  Saved: ${outPath} (${(buffer.length / 1024).toFixed(0)}KB)`);
  }
  console.log("\nAll characters generated.");
}

generateAll().catch(console.error);

// Supporting visuals - lean model for speed
const POLLINATIONS = "https://image.pollinations.ai/prompt";

const supporting = [
  { id: "father", prompt: "minimalist portrait elderly Asian father 70 hospital bed, gentle wise eyes, oxygen tube, soft warm light, painterly cinematic, vertical 9:16", seed: 2001 },
  { id: "boy", prompt: "minimalist portrait Asian boy 10 years old library desk laptop, curious bright eyes, soft warm light, painterly cinematic, vertical 9:16", seed: 2002 },
  { id: "mentor", prompt: "minimalist portrait grizzled Asian man 75 librarian, kind tired eyes, books background, painterly cinematic, vertical 9:16", seed: 2003 },
  { id: "cofounder_leave", prompt: "minimalist back view person walking away through glass door leaving office, boxes, cold cyan-grey, painterly cinematic, vertical 9:16", seed: 2004 },
  { id: "grave", prompt: "minimalist small gravestone cemetery golden hour, IPO lanyard on stone, founder kneeling, soft sunset, painterly cinematic, vertical 9:16", seed: 2005 },
  { id: "laptop_zero", prompt: "minimalist close-up cracked laptop screen zero dollars red text, dark room, red webcam LED, cold blue, painterly cinematic, vertical 9:16", seed: 2006 },
];

async function gen() {
  const fs = await import('fs');
  const path = await import('path');
  const assetDir = path.join(process.cwd(), 'public', 'assets');
  for (const c of supporting) {
    const url = `${POLLINATIONS}/${encodeURIComponent(c.prompt)}?width=1080&height=1920&seed=${c.seed}&nologo=true&model=turbo`;
    console.log(`Gen ${c.id} (turbo)...`);
    try {
      const r = await fetch(url, { signal: AbortSignal.timeout(60000) });
      if (!r.ok) { console.error(`  FAIL ${r.status}`); continue; }
      const buf = Buffer.from(await r.arrayBuffer());
      fs.writeFileSync(path.join(assetDir, `${c.id}.jpg`), buf);
      console.log(`  OK (${(buf.length/1024).toFixed(0)}KB)`);
    } catch (e) { console.error(`  TIMEOUT/ERR: ${e.message}`); }
  }
  console.log("done");
}
gen();

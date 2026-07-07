// Render B-AI-META storyboard to MP4
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import path from "path";
import fs from "fs";

async function main() {
  const start = Date.now();
  console.log("📦 Bundling Remotion project...");

  const bundleLocation = await bundle(
    path.join(process.cwd(), "src/index.ts"),
    () => undefined,
    { webpackCache: path.join(process.cwd(), ".cache") },
  );

  console.log("✅ Bundle done:", bundleLocation);

  const composition = await selectComposition({
    serveUrl: bundleLocation,
    id: "ZeroToOne",
  });

  const outputPath = path.join(process.cwd(), "out", "zero-to-zero-to-one.mp4");
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });

  console.log("🎬 Rendering", composition.durationInFrames, "frames @", composition.fps, "fps...");
  console.log("   Output:", outputPath);

  await renderMedia({
    composition,
    serveUrl: bundleLocation,
    outputLocation: outputPath,
    codec: "h264",
    pixelFormat: "yuv420p",
    crf: 23,
    concurrency: 2,
    onProgress: ({ progress }) => {
      process.stdout.write(`\r⏳ Progress: ${(progress * 100).toFixed(1)}%`);
    },
  });

  const elapsed = ((Date.now() - start) / 1000).toFixed(1);
  const sizeMB = (fs.statSync(outputPath).size / 1024 / 1024).toFixed(1);
  console.log(`\n✅ Done in ${elapsed}s | ${sizeMB}MB | ${outputPath}`);
}

main().catch((e) => {
  console.error("❌ Render failed:", e);
  process.exit(1);
});

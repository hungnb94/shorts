import { Composition, AbsoluteFill, useCurrentFrame, useVideoConfig, Img, Audio, Sequence, interpolate, spring, staticFile } from "remotion";
import { z } from "zod";
import { useMemo } from "react";

// ============= SCHEMA =============
export const storyboardSchema = z.object({
  totalDurationInFrames: z.number().default(1350), // 45s @ 30fps
  width: z.number().default(1080),
  height: z.number().default(1920),
  fps: z.number().default(30),
});

// ============= CHAPTER TIMING (45s, 30fps) =============
// Ch1: 0-6s (0-180f) FALL
// Ch2: 6-12s (180-360f) HUMILIATION
// Ch3: 12-16s (360-480f) FAKE HOPE
// Ch4: 16-22s (480-660f) FALSE VICTORY
// Ch5: 22-30s (660-900f) ABYSS
// Ch6: 30-36s (900-1080f) REAL RISE
// Ch7: 36-45s (1080-1350f) TOTAL DOMINANCE

const CHAPTERS = [
  { name: "FALL", start: 0, end: 180, asset: "ch1_founder", text: "I was born to lose.", accent: "#5eead4" },
  { name: "HUMILIATION", start: 180, end: 360, asset: "ch2_demo", text: "Even my partner stopped believing.", accent: "#94a3b8" },
  { name: "FAKE HOPE", start: 360, end: 480, asset: "ch3_guru", text: "I trusted a stranger with my father's watch.", accent: "#f0abfc" },
  { name: "FALSE VICTORY", start: 480, end: 660, asset: "ch4_fake_win", text: "I was the star of a lie I bought myself.", accent: "#fbbf24" },
  { name: "ABYSS", start: 660, end: 900, asset: "ch5_abyss", text: "I lost everything. Then I lost more.", accent: "#ef4444" },
  { name: "REAL RISE", start: 900, end: 1080, asset: "ch6_rise", text: "I stopped selling dreams.", accent: "#60a5fa" },
  { name: "TOTAL DOMINANCE", start: 1080, end: 1350, asset: "ch7_nasdaq", text: "I didn't build a company. I built a door.", accent: "#facc15" },
];

// ============= SUBTITLE BAR (kinetic, wild-style) =============
const Subtitle: React.FC<{ text: string; accent: string; chapterStart: number; chapterEnd: number }> = ({
  text, accent, chapterStart, chapterEnd,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Show subtitle from 0.3s into chapter, hold to end
  const startAt = chapterStart + 9;
  const endAt = chapterEnd - 6;

  if (frame < startAt || frame > endAt) return null;

  const localFrame = frame - startAt;
  const dur = endAt - startAt;

  // Word-by-word kinetic entrance
  const words = text.split(" ");
  const totalWords = words.length;

  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 280, pointerEvents: "none" }}>
      <div
        style={{
          fontFamily: "'Bebas Neue', 'Arial Black', sans-serif",
          fontSize: 76,  // Was 64, bigger
          color: "white",
          textAlign: "center",
          textShadow: `
            -3px -3px 0 #000, 3px -3px 0 #000, -3px 3px 0 #000, 3px 3px 0 #000,
            0 0 20px ${accent}, 0 0 40px ${accent}
          `,
          letterSpacing: 3,
          maxWidth: 960,
          lineHeight: 1.15,
          padding: "0 40px",
          fontWeight: 900,
        }}
      >
        {words.map((w, i) => {
          const wordAppear = i / totalWords;
          const wordDelay = 3 * i; // 0.1s per word
          const inFrame = localFrame >= wordDelay;
          const outFrame = localFrame >= dur - 30;
          if (!inFrame || outFrame) return null;
          return (
            <span
              key={i}
              style={{
                display: "inline-block",
                marginRight: 14,
                color: i === words.length - 1 || w.includes(".") ? accent : "white",
                transform: `translateY(${(1 - Math.min(1, (localFrame - wordDelay) / 8)) * 30}px)`,
                opacity: Math.min(1, (localFrame - wordDelay) / 8),
                fontWeight: w.includes(".") || w === "door" || w === "lie" || w === "more" ? 900 : 700,
              }}
            >
              {w.toUpperCase()}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// ============= CHAPTER LABEL (top) =============
const ChapterLabel: React.FC<{ name: string; chapterStart: number; accent: string }> = ({ name, chapterStart, accent }) => {
  const frame = useCurrentFrame();
  if (frame < chapterStart || frame > chapterStart + 45) return null;

  const localFrame = frame - chapterStart;
  const opacity = interpolate(localFrame, [0, 10, 35, 45], [0, 1, 1, 0], { extrapolateRight: "clamp" });
  const slideX = interpolate(localFrame, [0, 12], [-100, 0], { extrapolateRight: "clamp" });

  return (
    <div
      style={{
        position: "absolute",
        top: 120,
        left: 60,
        opacity,
        transform: `translateX(${slideX}px)`,
        fontFamily: "'Bebas Neue', sans-serif",
        fontSize: 42,
        letterSpacing: 6,
        color: accent,
        textShadow: `0 0 20px ${accent}`,
        borderLeft: `4px solid ${accent}`,
        paddingLeft: 16,
      }}
    >
      {name}
    </div>
  );
};

// ============= HOOK TEXT (frame 0-1.5s, BIG + BOLD + BLOCK BG) =============
const HookText: React.FC = () => {
  const frame = useCurrentFrame();
  // Extended hold: 0-1.5s (45 frames) for stronger impact
  if (frame > 45) return null;

  const opacity = interpolate(frame, [0, 6, 36, 45], [0, 1, 1, 0], { extrapolateRight: "clamp" });
  const scale = interpolate(frame, [0, 8, 30, 45], [0.6, 1.1, 1, 0.95], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", backgroundColor: "black" }}>
      {/* Subtle vignette glow */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(circle at center, rgba(94,234,212,0.15) 0%, transparent 60%)",
          opacity,
        }}
      />
      <div
        style={{
          fontFamily: "'Bebas Neue', 'Arial Black', sans-serif",
          fontSize: 160,  // Was 120, bigger
          fontWeight: 900,
          color: "white",
          opacity,
          transform: `scale(${scale})`,
          letterSpacing: 6,
          textAlign: "center",
          textShadow: "0 0 60px #5eead4, 0 0 120px #5eead4",
          padding: "0 40px",
          lineHeight: 1.0,
          maxWidth: 1000,
        }}
      >
        <span style={{ display: "block" }}>I BUILT A COMPANY.</span>
        <span style={{ display: "block", color: "#5eead4", marginTop: 20 }}>IT BUILT ME.</span>
        <span style={{
          display: "block",
          fontSize: 32,
          marginTop: 60,
          color: "rgba(255,255,255,0.6)",
          letterSpacing: 8,
        }}>
          [ A FOUNDER'S STORY ]
        </span>
      </div>
    </AbsoluteFill>
  );
};

// ============= CHAPTER SCENE (background image + zoom + particles) =============
const ChapterScene: React.FC<{ chapter: typeof CHAPTERS[number] }> = ({ chapter }) => {
  const frame = useCurrentFrame();
  const { height, width } = useVideoConfig();

  const localFrame = frame - chapter.start;
  const chapterDur = chapter.end - chapter.start;

  // Ken Burns: slow zoom in on slow chapters, snap zoom on action
  const slowZoom = interpolate(localFrame, [0, chapterDur], [1, 1.08], { extrapolateRight: "clamp" });
  const actionZoom = chapter.name === "ABYSS" ? interpolate(localFrame, [0, 30, chapterDur - 30, chapterDur], [1, 1.1, 1, 0.95]) : slowZoom;

  // Chapter color overlay (vignette + tint)
  const overlayColor =
    chapter.name === "FALL" ? "rgba(10, 20, 40, 0.4)" :
    chapter.name === "HUMILIATION" ? "rgba(20, 30, 50, 0.5)" :
    chapter.name === "FAKE HOPE" ? "rgba(80, 20, 100, 0.3)" :
    chapter.name === "FALSE VICTORY" ? "rgba(100, 70, 0, 0.2)" :
    chapter.name === "ABYSS" ? "rgba(80, 0, 0, 0.4)" :
    chapter.name === "REAL RISE" ? "rgba(0, 50, 100, 0.3)" :
    "rgba(100, 70, 0, 0.2)";

  // Particles: data-viz style
  const particles = useMemo(() => {
    return Array.from({ length: 12 }, (_, i) => ({
      x: (i * 97 + 30) % width,
      y: ((i * 137) % height),
      size: 2 + (i % 3),
      speed: 0.4 + (i % 4) * 0.2,
    }));
  }, [width, height]);

  // Camera shake on ABYSS
  const shakeX = chapter.name === "ABYSS" ? Math.sin(localFrame * 0.8) * 4 : 0;
  const shakeY = chapter.name === "ABYSS" ? Math.cos(localFrame * 0.7) * 3 : 0;

  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          transform: `scale(${actionZoom}) translate(${shakeX}px, ${shakeY}px)`,
          filter: chapter.name === "ABYSS" ? "contrast(1.1) saturate(0.6)" :
                  chapter.name === "TOTAL DOMINANCE" ? "contrast(1.1) saturate(1.2) brightness(1.1)" :
                  "saturate(0.85)",
        }}
      >
        <Img
          src={staticFile(`assets/${chapter.asset}_9x16.jpg`)}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </div>

      {/* Color overlay / vignette */}
      <div style={{ position: "absolute", inset: 0, background: overlayColor, mixBlendMode: "multiply" }} />
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(circle at center, transparent 40%, rgba(0,0,0,0.7) 100%)",
        }}
      />

      {/* Data-viz particles (constant motion - fixes "visual đơn điệu" from memory) */}
      {particles.map((p, i) => {
        const y = (p.y + localFrame * p.speed) % height;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: p.x,
              top: y,
              width: p.size,
              height: p.size,
              backgroundColor: chapter.accent,
              opacity: 0.6,
              boxShadow: `0 0 ${p.size * 3}px ${chapter.accent}`,
              borderRadius: "50%",
            }}
          />
        );
      })}

      {/* ABYSS: multi-frame red flash on reveal (first 1s) */}
      {chapter.name === "ABYSS" && localFrame < 30 && (
        <>
          <div
            style={{
              position: "absolute",
              top: height / 2,
              left: 0,
              right: 0,
              height: 6,
              backgroundColor: "rgba(255, 0, 0, 0.8)",
              transform: `translateY(${Math.sin(localFrame * 2) * 50}px)`,
              boxShadow: "0 0 30px red, 0 0 60px red",
            }}
          />
          {localFrame % 6 < 2 && (
            <div
              style={{
                position: "absolute",
                inset: 0,
                backgroundColor: "rgba(255, 0, 0, 0.15)",
                pointerEvents: "none",
              }}
            />
          )}
        </>
      )}

      {/* ABYSS: large "FRAUD" stamp on reveal */}
      {chapter.name === "ABYSS" && localFrame >= 5 && localFrame < 60 && (
        <div
          style={{
            position: "absolute",
            top: "40%",
            left: 0,
            right: 0,
            textAlign: "center",
            fontFamily: "'Arial Black', sans-serif",
            fontSize: 180,
            fontWeight: 900,
            color: "rgba(255, 0, 0, 0.85)",
            textShadow: "0 0 40px red",
            letterSpacing: 12,
            transform: `rotate(-12deg) scale(${1 + Math.sin(localFrame * 0.3) * 0.05})`,
            pointerEvents: "none",
          }}
        >
          FRAUD
        </div>
      )}

      {/* GHOST ECHO TELL #1: lagged reflection on FAKE HOPE */}
      {chapter.name === "FAKE HOPE" && localFrame < 60 && (
        <div
          style={{
            position: "absolute",
            right: 60,
            top: 200,
            width: 200,
            height: 200,
            border: "2px solid rgba(240, 171, 252, 0.5)",
            borderRadius: 4,
            opacity: 0.4 + Math.sin(localFrame * 0.3) * 0.2,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 12,
            color: "#f0abfc",
            fontFamily: "monospace",
          }}
        >
          [ scan-line artifact ]
        </div>
      )}

      {/* TOTAL DOMINANCE confetti */}
      {chapter.name === "TOTAL DOMINANCE" && (
        <Confetti />
      )}
    </AbsoluteFill>
  );
};

// ============= CONFETTI (Ch7 only) =============
const Confetti: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const confetti = useMemo(() =>
    Array.from({ length: 30 }, (_, i) => ({
      x: (i * 73) % width,
      delay: (i * 7) % 60,
      color: ["#facc15", "#f0abfc", "#5eead4", "#60a5fa"][i % 4],
      size: 6 + (i % 3) * 2,
    })), [width]);

  return (
    <>
      {confetti.map((c, i) => {
        const f = frame - c.delay;
        if (f < 0) return null;
        const y = (f * 6) % height;
        const x = c.x + Math.sin(f * 0.1) * 20;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: c.size,
              height: c.size,
              backgroundColor: c.color,
              transform: `rotate(${f * 8}deg)`,
              opacity: f > 200 ? 0 : 1,
            }}
          />
        );
      })}
    </>
  );
};

// ============= MAIN COMPOSITION =============
export const MainComposition: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      {/* Hook (0-0.8s) */}
      <HookText />

      {/* All chapters stacked - render via Sequences */}
      {CHAPTERS.map((ch) => (
        <Sequence key={ch.name} from={ch.start} durationInFrames={ch.end - ch.start}>
          <ChapterScene chapter={ch} />
          <ChapterLabel name={ch.name} chapterStart={0} accent={ch.accent} />
          <Subtitle text={ch.text} accent={ch.accent} chapterStart={0} chapterEnd={ch.end - ch.start} />
        </Sequence>
      ))}

      {/* Persistent: server hum visualizer (Ch1+2 only) */}
      <ServerHumLine />

      {/* Persistent: timestamp + chapter counter bottom-right */}
      <FrameCounter />
    </AbsoluteFill>
  );
};

// ============= SERVER HUM LINE (subtle, dies in Ch5) =============
const ServerHumLine: React.FC = () => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  if (frame > 900) return null; // dies in ABYSS

  const phase = Math.sin(frame * 0.05) * 30;
  const opacity = 0.3 - (frame / 900) * 0.25; // fades as story progresses

  return (
    <div
      style={{
        position: "absolute",
        top: 80 + phase,
        left: 0,
        right: 0,
        height: 2,
        backgroundColor: "#5eead4",
        opacity,
        boxShadow: "0 0 10px #5eead4",
      }}
    />
  );
};

// ============= FRAME COUNTER (debug + production) =============
const FrameCounter: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const seconds = (frame / fps).toFixed(1);
  return (
    <div
      style={{
        position: "absolute",
        bottom: 40,
        right: 40,
        fontFamily: "monospace",
        fontSize: 18,
        color: "rgba(255,255,255,0.4)",
      }}
    >
      {seconds}s / 45.0s
    </div>
  );
};

// ============= EXPORT =============
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="ZeroToOne"
        component={MainComposition}
        durationInFrames={1350}
        fps={30}
        width={1080}
        height={1920}
        schema={storyboardSchema}
        defaultProps={{
          totalDurationInFrames: 1350,
          width: 1080,
          height: 1920,
          fps: 30,
        }}
      />
    </>
  );
};

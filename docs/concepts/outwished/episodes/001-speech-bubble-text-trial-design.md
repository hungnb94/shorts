# OUTWISHED 001 — Speech-Bubble Text Trial Design

Date: 2026-07-22
Status: Approved for local trial render

## Goal

Make the current 57.725-second trimmed visual/SFX cut understandable without voice-over by burning concise English dialogue into comic speech bubbles.

## Visual treatment

- Show only one active bubble at a time.
- Use 2–5-word bursts when possible; never exceed two lines per bubble.
- Position bubbles near the speaker while avoiding faces, the Lamp, the vault keypad, and important action.
- Nico: warm cream fill, teal outline. Use a cloud-tail thought bubble for narration.
- Corrupt officer: white fill, red outline.
- Veyr: deep plum fill, cyan outline with white text.
- System state: dark compact panel with cyan outline, not a character bubble.
- Render English text with the checked-in Komika Axis font profile.

## Story text map

| Timeline | Speaker | Meaning |
|---|---|---|
| 0.20–3.80 | Nico thought | The officer knows Nico's private code despite being a stranger. |
| 4.20–8.20 | Nico thought | Ten minutes earlier, two burglars entered the house. |
| 8.55–12.25 | Nico | Home invasion; two suspects; send police. |
| 13.80–17.10 | Officer / Nico | The officer claims Nico is safe; Nico notes the unusually fast response. |
| 18.80–22.30 | Nico / Corrupt Cop | Exact reveal: `YOU'RE WITH THE BURGLARS?` / `I'M THEIR THIRD PARTNER.` Every later bubble uses the `CORRUPT COP` label. |
| 22.80–28.30 | Corrupt Cop | Closing the occupied vault sends a police alert. |
| 28.60–32.10 | Corrupt Cop / Nico thought | Nico is locked downstairs; dry reaction. |
| 33.55–41.30 | Veyr / Nico | Veyr identifies the heir and confirms that he grants wording literally. |
| 41.55–50.30 | Nico / Veyr | Exact three-thief vault wish; officer explicitly included. |
| 50.55–57.60 | Veyr / Corrupt Cop / System | Wish granted, criminals stacked, and `OTHER OFFICERS ALERTED` distinguishes incoming police from the accomplice. |

## Rendering

- Preserve the current video and audio unchanged except for the burned visual layer.
- Generate full-canvas transparent PNG overlays for each timed bubble.
- Composite overlays locally with ffmpeg; no Higgsfield generation or paid API call.
- Produce a separate `dialogue-text-trial` MP4, manifest, and contact sheet.

## Verification

- Probe for 1080x1920, H.264 High Level 4.2, true 24 fps CFR, and AAC stereo 48 kHz.
- Full-decode the final artifact.
- Run black, freeze, and silence detectors.
- Extract frames at every bubble event and manually check text legibility, speaker association, face avoidance, and action visibility.
- Keep the artifact labelled as a text-dialogue trial, not upload-final; SHOT-011/012, final VO, CTA, watermark, and publication authorization remain outside this trial. The copy below is upload-ready metadata, not permission to publish the current trial artifact.

## Publishing metadata

### Canonical YouTube title

`The Cop Knew My Safe Code 🚨🔐`

### YouTube description

```text
The Cop Knew My Safe Code 🚨🔐

Nico had never met him—and one precise wish exposes which side the officer is really on.

#shorts #AnimatedStory #PlotTwist
```

### YouTube Studio tags

`animated plot twist, corrupt cop story, genie wish story`

### YouTube Studio settings

- Audience: `Not made for kids`.
- Video language: `English`.
- Category: `Film & Animation`.
- Recording location: leave unset because the story is fictional.
- Playlist: `OUTWISHED`.
- Related video: leave unset until the next published OUTWISHED episode exists.

## Channel identity proposal

### Recommended channel name

**ClueFlip**

Brand architecture:

```text
ClueFlip — umbrella channel for animated plot-twist stories
└── OUTWISHED — first serialized show
```

Tagline: **Spot the clue. Catch the flip.**

One-line bio: **Animated stories with hidden clues, fair-play twists, and endings worth replaying.**

Why this name fits:

- `Clue` promises that the decisive setup is visible before the reveal.
- `Flip` promises a reversal that changes the meaning of an earlier scene.
- The name is short, pronounceable in English, and broad enough for fantasy, mystery, science fiction, crime comedy, and future series beyond OUTWISHED.
- It positions the channel around a repeatable audience game rather than one character, one Lamp, or one animation technique.

Naming status: recommended creative direction. A preliminary web collision scan on 2026-07-22 found no prominent animation/story brand using the exact `ClueFlip` name in the returned results. This is not YouTube handle reservation, company-name clearance, domain clearance, or trademark advice; verify those independently when creating the account.

### Channel About copy

```text
ClueFlip creates animated short stories built around hidden clues, smart reversals, and endings that change what you thought you saw. Every episode gives you a fair chance to spot the setup before the flip.

Our first series, OUTWISHED, follows strategist Nico Vale and trickster genie Veyr as they hide traps inside magical wishes—and inside each other's plans.

Watch closely. The clue is already on screen.
```

## Channel image prompts

### Profile picture / avatar prompt

```text
Create an original, text-free 1:1 YouTube channel avatar for an English animated plot-twist storytelling brand called ClueFlip. Design one bold emblem: an alert eye hidden inside a rectangular story frame that is visibly folding or flipping at one corner, with one tiny golden clue spark on the first side and an electric-cyan reversal streak emerging on the second side. Use a midnight-navy and deep-plum background, electric cyan outlines, one controlled clue-gold accent, and a small twist-magenta accent. Premium 2D cel-shaded animation identity, cinematic mystery-comedy energy, clever and slightly mischievous, mature general-audience tone, extremely clean silhouette, centered composition, thick readable shapes, strong contrast, recognizable at 48x48 pixels, circular-crop safe, generous edge padding. No words, no letters, no characters, no Lamp, no watermark, no platform logo, no photorealism, no gradients that muddy the silhouette, no preschool or children's-channel styling, no resemblance to copyrighted animation properties.
```

### YouTube banner prompt

```text
Create an original 2560x1440 YouTube channel banner for ClueFlip, an English channel of animated short stories with hidden clues and fair-play plot twists. Protect the full 1546x423 center safe area for later manual typography; do not generate any text. Build a cinematic horizontal 2D cel-shaded scene in which three story frames fold into one another from left to right: a modern mystery frame with a glowing vault keypad and an unnoticed clue spark, a fantasy-comedy frame with an ancient golden Lamp and a floating contract panel as a subtle OUTWISHED easter egg, and a future mystery frame with an unidentified device and a reversed shadow. Connect the frames with one electric-cyan clue trail that changes into a twist-magenta reversal streak. Midnight navy and deep plum base, electric cyan, controlled clue gold, small magenta accents, dramatic rim light, expressive but uncluttered storytelling, premium serialized-animation look, mature general-audience tone, strong depth, clean negative space in the center, key objects kept outside the text-safe area, mobile and TV crop safe. No generated words, no logos from existing brands, no Disney-like Genie or Aladdin design, no gore, no preschool styling, no crowded collage, no watermark, no photorealism.
```

### Manual typography overlay for the banner

Add this in a design editor after generating the image; do not ask the image model to render it:

```text
CLUEFLIP
Spot the clue. Catch the flip.
```

Keep both lines centered inside the 1546x423 safe area. Use an original bold comic-display face with clean geometry, off-white primary lettering, cyan edge light, and one small gold clue accent; do not imitate a copyrighted title treatment.

# Ronald Wayne — MONEY BLINDSPOT Production Record

**Artifact:** `2026-07-25-ronald-wayne-v1.mp4`  
**Render date:** 2026-07-25  
**Format:** English YouTube Short, 1080×1920, 60.000s, 30fps  
**Status:** **Rendered and technically verified; not uploaded**  
**Editorial gate:** Hook C approved by the user. Independent cold-viewer evidence was not supplied, so the production record does not claim that gate passed.

## Strategy

This edit uses MrBeast-derived execution principles rather than claiming a novel replacement formula:

1. Start with the universally familiar claim: `10% of Apple → $800`.
2. Break the expected story at 4.5 seconds: Wayne calls that shorthand false.
3. Replace a generic mystery with one explicit question: `So what actually happened?`
4. Escalation through hidden downside, not biography.
5. Proof alternates with mechanism graphics and first-person interview footage.
6. Visual source/state changes exactly every 1.5 seconds: 40 beats over 60 seconds.
7. CTA is integrated into the verdict at 39.0 seconds, before the final payoff.
8. Factual closure (`$500 → $1.59M contract`) leaves moral closure open (`fool or free?`).

The edit deliberately does **not** claim that the method guarantees one million views.

## Narration and Audio

- **TTS engine:** Edge TTS stock voice.
- **Voice:** `en-US-GuyNeural`.
- **Settings:** rate `+26%`, pitch `-8Hz`.
- **Selection reason:** male News/Novel voice chosen after the user rejected AriaNeural and requested a Zack D. Films-like documentary cadence.
- **Voice safety:** no Zack D. Films voice sample was cloned or used to create a speaker identity.
- **First-person evidence:** two short Ronald Wayne source-voice sections:
  - CBS around `47.5s` source time: right-product/right-time answer.
  - NextShark around `453.8s` source time: regret answer.
- **Music:** original synthetic three-state bed generated locally by the renderer; no copyrighted music asset.
- **Measured loudness:** `-16.08 LUFS`, true peak `-1.59 dBTP`, LRA `3.50`.

## Final Script

> The internet says he sold ten percent of Apple for eight hundred dollars. Wayne calls that false.
>
> So what actually happened? Wayne drafted Apple's partnership agreement, then removed his name twelve days later.
>
> Jobs later sent him eight hundred dollars. Apple was not a corporation, so every partner could be personally liable.
>
> Jobs and Wozniak were young and broke. Wayne was forty-one, with a house, a car, and money creditors could reach.
>
> The twist? Wayne believed in Apple.
>
> **Ronald Wayne source voice:** “None. It was the right product at the right time.”
>
> He left because he expected decades of paperwork instead of building his own inventions.
>
> Lock your verdict: sell or stay? Like, subscribe, and comment now.
>
> Wayne says he does not regret leaving Apple. What did he regret?
>
> He sold the original contract for five hundred dollars. In 2011, it sold for one point five nine million.
>
> **Ronald Wayne source voice:** “That, I regret.”
>
> So was he history's biggest fool—or did walking away give him freedom?

## Claim Guardrails

- The opening explicitly attributes `sold 10% for $800` to the internet shorthand and immediately states that Wayne disputes it.
- The factual sequence used is: Wayne drafted/signed the partnership agreement → removed his name → Jobs later sent an `$800` check. The Short does not describe the `$800` as an uncontested share-sale price.
- The script uses Wayne's account that he removed his name twelve days later; it does not claim all recollections agree that his total association lasted exactly twelve days.
- It says partners **could** be personally liable, not that Apple guaranteed Wayne's house would be taken.
- It does not state a present-day value for a hypothetical 10% Apple stake.
- The `contract-illustration.jpg` asset is generic licensed stock and is always labeled `CONTRACT ILLUSTRATION`; it is never presented as Apple's original contract.
- The `$1.59M` payoff refers to the original contract's 2011 auction price, not the value of Wayne's former Apple stake.

## Primary Video Sources

| ID | Publisher / subject | Production use |
|---|---|---|
| `bvWh8sh_wPY` | BBC — Ronald Wayne interview | hook, body proof, loop close |
| `YAF2-U7InWE` | NextShark — Ronald Wayne interview | first-person regret payoff |
| `M3R50CA9ok8` | CBS — Ronald Wayne interview | first-person right-product/right-time proof |
| `hPyI_RtHFGU` | P2P — Steve Wozniak talk | co-founder visual context |
| `_nFHSv5GxhI` | KPVM — Ronald Wayne interview | agreement/founding visual context |
| `Qwq80WpkCqo` | roompass / El Club del 1% — Ronald Wayne 2026 interview | corrective claim research: Wayne disputes the `$800 sale` shorthand; not used as footage |
| `w8GU3JelIlk` | Vintage Computer Federation — Ronald Wayne 2024 panel | payment-mechanics research: later `$800` check and `$1,500` release; not used as footage |

Full source and conflict ledger:

- `docs/research/costly-verdict-million-view-strategy-2026-07-25/SUPPLEMENTAL-SOURCES.md`
- `docs/research/costly-verdict-million-view-strategy-2026-07-25/REPORT.md`
- `docs/research/ronald-wayne-additional-youtube-2026-07-25/REPORT.md`

## Articles and Reference Sources

- BBC: `https://www.bbc.com/news/technology-35940300`
- CNN: `https://edition.cnn.com/2010/TECH/web/06/24/apple.forgotten.founder/index.html`
- CNBC: `https://www.cnbc.com/2017/05/05/why-ronald-wayne-sold-his-10-percent-stake-in-apple-for-800.html`
- NPR: `https://www.npr.org/2011/12/13/143641040/a-1-6-million-regret-apples-third-founder`
- Cult of Mac: `https://www.cultofmac.com/news/the-gambler-who-co-founded-apple-and-left-for-800`
- NextShark: `https://nextshark.com/ronald-wayne-interview-apple`

## Visual Assets

- Ronald Wayne portraits and historical images from Wikimedia Commons where available.
- Apple I image marked public domain in the downloaded source set.
- First Apple logo image from Wikimedia Commons.
- Generic contract illustration from Unsplash; labeled on-screen as illustration.
- Legal-liability, asset, money, CTA, verdict, and timeline cards generated locally by the renderer.
- Source hashes and ffprobe metadata: `source/asset-manifest.json`.
- Source registry entries: `data/source_videos.csv`.

## Edit Decision List

- `scripts/visual-edl-v1.json`
- `40` entries.
- Every entry lasts exactly `1.5s`.
- CTA starts at beat 26, timestamp `39.0s`.
- Contract payoff begins at beat 32, timestamp `48.0s`.
- First-person regret line starts at beat 36, timestamp `54.0s`.

## Verification Results

Automated verification was executed on the final, post-fix artifact—not the earlier draft.

| Check | Result |
|---|---|
| Duration | `60.000s` — pass |
| Video | H.264, 1080×1920, 30fps — pass |
| Audio | AAC, stereo, 48kHz — pass |
| Full decode | pass; no FFmpeg errors |
| EDL count | 40 — pass |
| EDL continuity | pass |
| Maximum visual-state duration | `1.5s` — pass |
| Keyframe boundaries | `40`, including every `1.5s` beat boundary — pass |
| Black frames | 0 events — pass |
| Freeze longer than 1.55s | 0 events — pass |
| Integrated loudness | `-16.08 LUFS` — pass |
| True peak | `-1.59 dBTP` — pass |
| Corrected opening 0–18s | 12 independently output-seeked beat frames manually checked |
| Full 40-beat contact sheet | manually checked |
| Regression spot-checks | `1.6s`, `10.6s`, `15.3s`, `39.3s`, `48.3s`, `54.3s`, `57.1s`, `59.7s` — pass |
| ASR | pass with `mlx-community/whisper-tiny.en-mlx` and word timestamps; all critical claims/numbers and both Wayne quotes recognized; one non-critical proper-name substitution: `Jobs and Wozniak` → `Jobs in Wozniac` |

Automated summary: `checks/verification-summary.json`. Final ASR outputs: `checks/asr-final/final.{txt,vtt,srt,tsv,json}`.

## Defects Found and Corrected During Manual QC

1. **15.0s:** an unrelated BBC article frame appeared under `PERSONAL LIABILITY`. It was replaced with a purpose-built legal-mechanism card.
2. **54.0s:** the NextShark vertical crop used the wrong x-coordinate and obscured Wayne. The source was re-inspected using exact output-seek, crop changed to `x=720`, source audio extraction changed to frame-accurate output-seek, and the final beat was re-rendered and manually rechecked.
3. **Factual conflict found after the first render:** new direct-Wayne research disputed the `sold 10% for $800` shorthand. The opening, 6–18s explanation, final verdict, TTS, and visual EDL were rewritten to distinguish the popular claim from the later `$800` payment.
4. **57.1s:** moving watermark overlapped `FREEDOM?`. The renderer now moves the watermark to `y=1180` on every subcaption beat; both affected beats (`10.5s` and `57.0s`) were invalidated, rerendered, and manually checked.

## Reproduction

```bash
python3 pipeline/ronaldwayne/generate_ronaldwayne_tts.py
uv run --with pillow python pipeline/ronaldwayne/render_ronaldwayne_v1.py
python3 pipeline/ronaldwayne/verify_ronaldwayne_v1.py
```

## Delivery Scope

This artifact is ready for human review and cold-viewer testing. It has not been uploaded or scheduled. A publish decision should still consider the independent cold-viewer Hook Gate that was explicitly not completed in this production session.

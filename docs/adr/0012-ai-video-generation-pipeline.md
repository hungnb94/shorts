# AI Video Generation Pipeline (Veo 3 / Kling / Seedance)

**Context**: Shorts project hiện tại chỉ dùng animation-based video types (Remotion, Pexels, ASCII) — zero footage từ AI video generation. User rejected 5/7 video types vì "thiếu chuyển động, visual đơn điệu" (Fact #51, #52 trong memory). Nhu cầu: tích hợp AI video generation (Veo 3.1, Kling 3.0, Seedance 2.0/2.5) để tạo cinematic clips xen kẽ với pipeline hiện tại.

**Decision**: Tích hợp AI video gen vào pipeline theo kiến trúc **Hybrid Interleave** — AI clips xen kẽ với Remotion animation + Pexels b-roll xuyên suốt 40s. Dùng Higgsfield platform làm unified identity layer (Soul ID) + multi-model gen (Veo/Seedance/Kling). Character mascot Kitty upgrade từ ASCII sang Pixar-style 3D cinematic, train 1 lần qua Soul ID, dùng xuyên suốt 108 videos/tháng.

---

## 1. Kiến Trúc Pipeline (Hybrid Interleave)

```
HOOK (0-2s)                     EXPLAIN + ILLUSTRATE (2-30s)         TEACH (30-40s)
Kitty AI clip                    Remotion DataViz                      Kitty AI clip
(8-10s cinematic)               + Pexels b-roll                         (5-8s closing)
                                  + Kitty AI clips (3-4 × 8s)

→ Total AI clips/video: ~5 clips × 8s = 40s
→ AI coverage: ~100% (xen kẽ với animation/b-roll)
→ Final: Remotion assembly, Pexels b-roll, AI clips → composite → 9:16 MP4
```

**5 Scenes AI-gen per video** (tham số không gắn cứng):
1. **Scene 1**: Hook — Kitty tại office/finance setting
2. **Scene 2**: Explain — Kitty + data viz background
3. **Scene 3**: Illustrate — Kitty explaining concept với gesture
4. **Scene 4**: Deep dive — cinematic scene đại diện concept
5. **Scene 5**: Close — Kitty final statement

---

## 2. Video Type Classification (Post-ADR)

| # | Type | AI Gen Role | Status |
|---|------|-------------|--------|
| 1 | Stock Footage | AI clips thay thế Pexels footage | Đục |
| 2 | Kinetic Typography | AI scene xen kẽ text overlay | Mới |
| 3 | Data Viz | AI clips làm backdrop cho chart/table | Đục |
| 4 | HTML/CSS Motion | AI clips xen kẽ với CSS animation | Mới |
| 5 | Whiteboard Sketch | AI clips thay thế sketch transitions | Đục |
| 6 | Meme/Notification | AI clips tạo meme reaction shots | Mới |
| 7 | Clip Curation Edit | AI clips bổ sung cho source footage | Thêm |
| **8** | **AI-Pure** | **100% AI gen, zero Remotion** | **Mới** |

---

## 3. Model Stack (Multi-Model Strategy)

| Model | Khi nào dùng | Strength | Cost/s | Ref inputs |
|-------|-----------|----------|--------|-----------|
| **Veo 3.1** | Quality scenes, hook, close | Best cinematic + native synced audio + native 9:16 | $0.15 | Up to 3 refs |
| **Seedance 2.0/2.5** | Need consistency, talking character | **9 reference inputs** (most) + native audio + strong lip-sync | $0.092-0.30 | Up to 9 refs |
| **Kling 3.0** | Budget scenes, bulk gen, lip-sync | Cheapest ($0.05/s) + native lip-sync 8+ languages + multi-angle | $0.05 | Multi-angle refs |

**Selection logic**:
- Hook scene → Veo 3.1 (cinematic quality, first impression)
- Kitty talking scenes → Seedance 2.0/2.5 (9 refs = best consistency)
- Background/atmospheric → Kling 3.0 (cheap filler)

---

## 4. Identity Layer — Soul ID / Higgsfield

**Character**: Kitty — stylized 3D cat (Pixar/DreamWorks style), anthropomorphic, business-casual attire (finance niche), expressive eyes, slightly sarcastic demeanor.

**Soul ID Workflow**:
1. Generate 20-50 reference images: front, 3/4, profile, full body, close-up, various outfits, expressions
2. Train Soul ID trên Higgsfield (3-5 minutes, cost ~$5-10 one-time)
3. Reference Soul ID trong mọi generation — consistency tự động across models
4. Vô hiệu hóa "re-upload per clip" bug — standard pipeline issue

**Fallback khi Soul ID fail**: Locked prompt template + image-to-video per scene (manual ref per gen, lower consistency)

---

## 5. Audio Strategy

| Layer | Source | Khi nào dùng |
|-------|--------|-------------|
| **Native synced audio** | Veo/Seedance (auto-generated, lip-synced) | AI clips có Kitty nói chuyện |
| **TTS voiceover** | Pipeline hiện tại (ElevenLabs/Coqui) | Narration chung, story telling, CTA |
| **Music** | Pipeline hiện tại (Uppbeat/Artlist) | Background track |
| **Sound design** | Pipeline hiện tại | Retention techniques |

**Conflict rule**: Khi AI clip có native audio → TTS chỉ overlay, không thay thế. Native audio luôn synced với lip movement.

---

## 6. Data Flow

```
Script (HEIT) →
  ├─ Soul ID Kitty refs (pre-generated, cached)
  ├─ Scene generation plan (AI model per scene)
  ├─ Parallel gen: Veo 3.1 / Seedance 2.0 / Kling 3.0
  ├─ Quality gate (9:16, 5-15s, no blur artifacts)
  ├─ TTS + sound design (existing pipeline)
  ├─ Remotion assembly (AI clips + animation + b-roll)
  └─ Final composite → MP4
```

**API calls per video**: ~5 gen calls (1/ video type × scene count)
**Parallelization**: 3+ models gen simultaneously → stitch sau
**Cost per video**: ~$1-3 (full pipeline), ~$0.20 (budget Kling-only)

---

## 7. Glossary (new terms)

- **Soul ID**: Trained identity model (20+ images → persistent character) by Higgsfield. Dùng như "casting database entry" — 1 lần train, reuse cho mọi generation.
- **Native Synced Audio**: AI-generated audio + lip movement được train cùng lúc (Veo/Seedance/Kling characteristic). Khác TTS post-sync.
- **Hybrid Interleave**: Pattern xen kẽ AI clips với non-AI content (Remotion/Pexels/animation) trong cùng 1 video. Goal: balance cost + visual variety + brand identity.
- **Video Type #8 (AI-Pure)**: 100% AI gen video, zero Remotion/animation. Dùng cho speed test, prototype, hoặc cost-sensitive scenarios.

---

## Consequences

**Positive**:
- Fix bottleneck #1: "thiếu chuyển động" — AI gen tạo cinematic motion
- Brand identity mạnh: Soul ID Kitty = instantly recognizable
- Scalable: 108 videos/month với 1 trained identity
- Cost predictable (subscription-based, không per-clip manual work)

**Negative**:
- Monthly cost $25-50 base + overage credits (cần monitor)
- Dependency on Higgsfield platform (lock-in risk)
- Soul ID cần retrain khi thay đổi character design
- API latency: ~30-90s per clip (phải xử lý background gen)

**Mitigation**:
- Spike trước: 1 test video ($2-5) → measure AVD → scale
- Fallback: Gemini API direct nếu Higgsfield down
- Budget cap: Kling 3.0 as default, upgrade to Veo khi budget cho phép

---

## Related

- ADR 0002: Animation Style (Kitty Explain)
- ADR 0008: Value-Added Editing (VAE expansion)
- ADR 0009: Autonomous Optimization System
- ADR 0007: Clip Curation Edit (transformative gate)
- CONTEXT.md: Soul ID, Native Synced Audio, Hybrid Interleave, Video Type #8

---

*Approved: 2026-07-08*
*Tags: ai-video-generation, veo-3, kling-3, seedance-2, soul-id, kitty-character, hybrid-interleave, video-type-8*

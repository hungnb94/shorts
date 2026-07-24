# AI Video Generation Pipeline (Veo 3 / Kling / Seedance)

**Context**: Shorts project hiện tại chỉ dùng animation-based video types (Remotion, Pexels, ASCII) — zero footage từ AI video generation. User rejected 5/7 video types vì "thiếu chuyển động, visual đơn điệu" (Fact #51, #52 trong memory). Nhu cầu: tích hợp AI video generation (Veo 3.1, Kling 3.0, Seedance 2.0/2.5) để tạo cinematic clips xen kẽ với pipeline hiện tại.

**Decision**: Tích hợp AI video gen vào pipeline theo kiến trúc **Hybrid Interleave** — AI clips xen kẽ với Remotion animation + Pexels b-roll xuyên suốt 40s. Dùng Higgsfield platform làm unified identity layer (Soul ID) + multi-model gen (Veo/Seedance/Kling).

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

## 5. Audio Strategy

| Layer | Source | Khi nào dùng |
|-------|--------|-------------|
| **Native synced audio** | Veo/Seedance (auto-generated, lip-synced) | AI clips có Kitty nói chuyện |
| **Music** | Pipeline hiện tại (Uppbeat/Artlist) | Background track |
| **Sound design** | Pipeline hiện tại | Retention techniques |

**Conflict rule**: Khi AI clip có native audio → TTS chỉ overlay, không thay thế. Native audio luôn synced với lip movement.

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

- ADR 0008: Value-Added Editing (VAE expansion)
- CONTEXT.md: Soul ID, Native Synced Audio, Hybrid Interleave, Video Type #8

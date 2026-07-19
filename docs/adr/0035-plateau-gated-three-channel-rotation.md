# ADR 0035: Plateau-Gated Three-Channel Rotation

**Date:** 2026-07-19  
**Status:** Accepted

## Context

The target architecture assumed one Destination Channel per vertical and a fixed six-Shorts-per-day, three-day upload cycle. The supplied `r/shortsAlgorithm` guide argues instead that each Short needs distribution time, recommends multiple aged test channels and advises materially revising content that never enters the Shorts Feed. During grilling, the user chose three channels per vertical, strict round-robin assignment, plateau-gated cadence and preservation of failed originals rather than deletion.

This changes channel topology, publishing cadence, experiment timing, credential scope and the future autonomous scheduler, so it is recorded separately from craft verification.

## Decision

### Channel Pool

1. Each vertical owns a `Channel Pool` of exactly three Destination Channels.
2. Every channel is phone-verified and aged for at least three weeks before its first upload. During aging it is used normally rather than left as an empty upload shell, while the first production batch is prepared offline.
3. New Shorts are assigned in strict round-robin order. A Short or its Material Revision is never uploaded simultaneously to multiple lanes.
4. Each Destination Channel has independent identity, playlist, Related Video state, audience history and Analytics authorization.

### Plateau-Gated Cadence

1. There is no fixed daily or weekly publishing quota.
2. Before the scheduler can publish to the next lane in round-robin order, the previous Short on that lane must reach `Distribution Plateau`: it is at least 48 hours old; the latest 24-hour view increment is at most 20% of the immediately preceding 24-hour increment; and this condition is observed at two consecutive checks.
3. If the next lane is not eligible, the queue waits rather than skipping the lane. This preserves strict round-robin attribution.
4. Exception: when the first Short on a new channel remains viral and has not plateaued, its second Short may publish after approximately seven days. The first Short is then updated to use the new Short as its Related Video. A slow second Short is retained because delayed pickup can still occur.
5. Once a lane becomes eligible, Sunday around 18:00 Atlantic/Halifax is the preferred release slot from the supplied guide, not a blocking gate; plateau eligibility takes precedence.

### First-48-Hour Distribution Gate

1. Traffic source is checked at 48 hours, not 24 hours, because pickup can take 24–48 hours.
2. Shorts Feed share of at least 70% is healthy.
3. Shorts Feed share from 60% to below 70% is a watch state: retain and monitor; do not revise solely from this metric.
4. Shorts Feed share below 60% is `No-Feed State`.
5. A No-Feed original is retained to preserve delayed pickup and measurement history. It is not deleted or reset.
6. Recovery requires a `Material Revision`: rebuild the entire 0–3 second opening (shot/framing, hook copy and early SFX) and change at least one additional axis among pacing/cut order, proof visuals, captions or music. Metadata-only changes, a simple re-export or a music-only swap do not qualify.
7. The Material Revision goes to the next Destination Channel in the Channel Pool when that lane becomes plateau-eligible.
8. Three consecutive No-Feed results on the same lane place that channel in `Channel Burn State`; remove it from rotation while a replacement channel completes phone verification and the three-week aging gate. Do not infer Channel Burn from one weak Short.

### Post-Publish Momentum

1. During the first 48 hours, reply to genuine questions and substantive comments to keep useful threads active; spam, abuse and repetitive engagement bait are excluded.
2. Every Short remains in the vertical's master playlist.
3. Related Video wiring is maintained from the current winner to the newest eligible Short.
4. At plateau, inspect AVD and 0–3 second retention and carry the weakest metric into the next Short's production brief.

## Superseded scope

This ADR supersedes fixed `6 videos/day × 3 days`, `18 videos per cycle`, one-channel-per-vertical and fixed five-day Optimization Cycle assumptions in live project documentation and ADR-0009's scheduling clauses. MAB and cohort math that depends on 18 fixed samples must be redesigned before the future autonomous system is implemented; historical experiment records are not rewritten.

## Consequences

- Throughput becomes variable and substantially lower per channel, while three lanes per vertical preserve some parallelism.
- Subscriber and recommendation history are fragmented across nine channels; analysis must include `channel_id` and must not pool lane outcomes as if channel history were controlled.
- Strict round-robin can block a ready lane behind a non-plateaued next lane. This is an explicit attribution trade-off.
- Each added channel requires separate operational ownership and Analytics authorization.
- The previous MAB convergence forecasts based on 18 videos per cycle are invalid until the scheduler and cohort definitions are redesigned.
- Keeping No-Feed originals avoids data loss and duplicate-delete loops but leaves weak public inventory unless separately unlisted for a non-algorithmic reason.

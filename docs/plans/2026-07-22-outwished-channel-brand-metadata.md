# OUTWISHED Channel Brand and Publishing Metadata Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Record the canonical episode metadata and the selected umbrella-channel identity for ClueFlip in the existing OUTWISHED episode document.

**Architecture:** Keep episode upload metadata and channel identity in the existing episode design document rather than creating a second metadata artifact. Separate episode-specific publishing copy from reusable channel-level brand assets and note that name-collision research is preliminary, not handle or trademark clearance.

**Tech Stack:** Markdown documentation and a Python validation command.

---

### Task 1: Add Canonical Publishing Metadata

**Files:**
- Modify: `docs/concepts/outwished/episodes/001-speech-bubble-text-trial-design.md`

- [x] Add the ADR-0034-compliant canonical title, mirrored description line, one descriptive sentence, exactly three visible hashtags, and exactly three Studio tags.
- [x] Add explicit YouTube settings: English, Film & Animation, Not made for kids, no recording location, and the OUTWISHED playlist.

### Task 2: Add ClueFlip Channel Identity

**Files:**
- Modify: `docs/concepts/outwished/episodes/001-speech-bubble-text-trial-design.md`

- [x] Record `ClueFlip` as the recommended umbrella channel name and `OUTWISHED` as its first series.
- [x] Record the tagline, one-line bio, full English About copy, brand rationale, and preliminary collision caveat.
- [x] Add production-ready English prompts for a text-free 1:1 avatar and a 2560x1440 YouTube banner with a protected 1546x423 center safe area.
- [x] Add negative constraints that prevent illegible generated typography, copyrighted character resemblance, child-channel styling, clutter, and watermarks.

### Task 3: Validate the Document

**Files:**
- Verify: `docs/concepts/outwished/episodes/001-speech-bubble-text-trial-design.md`

- [x] Run a Python assertion that the title is no more than 30 code points, contains exactly two selected emoji, description line 1 mirrors the title, visible hashtags equal three and include `#shorts`, and Studio tags equal three.
- [x] Search the updated document for `TBD`, `TODO`, placeholder copy, conflicting old metadata, and missing channel sections.
- [x] Run `git diff --check` on the document.

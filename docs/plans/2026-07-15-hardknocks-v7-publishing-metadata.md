# HardKnocks V7 Publishing Metadata Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a complete YouTube upload package for HardKnocks V7 and make metadata completeness a blocking workflow gate for every future video.

**Architecture:** Keep the canonical title, description, visible hashtags, and Studio tags in the video's production doc. Update Workflow Stages 5 and 6 so a video cannot be marked complete or uploaded while any field is missing. Do not create a second metadata artifact and do not change the renderer.

**Tech Stack:** Markdown documentation, repository workflow policy, shell/Python consistency checks.

---

### Task 1: Add the canonical V7 upload package

**Files:**
- Modify: `docs/production/hardknocks-v7-raising-canes-focus-bet.md`

- [ ] **Step 1: Add the metadata section before `Verification Results`**

Insert this exact content:

```markdown
## YouTube Metadata

### Title

`His Professor Said It Would Never Work. Now He's Worth $20B`

### Description

His professor said a restaurant built around one core product would never work. Todd Graves kept the focus, combined $50,000 of his own equity with a $50,000 SBA loan, rebuilt an old restaurant, and scaled Raising Cane's.

The lesson isn't “sell chicken.” It's build around a craveable product, focus the operation, build the team, then scale. The exact $50K loan amounts and $400M single-year figure are Todd Graves' source-reported claims; Forbes estimates his current net worth at about $22B as of July 13, 2026.

Source interview: School of Hard Knocks — https://www.youtube.com/watch?v=n5EmUiLNVjg

#Entrepreneurship #BusinessStrategy #Shorts

### Hashtags

`#Entrepreneurship #BusinessStrategy #Shorts`

### YouTube Tags

`Todd Graves, Raising Cane's, Raising Canes, School of Hard Knocks, entrepreneur, entrepreneurship, business strategy, restaurant business, focus strategy, startup story, business case study, founder story, SBA loan, chicken fingers, YouTube Shorts`
```

- [ ] **Step 2: Validate platform limits and factual guardrails**

Run:

```bash
python3 - <<'PY'
title="His Professor Said It Would Never Work. Now He's Worth $20B"
description_chars=647
tags_chars=247
assert len(title) == 59 and len(title) <= 100
assert description_chars <= 5000
assert tags_chars <= 500
print("METADATA_LIMITS_PASS")
PY
```

Expected: `METADATA_LIMITS_PASS`.

Confirm manually that the description labels the exact `$50K` loan amounts and `$400M` as source-reported, dates the Forbes estimate, contains no raw affiliate link, and ends with exactly three hashtags.

### Task 2: Enforce metadata in the standard workflow

**Files:**
- Modify: `docs/WORKFLOW.md:74-115`

- [ ] **Step 1: Add a blocking Stage 5 metadata checklist**

After the production-doc template sentence, require these four non-empty fields:

```markdown
### Publishing Metadata Gate (blocking)

Before setting a production doc to `Completed`, it must contain one canonical upload package:

1. `Title`: one selected title, ≤100 characters; no unresolved alternatives.
2. `Description`: complete upload copy, ≤5,000 characters; factual claims preserve independent-vs-source-reported distinctions; no raw affiliate link.
3. `Hashtags`: exactly three relevant visible hashtags intended for the end of the description.
4. `YouTube Tags`: a separate comma-delimited Studio tags field, ≤500 characters; only relevant entities/topics, with no misleading trend tags.

If any field is empty, placeholder text remains, or limits/claim guardrails fail, the video is not done and Stage 6 is blocked.
```

- [ ] **Step 2: Add the Stage 6 pre-upload check**

Change Stage 6 so its first action is to copy the canonical package from the production doc and verify all four fields against the Stage 5 gate before uploading. Preserve the existing raw-affiliate-link prohibition, experiment logging, and 48-hour wait.

- [ ] **Step 3: Verify the documentation contract**

Run:

```bash
rg -n "Publishing Metadata Gate|Title.*100|Description.*5,000|exactly three|YouTube Tags|Stage 6 is blocked" docs/WORKFLOW.md
rg -n "## YouTube Metadata|His Professor Said It Would Never Work|#Entrepreneurship #BusinessStrategy #Shorts|Todd Graves, Raising Cane's" docs/production/hardknocks-v7-raising-canes-focus-bet.md
git diff --check
```

Expected: every required contract phrase is found and `git diff --check` exits 0.

No commit or upload is part of this task.

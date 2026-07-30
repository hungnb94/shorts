# SFX Event Ledger Template

Use this section inside `docs/production/<video>.md`. Fill it from the actual EDL before asset search and update it after listening to the exact-final mix.

## Sonic Intent

| Field | Decision |
|---|---|
| Vertical / audience |  |
| Tone and credibility level |  |
| Emotional states |  |
| Default vertical palette |  |
| Excluded families and why |  |
| Hook sound job |  |
| Discovery/proof sound job |  |
| Payoff sound job |  |
| Library manifest version |  |

## Event Ledger

| ID | Final at / pre-lap | Visible or implied trigger | Story job | Family / role | Desired attributes | Functional search query | Asset ID | Gain | Rights | Full-mix verdict |
|---|---:|---|---|---|---|---|---|---:|---|---|
| `sfx-01` |  |  |  |  |  |  |  |  |  | `keep / replace / remove` |

Allowed production families:

- `diegetic_foley`;
- `motion_transition`;
- `state_emphasis`;
- `tension_context`.

`meme_voice_reference` is quarantined unless independent commercial rights, audience/language fit and vertical credibility are all documented.

## Exact-Final SFX QC

- [ ] Every retained cue maps to one ledger event or documented sustained context state.
- [ ] The cue is audible on the encoded MP4 at the declared timestamp/pre-lap.
- [ ] Critical spoken words remain intelligible in dialogue + music + SFX.
- [ ] No delayed cue rebases to t=0 or another unintended timestamp.
- [ ] Layered sounds have distinct anchor/sweetener/context jobs.
- [ ] Repeated motifs remain distinguishable and non-fatiguing.
- [ ] Every asset ID resolves to the shared manifest and publishable rights.
- [ ] Encoded loudness/true peak and full-decode gates pass.
- [ ] The post-publish experiment changes only the declared layer; there is no soundless low-quality control.

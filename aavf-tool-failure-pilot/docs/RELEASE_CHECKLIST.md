# Release checklist and blockers

## Status

**Code is reproducible as a controlled simulation, not a validated LLM-agent study.** You can share it as a clearly labeled research pilot after personal review. Public sharing is not the same as peer-reviewed publication.

### Complete before publicly posting any manuscript

- [ ] Replace `[Your full name]` and `[Your institution / independent researcher]` in the existing Word manuscript.
- [ ] Confirm the researcher has personally inspected and rerun the code and can explain the controller.
- [ ] Audit citations and relevant 2025–2026 verification/recovery papers.
- [ ] Decide whether to publish as a *working paper / preliminary pilot*, with this status plainly stated.
- [ ] Check any planned journal/conference preprint policy before uploading a manuscript to ResearchGate or another public site.
- [ ] Explain that synthetic benchmarks do **not** establish autonomous LLM reliability.
- [ ] Add the selected code license and check any third-party dependencies/assets for their own licenses.
- [ ] Ensure code, charts, outcomes, methods, and versions agree; no test secrets or private data committed.
- [ ] Disclose AI assistance and determine eligible authorship according to institutional/venue policy.

### Needed for stronger peer-reviewed publication claims

- [ ] Implement genuinely LLM-directed tool calls and stateful tasks rather than scripted actions.
- [ ] Compare additional modern baselines found through current literature search.
- [ ] Include multiple task domains, multiple models, and replicate runs / uncertainty estimates.
- [ ] Evaluate unreliable audit/check endpoints and vary fault assumptions.
- [ ] Measure latency, token usage, monetary compute costs if making cost-efficiency claims.
- [ ] Distinguish simple heuristics and previously known idempotency/read-back patterns from genuine novel methods.
- [ ] Obtain expert feedback and validate the contribution before venue submission.

## Recommended repository and archiving workflow

1. Keep editable Word drafts, raw data, revision history, and dated backups in a private project folder.
2. Publish the tested pilot code and selected reproducibility files in a GitHub repository, after choosing a license and reviewing contents.
3. Add a clearly titled manuscript PDF under `paper/` only after correcting author details and reviewing publication/preprint rights. Avoid uploading editable Word files to a public repo unnecessarily.
4. Add a ResearchGate working-paper entry only when ready for public dissemination, accurately labeled and with correct version/status. ResearchGate itself does not peer review.
5. Write a LinkedIn post linking the actual GitHub repository and manuscript when they exist. Avoid false timelines and claims of peer review or model performance.
6. Once the repository is stabilized and the license selected, archive a tagged release with a DOI using an appropriate research archive if useful.

## Disclosure sentence template

> The research workflow, code drafting, and manuscript language involved AI assistance. The named researcher reviewed the methods, executed and validated the simulation, interpreted its limitations, and takes responsibility for the reported work.

Adjust this only to describe work that actually happened.

# AAVF real-LLM extension protocol (PROPOSED / NOT YET RUN)

**Researcher:** Roshaan Ahmed Khan | BS Artificial Intelligence (BSAI) | Sindh Madressatul Islam University, Pakistan.

## Scientific change
The published pilot (if publicly shared) must remain labeled as a *scripted simulation*. This extension adds a **language-model backend that actually chooses each tool call and supplies tool inputs**. The middleware applies one of four verification policies to the tool outputs. A separate oracle evaluates final database state and final reported values; its hidden fault codes never appear in the model context or in the controller's decision rules.

## Methods
- Target model: Qwen2.5-1.5B-Instruct in Google Colab GPU (model weights download at runtime); CPU or smaller model alternatives may work but can perform poorly.
- Same task instructions and same synthetic fault scenarios for no_check, retry, adaptive, and verify_all; one LLM model for each paired comparison.
- Primary outcome: both final state and report correct. Also report: state-only correctness, report-only correctness, duplicate writes, tool calls, verification calls, LLM generation calls, invalid actions, completion, and elapsed runtime.
- Use `run_llm_experiment.py --n 3` for smoke test then `--n 20` or more for preliminary results. Collect multiple seeds or task families for publication, since 20 tasks is insufficient for strong conclusions.
- Save all traces and versions. Review traces for unanticipated model actions and benchmark bugs. Do not cherry-pick successful prompts.
- Add an ablation that disables the operation-status audit, and fault-rate sensitivity experiments if feasible. Test unreliable audits for external validity.
- Pre-register or at least fix thresholds and metrics before main evaluation. Use confidence intervals with paired scenario-level resampling; do not call nonsignificant performance differences equivalence.

## Public benchmark options (DO NOT claim integration yet)

| Candidate | Why consider | Caveat for our project |
|---|---|---|
| τ-bench (arXiv:2406.12045) | Stateful multi-turn tool-agent tasks with verifiable outcomes | Requires careful adaptation to inject tool faults while preserving evaluation semantics |
| AgentBench (arXiv:2308.03688) | Broader interactive agent evaluation | Environment setup and comparable score reporting may be complex |
| BFCL (Berkeley Function Calling Leaderboard) | Standardizes some tool/function-calling evaluation | Tool-call accuracy is **not** the same as failure recovery or state safety |
| Kaggle mirrors and datasets | Convenient dataset discovery/storage | Verify provenance, license, benchmark splits, and that the original authors' evaluation code is used |

**Recommended sequence:** first validate the LLM harness on our own observable-fault simulator; next adapt a small, license-compatible subset of τ-bench or another stateful benchmark without modifying its scoring rules; compare with the official benchmark baseline as applicable. A benchmark is not automatically a novelty claim.

## Literature gap audit (2025–2026) before claiming originality

This environment does not have live web access. Run searches on Google Scholar, OpenReview, arXiv, Semantic Scholar, ACL Anthology, IEEE Xplore, and conference proceedings. Search phrases:
- "agentic tool failure recovery benchmark"
- "LLM agent adaptive verification cost"
- "tool-result corruption silent errors agents"
- "stateful tool execution retry idempotency agent"
- "fault injection agent tool use benchmark"
- "LLM agent unreliable tools observability"

For each relevant paper, record DOI/arXiv ID, year, code, datasets, exact verification signals, fault types, failure-mode coverage, whether state-changing writes are tested, baseline comparisons, and total cost. Formulate an originality claim only after comparing the closest papers.

## Disclosure and reporting status

**Already performed:** deterministic scripted simulation, 1,600 matched scenarios, seven original checks, reported results in manuscript v1.

**Verified offline for this extension:** AAVF model-action evaluation harness code and five mock-backend unit tests. **No external model weights downloaded or real LLM experiment run in this environment.** The mock backend is a testing stub, not an AI model.

**Not performed:** external benchmark integration, real LLM inference, quantitative LLM success-rate comparison, current 2025–2026 literature audit, originality verification, peer review.

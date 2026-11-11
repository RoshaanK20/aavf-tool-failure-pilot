# AAVF: Adaptive Agent Verification Framework

**A reproducible study of verification and recovery policies for tool-using agent workflows.**

> **Research status:** Version 1.0 is an **unreviewed working paper** and a **controlled Python simulation**. The reported results do **not** come from an autonomous LLM agent, a public agent benchmark, or a real-world deployment. A real-LLM evaluation harness is included for future experiments, but no real-model results are included in the v1.0 findings.

**Researcher:** Roshaan Ahmed Khan  
**Affiliation:** BS Artificial Intelligence (BSAI), Sindh Madressatul Islam University, Pakistan  
**Version:** v1.0 | Preliminary experimental release

## Why this project?

Agents can interact with databases, APIs, and software tools, but an apparently successful response does not always mean the operation worked. A response may be incomplete, outdated, silently corrupted, or missing after a state-changing operation. Retrying blindly can also create duplicate updates.

**AAVF** explores whether a *fixed-rule, risk-aware selective verification policy* can offer a useful balance between task success and verification overhead. This first release compares it with three simple policies in a fully controlled simulation.

## Research questions

- Can selective checking improve task success when tool responses may fail or be misleading?
- How much verification overhead can be avoided compared with checking every tool interaction?
- Can reading the resulting state before retrying help prevent duplicate state-changing operations?

## System overview

![Pilot architecture](figures/pilot_architecture.png)

The simulated workflow performs inventory-related reads and writes under injected faults. Every policy is evaluated on the same 1,600 generated scenarios. The evaluation checks final database state and task reporting, rather than accepting the workflow's own claim of success.

### Policies compared

1. **No check:** Continue without a dedicated verification step.
2. **Naive retry:** Apply a bounded retry policy when an operation appears to fail.
3. **Verify all:** Verify every eligible operation.
4. **Selective verification (AAVF):** Apply fixed risk rules to decide when to check or recover.

## Pilot results

**1,600 matched synthetic scenarios; 4 policies; 6,400 policy outcomes.** Seed: `20261110`.

| Policy | End-to-end task success | Mean tool calls | Duplicate updates |
|---|---:|---:|---:|
| No check | 62.13% | 3.00 | 0 |
| Naive retry | 79.00% | 3.30 | 67 |
| Verify all | 100.00% | 6.13 | 0 |
| **Selective verification (AAVF)** | **85.13%** | **4.11** | **0** |

![Task success rates](figures/simulation_success.png)

![Verification overhead](figures/simulation_calls.png)

**Interpretation:** In this simulation, selective verification improved success by **23 percentage points** over no checking and used approximately **33% fewer tool calls** than verifying every action. However, verify-all still achieved higher success. Its **100% result depends on a perfectly reliable, immediately consistent audit endpoint** built into the simulator. It is not evidence of perfect real-world agent reliability.

The selective policy can miss some *plausible but incorrect* tool responses. Results depend on the simulated failure probabilities, decision rules, and task design. See [`results/summary.json`](results/summary.json) for the exact metrics and paired bootstrap comparisons.

## Reproduce the simulation

**Requirements:** Python 3.9+; the core experiment uses the standard library. Matplotlib is optional for regenerating figures.

```bash
# Clone your repository after uploading it to GitHub, then enter its folder.
# (Or unzip the public release package and open the repository folder.)

python -m unittest discover -s tests -p "test_*.py" -v
python run_experiment.py
```

Optional plots:

```bash
pip install matplotlib
python run_experiment.py
```

Generated artifacts:

- `results/scenarios.jsonl` — reproducible synthetic scenarios
- `results/outcomes.csv` — outcome of each policy on each scenario
- `results/summary.json` — aggregate results and confidence intervals
- `figures/` — architecture and plots

The experiment uses 3,000 paired bootstrap resamples in its summary comparisons.

## Repository structure

```text
aavf-tool-failure-pilot/
├── README.md
├── run_experiment.py
├── run_llm_experiment.py       # extension; not used for v1 results
├── src/
│   ├── aavf_sim.py           # simulator and four policies
│   ├── llm_agent_eval.py     # LLM-action evaluation harness
│   └── hf_backend.py         # optional open-weight model backend
├── tests/                    # 12 passing local tests
├── notebooks/                # pilot and optional LLM Colab notebooks
├── adapters/                 # optional FastAPI / MCP wrappers
├── results/                  # simulated scenario data and outcomes
├── figures/                  # research graphics
├── manuscript/               # working paper PDF
├── docs/                     # scope, release notes, literature checklist
└── CITATION.cff
```

## Optional real-LLM extension

A separate harness allows an open-weight language model to select tool actions. To try this experiment in a GPU-capable environment such as Google Colab:

```bash
pip install -r requirements-llm.txt
python run_llm_experiment.py --n 12 --model Qwen/Qwen2.5-1.5B-Instruct
```

You can also start from `notebooks/02_real_llm_colab.ipynb`.

**Important:** This command requires model downloads and sufficient RAM/VRAM; it has **not** been used to produce the v1.0 paper results. The 12 automated tests use the simulator and a mock model where needed. The optional FastAPI and MCP adapters also are **not part of the reported experiment**, and the MCP adapter has not been validated in the release audit.

## Working paper

**Document:** *AAVF Working Paper v1.0*  
**Author:** Roshaan Ahmed Khan  
**Status:** Preliminary, unreviewed working paper.

[Read the PDF manuscript](aavf-tool-failure-pilot/manuscript/AAVF_Working_Paper_v1.0_Roshaan_Ahmed_Khan.pdf)

Do not describe this version as a peer-reviewed paper, a verified original method, or an LLM-agent benchmark. A comparison with relevant 2025–2026 literature remains outstanding; see `docs/2025_2026_LITERATURE_AUDIT_TEMPLATE.csv`.

## Roadmap

- [x] Implement four verification-policy simulations
- [x] Record 1,600 reproducible scenarios and results
- [x] Add automated simulator and harness tests
- [x] Write preliminary working paper
- [ ] Complete current related-work and novelty audit
- [ ] Run genuine LLM action-selection experiments and inspect traces
- [ ] Adapt a suitable public benchmark under a clearly documented protocol
- [ ] Add failure-distribution sensitivity tests and less idealized verification
- [ ] Revise manuscript using validated new results

## Transparency, citation, and license

This project is a **research prototype**. It does not establish production safety or generalize automatically to larger agents or complex real applications. Code and manuscript drafting received AI assistance; experimental claims should be independently checked by the researcher. Full study limitations are described in the working paper and `docs/RESEARCH_SCOPE.md`.

Citation metadata is provided in [`CITATION.cff`](CITATION.cff). Please cite the **working-paper version** appropriately until a formally reviewed publication exists.

**License:** No open-source license has yet been selected for this repository. An optional MIT license template is included in the release package. A public repository is not automatically open source: add a reviewed `LICENSE` file before granting reuse permissions. Manuscript rights may be different from code rights.

---

**Feedback and collaboration:** Issues and research suggestions are welcome once the repository is public. Please reference the relevant simulation scenario or result when reporting problems.

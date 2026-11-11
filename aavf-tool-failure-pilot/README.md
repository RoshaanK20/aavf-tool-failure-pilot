# AAVF Tool-Failure Pilot | Working Paper v1.0

> **Research status: preliminary scripted-policy simulation.** This is **not an LLM-agent benchmark, a peer-reviewed publication, or proof of a novel method**. The repository is a reproducible research prototype.

This pilot compares four tool-use verification policies under synthetic inventory tool errors: no additional checking, bounded retry, verify-all, and a fixed-rule selective verification controller. It simulates missing, invalid, and plausible-but-wrong reads, as well as ambiguous write outcomes.

## Reproduce the experiment

Requires Python 3.9+; the core simulator uses only Python's standard library. From the repository root:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python run_experiment.py
```

Saved outputs: `results/scenarios.jsonl`, `results/outcomes.csv`, `results/summary.json`; plots are generated if Matplotlib is installed (`pip install matplotlib`). The scenario generator uses seed `20261110`; the paired bootstrap uses 3,000 replicates.

## Results from the controlled pilot

| Policy | Success, both final state and report | Mean total tool calls | Duplicate updates |
|---|---:|---:|---:|
| No check | 62.125% | 3.00 | 0 |
| Naive retry | 79.000% | 3.30 | 67 |
| Verify every action | 100.000% | 6.13 | 0 |
| Selective fixed-rule checks | 85.125% | 4.11 | 0 |

**These figures come from an artificial benchmark, not deployed AI agents.** In this setup, verify-all benefits from a perfectly reliable, immediately consistent audit endpoint, explaining its 100% success. Selective verification leaves some plausible silent corruptions unresolved. The results are conditional on the chosen fault distribution, simulated tools, and rule thresholds.

## Repository contents

- `src/aavf_sim.py`: deterministic simulation and four policy implementations
- `run_experiment.py`: experiment runner, results export, bootstrap analysis, charts
- `tests/test_aavf.py`: seven original automated tests
- `results/`: scenario data, outcomes, and numerical summaries
- `figures/`: simulation architecture and outcome charts
- `notebooks/01_colab_pilot.ipynb`: notebook for running the ZIP in Colab
- `adapters/`: optional FastAPI and MCP wrappers, **not used in reported results**
- `docs/`: release checklist, reference notes, methodology and disclosure

## Optional adapters

- FastAPI: `pip install fastapi uvicorn`, then `uvicorn adapters.fastapi_app:app` to serve `POST /simulate`. A smoke test passed with FastAPI installed; not part of the published numerical experiment.
- MCP: `pip install mcp`, then `python adapters/mcp_server.py`. This optional adapter was **not executed or validated** in the research audit. Check the installed SDK version before use.

These adapters expose a scripted simulator. Neither one creates an LLM reasoning agent by itself.

## Citation and publication status

This repository accompanies a **preliminary simulation manuscript**. The author and affiliation are filled in; current related-work completeness (2025–2026), originality, licensing and release permissions still require researcher review. See `docs/RELEASE_CHECKLIST.md`. Do not cite it as a peer-reviewed publication. Add a stable manuscript URL and citation metadata only after a version is published.

## License and provenance

A license has deliberately **not** been selected on behalf of the researcher. Before publishing, decide which permissions to grant and add a `LICENSE` file (MIT is one common permissive choice for code; a manuscript may need a different license or rights arrangement). Until a license is added, public visibility does not automatically grant reuse rights.

Code and text were prepared with AI assistance. Review the code, inspect all results, follow your institution's AI-use requirements, and preserve a traceable experimental record.

## Experimental extension (not part of reported manuscript results)

Researcher: **Roshaan Ahmed Khan**, BS Artificial Intelligence (BSAI), Sindh Madressatul Islam University, Pakistan.

An optional **real language-model action-selection harness** is added in `src/llm_agent_eval.py`, with `src/hf_backend.py` as an on-device model adapter, `run_llm_experiment.py` as the runner, and `notebooks/02_real_llm_colab.ipynb` as an execution guide. The model chooses tool actions and their parameters; the AAVF policy guards tool results. A small scripted stub is used only for offline tests. **No real LLM evaluation has been run or incorporated into the numerical results in this repository.** Read `docs/LLM_RESEARCH_EXTENSION.md` for the proposed protocol and benchmark limitations.

## Public working paper and publishing guide

- PDF: `manuscript/AAVF_Working_Paper_v1.0_Roshaan_Ahmed_Khan.pdf`
- Instructions: `docs/GITHUB_RESEARCHGATE_LINKEDIN_GUIDE.md`
- LinkedIn post: `docs/LINKEDIN_POST.md`
- ResearchGate copy: `docs/RESEARCHGATE_SUMMARY.md`
- Release status: `docs/PUBLIC_RELEASE_STATUS.md`

Open-source licensing is **not yet selected**. See the optional MIT license template and choose before describing this public repository as open source.

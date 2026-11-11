# Research scope and honest claim boundaries

**What was tested:** A deterministic synthetic inventory workflow with scripted decision logic. In 1,600 matched scenarios across four policies, read/write faults were injected, with outcomes exported for independent inspection.

**What was NOT tested:** An autonomous LLM selecting tools, MCP server integration, browser/web agent, production API reliability, different models, independent environments, unreliable audits, model token costs, or market deployment.

**Observation:** Selective verification improved overall synthetic task success by 23 percentage points over no checking, but lagged full verification by 14.875 points. Under the artificial assumption of a perfect audit service, verify-all achieved 100% task success. A fixed-rule selective controller did not catch all valid-looking errors.

**Not an originality claim:** Recovery from timeouts, idempotency semantics, feedback agents and self-correction have existing literature and engineering practice. A literature audit through 2026 is required before asserting a novel contribution.

**Study limitations:** Synthetic fault rates chosen by design, single task family, no model inference, optimistic audit behavior, narrow cost proxy, simple heuristic risk threshold, and no formal generalization to deployed agents.

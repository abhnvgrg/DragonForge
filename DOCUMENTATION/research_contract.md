# Research Contract — Claim Tags & Evidence

**Status: LIVING DOCUMENT** — Updated same day any claim's evidence status changes. Every claim tagged as **ESTABLISHED**, **MEASURED**, or **EXPLORATORY**.

---

## Tag Definitions

| Tag | Meaning | Evidence Required |
|-----|---------|-------------------|
| **ESTABLISHED** | Prior published result, reproduced or cited | Citation + reproduction in our setup |
| **MEASURED** | New result from our experiments | JSON in `results/` + statistical significance (p < 0.05, n ≥ 3 seeds) |
| **EXPLORATORY** | Hypothesis, not yet tested | Clear experimental plan, not yet run |
| **PARTIALLY_SUPPORTED** | Mixed evidence | Some metrics support, others contradict |

---

## Claims Registry

### C1: BDH has sparse positive activations
- **Tag:** ESTABLISHED
- **Source:** Pathway paper (arXiv:2509.26507), Section 3.2
- **Our Reproduction:** Measured activation sparsity in `results/structure/checkpoint_<N>.json`
- **Evidence:** `sparsity` field > 0.7 consistently across checkpoints
- **Last Updated:** 2026-08-09

### C2: BDH exhibits specific modularity / degree statistics
- **Tag:** MEASURED
- **Our Measurement:** Modularity (Louvain) + degree distribution from graph extraction
- **Evidence:** `modularity` and `degree_distribution` fields in `results/structure/checkpoint_<N>.json`
- **Random Control:** `modularity_random_control` computed on configuration model
- **Last Updated:** 2026-08-09

### C3: Relationship between structure and retention
- **Tag:** EXPLORATORY
- **Hypothesis:** Higher modularity → lower forgetting in continual learning
- **Planned Test:** Correlation between `modularity` (structure) and `forgetting` (continual learning) across seeds
- **Experimental Plan:** Run continual learning with 3 seeds, compute Pearson r
- **Last Updated:** 2026-08-09

### C4: Performance on our continual learning setup
- **Tag:** MEASURED
- **Our Measurement:** Split MNIST / Permuted MNIST continual learning
- **Evidence:** `results/continual/result.json` with `forgetting`, `task_a_before`, `task_a_after`, `baseline_transformer`
- **Seeds:** [1, 2, 3]
- **Last Updated:** 2026-08-09

### C5: Performance on long-context reasoning
- **Tag:** MEASURED
- **Our Measurement:** Needle-in-haystack, Multi-hop QA, Variable Tracking
- **Evidence:** `results/reasoning/result.json` with `bdh_accuracy_mean`, `bdh_accuracy_std`, `transformer_accuracy_mean`, `transformer_accuracy_std`
- **Seeds:** [1, 2, 3]
- **Last Updated:** 2026-08-09

### C6: Structural metrics predict long-context accuracy
- **Tag:** EXPLORATORY
- **Hypothesis:** Sparsity/modularity correlates with reasoning accuracy at long contexts
- **Planned Test:** Cross-seed correlation between structural metrics and `results/reasoning/result.json` accuracy
- **Last Updated:** 2026-08-09

---

## Claim-to-Result Mapping

| Claim | Primary Result File | Key Fields |
|-------|---------------------|------------|
| C1 | `results/structure/checkpoint_<N>.json` | `sparsity` |
| C2 | `results/structure/checkpoint_<N>.json` | `modularity`, `degree_distribution`, `clustering_coefficient`, `modularity_random_control` |
| C3 | `results/continual/result.json` + `results/structure/checkpoint_<N>.json` | Correlation analysis (post-hoc) |
| C4 | `results/continual/result.json` | `forgetting`, `task_a_before`, `task_a_after`, `baseline_transformer` |
| C5 | `results/reasoning/result.json` | `bdh_accuracy_mean`, `transformer_accuracy_mean`, stds |
| C6 | Cross-file analysis | Post-hoc correlation |

---

## Statistical Standards

- **Seeds:** Minimum 3 seeds per experiment (config: `training.seeds: [1, 2, 3]`)
- **Significance:** p < 0.05 (two-tailed)
- **Effect Size:** Report Cohen's d for mean differences
- **Confidence Intervals:** 95% CI on all mean estimates
- **Random Controls:** 100 iterations for graph null models

---

## Updating Procedure

When a claim's tag changes:

1. Edit this file **same day** the evidence is generated
2. Update the "Last Updated" field
3. Add the specific result file path and key numbers
4. If tag changes from EXPLORATORY → MEASURED, update `docs/if_we_had_a_larger_model.md` if implications change
5. Announce in team chat: "Claim C3 updated: EXPLORATORY → MEASURED (r=0.62, p=0.03)"

---

## Current Summary (as of 2026-08-09)

| Tag | Count | Claims |
|-----|-------|--------|
| ESTABLISHED | 1 | C1 |
| MEASURED | 2 | C2, C4, C5 |
| EXPLORATORY | 2 | C3, C6 |
| PARTIALLY_SUPPORTED | 0 | — |

---

**Next Review:** After first full pipeline run completes.
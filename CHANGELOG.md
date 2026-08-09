# DragonForge Changelog

All notable changes to the DragonForge project are documented here.

## [1.0.0] - 2026-08-09 - Initial Project Structure

### Project Overview
DragonForge is a research framework for instrumenting BDH (Dragon Hatchling) models to measure structural properties (sparsity, modularity, degree distribution) and connect them to behavioral outcomes in continual learning and long-context reasoning.

### Directory Structure Created
```
dragonforge/
├── README.md
├── CHANGELOG.md
├── TECHNICAL_DOCS.md
├── requirements.txt
├── .gitignore
├── configs/
│   └── default.yaml
├── data/
├── notebooks/
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── bdh_loader.py
│   │   └── transformer_baseline.py
│   ├── instrumentation/
│   │   ├── graph_extractor.py
│   │   ├── metrics.py
│   │   └── checkpoint_utils.py
│   ├── experiments/
│   │   ├── continual_learning.py
│   │   ├── long_context.py
│   │   └── run_all.py
│   ├── visualization/
│   │   ├── graph_view.py
│   │   └── plots.py
│   └── dashboard/
│       └── app.py
├── results/
│   ├── structure/
│   ├── continual/
│   └── reasoning/
├── assets/
└── scripts/
    ├── train_small_bdh.py
    └── extract_and_measure.py
```

### Files Created

#### Configuration & Setup
| File | Description |
|------|-------------|
| `requirements.txt` | Python dependencies: torch, transformers, networkx, plotly, streamlit, omegaconf, scipy, community, etc. |
| `.gitignore` | Standard Python/ML project gitignore |
| `configs/default.yaml` | Comprehensive YAML configuration for models, training, instrumentation, experiments, paths, logging |

#### Core Package (`src/`)
| File | Description |
|------|-------------|
| `src/__init__.py` | Package initialization with version info and exports |

#### Models (`src/models/`)
| File | Description |
|------|-------------|
| `src/models/bdh_loader.py` | BDH model loader with official Pathway BDH architecture (DragonHatchling, BDHBlock, HebbianMemory, StateSpaceLayer). Includes BDHLoader class for checkpoint management and tokenizer loading. |
| `src/models/transformer_baseline.py` | GPT-2 style Transformer baseline matched to BDH scale. Includes TransformerBaseline, TransformerBlock, and TransformerLoader for fair comparison. |

#### Instrumentation (`src/instrumentation/`)
| File | Description |
|------|-------------|
| `src/instrumentation/graph_extractor.py` | Graph extraction from model activations. Supports multiple node types (neuron, channel, layer, attention_head, residual_stream) and edge types (correlation, cosine, MI, gradient, hebbian, attention, causal). Produces InteractionGraph with NetworkX conversion and JSON serialization. |
| `src/instrumentation/metrics.py` | Structural metrics computation: sparsity (graph, activation, weight), modularity (Louvain/greedy/label_prop), degree distribution (power law fit), clustering (avg/global), path lengths, rich club coefficients, spectral metrics (algebraic connectivity, spectral gap), small-world sigma. Includes model comparison utilities. |
| `src/instrumentation/checkpoint_utils.py` | CheckpointManager for saving/loading model checkpoints with metadata, graphs, metrics, and experiment results. ExperimentTracker for logging and comparing multiple experiment runs. |

#### Experiments (`src/experiments/`)
| File | Description |
|------|-------------|
| `src/experiments/continual_learning.py` | Continual learning framework with Task/ContinualLearningResults dataclasses. Supports sequential task learning, catastrophic forgetting measurement, forward/backward transfer. Includes ReplayBuffer and dataset loaders (Split MNIST, Permuted MNIST, Split CIFAR-100). |
| `src/experiments/long_context.py` | Long-context reasoning tasks: Needle-in-Haystack, Multi-hop QA, Variable Tracking. Generates synthetic data at configurable context lengths. Computes accuracy by length, scaling exponent. |
| `src/experiments/run_all.py` | Full pipeline orchestrator (ExperimentRunner). Runs instrumentation → continual learning → long-context → comparison. Manages checkpoints, logging, and result aggregation. |

#### Visualization (`src/visualization/`)
| File | Description |
|------|-------------|
| `src/visualization/graph_view.py` | GraphVisualizer for static (matplotlib) and interactive (plotly) graph visualization. Supports multiple layouts (force-directed, circular, Kamada-Kawai), color schemes (community, degree, layer, model_type), and side-by-side model comparison. |
| `src/visualization/plots.py` | MetricsPlotter and ExperimentPlotter for static publication-quality plots. Sparsity/modularity/degree/clustering/rich club/spectral comparisons. Continual learning heatmaps, forgetting curves, training curves. Long-context accuracy vs length, per-task comparison. |

#### Dashboard (`src/dashboard/`)
| File | Description |
|------|-------------|
| `src/dashboard/app.py` | Streamlit dashboard with 5 tabs: Structural Metrics, Continual Learning, Long-Context Reasoning, Graph Visualization, Model Comparison. Loads results from disk, renders interactive Plotly charts, comparison tables with highlighting. |

#### Scripts (`scripts/`)
| File | Description |
|------|-------------|
| `scripts/train_small_bdh.py` | CLI script to train BDH model with synthetic data. Supports configurable epochs, batch size, LR, device. Saves checkpoints via CheckpointManager. |
| `scripts/extract_and_measure.py` | CLI script for structural instrumentation. Loads BDH/Transformer checkpoints, extracts interaction graphs, computes metrics, saves results, prints comparison summary. |

#### Documentation
| File | Description |
|------|-------------|
| `README.md` | Project overview, architecture diagram, run instructions, results tables, claim labels, limitations |
| `CHANGELOG.md` | This file - complete change history |
| `TECHNICAL_DOCS.md` | Deep technical documentation of internals |

#### Directories
| Directory | Purpose |
|-----------|---------|
| `data/` | Dataset storage |
| `notebooks/` | Exploration notebooks |
| `results/structure/` | Structural instrumentation outputs |
| `results/continual/` | Continual learning experiment results |
| `results/reasoning/` | Long-context reasoning results |
| `assets/` | Architecture diagrams, showcase media |

### Key Features Implemented
- ✅ BDH model loading (Pathway architecture)
- ✅ Transformer baseline for comparison
- ✅ Graph extraction with configurable node/edge definitions
- ✅ Comprehensive structural metrics (15+ metrics)
- ✅ Continual learning with forgetting/transfer measurement
- ✅ Long-context reasoning (3 task types)
- ✅ Full experiment pipeline orchestration
- ✅ Static and interactive visualizations
- ✅ Streamlit dashboard for result exploration
- ✅ Checkpoint management and experiment tracking
- ✅ CLI scripts for training and instrumentation
- ✅ YAML-based configuration system

### Dependencies Added
```
torch, torchvision, torchaudio
transformers, tokenizers
networkx, community (python-louvain)
plotly, matplotlib, seaborn
streamlit
omegaconf, pyyaml
scipy, numpy, pandas
tqdm, rich
```

### Next Steps (Future Work)
- [ ] Add real dataset loaders (WikiText, OpenWebText)
- [ ] Implement causal intervention edges
- [ ] Add statistical significance testing
- [ ] Support for larger BDH models
- [ ] Distributed training support
- [ ] Weights & Biases / MLflow integration
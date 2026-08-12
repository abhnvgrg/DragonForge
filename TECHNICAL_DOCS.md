# NeuroLens Technical Documentation

## Deep Technical Reference for Internal Workings

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Model Layer](#model-layer)
3. [Instrumentation Pipeline](#instrumentation-pipeline)
4. [Experiment Framework](#experiment-framework)
4. [Visualization System](#visualization-system)
5. [Dashboard](#dashboard)
6. [Data Flow](#data-flow)
7. [Configuration System](#configuration-system)
8. [Checkpoint & Experiment Tracking](#checkpoint--experiment-tracking)
9. [CLI Scripts](#cli-scripts)
10. [Extension Points](#extension-points)

---

## Architecture Overview

### High-Level Design

NeuroLens follows a modular pipeline architecture:

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│   Models    │────▶│  Instrumentation │────▶│    Experiments      │
│  (BDH/Trans)│     │ (Graph + Metrics)│     │ (CL / Long-Context) │
└─────────────┘     └──────────────────┘     └─────────────────────┘
                           │                        │
                           ▼                        ▼
                    ┌──────────────────┐     ┌─────────────────────┐
                    │  Visualization   │     │    Dashboard        │
                    │ (Graphs + Plots) │     │  (Streamlit App)    │
                    └──────────────────┘     └─────────────────────┘
```

### Core Principles

1. **Separation of Concerns**: Models, instrumentation, experiments, and visualization are independent modules
2. **Config-Driven**: All parameters controlled via YAML configuration
3. **Reproducibility**: Checkpoint management, experiment tracking, and seeded randomness
4. **Comparative Design**: Every component supports BDH vs Transformer comparison
5. **Extensibility**: Plugin-style architecture for new node/edge types, metrics, tasks

---

## Model Layer

### BDH Model (`src/models/bdh_loader.py`)

#### Architecture Components

**DragonHatchling** (Main Model Class)
```python
class DragonHatchling(nn.Module):
    - token_embedding: nn.Embedding(vocab_size, d_model)
    - position_embedding: nn.Embedding(max_seq_len, d_model)
    - blocks: nn.ModuleList[BDHBlock]  # n_layers
    - ln_f: nn.LayerNorm(d_model)
    - head: nn.Linear(d_model, vocab_size, bias=False)  # tied to token_embedding
```

**BDHBlock** (Single Layer)
```python
class BDHBlock(nn.Module):
    - attention: StateSpaceLayer  # SSM-based attention
    - hebbian_memory: HebbianMemory  # Plasticity-based working memory
    - ff_up: nn.Linear(d_model, d_ff)
    - ff_down: nn.Linear(d_ff, d_model)
    - ln_1, ln_2: LayerNorm
    - dropout: nn.Dropout
```

**StateSpaceLayer** (SSM Attention)
- Implements structured state-space attention (S4/S5 style)
- `A, B, C, D` matrices for state transitions
- `discretize()`: Continuous → discrete via bilinear/ZOH
- `forward()`: Parallel scan for efficient sequence processing
- Complexity: O(L) vs O(L²) for standard attention

**HebbianMemory** (Plasticity-Based Memory)
- `hebbian_trace`: Running outer product of pre/post activations
- `update()`: Hebbian learning rule with decay
- `read()`: Memory retrieval via similarity
- Provides monosemantic, interpretable memory slots

#### Key BDH Properties
| Property | Implementation |
|----------|----------------|
| Sparse positive activations | ReLU + sparsity regularization in StateSpaceLayer |
| Scale-free topology | StateSpaceLayer A matrix initialization |
| Local interactions | HebbianMemory operates on local neuron groups |
| Interpretability | Hebbian traces directly readable as memory |

#### BDHLoader Class
```python
class BDHLoader:
    - load_model(config, checkpoint_path) -> DragonHatchling
    - load_tokenizer() -> GPT2TokenizerFast
    - generate(prompt, max_new_tokens, temperature, top_k) -> str
    - register_instrumentation_hooks(layer_indices) -> hooks
    - get_activations() -> Dict[str, Tensor]
```

### Transformer Baseline (`src/models/transformer_baseline.py`)

#### Architecture
Standard GPT-2 style (Pre-LN):
```
TransformerBaseline:
    - token_embedding + position_embedding
    - n_layers × TransformerBlock
    - ln_f + tied output head

TransformerBlock:
    - MultiheadAttention (Pre-LN)
    - FeedForward (GELU, Pre-LN)
    - Residual connections
```

#### Matching Strategy
- Same `d_model`, `n_layers`, `n_heads`, `vocab_size`, `max_seq_len`
- Parameter count matched via `match_model_sizes()` utility
- Same tokenizer (GPT-2) for fair comparison

---

## Instrumentation Pipeline

### Graph Extraction (`src/instrumentation/graph_extractor.py`)

#### Node Definitions (NodeType Enum)
| Type | Description | Node Count |
|------|-------------|------------|
| `NEURON` | Individual neurons/units | d_model per layer |
| `CHANNEL` | Groups of neurons (default 64) | d_model/64 per layer |
| `LAYER` | Entire layer output | 1 per layer |
| `ATTENTION_HEAD` | Individual attention heads | n_heads per attn layer |
| `RESIDUAL_STREAM` | Positions in residual stream | seq_len per layer |

#### Edge Definitions (EdgeType Enum)
| Type | Computation | Use Case |
|------|-------------|----------|
| `CORRELATION` | Pearson correlation | General connectivity |
| `COSINE_SIMILARITY` | Cosine similarity | Directional similarity |
| `MUTUAL_INFORMATION` | MI approximation | Non-linear dependencies |
| `GRADIENT_FLOW` | Gradient-based | Information flow |
| `HEBBIAN` | Hebbian trace (BDH-specific) | Plasticity structure |
| `ATTENTION` | Attention weights (Transformer) | Attention patterns |
| `CAUSAL` | Ablation/intervention | Causal connectivity |

#### GraphConfig Parameters
```python
@dataclass
class GraphConfig:
    node_type: NodeType = NEURON
    edge_type: EdgeType = CORRELATION
    correlation_threshold: float = 0.3
    top_k_edges: Optional[int] = None
    sample_batches: int = 100
    sample_seq_len: int = 512
    target_layers: Optional[List[int]] = None
    aggregate_over_seq: bool = True
    aggregate_over_batch: bool = True
```

#### Extraction Process
1. **Activation Collection**: Forward passes on dataloader, store activations per layer
2. **Node Definition**: Create nodes based on `node_type` and layer activations
3. **Edge Computation**: Pairwise similarity between node activations
4. **Thresholding**: Apply correlation threshold or top-k sparsification
5. **Graph Construction**: Build NetworkX graph with metadata

#### InteractionGraph Output
```python
@dataclass
class InteractionGraph:
    nodes: List[str]                    # Node identifiers
    edges: List[Tuple[str, str, float]] # (source, target, weight)
    adjacency_matrix: np.ndarray        # Dense adjacency
    node_metadata: Dict[str, Dict]      # Layer, position, type info
    graph_config: GraphConfig           # Config used
    model_type: str                     # "bdh" or "transformer"
    extraction_stats: Dict              # Statistics
```

### Structural Metrics (`src/instrumentation/metrics.py`)

#### Metrics Categories

**Sparsity Measures**
- `sparsity`: Graph edge sparsity (fraction of zero edges)
- `activation_sparsity`: Fraction of zero activations across layers
- `weight_sparsity`: Fraction of near-zero weights (|w| < 1e-6)

**Modularity / Community Structure**
- `modularity`: Louvain/greedy/label_prop modularity score
- `n_communities`: Number of detected communities
- `community_sizes`: Size distribution
- `community_assignments`: Node → community mapping

**Degree Distribution**
- `degree_distribution`: Histogram of node degrees
- `avg_degree`, `max_degree`: Summary statistics
- `degree_assortativity`: Degree correlation between connected nodes
- `power_law_exponent`, `power_law_p_value`: Power law fit (MLE + KS test)

**Clustering**
- `avg_clustering`: Mean local clustering coefficient
- `global_clustering`: Transitivity (3×triangles / connected triples)
- `clustering_distribution`: Histogram of clustering values

**Path Lengths**
- `avg_path_length`: Mean shortest path (largest component)
- `diameter`: Longest shortest path
- `radius`: Minimum eccentricity

**Rich Club**
- `rich_club_coefficients`: φ(k) for each degree threshold
- `rich_club_normalized`: φ_norm(k) vs random graphs

**Small-World**
- `small_world_sigma`: σ = (C/C_rand) / (L/L_rand)

**Spectral**
- `algebraic_connectivity`: Fiedler value (λ₂ of Laplacian)
- `spectral_gap`: λ₂ - λ₁ of normalized Laplacian
- `eigenvector_centrality`: Principal eigenvector of adjacency

#### MetricsComputer
```python
class MetricsComputer:
    compute_all(graph, adjacency_matrix, activations, model_weights) -> StructuralMetrics
    compute_layer_wise(layer_graphs, layer_adjacencies) -> Dict[str, StructuralMetrics]
```

#### Model Comparison
```python
compare_models(bdh_metrics, transformer_metrics) -> Dict
# Returns: sparsity, modularity, degree, clustering, path, spectral comparisons
```

---

## Experiment Framework

### Continual Learning (`src/experiments/continual_learning.py`)

#### Task Structure
```python
@dataclass
class Task:
    name: str
    dataset_name: str
    task_id: int
    num_classes: int
    train_data, val_data, test_data: Dataset
```

#### Metrics Computed
| Metric | Formula | Interpretation |
|--------|---------|----------------|
| `avg_accuracy` | Mean accuracy on all tasks (final model) | Overall retention |
| `forgetting[task]` | max_acc(task) - final_acc(task) | Catastrophic forgetting |
| `forward_transfer[task]` | acc(task | prev tasks) - acc(task | random) | Positive transfer |
| `backward_transfer[task]` | final_acc(task) - acc(task | when learned) | Retroactive interference |

#### ReplayBuffer
- Random sampling strategy (extensible to herding, reservoir)
- Configurable buffer size
- Mixed with current task data during training

#### Dataset Loaders
- `load_split_mnist(task_id, num_tasks=5)`: 2 classes/task
- `load_permuted_mnist(task_id, num_tasks=5)`: Fixed pixel permutation
- `load_split_cifar100(task_id, num_tasks=10)`: 10 classes/task

### Long-Context Reasoning (`src/experiments/long_context.py`)

#### Task Types

**1. Needle in Haystack**
- Context: Random tokens + single "needle" token at random position
- Query: "What is the needle?" (separator token)
- Answer: Needle token
- Tests: Retrieval from long context

**2. Multi-hop QA**
- Context: Chain of relations (A→B, B→C, C→D...)
- Query: "What does A lead to?"
- Answer: Final entity in chain
- Tests: Multi-step reasoning

**3. Variable Tracking**
- Context: Sequence of assignments (x=1, y=2, x=3, z=4...)
- Query: "What is the value of x?"
- Answer: Final value of queried variable
- Tests: State tracking over long sequences

#### LongContextTask Config
```python
@dataclass
class LongContextTask:
    name: str
    context_lengths: List[int]  # e.g., [128, 256, 512, 1024, 2048]
    num_samples: int
    needle_type: str = "random_token"
    num_hops: int = 2
    num_variables: int = 3
```

#### Metrics
- `accuracies[task][length]`: Per-task, per-length accuracy
- `accuracy_by_length[length]`: Aggregate across tasks
- `length_scaling_exponent`: Slope of log(accuracy) vs log(length)
- `avg_accuracy`: Overall mean

### Full Pipeline (`src/experiments/run_all.py`)

#### ExperimentRunner Flow
```python
def run_all():
    1. Load models (BDH + Transformer)
    2. Create instrumentation dataloader
    3. Run structural instrumentation (if enabled)
       - Extract graphs for both models
       - Compute metrics
       - Compare
    4. Run continual learning (if enabled)
       - Fresh model copies for fair comparison
       - Sequential task training
       - Evaluate on all previous tasks
       - Compare forgetting/transfer
    5. Run long-context (if enabled)
       - Generate tasks at multiple lengths
       - Evaluate both models
       - Compare scaling
    6. Overall comparison logging
    7. Save aggregated results
    8. Log to ExperimentTracker
```

#### Key Design Decisions
- **Fresh model copies**: Each experiment gets independently loaded model to avoid contamination
- **Same dataloader**: Instrumentation uses identical data for both models
- **Config-driven**: All hyperparameters from YAML
- **Checkpoint integration**: Automatic saving at each stage

---

## Visualization System

### Graph Visualization (`src/visualization/graph_view.py`)

#### GraphVisualizer
```python
class GraphVisualizer:
    visualize(graph, save_path, interactive) -> Figure
    visualize_comparison(bdh_graph, trans_graph, save_path) -> Figure
```

#### Layout Algorithms
| Layout | Algorithm | Best For |
|--------|-----------|----------|
| `force_directed` | Fruchterman-Reingold | General purpose |
| `circular` | Circular | Small graphs |
| `kamada_kawai` | Kamada-Kawai | Aesthetic |
| `hierarchical` | Graphviz dot | Layered structure |

#### Color Schemes
| Scheme | Source | Description |
|--------|--------|-------------|
| `community` | Louvain communities | Modular structure |
| `degree` | Node degree | Hub identification |
| `layer` | Layer index | Depth visualization |
| `model_type` | BDH vs Transformer | Model comparison |

#### Output Formats
- Static: Matplotlib (PNG, PDF, SVG)
- Interactive: Plotly (HTML with hover tooltips)

### Static Plots (`src/visualization/plots.py`)

#### MetricsPlotter
- `plot_sparsity_comparison()`: 3-bar grouped chart
- `plot_modularity_comparison()`: Modularity + community count
- `plot_degree_distribution()`: Log-scale histograms
- `plot_clustering_comparison()`: Avg + global clustering
- `plot_rich_club()`: Raw + normalized curves
- `plot_spectral_metrics()`: Algebraic connectivity + spectral gap
- `plot_all_structural_comparison()`: Batch generation

#### ExperimentPlotter
- `plot_continual_learning_results()`: 2×2 grid (heatmaps, forgetting, transfer)
- `plot_long_context_results()`: 2×2 grid (length scaling, per-task, exponent, summary)
- `plot_training_curves()`: Per-task validation curves

---

## Dashboard (`src/dashboard/app.py`)

### Streamlit App Structure

#### Tabs
1. **Structural Metrics**: Key metric cards, detailed comparison charts (sparsity, modularity, degree, rich club)
2. **Continual Learning**: Accuracy heatmaps, forgetting comparison, training curves
3. **Long-Context Reasoning**: Accuracy vs length, per-task comparison, scaling exponent
4. **Graph Visualization**: Graph file loader, metadata display
5. **Model Comparison**: Unified comparison table with color-coded differences

#### Data Loading
```python
_load_metrics(model_type, experiment) -> Dict
_load_results(model_type, experiment) -> Dict
# Searches results/ directory for latest JSON files
```

#### Interactive Features
- Plotly charts with zoom/pan/hover
- Sidebar model selection (BDH/Transformer toggle)
- Auto-refresh option
- Results directory configuration

---

## Data Flow

### Complete Pipeline Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CONFIG (configs/default.yaml)                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EXPERIMENT RUNNER (run_all.py)                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│  INSTRUMENTATION│         │ CONTINUAL LEARN │         │ LONG CONTEXT    │
│  (graph_extract)│         │ (cl_experiment) │         │ (lc_experiment) │
└────────┬────────┘         └────────┬────────┘         └────────┬────────┘
         │                           │                           │
         ▼                           ▼                           ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ InteractionGraph│         │ CLResults       │         │ LCResults       │
│ StructuralMetrics│        │ (forgetting,    │         │ (accuracy_by_   │
│                 │         │  transfer)      │         │  length, exp)   │
└────────┬────────┘         └────────┬────────┘         └────────┬────────┘
         │                           │                           │
         └───────────────────────────┼───────────────────────────┘
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CHECKPOINT MANAGER / EXPERIMENT TRACKER                   │
│  checkpoints/models/  checkpoints/graphs/  checkpoints/metrics/             │
│  checkpoints/results/  checkpoints/experiments/                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VISUALIZATION / DASHBOARD                            │
│  graph_view.py (static/interactive)  plots.py (publication)                 │
│  dashboard/app.py (Streamlit interactive exploration)                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Structures at Each Stage

| Stage | Input | Output | Saved To |
|-------|-------|--------|----------|
| Model Load | Config + Checkpoint | `nn.Module` | Memory |
| Instrumentation | Model + Dataloader | `InteractionGraph` + `StructuralMetrics` | `checkpoints/graphs/`, `checkpoints/metrics/` |
| Continual Learning | Model + Tasks | `ContinualLearningResults` | `checkpoints/results/` |
| Long Context | Model + Tasks | `LongContextResults` | `checkpoints/results/` |
| Full Pipeline | All above | `FullExperimentResults` | `results/full_experiment_results_*.json` |

---

## Configuration System

### YAML Structure (`configs/default.yaml`)

```yaml
model:
  bdh:
    vocab_size: 50257
    d_model: 256
    n_layers: 6
    n_heads: 4
    d_ff: 1024
    max_seq_len: 1024
    dropout: 0.1
    state_dim: 64
    hebbian_lr: 0.01
    hebbian_decay: 0.99
    device: "cuda"
    checkpoint_path: null

  transformer:
    vocab_size: 50257
    d_model: 256
    n_layers: 6
    n_heads: 4
    d_ff: 1024
    max_seq_len: 1024
    dropout: 0.1
    device: "cuda"
    checkpoint_path: null

training:
  batch_size: 32
  learning_rate: 3e-4
  weight_decay: 0.01
  max_epochs: 10
  gradient_clip: 1.0
  device: "cuda"
  num_workers: 4

instrumentation:
  graph_extraction:
    node_type: "neuron"
    edge_type: "correlation"
    correlation_threshold: 0.3
    top_k_edges: null
    sample_batches: 100
    sample_seq_len: 512
    target_layers: null
  metrics:
    compute_modularity: true
    compute_degree_distribution: true
    compute_clustering: true
    compute_path_length: true
    compute_rich_club: true
    modularity_resolution: 1.0
    community_algorithm: "louvain"

continual_learning:
  epochs_per_task: 5
  tasks:
    - name: "split_mnist_0"
      dataset: "split_mnist"
      task_id: 0
      num_classes: 2
    # ... more tasks
  replay:
    enabled: false
    buffer_size: 1000
    strategy: "random"

long_context:
  eval_batch_size: 16
  tasks:
    - name: "needle_in_haystack"
      context_lengths: [128, 256, 512, 1024, 2048]
      num_samples: 100
      needle_type: "random_token"
    # ... more tasks

paths:
  checkpoints_dir: "checkpoints/"
  results_dir: "results/"
  data_dir: "data/"
  assets_dir: "assets/"

logging:
  level: "INFO"
  log_dir: "logs/"
```

### Configuration Access
```python
from omegaconf import OmegaConf
config = OmegaConf.load("configs/default.yaml")
# Access: config.model.bdh.d_model, config.training.batch_size, etc.
```

---

## Checkpoint & Experiment Tracking

### CheckpointManager (`src/instrumentation/checkpoint_utils.py`)

#### Directory Structure
```
checkpoints/
├── models/
│   ├── bdh_epoch1_step500_2026-08-09T12-00-00.pt
│   ├── bdh_epoch1_step500_2026-08-09T12-00-00_meta.json
│   └── ...
├── graphs/
│   ├── bdh_instrumentation_2026-08-09T12-00-00.json
│   └── ...
├── metrics/
│   ├── bdh_instrumentation_2026-08-09T12-00-00.json
│   └── ...
└── results/
    ├── bdh_continual_learning_2026-08-09T12-00-00.json
    └── ...
```

#### Checkpoint Contents
```python
{
    'metadata': CheckpointMetadata,  # timestamp, config, metrics, tags
    'model_state_dict': OrderedDict,
    'optimizer_state_dict': OrderedDict,
    'scheduler_state_dict': OrderedDict,
    'epoch': int,
    'step': int,
    'loss': float
}
```

#### Key Methods
- `save_model_checkpoint()`: Full training checkpoint
- `load_model_checkpoint()`: Restore model + optimizer + scheduler
- `save_graph()` / `load_graph()`: InteractionGraph persistence
- `save_metrics()` / `load_metrics()`: StructuralMetrics persistence
- `save_experiment_results()` / `load_experiment_results()`: Experiment outputs
- `list_checkpoints()`: Query available checkpoints
- `get_latest_checkpoint()`: Resume training
- `cleanup_old_checkpoints()`: Disk space management

### ExperimentTracker

#### Experiment Index
```
checkpoints/experiments/
├── experiment_index.json  # Master index
├── exp1_results.json      # Full experiment record
└── exp2_results.json
```

#### Experiment Record
```json
{
  "id": "continual_learning_bdh_2026-08-09T12-00-00",
  "name": "continual_learning",
  "model_type": "bdh",
  "timestamp": "2026-08-09T12:00:00",
  "config": {...},
  "results": {...},
  "tags": ["bdh", "continual_learning"]
}
```

#### Query & Comparison
- `get_experiments(name, model_type, tags)`: Filter experiments
- `compare_experiments(exp_ids)`: Side-by-side metric comparison

---

## CLI Scripts

### train_small_bdh.py
```bash
python scripts/train_small_bdh.py \
    --config configs/default.yaml \
    --epochs 10 \
    --batch-size 32 \
    --lr 3e-4 \
    --device cuda \
    --output-dir checkpoints/
```
- Creates synthetic language modeling data
- Trains BDH with AdamW + cosine scheduling
- Saves checkpoints every epoch via CheckpointManager
- Outputs final model to `checkpoints/models/bdh_final.pt`

### extract_and_measure.py
```bash
python scripts/extract_and_measure.py \
    --config configs/default.yaml \
    --bdh-checkpoint checkpoints/models/bdh_final.pt \
    --transformer-checkpoint checkpoints/models/transformer_final.pt \
    --model-type both \
    --device cuda \
    --output-dir results/structure/ \
    --node-type neuron \
    --edge-type correlation \
    --correlation-threshold 0.3 \
    --sample-batches 100 \
    --sample-seq-len 512
```
- Loads models from checkpoints (or random init)
- Runs graph extraction with specified config
- Computes all structural metrics
- Saves graphs and metrics to output directory
- Prints comparison summary to console

---

## Extension Points

### Adding New Node Types
1. Add to `NodeType` enum in `graph_extractor.py`
2. Implement node creation in `_define_nodes()`
3. Implement activation extraction in `_compute_edges()`

### Adding New Edge Types
1. Add to `EdgeType` enum
2. Implement similarity computation in `_compute_edges()`
3. Add any required dependencies

### Adding New Metrics
1. Add field to `StructuralMetrics` dataclass
2. Implement computation in `MetricsComputer`
3. Add to `compute_all()` method
4. Update `to_dict()` for serialization
5. Add comparison in `compare_models()`

### Adding New Continual Learning Tasks
1. Create dataset loader function (like `load_split_mnist`)
2. Add to `dataset_loader` in `run_all.py`
3. Configure in YAML under `continual_learning.tasks`

### Adding New Long-Context Tasks
1. Add task type to `LongContextExperiment`
2. Implement `generate_<task>()` method
3. Add to `prepare_all_data()` dispatch
4. Configure in YAML under `long_context.tasks`

### Adding New Visualizations
1. Add method to `GraphVisualizer` or `MetricsPlotter`/`ExperimentPlotter`
2. Add corresponding dashboard tab in `app.py`
3. Update `visualize_comparison()` if needed

### Adding New Models
1. Create loader in `src/models/`
2. Implement `forward()` with `return_activations=True`
3. Implement `register_instrumentation_hooks()`
4. Add to `run_all.py` model loading
5. Add config section in YAML

---

## Performance Considerations

### Graph Extraction Complexity
| Node Type | Nodes | Edge Computation | Memory |
|-----------|-------|------------------|--------|
| NEURON | O(L×d) | O((L×d)²) | High |
| CHANNEL | O(L×d/64) | O((L×d/64)²) | Medium |
| LAYER | O(L) | O(L²) | Low |
| ATTENTION_HEAD | O(L×h) | O((L×h)²) | Medium |

### Recommendations
- Use `CHANNEL` or `LAYER` nodes for large models
- Use `top_k_edges` instead of threshold for sparse graphs
- Limit `sample_batches` for quick exploration
- Use `target_layers` to focus on specific depths

### Memory Optimization
- Activations aggregated over batch/seq by default
- Use `aggregate_over_batch=True`, `aggregate_over_seq=True`
- For neuron-level: consider `target_layers` subset

---

## Testing & Validation

### Unit Tests (Recommended)
```python
# Test graph extraction
def test_graph_extraction():
    model = create_bdh_model(config)
    graph = extract_interaction_graph(model, dataloader, device, "bdh")
    assert len(graph.nodes) > 0
    assert graph.adjacency_matrix.shape[0] == len(graph.nodes)

# Test metrics
def test_metrics_computation():
    metrics = compute_structural_metrics(graph.to_networkx())
    assert 0 <= metrics.sparsity <= 1
    assert metrics.modularity >= 0

# Test continual learning
def test_continual_learning():
    results = cl_exp.run(model, optimizer_fn)
    assert 0 <= results.avg_accuracy <= 1
    assert results.avg_forgetting >= 0
```

### Integration Tests
- Full pipeline run with small config
- Checkpoint save/load roundtrip
- Dashboard data loading from results

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| OOM during graph extraction | Too many nodes (NEURON type) | Use CHANNEL/LAYER, reduce sample_batches |
| Slow metric computation | Large dense adjacency | Use top_k_edges, sparse matrices |
| Dashboard shows no data | Results not in expected location | Check `results_dir` config, run experiments |
| Import errors | Missing dependencies | `pip install -r requirements.txt` |
| CUDA OOM | Batch size too large | Reduce `batch_size` in config |

### Debugging Tips
- Enable `logging.DEBUG` for detailed instrumentation logs
- Use `graph.extraction_stats` to verify data collection
- Check `results/` directory structure matches expectations
- Use `checkpoint_manager.list_checkpoints()` to verify saves

---

## Future Architecture Considerations

### Scalability
- Distributed graph extraction (model parallelism)
- Streaming metrics computation (online algorithms)
- GPU-accelerated correlation (cuBLAS/cuGraph)

### Extensibility
- Plugin system for custom metrics
- DAG-based experiment pipeline (Airflow/Prefect style)
- Model zoo integration (HuggingFace Hub)

### Reproducibility
- Git commit tracking in metadata
- Environment capture (conda/pip freeze)
- Deterministic seeding across all components

---

*This document is maintained alongside the codebase. Update when adding new components or changing architectures.*
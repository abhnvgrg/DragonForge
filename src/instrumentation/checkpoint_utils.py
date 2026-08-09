"""
Checkpoint Utilities for DragonForge

Handles saving/loading model checkpoints with instrumentation data,
experiment results, and structural metrics.
"""

import torch
import torch.nn as nn
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import json
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
from omegaconf import DictConfig, OmegaConf
import pickle

logger = logging.getLogger(__name__)


@dataclass
class CheckpointMetadata:
    """Metadata for a checkpoint."""
    timestamp: str
    model_type: str  # "bdh" or "transformer"
    model_config: Dict[str, Any]
    training_config: Dict[str, Any]
    epoch: int
    step: int
    loss: float
    metrics: Dict[str, float]
    git_commit: Optional[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class CheckpointManager:
    """
    Manages model checkpoints with instrumentation data.
    
    Supports:
    - Standard PyTorch checkpoints
    - Instrumentation graphs and metrics
    - Experiment results
    - Configuration tracking
    """
    
    def __init__(self, checkpoint_dir: Union[str, Path] = "checkpoints/"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories
        self.models_dir = self.checkpoint_dir / "models"
        self.graphs_dir = self.checkpoint_dir / "graphs"
        self.metrics_dir = self.checkpoint_dir / "metrics"
        self.results_dir = self.checkpoint_dir / "results"
        
        for d in [self.models_dir, self.graphs_dir, self.metrics_dir, self.results_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    def save_model_checkpoint(self,
                             model: nn.Module,
                             optimizer: Optional[torch.optim.Optimizer],
                             scheduler: Optional[torch.optim.lr_scheduler._LRScheduler],
                             epoch: int,
                             step: int,
                             loss: float,
                             metrics: Dict[str, float],
                             model_type: str,
                             model_config: DictConfig,
                             training_config: DictConfig,
                             name: Optional[str] = None,
                             tags: List[str] = None) -> Path:
        """
        Save a complete model checkpoint.
        
        Returns:
            Path to saved checkpoint
        """
        timestamp = datetime.now().isoformat()
        
        if name is None:
            name = f"{model_type}_epoch{epoch}_step{step}_{timestamp.replace(':', '-')}"
        
        checkpoint_path = self.models_dir / f"{name}.pt"
        
        # Prepare metadata
        metadata = CheckpointMetadata(
            timestamp=timestamp,
            model_type=model_type,
            model_config=OmegaConf.to_container(model_config, resolve=True),
            training_config=OmegaConf.to_container(training_config, resolve=True),
            epoch=epoch,
            step=step,
            loss=loss,
            metrics=metrics,
            tags=tags or [],
        )
        
        # Save checkpoint
        checkpoint = {
            'metadata': asdict(metadata),
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict() if optimizer else None,
            'scheduler_state_dict': scheduler.state_dict() if scheduler else None,
            'epoch': epoch,
            'step': step,
            'loss': loss,
        }
        
        torch.save(checkpoint, checkpoint_path)
        logger.info(f"Saved checkpoint to {checkpoint_path}")
        
        # Also save metadata as JSON for easy reading
        meta_path = self.models_dir / f"{name}_meta.json"
        with open(meta_path, 'w') as f:
            json.dump(asdict(metadata), f, indent=2, default=str)
        
        return checkpoint_path
    
    def load_model_checkpoint(self,
                             checkpoint_path: Union[str, Path],
                             model: nn.Module,
                             optimizer: Optional[torch.optim.Optimizer] = None,
                             scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None,
                             device: Optional[torch.device] = None) -> Dict[str, Any]:
        """
        Load a model checkpoint.
        
        Returns:
            Dictionary with metadata and training state
        """
        checkpoint_path = Path(checkpoint_path)
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
        
        if device is None:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        checkpoint = torch.load(checkpoint_path, map_location=device)
        
        # Load model state
        model.load_state_dict(checkpoint['model_state_dict'])
        
        # Load optimizer/scheduler if provided
        if optimizer and checkpoint.get('optimizer_state_dict'):
            optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        if scheduler and checkpoint.get('scheduler_state_dict'):
            scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        
        logger.info(f"Loaded checkpoint from {checkpoint_path}")
        logger.info(f"  Epoch: {checkpoint['epoch']}, Step: {checkpoint['step']}, Loss: {checkpoint['loss']:.4f}")
        
        return {
            'metadata': checkpoint['metadata'],
            'epoch': checkpoint['epoch'],
            'step': checkpoint['step'],
            'loss': checkpoint['loss'],
        }
    
    def save_graph(self, graph: Any, name: str, model_type: str) -> Path:
        """Save interaction graph."""
        timestamp = datetime.now().isoformat().replace(':', '-')
        filename = f"{model_type}_{name}_{timestamp}.json"
        graph_path = self.graphs_dir / filename
        
        if hasattr(graph, 'save'):
            graph.save(str(graph_path))
        else:
            # Assume it's a NetworkX graph
            import networkx as nx
            data = nx.node_link_data(graph)
            with open(graph_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Saved graph to {graph_path}")
        return graph_path
    
    def load_graph(self, graph_path: Union[str, Path]) -> Any:
        """Load interaction graph."""
        graph_path = Path(graph_path)
        with open(graph_path, 'r') as f:
            data = json.load(f)
        
        # Try to reconstruct based on format
        if 'nodes' in data and 'edges' in data:
            # Our InteractionGraph format
            from .graph_extractor import InteractionGraph, GraphConfig, NodeType, EdgeType
            config = GraphConfig(
                node_type=NodeType(data['graph_config']['node_type']),
                edge_type=EdgeType(data['graph_config']['edge_type']),
                correlation_threshold=data['graph_config']['correlation_threshold'],
                top_k_edges=data['graph_config']['top_k_edges'],
            )
            return InteractionGraph.load(str(graph_path))
        else:
            # NetworkX node-link format
            import networkx as nx
            return nx.node_link_graph(data)
    
    def save_metrics(self, metrics: Any, name: str, model_type: str) -> Path:
        """Save structural metrics."""
        timestamp = datetime.now().isoformat().replace(':', '-')
        filename = f"{model_type}_{name}_{timestamp}.json"
        metrics_path = self.metrics_dir / filename
        
        if hasattr(metrics, 'to_dict'):
            data = metrics.to_dict()
        else:
            data = metrics
        
        with open(metrics_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Saved metrics to {metrics_path}")
        return metrics_path
    
    def load_metrics(self, metrics_path: Union[str, Path]) -> Dict[str, Any]:
        """Load structural metrics."""
        metrics_path = Path(metrics_path)
        with open(metrics_path, 'r') as f:
            return json.load(f)
    
    def save_experiment_results(self,
                               results: Dict[str, Any],
                               experiment_name: str,
                               model_type: str) -> Path:
        """Save experiment results."""
        timestamp = datetime.now().isoformat().replace(':', '-')
        filename = f"{model_type}_{experiment_name}_{timestamp}.json"
        results_path = self.results_dir / filename
        
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Saved experiment results to {results_path}")
        return results_path
    
    def load_experiment_results(self, results_path: Union[str, Path]) -> Dict[str, Any]:
        """Load experiment results."""
        results_path = Path(results_path)
        with open(results_path, 'r') as f:
            return json.load(f)
    
    def list_checkpoints(self, model_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available checkpoints."""
        checkpoints = []
        
        for meta_file in self.models_dir.glob("*_meta.json"):
            with open(meta_file, 'r') as f:
                meta = json.load(f)
            
            if model_type is None or meta.get('model_type') == model_type:
                # Find corresponding .pt file
                pt_file = meta_file.with_suffix('').with_suffix('.pt')
                meta['checkpoint_path'] = str(pt_file) if pt_file.exists() else None
                meta['meta_path'] = str(meta_file)
                checkpoints.append(meta)
        
        # Sort by timestamp
        checkpoints.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return checkpoints
    
    def get_latest_checkpoint(self, model_type: str) -> Optional[Path]:
        """Get the latest checkpoint for a model type."""
        checkpoints = self.list_checkpoints(model_type)
        if checkpoints:
            return Path(checkpoints[0]['checkpoint_path'])
        return None
    
    def cleanup_old_checkpoints(self, keep: int = 5, model_type: Optional[str] = None):
        """Remove old checkpoints, keeping only the most recent N."""
        checkpoints = self.list_checkpoints(model_type)
        
        if len(checkpoints) <= keep:
            return
        
        for meta in checkpoints[keep:]:
            # Remove .pt file
            pt_path = Path(meta['checkpoint_path'])
            if pt_path.exists():
                pt_path.unlink()
                logger.info(f"Removed old checkpoint: {pt_path}")
            
            # Remove meta file
            meta_path = Path(meta['meta_path'])
            if meta_path.exists():
                meta_path.unlink()


class ExperimentTracker:
    """
    Tracks experiments across multiple runs with different configurations.
    """
    
    def __init__(self, tracker_dir: Union[str, Path] = "checkpoints/experiments/"):
        self.tracker_dir = Path(tracker_dir)
        self.tracker_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.tracker_dir / "experiment_index.json"
        self._load_index()
    
    def _load_index(self):
        """Load experiment index."""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {'experiments': []}
    
    def _save_index(self):
        """Save experiment index."""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2, default=str)
    
    def log_experiment(self,
                      experiment_name: str,
                      config: DictConfig,
                      results: Dict[str, Any],
                      model_type: str,
                      tags: List[str] = None) -> str:
        """Log an experiment run."""
        timestamp = datetime.now().isoformat()
        exp_id = f"{experiment_name}_{model_type}_{timestamp.replace(':', '-')}"
        
        exp_record = {
            'id': exp_id,
            'name': experiment_name,
            'model_type': model_type,
            'timestamp': timestamp,
            'config': OmegaConf.to_container(config, resolve=True),
            'results': results,
            'tags': tags or [],
        }
        
        self.index['experiments'].append(exp_record)
        self._save_index()
        
        # Save detailed results
        results_file = self.tracker_dir / f"{exp_id}_results.json"
        with open(results_file, 'w') as f:
            json.dump(exp_record, f, indent=2, default=str)
        
        logger.info(f"Logged experiment: {exp_id}")
        return exp_id
    
    def get_experiments(self, 
                       experiment_name: Optional[str] = None,
                       model_type: Optional[str] = None,
                       tags: List[str] = None) -> List[Dict[str, Any]]:
        """Query experiments."""
        results = self.index['experiments']
        
        if experiment_name:
            results = [e for e in results if e['name'] == experiment_name]
        if model_type:
            results = [e for e in results if e['model_type'] == model_type]
        if tags:
            results = [e for e in results if any(t in e.get('tags', []) for t in tags)]
        
        return sorted(results, key=lambda x: x['timestamp'], reverse=True)
    
    def compare_experiments(self, exp_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple experiments."""
        experiments = [e for e in self.index['experiments'] if e['id'] in exp_ids]
        
        if len(experiments) < 2:
            return {}
        
        # Compare results keys
        comparison = {'experiments': experiments}
        
        # Find common numeric result keys
        all_keys = set()
        for exp in experiments:
            for k, v in exp.get('results', {}).items():
                if isinstance(v, (int, float)):
                    all_keys.add(k)
        
        comparison['metrics_comparison'] = {}
        for key in all_keys:
            comparison['metrics_comparison'][key] = {
                exp['id']: exp['results'].get(key) for exp in experiments
            }
        
        return comparison


def create_checkpoint_manager(config: DictConfig) -> CheckpointManager:
    """Factory function to create CheckpointManager from config."""
    checkpoint_dir = config.paths.get('checkpoints_dir', 'checkpoints/')
    return CheckpointManager(checkpoint_dir)


def create_experiment_tracker(config: DictConfig) -> ExperimentTracker:
    """Factory function to create ExperimentTracker from config."""
    tracker_dir = config.paths.get('checkpoints_dir', 'checkpoints/') + "experiments/"
    return ExperimentTracker(tracker_dir)
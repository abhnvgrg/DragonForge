"""
Plotting Utilities for NeuroLens

Static plots for structural metrics, experiment results, and comparisons.
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import logging

from ..instrumentation.metrics import StructuralMetrics

logger = logging.getLogger(__name__)


@dataclass
class PlotConfig:
    """Configuration for plots."""
    style: str = "seaborn-v0_8-whitegrid"
    dpi: int = 150
    figsize: Tuple[int, int] = (10, 6)
    save_format: str = "png"  # "png", "pdf", "svg"
    color_palette: str = "viridis"
    font_size: int = 12
    title_font_size: int = 14
    label_font_size: int = 12


class MetricsPlotter:
    """
    Creates static plots for structural metrics and experiment results.
    """
    
    def __init__(self, config: Optional[PlotConfig] = None):
        self.config = config or PlotConfig()
        plt.style.use(self.config.style)
        sns.set_palette(self.config.color_palette)
    
    def plot_sparsity_comparison(self,
                                bdh_metrics: StructuralMetrics,
                                transformer_metrics: StructuralMetrics,
                                save_path: Optional[str] = None) -> plt.Figure:
        """Plot sparsity comparison between models."""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5), dpi=self.config.dpi)
        
        metrics = [
            ('Graph Sparsity', bdh_metrics.sparsity, transformer_metrics.sparsity),
            ('Activation Sparsity', bdh_metrics.activation_sparsity, transformer_metrics.activation_sparsity),
            ('Weight Sparsity', bdh_metrics.weight_sparsity, transformer_metrics.weight_sparsity),
        ]
        
        for ax, (name, bdh_val, trans_val) in zip(axes, metrics):
            bars = ax.bar(['BDH', 'Transformer'], [bdh_val, trans_val], 
                         color=['#2E86AB', '#A23B72'], alpha=0.8, edgecolor='black')
            ax.set_title(name, fontsize=self.config.title_font_size)
            ax.set_ylabel('Sparsity', fontsize=self.config.label_font_size)
            ax.set_ylim(0, 1.0)
            
            # Add value labels
            for bar, val in zip(bars, [bdh_val, trans_val]):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                       f'{val:.3f}', ha='center', va='bottom', fontsize=self.config.font_size)
        
        plt.suptitle('Sparsity Comparison', fontsize=self.config.title_font_size + 2)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
            logger.info(f"Saved sparsity comparison to {save_path}")
        
        return fig
    
    def plot_modularity_comparison(self,
                                  bdh_metrics: StructuralMetrics,
                                  transformer_metrics: StructuralMetrics,
                                  save_path: Optional[str] = None) -> plt.Figure:
        """Plot modularity and community structure comparison."""
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=self.config.dpi)
        
        # Modularity
        ax = axes[0]
        bars = ax.bar(['BDH', 'Transformer'], 
                     [bdh_metrics.modularity, transformer_metrics.modularity],
                     color=['#2E86AB', '#A23B72'], alpha=0.8, edgecolor='black')
        ax.set_title('Modularity', fontsize=self.config.title_font_size)
        ax.set_ylabel('Modularity Score', fontsize=self.config.label_font_size)
        for bar, val in zip(bars, [bdh_metrics.modularity, transformer_metrics.modularity]):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                   f'{val:.3f}', ha='center', va='bottom', fontsize=self.config.font_size)
        
        # Number of communities
        ax = axes[1]
        bars = ax.bar(['BDH', 'Transformer'],
                     [bdh_metrics.n_communities, transformer_metrics.n_communities],
                     color=['#2E86AB', '#A23B72'], alpha=0.8, edgecolor='black')
        ax.set_title('Number of Communities', fontsize=self.config.title_font_size)
        ax.set_ylabel('Count', fontsize=self.config.label_font_size)
        for bar, val in zip(bars, [bdh_metrics.n_communities, transformer_metrics.n_communities]):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                   f'{val}', ha='center', va='bottom', fontsize=self.config.font_size)
        
        plt.suptitle('Community Structure Comparison', fontsize=self.config.title_font_size + 2)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
            logger.info(f"Saved modularity comparison to {save_path}")
        
        return fig
    
    def plot_degree_distribution(self,
                                bdh_metrics: StructuralMetrics,
                                transformer_metrics: StructuralMetrics,
                                save_path: Optional[str] = None) -> plt.Figure:
        """Plot degree distributions."""
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=self.config.dpi)
        
        for ax, metrics, title in [(axes[0], bdh_metrics, 'BDH'), (axes[1], transformer_metrics, 'Transformer')]:
            deg_dist = metrics.degree_distribution
            if deg_dist:
                degrees = list(deg_dist.keys())
                counts = list(deg_dist.values())
                ax.bar(degrees, counts, alpha=0.7, color='#2E86AB' if title == 'BDH' else '#A23B72', edgecolor='black')
                ax.set_xlabel('Degree', fontsize=self.config.label_font_size)
                ax.set_ylabel('Count', fontsize=self.config.label_font_size)
                ax.set_title(f'{title} Degree Distribution', fontsize=self.config.title_font_size)
                ax.set_yscale('log')
        
        plt.suptitle('Degree Distributions', fontsize=self.config.title_font_size + 2)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
            logger.info(f"Saved degree distribution to {save_path}")
        
        return fig
    
    def plot_clustering_comparison(self,
                                  bdh_metrics: StructuralMetrics,
                                  transformer_metrics: StructuralMetrics,
                                  save_path: Optional[str] = None) -> plt.Figure:
        """Plot clustering coefficient comparison."""
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=self.config.dpi)
        
        # Average clustering
        ax = axes[0]
        bars = ax.bar(['BDH', 'Transformer'],
                     [bdh_metrics.avg_clustering, transformer_metrics.avg_clustering],
                     color=['#2E86AB', '#A23B72'], alpha=0.8, edgecolor='black')
        ax.set_title('Average Clustering Coefficient', fontsize=self.config.title_font_size)
        ax.set_ylabel('Clustering', fontsize=self.config.label_font_size)
        for bar, val in zip(bars, [bdh_metrics.avg_clustering, transformer_metrics.avg_clustering]):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                   f'{val:.3f}', ha='center', va='bottom', fontsize=self.config.font_size)
        
        # Global clustering (transitivity)
        ax = axes[1]
        bars = ax.bar(['BDH', 'Transformer'],
                     [bdh_metrics.global_clustering, transformer_metrics.global_clustering],
                     color=['#2E86AB', '#A23B72'], alpha=0.8, edgecolor='black')
        ax.set_title('Global Clustering (Transitivity)', fontsize=self.config.title_font_size)
        ax.set_ylabel('Transitivity', fontsize=self.config.label_font_size)
        for bar, val in zip(bars, [bdh_metrics.global_clustering, transformer_metrics.global_clustering]):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                   f'{val:.3f}', ha='center', va='bottom', fontsize=self.config.font_size)
        
        plt.suptitle('Clustering Comparison', fontsize=self.config.title_font_size + 2)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
            logger.info(f"Saved clustering comparison to {save_path}")
        
        return fig
    
    def plot_rich_club(self,
                      bdh_metrics: StructuralMetrics,
                      transformer_metrics: StructuralMetrics,
                      save_path: Optional[str] = None) -> plt.Figure:
        """Plot rich club coefficients."""
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=self.config.dpi)
        
        for ax, metrics, title in [(axes[0], bdh_metrics, 'BDH'), (axes[1], transformer_metrics, 'Transformer')]:
            rc = metrics.rich_club_coefficients
            rc_norm = metrics.rich_club_normalized
            
            if rc:
                degrees = sorted(rc.keys())
                coeffs = [rc[d] for d in degrees]
                ax.plot(degrees, coeffs, 'o-', label='Raw', color='#2E86AB' if title == 'BDH' else '#A23B72')
            
            if rc_norm:
                degrees = sorted(rc_norm.keys())
                coeffs = [rc_norm[d] for d in degrees]
                ax.plot(degrees, coeffs, 's--', label='Normalized', color='#F24236')
            
            ax.set_xlabel('Degree Threshold', fontsize=self.config.label_font_size)
            ax.set_ylabel('Rich Club Coefficient', fontsize=self.config.label_font_size)
            ax.set_title(f'{title} Rich Club', fontsize=self.config.title_font_size)
            ax.legend()
            ax.set_ylim(0, 1.1)
        
        plt.suptitle('Rich Club Coefficients', fontsize=self.config.title_font_size + 2)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
            logger.info(f"Saved rich club plot to {save_path}")
        
        return fig
    
    def plot_spectral_metrics(self,
                             bdh_metrics: StructuralMetrics,
                             transformer_metrics: StructuralMetrics,
                             save_path: Optional[str] = None) -> plt.Figure:
        """Plot spectral metrics comparison."""
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=self.config.dpi)
        
        metrics = [
            ('Algebraic Connectivity', bdh_metrics.algebraic_connectivity, transformer_metrics.algebraic_connectivity),
            ('Spectral Gap', bdh_metrics.spectral_gap, transformer_metrics.spectral_gap),
        ]
        
        for ax, (name, bdh_val, trans_val) in zip(axes, metrics):
            if bdh_val is not None and trans_val is not None:
                bars = ax.bar(['BDH', 'Transformer'], [bdh_val, trans_val],
                             color=['#2E86AB', '#A23B72'], alpha=0.8, edgecolor='black')
                ax.set_title(name, fontsize=self.config.title_font_size)
                ax.set_ylabel('Value', fontsize=self.config.label_font_size)
                for bar, val in zip(bars, [bdh_val, trans_val]):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                           f'{val:.4f}', ha='center', va='bottom', fontsize=self.config.font_size)
        
        plt.suptitle('Spectral Metrics Comparison', fontsize=self.config.title_font_size + 2)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
            logger.info(f"Saved spectral metrics to {save_path}")
        
        return fig
    
    def plot_all_structural_comparison(self,
                                      bdh_metrics: StructuralMetrics,
                                      transformer_metrics: StructuralMetrics,
                                      save_dir: Optional[str] = None) -> Dict[str, plt.Figure]:
        """Generate all structural comparison plots."""
        figures = {}
        
        if save_dir:
            save_dir = Path(save_dir)
            save_dir.mkdir(parents=True, exist_ok=True)
        
        # Sparsity
        path = str(save_dir / "sparsity_comparison.png") if save_dir else None
        figures['sparsity'] = self.plot_sparsity_comparison(bdh_metrics, transformer_metrics, path)
        
        # Modularity
        path = str(save_dir / "modularity_comparison.png") if save_dir else None
        figures['modularity'] = self.plot_modularity_comparison(bdh_metrics, transformer_metrics, path)
        
        # Degree distribution
        path = str(save_dir / "degree_distribution.png") if save_dir else None
        figures['degree_distribution'] = self.plot_degree_distribution(bdh_metrics, transformer_metrics, path)
        
        # Clustering
        path = str(save_dir / "clustering_comparison.png") if save_dir else None
        figures['clustering'] = self.plot_clustering_comparison(bdh_metrics, transformer_metrics, path)
        
        # Rich club
        path = str(save_dir / "rich_club.png") if save_dir else None
        figures['rich_club'] = self.plot_rich_club(bdh_metrics, transformer_metrics, path)
        
        # Spectral
        path = str(save_dir / "spectral_metrics.png") if save_dir else None
        figures['spectral'] = self.plot_spectral_metrics(bdh_metrics, transformer_metrics, path)
        
        return figures


class ExperimentPlotter:
    """
    Creates plots for experiment results (continual learning, long-context).
    """
    
    def __init__(self, config: Optional[PlotConfig] = None):
        self.config = config or PlotConfig()
        plt.style.use(self.config.style)
        sns.set_palette(self.config.color_palette)
    
    def plot_continual_learning_results(self,
                                       bdh_results: Any,
                                       transformer_results: Any,
                                       save_path: Optional[str] = None) -> plt.Figure:
        """Plot continual learning results comparison."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=self.config.dpi)
        
        # Accuracy matrix heatmap
        ax = axes[0, 0]
        self._plot_accuracy_heatmap(ax, bdh_results, 'BDH')
        
        ax = axes[0, 1]
        self._plot_accuracy_heatmap(ax, transformer_results, 'Transformer')
        
        # Forgetting comparison
        ax = axes[1, 0]
        self._plot_forgetting_comparison(ax, bdh_results, transformer_results)
        
        # Transfer comparison
        ax = axes[1, 1]
        self._plot_transfer_comparison(ax, bdh_results, transformer_results)
        
        plt.suptitle('Continual Learning Results', fontsize=self.config.title_font_size + 2)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
            logger.info(f"Saved continual learning results to {save_path}")
        
        return fig
    
    def _plot_accuracy_heatmap(self, ax, results, title):
        """Plot accuracy matrix as heatmap."""
        if not results.task_accuracies:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes)
            return
        
        tasks = list(results.task_accuracies.keys())
        n_tasks = len(tasks)
        matrix = np.zeros((n_tasks, n_tasks))
        
        for i, train_task in enumerate(tasks):
            for j, eval_task in enumerate(tasks):
                matrix[i, j] = results.task_accuracies[train_task].get(eval_task, 0)
        
        im = ax.imshow(matrix, cmap='RdYlGn', vmin=0, vmax=1, aspect='auto')
        ax.set_xticks(range(n_tasks))
        ax.set_yticks(range(n_tasks))
        ax.set_xticklabels(tasks, rotation=45, ha='right')
        ax.set_yticklabels(tasks)
        ax.set_xlabel('Eval Task')
        ax.set_ylabel('Train Task')
        ax.set_title(f'{title} Accuracy Matrix')
        plt.colorbar(im, ax=ax, label='Accuracy')
        
        # Add text annotations
        for i in range(n_tasks):
            for j in range(n_tasks):
                ax.text(j, i, f'{matrix[i, j]:.2f}', ha='center', va='center', 
                       color='white' if matrix[i, j] < 0.5 else 'black', fontsize=10)
    
    def _plot_forgetting_comparison(self, ax, bdh_results, transformer_results):
        """Plot forgetting comparison."""
        tasks = list(set(bdh_results.forgetting.keys()) | set(transformer_results.forgetting.keys()))
        x = np.arange(len(tasks))
        width = 0.35
        
        bdh_vals = [bdh_results.forgetting.get(t, 0) for t in tasks]
        trans_vals = [transformer_results.forgetting.get(t, 0) for t in tasks]
        
        ax.bar(x - width/2, bdh_vals, width, label='BDH', color='#2E86AB', alpha=0.8)
        ax.bar(x + width/2, trans_vals, width, label='Transformer', color='#A23B72', alpha=0.8)
        
        ax.set_xlabel('Task')
        ax.set_ylabel('Forgetting')
        ax.set_title('Catastrophic Forgetting')
        ax.set_xticks(x)
        ax.set_xticklabels(tasks, rotation=45, ha='right')
        ax.legend()
    
    def _plot_transfer_comparison(self, ax, bdh_results, transformer_results):
        """Plot forward/backward transfer comparison."""
        metrics = ['Forward Transfer', 'Backward Transfer']
        bdh_vals = [bdh_results.avg_forward_transfer, bdh_results.avg_backward_transfer]
        trans_vals = [transformer_results.avg_forward_transfer, transformer_results.avg_backward_transfer]
        
        x = np.arange(len(metrics))
        width = 0.35
        
        ax.bar(x - width/2, bdh_vals, width, label='BDH', color='#2E86AB', alpha=0.8)
        ax.bar(x + width/2, trans_vals, width, label='Transformer', color='#A23B72', alpha=0.8)
        
        ax.set_ylabel('Transfer Score')
        ax.set_title('Forward/Backward Transfer')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics)
        ax.legend()
        ax.axhline(y=0, color='black', linewidth=0.5)
    
    def plot_long_context_results(self,
                                 bdh_results: Any,
                                 transformer_results: Any,
                                 save_path: Optional[str] = None) -> plt.Figure:
        """Plot long-context reasoning results."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=self.config.dpi)
        
        # Accuracy by context length
        ax = axes[0, 0]
        self._plot_accuracy_by_length(ax, bdh_results, transformer_results)
        
        # Per-task accuracy
        ax = axes[0, 1]
        self._plot_per_task_accuracy(ax, bdh_results, transformer_results)
        
        # Scaling exponent
        ax = axes[1, 0]
        self._plot_scaling_exponent(ax, bdh_results, transformer_results)
        
        # Summary bar chart
        ax = axes[1, 1]
        self._plot_avg_accuracy_summary(ax, bdh_results, transformer_results)
        
        plt.suptitle('Long-Context Reasoning Results', fontsize=self.config.title_font_size + 2)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
            logger.info(f"Saved long-context results to {save_path}")
        
        return fig
    
    def _plot_accuracy_by_length(self, ax, bdh_results, transformer_results):
        """Plot accuracy vs context length."""
        for results, label, color in [(bdh_results, 'BDH', '#2E86AB'), (transformer_results, 'Transformer', '#A23B72')]:
            lengths = sorted(results.accuracy_by_length.keys())
            accs = [results.accuracy_by_length[l] for l in lengths]
            ax.plot(lengths, accs, 'o-', label=label, color=color, linewidth=2, markersize=8)
        
        ax.set_xlabel('Context Length')
        ax.set_ylabel('Accuracy')
        ax.set_title('Accuracy vs Context Length')
        ax.set_xscale('log', base=2)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_per_task_accuracy(self, ax, bdh_results, transformer_results):
        """Plot per-task accuracy comparison."""
        all_tasks = set(bdh_results.accuracies.keys()) | set(transformer_results.accuracies.keys())
        tasks = sorted(all_tasks)
        
        x = np.arange(len(tasks))
        width = 0.35
        
        for i, task in enumerate(tasks):
            bdh_accs = bdh_results.accuracies.get(task, {})
            trans_accs = transformer_results.accuracies.get(task, {})
            
            bdh_avg = np.mean(list(bdh_accs.values())) if bdh_accs else 0
            trans_avg = np.mean(list(trans_accs.values())) if trans_accs else 0
            
            ax.bar(i - width/2, bdh_avg, width, color='#2E86AB', alpha=0.8, label='BDH' if i == 0 else '')
            ax.bar(i + width/2, trans_avg, width, color='#A23B72', alpha=0.8, label='Transformer' if i == 0 else '')
        
        ax.set_xlabel('Task')
        ax.set_ylabel('Average Accuracy')
        ax.set_title('Per-Task Average Accuracy')
        ax.set_xticks(x)
        ax.set_xticklabels(tasks, rotation=45, ha='right')
        ax.legend()
    
    def _plot_scaling_exponent(self, ax, bdh_results, transformer_results):
        """Plot length scaling exponent."""
        labels = ['BDH', 'Transformer']
        exponents = [bdh_results.length_scaling_exponent, transformer_results.length_scaling_exponent]
        colors = ['#2E86AB', '#A23B72']
        
        bars = ax.bar(labels, [e if e is not None else 0 for e in exponents], color=colors, alpha=0.8)
        
        for bar, exp in zip(bars, exponents):
            if exp is not None:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                       f'{exp:.3f}', ha='center', va='bottom', fontsize=self.config.font_size)
            else:
                ax.text(bar.get_x() + bar.get_width()/2, 0.01,
                       'N/A', ha='center', va='bottom', fontsize=self.config.font_size)
        
        ax.set_ylabel('Scaling Exponent')
        ax.set_title('Length Scaling Exponent (log-log slope)')
        ax.axhline(y=0, color='black', linewidth=0.5)
    
    def _plot_avg_accuracy_summary(self, ax, bdh_results, transformer_results):
        """Plot average accuracy summary."""
        labels = ['BDH', 'Transformer']
        accs = [bdh_results.avg_accuracy, transformer_results.avg_accuracy]
        colors = ['#2E86AB', '#A23B72']
        
        bars = ax.bar(labels, accs, color=colors, alpha=0.8, edgecolor='black')
        
        for bar, acc in zip(bars, accs):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                   f'{acc:.3f}', ha='center', va='bottom', fontsize=self.config.font_size + 2)
        
        ax.set_ylabel('Average Accuracy')
        ax.set_title('Overall Average Accuracy')
        ax.set_ylim(0, 1.1)
    
    def plot_training_curves(self,
                            bdh_results: Any,
                            transformer_results: Any,
                            save_path: Optional[str] = None) -> plt.Figure:
        """Plot training curves for continual learning."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=self.config.dpi)
        
        for ax, results, title in [(axes[0], bdh_results, 'BDH'), (axes[1], transformer_results, 'Transformer')]:
            curves = results.training_curves
            for task_name, curve in curves.items():
                ax.plot(range(1, len(curve) + 1), curve, 'o-', label=task_name, linewidth=2, markersize=6)
            
            ax.set_xlabel('Epoch')
            ax.set_ylabel('Validation Accuracy')
            ax.set_title(f'{title} Training Curves')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.suptitle('Continual Learning Training Curves', fontsize=self.config.title_font_size + 2)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
            logger.info(f"Saved training curves to {save_path}")
        
        return fig


def create_metrics_plotter(config: Optional[Dict] = None) -> MetricsPlotter:
    """Factory function to create MetricsPlotter."""
    if config:
        plot_config = PlotConfig(**config)
    else:
        plot_config = PlotConfig()
    return MetricsPlotter(plot_config)


def create_experiment_plotter(config: Optional[Dict] = None) -> ExperimentPlotter:
    """Factory function to create ExperimentPlotter."""
    if config:
        plot_config = PlotConfig(**config)
    else:
        plot_config = PlotConfig()
    return ExperimentPlotter(plot_config)
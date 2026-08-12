"""
Structural Metrics for Neural Network Interaction Graphs

Computes sparsity, modularity, degree distribution, clustering,
and other graph-theoretic measures for BDH and Transformer models.
"""

import numpy as np
import networkx as nx
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from scipy import stats
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
import logging
from collections import Counter
import community as community_louvain  # python-louvain

logger = logging.getLogger(__name__)


@dataclass
class StructuralMetrics:
    """Container for all structural metrics."""
    # Sparsity measures
    sparsity: float = 0.0
    activation_sparsity: float = 0.0
    weight_sparsity: float = 0.0
    
    # Modularity / Community structure
    modularity: float = 0.0
    n_communities: int = 0
    community_sizes: List[int] = field(default_factory=list)
    community_assignments: Dict[int, int] = field(default_factory=dict)
    
    # Degree distribution
    degree_distribution: Dict[int, int] = field(default_factory=dict)
    avg_degree: float = 0.0
    max_degree: int = 0
    degree_assortativity: float = 0.0
    power_law_exponent: Optional[float] = None
    power_law_p_value: Optional[float] = None
    
    # Clustering
    avg_clustering: float = 0.0
    global_clustering: float = 0.0
    clustering_distribution: Dict[float, int] = field(default_factory=dict)
    
    # Path lengths
    avg_path_length: Optional[float] = None
    diameter: Optional[int] = None
    radius: Optional[int] = None
    
    # Rich club
    rich_club_coefficients: Dict[int, float] = field(default_factory=dict)
    rich_club_normalized: Dict[int, float] = field(default_factory=dict)
    
    # Small-world
    small_world_sigma: Optional[float] = None
    
    # Spectral
    spectral_gap: Optional[float] = None
    algebraic_connectivity: Optional[float] = None
    eigenvector_centrality: Dict[int, float] = field(default_factory=dict)
    
    # Layer-wise (for multi-layer graphs)
    layer_metrics: Dict[str, Dict] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'sparsity': self.sparsity,
            'activation_sparsity': self.activation_sparsity,
            'weight_sparsity': self.weight_sparsity,
            'modularity': self.modularity,
            'n_communities': self.n_communities,
            'community_sizes': self.community_sizes,
            'community_assignments': self.community_assignments,
            'degree_distribution': self.degree_distribution,
            'avg_degree': self.avg_degree,
            'max_degree': self.max_degree,
            'degree_assortativity': self.degree_assortativity,
            'power_law_exponent': self.power_law_exponent,
            'power_law_p_value': self.power_law_p_value,
            'avg_clustering': self.avg_clustering,
            'global_clustering': self.global_clustering,
            'clustering_distribution': {str(k): v for k, v in self.clustering_distribution.items()},
            'avg_path_length': self.avg_path_length,
            'diameter': self.diameter,
            'radius': self.radius,
            'rich_club_coefficients': {str(k): v for k, v in self.rich_club_coefficients.items()},
            'rich_club_normalized': {str(k): v for k, v in self.rich_club_normalized.items()},
            'small_world_sigma': self.small_world_sigma,
            'spectral_gap': self.spectral_gap,
            'algebraic_connectivity': self.algebraic_connectivity,
            'eigenvector_centrality': self.eigenvector_centrality,
            'layer_metrics': self.layer_metrics,
        }


class MetricsComputer:
    """
    Computes structural metrics from interaction graphs.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.compute_modularity = self.config.get('compute_modularity', True)
        self.compute_degree_distribution = self.config.get('compute_degree_distribution', True)
        self.compute_clustering = self.config.get('compute_clustering', True)
        self.compute_path_length = self.config.get('compute_path_length', True)
        self.compute_rich_club = self.config.get('compute_rich_club', True)
        self.modularity_resolution = self.config.get('modularity_resolution', 1.0)
        self.community_algorithm = self.config.get('community_algorithm', 'louvain')
        
    def compute_all(self, 
                   graph: nx.Graph,
                   adjacency_matrix: Optional[np.ndarray] = None,
                   activations: Optional[Dict[str, np.ndarray]] = None,
                   model_weights: Optional[Dict[str, torch.Tensor]] = None) -> StructuralMetrics:
        """
        Compute all structural metrics for a graph.
        
        Args:
            graph: NetworkX graph
            adjacency_matrix: Dense adjacency matrix (optional)
            activations: Dict of layer activations for activation sparsity
            model_weights: Dict of model weights for weight sparsity
            
        Returns:
            StructuralMetrics object with all computed metrics
        """
        metrics = StructuralMetrics()
        
        if graph.number_of_nodes() == 0:
            logger.warning("Empty graph, returning zero metrics")
            return metrics
        
        # Convert to adjacency matrix if not provided
        if adjacency_matrix is None:
            adjacency_matrix = nx.to_numpy_array(graph, weight='weight')
        
        # Sparsity metrics
        metrics.sparsity = self._compute_graph_sparsity(adjacency_matrix)
        if activations is not None:
            metrics.activation_sparsity = self._compute_activation_sparsity(activations)
        if model_weights is not None:
            metrics.weight_sparsity = self._compute_weight_sparsity(model_weights)
        
        # Modularity
        if self.compute_modularity:
            self._compute_modularity_metrics(graph, metrics)
        
        # Degree distribution
        if self.compute_degree_distribution:
            self._compute_degree_metrics(graph, metrics)
        
        # Clustering
        if self.compute_clustering:
            self._compute_clustering_metrics(graph, metrics)
        
        # Path lengths
        if self.compute_path_length:
            self._compute_path_metrics(graph, metrics)
        
        # Rich club
        if self.compute_rich_club:
            self._compute_rich_club_metrics(graph, metrics)
        
        # Spectral metrics
        self._compute_spectral_metrics(adjacency_matrix, metrics)
        
        # Small-world
        self._compute_small_world_metrics(graph, metrics)
        
        return metrics
    
    def _compute_graph_sparsity(self, adj: np.ndarray) -> float:
        """Compute graph sparsity (fraction of zero edges)."""
        n = adj.shape[0]
        if n <= 1:
            return 1.0
        total_possible = n * (n - 1) / 2
        actual_edges = np.count_nonzero(np.triu(adj, k=1))
        return 1.0 - (actual_edges / total_possible)
    
    def _compute_activation_sparsity(self, activations: Dict[str, np.ndarray]) -> float:
        """Compute average activation sparsity across layers."""
        sparsities = []
        for layer_name, act in activations.items():
            # act shape: [batch, seq, features] or [batch, features]
            flat = act.flatten()
            zero_frac = np.mean(flat == 0)
            sparsities.append(zero_frac)
        return np.mean(sparsities) if sparsities else 0.0
    
    def _compute_weight_sparsity(self, weights: Dict[str, torch.Tensor]) -> float:
        """Compute weight sparsity (fraction of near-zero weights)."""
        sparsities = []
        for name, w in weights.items():
            if w.dim() >= 2:  # Only weight matrices
                flat = w.detach().cpu().numpy().flatten()
                zero_frac = np.mean(np.abs(flat) < 1e-6)
                sparsities.append(zero_frac)
        return np.mean(sparsities) if sparsities else 0.0
    
    def _compute_modularity_metrics(self, graph: nx.Graph, metrics: StructuralMetrics):
        """Compute modularity and community structure."""
        try:
            if self.community_algorithm == 'louvain':
                # Use python-louvain
                partition = community_louvain.best_partition(
                    graph, 
                    weight='weight',
                    resolution=self.modularity_resolution,
                    random_state=42
                )
            elif self.community_algorithm == 'greedy':
                # NetworkX greedy modularity
                communities = nx.algorithms.community.greedy_modularity_communities(
                    graph, weight='weight', resolution=self.modularity_resolution
                )
                partition = {}
                for i, comm in enumerate(communities):
                    for node in comm:
                        partition[node] = i
            else:
                # Label propagation
                communities = nx.algorithms.community.label_propagation_communities(graph)
                partition = {}
                for i, comm in enumerate(communities):
                    for node in comm:
                        partition[node] = i
            
            # Compute modularity
            metrics.modularity = community_louvain.modularity(partition, graph, weight='weight')
            
            # Community stats
            comm_counts = Counter(partition.values())
            metrics.n_communities = len(comm_counts)
            metrics.community_sizes = list(comm_counts.values())
            metrics.community_assignments = {int(k): int(v) for k, v in partition.items()}
            
        except Exception as e:
            logger.warning(f"Modularity computation failed: {e}")
            metrics.modularity = 0.0
            metrics.n_communities = 0
    
    def _compute_degree_metrics(self, graph: nx.Graph, metrics: StructuralMetrics):
        """Compute degree distribution and related metrics."""
        degrees = [d for _, d in graph.degree(weight='weight')]
        
        if not degrees:
            return
            
        metrics.avg_degree = np.mean(degrees)
        metrics.max_degree = max(degrees)
        
        # Degree distribution (histogram)
        max_deg = max(degrees)
        hist, bins = np.histogram(degrees, bins=min(50, max_deg+1), range=(0, max_deg+1))
        metrics.degree_distribution = {int(bins[i]): int(hist[i]) for i in range(len(hist)) if hist[i] > 0}
        
        # Degree assortativity
        try:
            metrics.degree_assortativity = nx.degree_assortativity_coefficient(graph, weight='weight')
        except:
            metrics.degree_assortativity = 0.0
        
        # Power law fit
        try:
            metrics.power_law_exponent, metrics.power_law_p_value = self._fit_power_law(degrees)
        except:
            metrics.power_law_exponent = None
            metrics.power_law_p_value = None
    
    def _fit_power_law(self, degrees: List[float]) -> Tuple[Optional[float], Optional[float]]:
        """Fit power law to degree distribution."""
        # Filter positive degrees
        deg_array = np.array([d for d in degrees if d > 0])
        if len(deg_array) < 10:
            return None, None
        
        # Use maximum likelihood estimation for power law exponent
        # p(k) ~ k^(-alpha)
        # alpha = 1 + n / sum(log(k/k_min))
        k_min = deg_array.min()
        if k_min <= 0:
            return None, None
            
        n = len(deg_array)
        alpha = 1 + n / np.sum(np.log(deg_array / k_min))
        
        # Kolmogorov-Smirnov test for goodness of fit
        # Simplified: compare empirical CDF to theoretical
        from scipy import stats as scipy_stats
        empirical_cdf = np.arange(1, n+1) / n
        theoretical_cdf = 1 - (deg_array / k_min) ** (-(alpha - 1))
        ks_stat = np.max(np.abs(empirical_cdf - theoretical_cdf))
        
        # Approximate p-value (very rough)
        p_value = np.exp(-2 * n * ks_stat**2) if n > 0 else 1.0
        
        return float(alpha), float(p_value)
    
    def _compute_clustering_metrics(self, graph: nx.Graph, metrics: StructuralMetrics):
        """Compute clustering coefficients."""
        try:
            # Average clustering coefficient
            metrics.avg_clustering = nx.average_clustering(graph, weight='weight')
            
            # Global clustering (transitivity)
            metrics.global_clustering = nx.transitivity(graph)
            
            # Clustering distribution
            clustering = nx.clustering(graph, weight='weight')
            hist, bins = np.histogram(list(clustering.values()), bins=20, range=(0, 1))
            metrics.clustering_distribution = {float(bins[i]): int(hist[i]) for i in range(len(hist)) if hist[i] > 0}
            
        except Exception as e:
            logger.warning(f"Clustering computation failed: {e}")
            metrics.avg_clustering = 0.0
            metrics.global_clustering = 0.0
    
    def _compute_path_metrics(self, graph: nx.Graph, metrics: StructuralMetrics):
        """Compute path length metrics."""
        try:
            # Check if graph is connected
            if nx.is_connected(graph):
                metrics.avg_path_length = nx.average_shortest_path_length(graph, weight='weight')
                metrics.diameter = nx.diameter(graph, weight='weight')
                metrics.radius = nx.radius(graph, weight='weight')
            else:
                # For disconnected graphs, compute on largest component
                largest_cc = max(nx.connected_components(graph), key=len)
                subgraph = graph.subgraph(largest_cc)
                if subgraph.number_of_nodes() > 1:
                    metrics.avg_path_length = nx.average_shortest_path_length(subgraph, weight='weight')
                    metrics.diameter = nx.diameter(subgraph, weight='weight')
                    metrics.radius = nx.radius(subgraph, weight='weight')
                else:
                    metrics.avg_path_length = None
                    metrics.diameter = None
                    metrics.radius = None
        except Exception as e:
            logger.warning(f"Path length computation failed: {e}")
            metrics.avg_path_length = None
            metrics.diameter = None
            metrics.radius = None
    
    def _compute_rich_club_metrics(self, graph: nx.Graph, metrics: StructuralMetrics):
        """Compute rich club coefficients."""
        try:
            # NetworkX rich club coefficient
            rc = nx.rich_club_coefficient(graph, normalized=False, weight='weight')
            metrics.rich_club_coefficients = {int(k): float(v) for k, v in rc.items()}
            
            # Normalized rich club
            rc_norm = nx.rich_club_coefficient(graph, normalized=True, weight='weight', Q=100)
            metrics.rich_club_normalized = {int(k): float(v) for k, v in rc_norm.items()}
        except Exception as e:
            logger.warning(f"Rich club computation failed: {e}")
            metrics.rich_club_coefficients = {}
            metrics.rich_club_normalized = {}
    
    def _compute_spectral_metrics(self, adj: np.ndarray, metrics: StructuralMetrics):
        """Compute spectral metrics from adjacency matrix."""
        try:
            # Laplacian matrix
            degree = np.sum(adj, axis=1)
            laplacian = np.diag(degree) - adj
            
            # Eigenvalues of Laplacian
            eigenvals = np.linalg.eigvalsh(laplacian)
            eigenvals = np.sort(eigenvals)
            
            # Algebraic connectivity (Fiedler value)
            if len(eigenvals) > 1:
                metrics.algebraic_connectivity = float(eigenvals[1])
            
            # Spectral gap (difference between first two eigenvalues of normalized Laplacian)
            # Normalized Laplacian: I - D^(-1/2) A D^(-1/2)
            with np.errstate(divide='ignore', invalid='ignore'):
                d_inv_sqrt = 1.0 / np.sqrt(degree)
                d_inv_sqrt[degree == 0] = 0
                D_inv_sqrt = np.diag(d_inv_sqrt)
                norm_laplacian = np.eye(adj.shape[0]) - D_inv_sqrt @ adj @ D_inv_sqrt
                norm_eigenvals = np.linalg.eigvalsh(norm_laplacian)
                norm_eigenvals = np.sort(norm_eigenvals)
                if len(norm_eigenvals) > 1:
                    metrics.spectral_gap = float(norm_eigenvals[1] - norm_eigenvals[0])
            
            # Eigenvector centrality (using adjacency matrix)
            try:
                eigenvals, eigenvecs = np.linalg.eigh(adj)
                # Principal eigenvector
                principal_idx = np.argmax(eigenvals)
                centrality = np.abs(eigenvecs[:, principal_idx])
                centrality = centrality / np.sum(centrality) if np.sum(centrality) > 0 else centrality
                metrics.eigenvector_centrality = {i: float(c) for i, c in enumerate(centrality)}
            except:
                pass
                
        except Exception as e:
            logger.warning(f"Spectral metrics computation failed: {e}")
    
    def _compute_small_world_metrics(self, graph: nx.Graph, metrics: StructuralMetrics):
        """Compute small-world sigma coefficient."""
        try:
            if metrics.avg_clustering is not None and metrics.avg_path_length is not None:
                # Generate equivalent random graph
                n = graph.number_of_nodes()
                m = graph.number_of_edges()
                
                if n > 0 and m > 0:
                    # Erdos-Renyi random graph
                    p = 2 * m / (n * (n - 1)) if n > 1 else 0
                    if p > 0 and p < 1:
                        # Generate a few random graphs and average
                        rand_clustering = []
                        rand_path_length = []
                        for _ in range(5):
                            try:
                                rand_g = nx.erdos_renyi_graph(n, p)
                                if nx.is_connected(rand_g):
                                    rand_clustering.append(nx.average_clustering(rand_g))
                                    rand_path_length.append(nx.average_shortest_path_length(rand_g))
                            except:
                                pass
                        
                        if rand_clustering and rand_path_length:
                            c_rand = np.mean(rand_clustering)
                            l_rand = np.mean(rand_path_length)
                            if c_rand > 0 and l_rand > 0:
                                metrics.small_world_sigma = (metrics.avg_clustering / c_rand) / (metrics.avg_path_length / l_rand)
        except Exception as e:
            logger.warning(f"Small-world computation failed: {e}")
    
    def compute_layer_wise(self, 
                          layer_graphs: Dict[str, nx.Graph],
                          layer_adjacencies: Dict[str, np.ndarray]) -> Dict[str, StructuralMetrics]:
        """Compute metrics for each layer separately."""
        layer_metrics = {}
        for layer_name, graph in layer_graphs.items():
            adj = layer_adjacencies.get(layer_name)
            layer_metrics[layer_name] = self.compute_all(graph, adj)
        return layer_metrics


def compute_structural_metrics(graph: nx.Graph,
                              config: Optional[Dict] = None,
                              **kwargs) -> StructuralMetrics:
    """Convenience function to compute all metrics."""
    computer = MetricsComputer(config)
    return computer.compute_all(graph, **kwargs)


def compare_models(bdh_metrics: StructuralMetrics,
                  transformer_metrics: StructuralMetrics) -> Dict[str, Any]:
    """Compare metrics between BDH and Transformer models."""
    comparison = {}
    
    # Sparsity comparison
    comparison['sparsity'] = {
        'bdh': bdh_metrics.sparsity,
        'transformer': transformer_metrics.sparsity,
        'ratio': bdh_metrics.sparsity / transformer_metrics.sparsity if transformer_metrics.sparsity > 0 else None,
        'difference': bdh_metrics.sparsity - transformer_metrics.sparsity,
    }
    
    comparison['activation_sparsity'] = {
        'bdh': bdh_metrics.activation_sparsity,
        'transformer': transformer_metrics.activation_sparsity,
        'ratio': bdh_metrics.activation_sparsity / transformer_metrics.activation_sparsity if transformer_metrics.activation_sparsity > 0 else None,
    }
    
    # Modularity comparison
    comparison['modularity'] = {
        'bdh': bdh_metrics.modularity,
        'transformer': transformer_metrics.modularity,
        'difference': bdh_metrics.modularity - transformer_metrics.modularity,
    }
    
    comparison['n_communities'] = {
        'bdh': bdh_metrics.n_communities,
        'transformer': transformer_metrics.n_communities,
    }
    
    # Degree comparison
    comparison['avg_degree'] = {
        'bdh': bdh_metrics.avg_degree,
        'transformer': transformer_metrics.avg_degree,
    }
    
    comparison['degree_assortativity'] = {
        'bdh': bdh_metrics.degree_assortativity,
        'transformer': transformer_metrics.degree_assortativity,
    }
    
    comparison['power_law_exponent'] = {
        'bdh': bdh_metrics.power_law_exponent,
        'transformer': transformer_metrics.power_law_exponent,
    }
    
    # Clustering comparison
    comparison['avg_clustering'] = {
        'bdh': bdh_metrics.avg_clustering,
        'transformer': transformer_metrics.avg_clustering,
    }
    
    comparison['global_clustering'] = {
        'bdh': bdh_metrics.global_clustering,
        'transformer': transformer_metrics.global_clustering,
    }
    
    # Path length comparison
    comparison['avg_path_length'] = {
        'bdh': bdh_metrics.avg_path_length,
        'transformer': transformer_metrics.avg_path_length,
    }
    
    comparison['small_world_sigma'] = {
        'bdh': bdh_metrics.small_world_sigma,
        'transformer': transformer_metrics.small_world_sigma,
    }
    
    # Spectral comparison
    comparison['algebraic_connectivity'] = {
        'bdh': bdh_metrics.algebraic_connectivity,
        'transformer': transformer_metrics.algebraic_connectivity,
    }
    
    comparison['spectral_gap'] = {
        'bdh': bdh_metrics.spectral_gap,
        'transformer': transformer_metrics.spectral_gap,
    }
    
    return comparison


# Import torch for weight sparsity
import torch
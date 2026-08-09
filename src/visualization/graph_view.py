"""
Graph Visualization for Neural Network Interaction Graphs

Interactive and static visualization of structural graphs extracted from models.
"""

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import logging
import json

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from ..instrumentation.graph_extractor import InteractionGraph, NodeType

logger = logging.getLogger(__name__)


@dataclass
class VisualizationConfig:
    """Configuration for graph visualization."""
    layout: str = "force_directed"  # "force_directed", "circular", "hierarchical", "kamada_kawai"
    node_size_factor: float = 10.0
    edge_width_factor: float = 2.0
    max_nodes_display: int = 500
    color_by: str = "community"  # "community", "degree", "layer", "activation", "model_type"
    colormap: str = "viridis"
    figsize: Tuple[int, int] = (12, 10)
    dpi: int = 150
    show_labels: bool = False
    edge_alpha: float = 0.5
    node_alpha: float = 0.8


class GraphVisualizer:
    """
    Visualizes interaction graphs from neural network models.
    Supports both static (matplotlib) and interactive (plotly) visualizations.
    """
    
    def __init__(self, config: Optional[VisualizationConfig] = None):
        self.config = config or VisualizationConfig()
    
    def visualize(self, 
                 graph: InteractionGraph,
                 save_path: Optional[str] = None,
                 interactive: bool = False) -> Any:
        """
        Visualize an interaction graph.
        
        Args:
            graph: InteractionGraph to visualize
            save_path: Optional path to save figure
            interactive: Whether to create interactive plotly visualization
            
        Returns:
            Figure object (matplotlib or plotly)
        """
        # Subsample if too many nodes
        G = graph.to_networkx()
        if G.number_of_nodes() > self.config.max_nodes_display:
            G = self._subsample_graph(G)
            logger.info(f"Subsampled graph to {G.number_of_nodes()} nodes for visualization")
        
        if interactive and PLOTLY_AVAILABLE:
            return self._visualize_plotly(G, graph, save_path)
        else:
            return self._visualize_matplotlib(G, graph, save_path)
    
    def _subsample_graph(self, G: nx.Graph) -> nx.Graph:
        """Subsample graph to max_nodes_display nodes."""
        # Keep highest degree nodes
        degrees = dict(G.degree(weight='weight'))
        top_nodes = sorted(degrees.keys(), key=lambda x: degrees[x], reverse=True)[:self.config.max_nodes_display]
        return G.subgraph(top_nodes).copy()
    
    def _get_node_colors(self, G: nx.Graph, graph: InteractionGraph) -> Tuple[np.ndarray, str]:
        """Get node colors based on config."""
        color_by = self.config.color_by
        
        if color_by == "community":
            # Use community assignments from metadata
            communities = {}
            for node in G.nodes():
                meta = graph.node_metadata.get(node, {})
                comm = meta.get('community', 0)
                communities[node] = comm
            
            if communities:
                unique_comms = list(set(communities.values()))
                comm_to_color = {c: i for i, c in enumerate(unique_comms)}
                colors = np.array([comm_to_color[communities[n]] for n in G.nodes()])
                return colors, f"Community ({len(unique_comms)} communities)"
        
        elif color_by == "degree":
            degrees = dict(G.degree(weight='weight'))
            colors = np.array([degrees[n] for n in G.nodes()])
            return colors, "Degree"
        
        elif color_by == "layer":
            layers = {}
            for node in G.nodes():
                meta = graph.node_metadata.get(node, {})
                layer_name = meta.get('layer', 'unknown')
                # Extract layer index
                try:
                    layer_idx = int(layer_name.split('_')[-1])
                except:
                    layer_idx = 0
                layers[node] = layer_idx
            
            colors = np.array([layers[n] for n in G.nodes()])
            return colors, "Layer"
        
        elif color_by == "model_type":
            model_types = {}
            for node in G.nodes():
                meta = graph.node_metadata.get(node, {})
                mt = meta.get('model_type', 'unknown')
                model_types[node] = 0 if mt == 'bdh' else 1
            
            colors = np.array([model_types[n] for n in G.nodes()])
            return colors, "Model Type"
        
        # Default: uniform color
        colors = np.ones(G.number_of_nodes())
        return colors, "Uniform"
    
    def _get_node_sizes(self, G: nx.Graph) -> np.ndarray:
        """Get node sizes based on degree."""
        degrees = dict(G.degree(weight='weight'))
        max_deg = max(degrees.values()) if degrees else 1
        sizes = np.array([self.config.node_size_factor * (degrees[n] / max_deg + 0.1) for n in G.nodes()])
        return sizes
    
    def _get_edge_widths(self, G: nx.Graph) -> np.ndarray:
        """Get edge widths based on weight."""
        widths = []
        for u, v, data in G.edges(data=True):
            w = data.get('weight', 1.0)
            widths.append(self.config.edge_width_factor * max(abs(w), 0.1))
        return np.array(widths)
    
    def _get_layout(self, G: nx.Graph) -> Dict:
        """Compute node positions based on layout algorithm."""
        layout = self.config.layout
        
        if layout == "force_directed":
            return nx.spring_layout(G, k=1/np.sqrt(G.number_of_nodes()), iterations=50, seed=42)
        elif layout == "circular":
            return nx.circular_layout(G)
        elif layout == "kamada_kawai":
            return nx.kamada_kawai_layout(G)
        elif layout == "hierarchical":
            # Try to use layer info for hierarchical layout
            try:
                return nx.nx_agraph.graphviz_layout(G, prog='dot')
            except:
                return nx.spring_layout(G, seed=42)
        else:
            return nx.spring_layout(G, seed=42)
    
    def _visualize_matplotlib(self, G: nx.Graph, graph: InteractionGraph, save_path: Optional[str]) -> plt.Figure:
        """Create matplotlib visualization."""
        fig, ax = plt.subplots(figsize=self.config.figsize, dpi=self.config.dpi)
        
        # Get layout
        pos = self._get_layout(G)
        
        # Get colors, sizes, widths
        node_colors, color_label = self._get_node_colors(G, graph)
        node_sizes = self._get_node_sizes(G)
        edge_widths = self._get_edge_widths(G)
        
        # Draw edges
        nx.draw_networkx_edges(
            G, pos,
            width=edge_widths,
            alpha=self.config.edge_alpha,
            edge_color='gray',
            ax=ax
        )
        
        # Draw nodes
        scatter = nx.draw_networkx_nodes(
            G, pos,
            node_size=node_sizes,
            node_color=node_colors,
            cmap=plt.get_cmap(self.config.colormap),
            alpha=self.config.node_alpha,
            ax=ax
        )
        
        # Add colorbar
        if len(set(node_colors)) > 1:
            plt.colorbar(scatter, ax=ax, label=color_label, shrink=0.8)
        
        # Labels
        if self.config.show_labels and G.number_of_nodes() <= 50:
            nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)
        
        # Title
        model_type = graph.model_type.upper()
        n_nodes = G.number_of_nodes()
        n_edges = G.number_of_edges()
        ax.set_title(f"{model_type} Interaction Graph\n{n_nodes} nodes, {n_edges} edges", fontsize=14)
        
        ax.axis('off')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
            logger.info(f"Saved visualization to {save_path}")
        
        return fig
    
    def _visualize_plotly(self, G: nx.Graph, graph: InteractionGraph, save_path: Optional[str]) -> 'go.Figure':
        """Create interactive plotly visualization."""
        if not PLOTLY_AVAILABLE:
            logger.warning("Plotly not available, falling back to matplotlib")
            return self._visualize_matplotlib(G, graph, save_path)
        
        pos = self._get_layout(G)
        node_colors, color_label = self._get_node_colors(G, graph)
        node_sizes = self._get_node_sizes(G)
        
        # Edge traces
        edge_x = []
        edge_y = []
        edge_weights = []
        
        for u, v, data in G.edges(data=True):
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_weights.append(data.get('weight', 1.0))
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='rgba(128,128,128,0.5)'),
            hoverinfo='none',
            mode='lines',
            showlegend=False
        )
        
        # Node trace
        node_x = [pos[n][0] for n in G.nodes()]
        node_y = [pos[n][1] for n in G.nodes()]
        
        # Node metadata for hover
        node_text = []
        for n in G.nodes():
            meta = graph.node_metadata.get(n, {})
            text = f"Node: {n}<br>"
            for k, v in meta.items():
                text += f"{k}: {v}<br>"
            node_text.append(text)
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            hovertext=node_text,
            marker=dict(
                showscale=True,
                colorscale=self.config.colormap,
                color=node_colors,
                size=node_sizes,
                colorbar=dict(
                    thickness=15,
                    title=color_label,
                    xanchor='left',
                    titleside='right'
                ),
                line_width=1
            ),
            showlegend=False
        )
        
        # Create figure
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title=f"{graph.model_type.upper()} Interaction Graph<br>{G.number_of_nodes()} nodes, {G.number_of_edges()} edges",
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='white'
            )
        )
        
        if save_path:
            fig.write_html(save_path)
            logger.info(f"Saved interactive visualization to {save_path}")
        
        return fig
    
    def visualize_comparison(self,
                            bdh_graph: InteractionGraph,
                            transformer_graph: InteractionGraph,
                            save_path: Optional[str] = None) -> plt.Figure:
        """Create side-by-side comparison visualization."""
        fig, axes = plt.subplots(1, 2, figsize=(24, 10), dpi=self.config.dpi)
        
        for ax, graph, title in [(axes[0], bdh_graph, "BDH"), (axes[1], transformer_graph, "Transformer")]:
            G = graph.to_networkx()
            if G.number_of_nodes() > self.config.max_nodes_display:
                G = self._subsample_graph(G)
            
            pos = self._get_layout(G)
            node_colors, _ = self._get_node_colors(G, graph)
            node_sizes = self._get_node_sizes(G)
            edge_widths = self._get_edge_widths(G)
            
            nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=self.config.edge_alpha, edge_color='gray', ax=ax)
            scatter = nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, 
                                            cmap=plt.get_cmap(self.config.colormap), alpha=self.config.node_alpha, ax=ax)
            
            if len(set(node_colors)) > 1:
                plt.colorbar(scatter, ax=ax, shrink=0.8)
            
            ax.set_title(f"{title} Model\n{G.number_of_nodes()} nodes, {G.number_of_edges()} edges", fontsize=14)
            ax.axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
            logger.info(f"Saved comparison visualization to {save_path}")
        
        return fig


def create_graph_visualizer(config: Optional[Dict] = None) -> GraphVisualizer:
    """Factory function to create GraphVisualizer."""
    if config:
        viz_config = VisualizationConfig(**config)
    else:
        viz_config = VisualizationConfig()
    return GraphVisualizer(viz_config)
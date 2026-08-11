"""
NeuroLens Dashboard

Streamlit-based interactive dashboard for visualizing structural metrics
and experiment results from BDH and Transformer models.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

# Configure page
st.set_page_config(
    page_title="NeuroLens Dashboard",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="expanded"
)

logger = logging.getLogger(__name__)


@dataclass
class DashboardConfig:
    """Dashboard configuration."""
    results_dir: str = "results/"
    refresh_interval: int = 30
    theme: str = "light"


class NeuroLensDashboard:
    """Main dashboard application."""
    
    def __init__(self, config: DashboardConfig):
        self.config = config
        self.results_dir = Path(config.results_dir)
    
    def run(self):
        """Run the dashboard."""
        st.title("🐉 NeuroLens: BDH Structural Analysis Dashboard")
        st.markdown("""
        **NeuroLens** instruments BDH (Dragon Hatchling) models to measure structural properties
        (sparsity, modularity, degree distribution) and connects them to behavioral outcomes
        in continual learning and long-context reasoning.
        """)
        
        # Sidebar
        self._render_sidebar()
        
        # Main content tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Structural Metrics", 
            "🔄 Continual Learning", 
            "📏 Long-Context Reasoning",
            "🔍 Graph Visualization",
            "📈 Model Comparison"
        ])
        
        with tab1:
            self._render_structural_tab()
        
        with tab2:
            self._render_continual_learning_tab()
        
        with tab3:
            self._render_long_context_tab()
        
        with tab4:
            self._render_graph_visualization_tab()
        
        with tab5:
            self._render_comparison_tab()
    
    def _render_sidebar(self):
        """Render sidebar with controls."""
        st.sidebar.header("⚙️ Controls")
        
        # Results directory
        results_dir = st.sidebar.text_input(
            "Results Directory", 
            value=str(self.results_dir),
            help="Path to experiment results"
        )
        self.results_dir = Path(results_dir)
        
        # Refresh button
        if st.sidebar.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
        
        # Auto-refresh
        auto_refresh = st.sidebar.checkbox("Auto-refresh", value=False)
        if auto_refresh:
            st.sidebar.info(f"Refreshing every {self.config.refresh_interval}s")
        
        # Model selection
        st.sidebar.header("📋 Model Selection")
        self.show_bdh = st.sidebar.checkbox("Show BDH", value=True)
        self.show_transformer = st.sidebar.checkbox("Show Transformer", value=True)
        
        # Experiment info
        st.sidebar.header("ℹ️ Experiment Info")
        self._show_experiment_info()
    
    def _show_experiment_info(self):
        """Show experiment metadata in sidebar."""
        # Look for latest results
        result_files = list(self.results_dir.glob("**/*full_experiment_results*.json"))
        if result_files:
            latest = max(result_files, key=lambda f: f.stat().st_mtime)
            try:
                with open(latest, 'r') as f:
                    data = json.load(f)
                st.sidebar.success(f"Latest: {latest.name}")
                st.sidebar.text(f"Timestamp: {data.get('timestamp', 'Unknown')}")
                if data.get('git_commit'):
                    st.sidebar.text(f"Commit: {data['git_commit'][:8]}")
            except:
                st.sidebar.warning("Could not parse latest results")
        else:
            st.sidebar.info("No experiment results found")
    
    def _render_structural_tab(self):
        """Render structural metrics tab."""
        st.header("📊 Structural Metrics")
        
        # Load metrics
        bdh_metrics = self._load_metrics("bdh", "instrumentation")
        trans_metrics = self._load_metrics("transformer", "instrumentation")
        
        if not bdh_metrics and not trans_metrics:
            st.warning("No structural metrics found. Run instrumentation experiment first.")
            return
        
        # Key metrics cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self._metric_card("Graph Sparsity", 
                            bdh_metrics.get('sparsity', 0) if bdh_metrics else 0,
                            trans_metrics.get('sparsity', 0) if trans_metrics else 0)
        
        with col2:
            self._metric_card("Activation Sparsity",
                            bdh_metrics.get('activation_sparsity', 0) if bdh_metrics else 0,
                            trans_metrics.get('activation_sparsity', 0) if trans_metrics else 0)
        
        with col3:
            self._metric_card("Modularity",
                            bdh_metrics.get('modularity', 0) if bdh_metrics else 0,
                            trans_metrics.get('modularity', 0) if trans_metrics else 0)
        
        with col4:
            self._metric_card("Avg Clustering",
                            bdh_metrics.get('avg_clustering', 0) if bdh_metrics else 0,
                            trans_metrics.get('avg_clustering', 0) if trans_metrics else 0)
        
        # Detailed comparison charts
        if bdh_metrics and trans_metrics:
            self._render_structural_comparison_charts(bdh_metrics, trans_metrics)
        
        # Raw metrics tables
        with st.expander("📋 Raw Metrics Data"):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("BDH Metrics")
                st.json(bdh_metrics)
            with col2:
                st.subheader("Transformer Metrics")
                st.json(trans_metrics)
    
    def _metric_card(self, title: str, bdh_val: float, trans_val: float):
        """Render a metric comparison card."""
        diff = bdh_val - trans_val
        diff_color = "green" if diff > 0 else "red" if diff < 0 else "gray"
        
        st.metric(
            label=title,
            value=f"{bdh_val:.4f}",
            delta=f"{diff:+.4f} vs Transformer",
            delta_color="normal"
        )
    
    def _render_structural_comparison_charts(self, bdh: Dict, trans: Dict):
        """Render comparison charts for structural metrics."""
        st.subheader("📈 Detailed Comparison")
        
        # Sparsity comparison
        fig = go.Figure()
        categories = ['Graph Sparsity', 'Activation Sparsity', 'Weight Sparsity']
        bdh_vals = [bdh.get('sparsity', 0), bdh.get('activation_sparsity', 0), bdh.get('weight_sparsity', 0)]
        trans_vals = [trans.get('sparsity', 0), trans.get('activation_sparsity', 0), trans.get('weight_sparsity', 0)]
        
        fig.add_trace(go.Bar(name='BDH', x=categories, y=bdh_vals, marker_color='#2E86AB'))
        fig.add_trace(go.Bar(name='Transformer', x=categories, y=trans_vals, marker_color='#A23B72'))
        fig.update_layout(title='Sparsity Comparison', barmode='group', yaxis_title='Sparsity')
        st.plotly_chart(fig, use_container_width=True)
        
        # Modularity & Communities
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(name='BDH', x=['Modularity'], y=[bdh.get('modularity', 0)], marker_color='#2E86AB'))
            fig.add_trace(go.Bar(name='Transformer', x=['Modularity'], y=[trans.get('modularity', 0)], marker_color='#A23B72'))
            fig.update_layout(title='Modularity', barmode='group')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure()
            fig.add_trace(go.Bar(name='BDH', x=['Communities'], y=[bdh.get('n_communities', 0)], marker_color='#2E86AB'))
            fig.add_trace(go.Bar(name='Transformer', x=['Communities'], y=[trans.get('n_communities', 0)], marker_color='#A23B72'))
            fig.update_layout(title='Number of Communities', barmode='group')
            st.plotly_chart(fig, use_container_width=True)
        
        # Degree distribution
        if bdh.get('degree_distribution') and trans.get('degree_distribution'):
            st.subheader("Degree Distribution")
            fig = make_subplots(rows=1, cols=2, subplot_titles=('BDH', 'Transformer'))
            
            for i, (metrics, name) in enumerate([(bdh, 'BDH'), (trans, 'Transformer')]):
                deg_dist = metrics.get('degree_distribution', {})
                if deg_dist:
                    degrees = list(deg_dist.keys())
                    counts = list(deg_dist.values())
                    fig.add_trace(go.Bar(x=degrees, y=counts, name=name, 
                                        marker_color='#2E86AB' if name == 'BDH' else '#A23B72'), 
                                 row=1, col=i+1)
            
            fig.update_layout(title='Degree Distributions', showlegend=False)
            fig.update_yaxes(type="log")
            st.plotly_chart(fig, use_container_width=True)
        
        # Rich club
        if bdh.get('rich_club_coefficients') and trans.get('rich_club_coefficients'):
            st.subheader("Rich Club Coefficients")
            fig = go.Figure()
            
            for metrics, name, color in [(bdh, 'BDH', '#2E86AB'), (trans, 'Transformer', '#A23B72')]:
                rc = metrics.get('rich_club_coefficients', {})
                if rc:
                    degrees = sorted(rc.keys())
                    coeffs = [rc[d] for d in degrees]
                    fig.add_trace(go.Scatter(x=degrees, y=coeffs, mode='lines+markers', 
                                            name=f'{name} (raw)', line=dict(color=color)))
                
                rc_norm = metrics.get('rich_club_normalized', {})
                if rc_norm:
                    degrees = sorted(rc_norm.keys())
                    coeffs = [rc_norm[d] for d in degrees]
                    fig.add_trace(go.Scatter(x=degrees, y=coeffs, mode='lines+markers', 
                                            name=f'{name} (norm)', line=dict(color=color, dash='dash')))
            
            fig.update_layout(title='Rich Club Coefficients', xaxis_title='Degree Threshold', 
                            yaxis_title='Coefficient', yaxis_range=[0, 1.1])
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_continual_learning_tab(self):
        """Render continual learning results tab."""
        st.header("🔄 Continual Learning Results")
        
        bdh_results = self._load_results("bdh", "continual_learning")
        trans_results = self._load_results("transformer", "continual_learning")
        
        if not bdh_results and not trans_results:
            st.warning("No continual learning results found.")
            return
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            bdh_acc = bdh_results.get('avg_accuracy', 0) if bdh_results else 0
            trans_acc = trans_results.get('avg_accuracy', 0) if trans_results else 0
            self._metric_card("Avg Accuracy", bdh_acc, trans_acc)
        
        with col2:
            bdh_forget = bdh_results.get('avg_forgetting', 0) if bdh_results else 0
            trans_forget = trans_results.get('avg_forgetting', 0) if trans_results else 0
            self._metric_card("Avg Forgetting", bdh_forget, trans_forget)
        
        with col3:
            bdh_fwd = bdh_results.get('avg_forward_transfer', 0) if bdh_results else 0
            trans_fwd = trans_results.get('avg_forward_transfer', 0) if trans_results else 0
            self._metric_card("Forward Transfer", bdh_fwd, trans_fwd)
        
        with col4:
            bdh_bwd = bdh_results.get('avg_backward_transfer', 0) if bdh_results else 0
            trans_bwd = trans_results.get('avg_backward_transfer', 0) if trans_results else 0
            self._metric_card("Backward Transfer", bdh_bwd, trans_bwd)
        
        # Accuracy heatmaps
        if bdh_results and trans_results:
            st.subheader("📊 Accuracy Matrices")
            col1, col2 = st.columns(2)
            
            with col1:
                self._plot_accuracy_heatmap(bdh_results, "BDH")
            
            with col2:
                self._plot_accuracy_heatmap(trans_results, "Transformer")
            
            # Forgetting comparison
            st.subheader("📉 Forgetting Comparison")
            self._plot_forgetting_comparison(bdh_results, trans_results)
            
            # Training curves
            if bdh_results.get('training_curves') or trans_results.get('training_curves'):
                st.subheader("📈 Training Curves")
                self._plot_training_curves(bdh_results, trans_results)
    
    def _plot_accuracy_heatmap(self, results: Dict, title: str):
        """Plot accuracy matrix heatmap."""
        task_accuracies = results.get('task_accuracies', {})
        if not task_accuracies:
            st.info(f"No accuracy data for {title}")
            return
        
        tasks = list(task_accuracies.keys())
        n = len(tasks)
        matrix = np.zeros((n, n))
        
        for i, train_task in enumerate(tasks):
            for j, eval_task in enumerate(tasks):
                matrix[i, j] = task_accuracies[train_task].get(eval_task, 0)
        
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=tasks,
            y=tasks,
            colorscale='RdYlGn',
            zmin=0,
            zmax=1,
            text=np.round(matrix, 2),
            texttemplate='%{text}',
            textfont={"size": 12}
        ))
        fig.update_layout(title=f'{title} Accuracy Matrix', 
                         xaxis_title='Eval Task', yaxis_title='Train Task',
                         height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    def _plot_forgetting_comparison(self, bdh_results: Dict, trans_results: Dict):
        """Plot forgetting comparison."""
        bdh_forget = bdh_results.get('forgetting', {})
        trans_forget = trans_results.get('forgetting', {})
        
        tasks = list(set(bdh_forget.keys()) | set(trans_forget.keys()))
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='BDH', x=tasks, 
                            y=[bdh_forget.get(t, 0) for t in tasks], marker_color='#2E86AB'))
        fig.add_trace(go.Bar(name='Transformer', x=tasks,
                            y=[trans_forget.get(t, 0) for t in tasks], marker_color='#A23B72'))
        fig.update_layout(title='Catastrophic Forgetting by Task', barmode='group',
                         yaxis_title='Forgetting (max_acc - final_acc)')
        st.plotly_chart(fig, use_container_width=True)
    
    def _plot_training_curves(self, bdh_results: Dict, trans_results: Dict):
        """Plot training curves."""
        fig = make_subplots(rows=1, cols=2, subplot_titles=('BDH', 'Transformer'))
        
        for col, (results, name) in enumerate([(bdh_results, 'BDH'), (trans_results, 'Transformer')], 1):
            curves = results.get('training_curves', {})
            for task_name, curve in curves.items():
                fig.add_trace(go.Scatter(x=list(range(1, len(curve)+1)), y=curve,
                                        mode='lines+markers', name=f'{name}: {task_name}',
                                        line=dict(color='#2E86AB' if name == 'BDH' else '#A23B72')),
                             row=1, col=col)
        
        fig.update_layout(title='Training Curves', xaxis_title='Epoch', yaxis_title='Validation Accuracy')
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_long_context_tab(self):
        """Render long-context reasoning results tab."""
        st.header("📏 Long-Context Reasoning Results")
        
        bdh_results = self._load_results("bdh", "long_context")
        trans_results = self._load_results("transformer", "long_context")
        
        if not bdh_results and not trans_results:
            st.warning("No long-context results found.")
            return
        
        # Summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            bdh_acc = bdh_results.get('avg_accuracy', 0) if bdh_results else 0
            trans_acc = trans_results.get('avg_accuracy', 0) if trans_results else 0
            self._metric_card("Avg Accuracy", bdh_acc, trans_acc)
        
        with col2:
            bdh_exp = bdh_results.get('length_scaling_exponent', 0) if bdh_results else 0
            trans_exp = trans_results.get('length_scaling_exponent', 0) if trans_results else 0
            self._metric_card("Scaling Exponent", bdh_exp, trans_exp)
        
        with col3:
            st.metric("Tasks Evaluated", 
                     len(bdh_results.get('accuracies', {})) if bdh_results else 0)
        
        # Accuracy by context length
        if bdh_results and trans_results:
            st.subheader("📈 Accuracy vs Context Length")
            self._plot_accuracy_by_length(bdh_results, trans_results)
            
            # Per-task comparison
            st.subheader("🎯 Per-Task Accuracy")
            self._plot_per_task_comparison(bdh_results, trans_results)
    
    def _plot_accuracy_by_length(self, bdh_results: Dict, trans_results: Dict):
        """Plot accuracy by context length."""
        fig = go.Figure()
        
        for results, name, color in [(bdh_results, 'BDH', '#2E86AB'), (trans_results, 'Transformer', '#A23B72')]:
            acc_by_len = results.get('accuracy_by_length', {})
            if acc_by_len:
                lengths = sorted(acc_by_len.keys())
                accs = [acc_by_len[l] for l in lengths]
                fig.add_trace(go.Scatter(x=lengths, y=accs, mode='lines+markers',
                                        name=name, line=dict(color=color, width=3),
                                        marker=dict(size=10)))
        
        fig.update_layout(title='Accuracy vs Context Length', 
                         xaxis_title='Context Length', yaxis_title='Accuracy',
                         xaxis_type='log', xaxis_dtick=1)
        st.plotly_chart(fig, use_container_width=True)
    
    def _plot_per_task_comparison(self, bdh_results: Dict, trans_results: Dict):
        """Plot per-task accuracy comparison."""
        all_tasks = set(bdh_results.get('accuracies', {}).keys()) | set(trans_results.get('accuracies', {}).keys())
        tasks = sorted(all_tasks)
        
        fig = go.Figure()
        
        for results, name, color in [(bdh_results, 'BDH', '#2E86AB'), (trans_results, 'Transformer', '#A23B72')]:
            task_accs = results.get('accuracies', {})
            avg_accs = []
            for task in tasks:
                accs = task_accs.get(task, {})
                avg_accs.append(np.mean(list(accs.values())) if accs else 0)
            
            fig.add_trace(go.Bar(name=name, x=tasks, y=avg_accs, marker_color=color))
        
        fig.update_layout(title='Average Accuracy by Task', barmode='group',
                         xaxis_title='Task', yaxis_title='Average Accuracy')
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_graph_visualization_tab(self):
        """Render graph visualization tab."""
        st.header("🔍 Graph Visualization")
        
        st.info("""
        Interactive graph visualizations require saved interaction graphs.
        Run the instrumentation experiment to generate graphs.
        """)
        
        # Check for saved graphs
        graph_files = list(self.results_dir.glob("**/graphs/*instrumentation*.json"))
        
        if graph_files:
            selected_graph = st.selectbox("Select Graph", graph_files, 
                                         format_func=lambda f: f.name)
            
            if st.button("Load Graph"):
                with open(selected_graph, 'r') as f:
                    graph_data = json.load(f)
                
                st.success(f"Loaded: {selected_graph.name}")
                st.json({
                    'nodes': len(graph_data.get('nodes', [])),
                    'edges': len(graph_data.get('edges', [])),
                    'model_type': graph_data.get('model_type', 'unknown'),
                    'config': graph_data.get('graph_config', {})
                })
        else:
            st.warning("No graph files found in results directory.")
    
    def _render_comparison_tab(self):
        """Render overall model comparison tab."""
        st.header("📈 Model Comparison Summary")
        
        # Load all results
        bdh_struct = self._load_metrics("bdh", "instrumentation")
        trans_struct = self._load_metrics("transformer", "instrumentation")
        bdh_cl = self._load_results("bdh", "continual_learning")
        trans_cl = self._load_results("transformer", "continual_learning")
        bdh_lc = self._load_results("bdh", "long_context")
        trans_lc = self._load_results("transformer", "long_context")
        
        # Create comparison table
        comparison_data = []
        
        # Structural metrics
        if bdh_struct and trans_struct:
            for metric in ['sparsity', 'activation_sparsity', 'weight_sparsity', 
                          'modularity', 'avg_clustering', 'avg_degree']:
                comparison_data.append({
                    'Category': 'Structural',
                    'Metric': metric.replace('_', ' ').title(),
                    'BDH': bdh_struct.get(metric, 'N/A'),
                    'Transformer': trans_struct.get(metric, 'N/A'),
                    'Difference': (bdh_struct.get(metric, 0) - trans_struct.get(metric, 0)) 
                                 if isinstance(bdh_struct.get(metric), (int, float)) and 
                                    isinstance(trans_struct.get(metric), (int, float)) else 'N/A'
                })
        
        # Continual learning
        if bdh_cl and trans_cl:
            for metric in ['avg_accuracy', 'avg_forgetting', 'avg_forward_transfer', 'avg_backward_transfer']:
                comparison_data.append({
                    'Category': 'Continual Learning',
                    'Metric': metric.replace('_', ' ').title(),
                    'BDH': bdh_cl.get(metric, 'N/A'),
                    'Transformer': trans_cl.get(metric, 'N/A'),
                    'Difference': (bdh_cl.get(metric, 0) - trans_cl.get(metric, 0))
                                 if isinstance(bdh_cl.get(metric), (int, float)) and 
                                    isinstance(trans_cl.get(metric), (int, float)) else 'N/A'
                })
        
        # Long context
        if bdh_lc and trans_lc:
            for metric in ['avg_accuracy', 'length_scaling_exponent']:
                comparison_data.append({
                    'Category': 'Long Context',
                    'Metric': metric.replace('_', ' ').title(),
                    'BDH': bdh_lc.get(metric, 'N/A'),
                    'Transformer': trans_lc.get(metric, 'N/A'),
                    'Difference': (bdh_lc.get(metric, 0) - trans_lc.get(metric, 0))
                                 if isinstance(bdh_lc.get(metric), (int, float)) and 
                                    isinstance(trans_lc.get(metric), (int, float)) else 'N/A'
                })
        
        if comparison_data:
            df = pd.DataFrame(comparison_data)
            
            # Style the dataframe
            def highlight_diff(val):
                if isinstance(val, (int, float)):
                    if val > 0:
                        return 'background-color: #d4edda'
                    elif val < 0:
                        return 'background-color: #f8d7da'
                return ''
            
            styled_df = df.style.applymap(highlight_diff, subset=['Difference'])
            st.dataframe(styled_df, use_container_width=True)
            
            # Summary
            st.subheader("📋 Key Findings")
            self._generate_key_findings(comparison_data)
        else:
            st.info("Run experiments to generate comparison data.")
    
    def _generate_key_findings(self, comparison_data: List[Dict]):
        """Generate key findings from comparison data."""
        findings = []
        
        for item in comparison_data:
            diff = item['Difference']
            if isinstance(diff, (int, float)) and abs(diff) > 0.01:
                direction = "higher" if diff > 0 else "lower"
                findings.append(f"**{item['Metric']}**: BDH is {direction} than Transformer by {abs(diff):.4f}")
        
        if findings:
            for finding in findings:
                st.markdown(f"• {finding}")
        else:
            st.info("No significant differences detected.")
    
    def _load_metrics(self, model_type: str, experiment: str) -> Optional[Dict]:
        """Load metrics from results directory."""
        metric_files = list(self.results_dir.glob(f"**/metrics/*{model_type}*{experiment}*.json"))
        if metric_files:
            latest = max(metric_files, key=lambda f: f.stat().st_mtime)
            try:
                with open(latest, 'r') as f:
                    return json.load(f)
            except:
                pass
        return None
    
    def _load_results(self, model_type: str, experiment: str) -> Optional[Dict]:
        """Load experiment results from results directory."""
        result_files = list(self.results_dir.glob(f"**/results/*{model_type}*{experiment}*.json"))
        if result_files:
            latest = max(result_files, key=lambda f: f.stat().st_mtime)
            try:
                with open(latest, 'r') as f:
                    return json.load(f)
            except:
                pass
        return None


def main():
    """Main entry point for Streamlit dashboard."""
    config = DashboardConfig()
    dashboard = NeuroLensDashboard(config)
    dashboard.run()


if __name__ == "__main__":
    main()
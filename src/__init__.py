"""
NeuroLens: Structural Instrumentation and Behavioral Analysis of BDH Models

A research framework for measuring structural properties of Dragon Hatchling (BDH) models
and connecting them to continual learning and long-context reasoning capabilities.
"""

__version__ = "0.1.0"
__author__ = "NeuroLens Team"

# Core modules
from .models import BDHLoader, TransformerBaseline
from .instrumentation import GraphExtractor, StructuralMetrics, CheckpointManager
from .experiments import ContinualLearningExperiment, LongContextExperiment
from .visualization import GraphVisualizer, MetricsPlotter
from .dashboard import DashboardApp

__all__ = [
    "BDHLoader",
    "TransformerBaseline",
    "GraphExtractor",
    "StructuralMetrics",
    "CheckpointManager",
    "ContinualLearningExperiment",
    "LongContextExperiment",
    "GraphVisualizer",
    "MetricsPlotter",
    "DashboardApp",
]
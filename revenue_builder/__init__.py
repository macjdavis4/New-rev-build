"""
Revenue Builder - Comprehensive ML-Powered Revenue Forecasting System

A production-ready, modular system for revenue forecasting that supports
multiple business models and forecasting methodologies.
"""

__version__ = "1.0.0"
__author__ = "Revenue Builder Team"

from .core.revenue_model import RevenueModel
from .core.config import Config
from .data.ingestion import DataIngestion
from .models.model_factory import ModelFactory
from .business_models.templates import BusinessModelTemplates
from .metrics.calculator import MetricsCalculator
from .scenarios.planner import ScenarioPlanner
from .visualization.dashboard import Dashboard

__all__ = [
    'RevenueModel',
    'Config',
    'DataIngestion',
    'ModelFactory',
    'BusinessModelTemplates',
    'MetricsCalculator',
    'ScenarioPlanner',
    'Dashboard'
]

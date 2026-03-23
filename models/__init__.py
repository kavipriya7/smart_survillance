"""
Smart Health Surveillance and Early Warning Platform
AI-Based Early Warning System for Water-Borne and Vector-Borne Diseases

Package: models
Contains all machine learning, data processing, and alert system components
"""

__version__ = "1.0.0"
__author__ = "Health Surveillance Team"
__description__ = "AI-based disease surveillance and early warning system"

# Import main components for easy access
from .data_processor import DataProcessor
from .model_builder import DiseasePredictor, DiseaseSeverityClassifier
from .alert_system import AlertSystem, WeatherRiskAnalyzer, AlertLevel
from .community_reporting import (
    CommunityReportingSystem,
    CommunityReport,
    SymptomType,
    ReportStatus
)

__all__ = [
    'DataProcessor',
    'DiseasePredictor',
    'DiseaseSeverityClassifier',
    'AlertSystem',
    'WeatherRiskAnalyzer',
    'AlertLevel',
    'CommunityReportingSystem',
    'CommunityReport',
    'SymptomType',
    'ReportStatus'
]

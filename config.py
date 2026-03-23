"""
Configuration Settings for Smart Health Surveillance Platform
"""

import os
from datetime import datetime

# ============================================================================
# SYSTEM CONFIGURATION
# ============================================================================

# Project Paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')
NOTEBOOKS_DIR = os.path.join(PROJECT_ROOT, 'notebooks')

# Data Files
WEATHER_DATA_PATH = os.path.join(DATA_DIR, 'weather_data.csv')
DISEASE_DATA_PATH = os.path.join(DATA_DIR, 'disease_data.csv')

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

# Random Forest Parameters
RANDOM_FOREST_CONFIG = {
    'n_estimators': 100,
    'max_depth': 15,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'random_state': 42,
    'n_jobs': -1
}

# Gradient Boosting Parameters
GRADIENT_BOOSTING_CONFIG = {
    'n_estimators': 100,
    'learning_rate': 0.1,
    'max_depth': 5,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'random_state': 42
}

# Train-Test Split
TRAIN_TEST_SPLIT_RATIO = 0.2
RANDOM_STATE = 42

# ============================================================================
# ALERT SYSTEM CONFIGURATION
# ============================================================================

# Risk Thresholds for Alert Levels (0-100 scale)
ALERT_THRESHOLDS = {
    'green': 25,      # Safe
    'yellow': 50,     # Warning
    'orange': 75      # Danger
    # Red is everything above 75
}

# Water-Borne Disease Thresholds
WATER_BORNE_THRESHOLDS = {
    'temperature_high': 35,          # °C - Optimal for bacteria
    'temperature_low': 15,           # °C - Minimum for bacteria
    'humidity_high': 80,             # % - High humidity aids spread
    'rainfall_high': 50,             # mm - Heavy rainfall causes flooding
    'monsoon_factor': 1.5            # Multiplier for monsoon season
}

# Vector-Borne Disease Thresholds
VECTOR_BORNE_THRESHOLDS = {
    'temperature_optimal_low': 20,   # °C - Lower optimal range
    'temperature_optimal_high': 32,  # °C - Upper optimal range
    'humidity_high': 70,             # % - High humidity for mosquitoes
    'rainfall_high': 40,             # mm - Creates breeding grounds
    'stagnant_water_days': 7         # Days with water - breeding period
}

# ============================================================================
# COMMUNITY REPORTING CONFIGURATION
# ============================================================================

# Outbreak Detection Parameters
OUTBREAK_DETECTION = {
    'lookback_days': 7,              # Days to look back for outbreak detection
    'green_threshold': 5,             # Minimum reports for Yellow alert
    'yellow_threshold': 15,           # Minimum reports for Orange alert
    'orange_threshold': 30,           # Minimum reports for Red alert
}

# Symptom Verification Score Weights
SYMPTOM_VERIFICATION_WEIGHTS = {
    'symptom_pattern_match': 50,     # Matching known disease patterns
    'detailed_reporting': 20,        # Multiple symptoms reported
    'consistency_check': 20,         # Symptom consistency
    'vague_symptom_penalty': -10     # Penalty for vague reporting
}

# ============================================================================
# DATA PREPROCESSING CONFIGURATION
# ============================================================================

# Feature Engineering
FEATURE_ENGINEERING = {
    'lag_days': [1, 2, 3],           # Lag features for time series
    'rolling_window': 7,              # 7-day rolling statistics
}

# Standardization
STANDARDIZATION_ENABLED = True
SCALING_METHOD = 'standard'          # 'standard' or 'minmax'

# ============================================================================
# LOCATIONS CONFIGURATION
# ============================================================================

# Monitored Locations
MONITORED_LOCATIONS = [
    'Mumbai',
    'Chennai',
    'Kolkata',
    'Delhi',
    'Bangalore'
]

# City to State Mapping
CITY_TO_STATE_MAPPING = {
    'Mumbai': 'Maharashtra',
    'Chennai': 'Tamil Nadu',
    'Kolkata': 'West Bengal',
    'Delhi': 'Delhi',
    'Bangalore': 'Karnataka'
}

# ============================================================================
# DISEASE CONFIGURATION
# ============================================================================

# Water-Borne Diseases
WATER_BORNE_DISEASES = {
    'Cholera': {
        'incubation_days': [1, 3],
        'symptoms': ['Diarrhea', 'Vomiting', 'Dehydration', 'Abdominal Pain']
    },
    'Typhoid': {
        'incubation_days': [6, 30],
        'symptoms': ['High Fever', 'Abdominal Pain', 'Headache', 'Body Ache']
    },
    'Dysentery': {
        'incubation_days': [1, 3],
        'symptoms': ['Diarrhea', 'Abdominal Pain', 'Fever with GI symptoms']
    }
}

# Vector-Borne Diseases
VECTOR_BORNE_DISEASES = {
    'Dengue': {
        'incubation_days': [3, 14],
        'symptoms': ['High Fever', 'Joint Pain', 'Muscle Pain', 'Rash']
    },
    'Malaria': {
        'incubation_days': [10, 30],
        'symptoms': ['High Fever', 'Chills', 'Body Ache', 'Headache']
    },
    'Chikungunya': {
        'incubation_days': [2, 12],
        'symptoms': ['High Fever', 'Joint Pain', 'Muscle Pain', 'Rash']
    }
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '[%(asctime)s] %(levelname)s: %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S'
}

# ============================================================================
# DASHBOARD CONFIGURATION
# ============================================================================

# Streamlit Settings
STREAMLIT_CONFIG = {
    'page_title': 'Health Surveillance Platform',
    'page_icon': '🏥',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Refresh Intervals (seconds)
REFRESH_INTERVALS = {
    'weather_data': 3600,            # 1 hour
    'model_predictions': 1800,       # 30 minutes
    'alerts': 600,                   # 10 minutes
    'community_reports': 300         # 5 minutes
}

# ============================================================================
# EXPORT CONFIGURATION
# ============================================================================

# Export Settings
EXPORT_CONFIG = {
    'format': ['csv', 'json', 'pdf'],
    'include_timestamp': True,
    'compression': 'gzip'
}

# ============================================================================
# API CONFIGURATION (Future)
# ============================================================================

# API Settings
API_CONFIG = {
    'host': 'localhost',
    'port': 8000,
    'debug': True,
    'version': '1.0'
}

# ============================================================================
# PERFORMANCE METRICS
# ============================================================================

# Model Performance Baselines
PERFORMANCE_BASELINES = {
    'gradient_boosting': {
        'r2_score': 0.87,
        'rmse': 45,
        'mae': 35
    },
    'random_forest': {
        'r2_score': 0.84,
        'rmse': 52,
        'mae': 40
    },
    'linear_regression': {
        'r2_score': 0.71,
        'rmse': 78,
        'mae': 60
    }
}

# ============================================================================
# ALERT RECOMMENDATIONS
# ============================================================================

ALERT_RECOMMENDATIONS = {
    'Green': {
        'label': 'Safe',
        'color': '#00AA00',
        'actions': [
            'Continue routine health surveillance',
            'Maintain hygiene standards',
            'Regular monitoring of water quality',
            'Monthly health check-ups'
        ]
    },
    'Yellow': {
        'label': 'Warning',
        'color': '#FFFF00',
        'actions': [
            'Increase surveillance frequency to weekly',
            'Distribute health awareness materials',
            'Increase water quality testing',
            'Monitor symptoms in community',
            'Prepare healthcare resources'
        ]
    },
    'Orange': {
        'label': 'Danger',
        'color': '#FF8800',
        'actions': [
            'Activate early warning protocols',
            'Daily health surveillance',
            'Issue community health advisory',
            'Intensify water testing (every 2-3 days)',
            'Set up screening camps in communities',
            'Prepare isolation facilities'
        ]
    },
    'Red': {
        'label': 'Critical',
        'color': '#FF0000',
        'actions': [
            'EMERGENCY: Activate crisis management team',
            'Deploy mobile health clinics immediately',
            'Launch mass awareness campaign',
            'Implement quarantine measures if needed',
            'Daily water supply testing',
            'Hospital emergency preparedness',
            'Contact tracing and surveillance'
        ]
    }
}

# ============================================================================
# SYSTEM METADATA
# ============================================================================

SYSTEM_INFO = {
    'name': 'Smart Health Surveillance and Early Warning Platform',
    'version': '1.0.0',
    'release_date': '2026-02-09',
    'description': 'AI-Based Early Warning System for Water-Borne and Vector-Borne Diseases',
    'author': 'Health Surveillance Team',
    'contact': 'health.surveillance@example.com'
}

# ============================================================================
# VALIDATION RULES
# ============================================================================

# Input Validation
VALIDATION_RULES = {
    'temperature': {'min': -10, 'max': 50},          # Celsius
    'humidity': {'min': 0, 'max': 100},              # Percentage
    'rainfall': {'min': 0, 'max': 500},              # Millimeters
    'wind_speed': {'min': 0, 'max': 100},            # km/h
    'affected_count': {'min': 1, 'max': 10000}       # Number of people
}

# ============================================================================
# DEFAULT VALUES
# ============================================================================

DEFAULT_VALUES = {
    'temperature': 25,               # °C
    'humidity': 60,                  # %
    'rainfall': 20,                  # mm
    'wind_speed': 10,                # km/h
    'monsoon_season': False,
    'days_since_rain': 5,
    'affected_count': 1
}

# ============================================================================
# FEATURE COLUMNS
# ============================================================================

WEATHER_FEATURES = [
    'Temperature_C',
    'Humidity_%',
    'Wind_Speed_kmph',
    'Rainfall_mm',
    'Day_of_Year',
    'Month',
    'Quarter',
    'Is_Monsoon',
    'Temp_Humidity_Index',
    'Rainfall_7day_avg',
    'Weather_Condition_Encoded'
]

# ============================================================================
# CACHING CONFIGURATION
# ============================================================================

CACHING = {
    'enabled': True,
    'ttl_seconds': 3600,             # Cache time-to-live
    'max_size_mb': 500
}

# ============================================================================
# TESTING CONFIGURATION
# ============================================================================

TEST_DATA = {
    'sample_weather': {
        'temperature': 28,
        'humidity': 75,
        'rainfall': 50,
        'is_monsoon': False
    },
    'sample_location': 'Mumbai',
    'sample_symptoms': ['Diarrhea', 'Vomiting']
}

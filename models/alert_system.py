"""
Real-time Alert System for Disease Surveillance
Monitors weather patterns and triggers alerts for disease outbreaks
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from enum import Enum
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels"""
    GREEN = {"level": 0, "name": "Safe", "color": "#00AA00", "action": "routine"}
    YELLOW = {"level": 1, "name": "Warning", "color": "#FFFF00", "action": "caution"}
    ORANGE = {"level": 2, "name": "Danger", "color": "#FF8800", "action": "active"}
    RED = {"level": 3, "name": "Critical", "color": "#FF0000", "action": "emergency"}


class WeatherRiskAnalyzer:
    """Analyze weather conditions for disease spread risk"""
    
    def __init__(self):
        """Initialize weather risk thresholds"""
        self.thresholds = {
            'water_borne': {  # Cholera, Typhoid, Dysentery
                'temperature_high': 35,
                'temperature_low': 15,
                'humidity_high': 80,
                'rainfall_high': 50,
                'monsoon_factor': 1.5
            },
            'vector_borne': {  # Dengue, Malaria, Chikungunya
                'temperature_optimal_low': 20,
                'temperature_optimal_high': 32,
                'humidity_high': 70,
                'rainfall_high': 40,
                'stagnant_water_days': 7
            }
        }
        self.water_stagnant_days = {}  # Track days with stagnant water conditions
    
    def assess_water_borne_risk(self, temperature, humidity, rainfall, is_monsoon):
        """
        Calculate risk score for water-borne diseases
        
        Args:
            temperature: Average temperature in Celsius
            humidity: Average humidity percentage
            rainfall: Total rainfall in mm
            is_monsoon: Boolean indicating monsoon season
        
        Returns:
            risk_score: Score from 0-100
            risk_factors: List of contributing factors
        """
        risk_score = 0
        risk_factors = []
        
        thresholds = self.thresholds['water_borne']
        
        # Temperature risk (warm water promotes bacteria)
        if temperature > thresholds['temperature_high']:
            risk_score += 25
            risk_factors.append(f"High temperature ({temperature}°C)")
        elif temperature < thresholds['temperature_low']:
            risk_score += 10
            risk_factors.append(f"Low temperature ({temperature}°C)")
        
        # Humidity risk (affects contamination spread)
        if humidity > thresholds['humidity_high']:
            risk_score += 20
            risk_factors.append(f"High humidity ({humidity}%)")
        
        # Rainfall risk (floods cause contamination)
        if rainfall > thresholds['rainfall_high']:
            risk_score += 30
            risk_factors.append(f"Heavy rainfall ({rainfall}mm)")
        
        # Monsoon factor (seasonal peak)
        if is_monsoon:
            risk_score += 15
            risk_factors.append("Monsoon season")
        
        return min(risk_score, 100), risk_factors
    
    def assess_vector_borne_risk(self, temperature, humidity, rainfall, days_since_rain):
        """
        Calculate risk score for vector-borne diseases
        
        Args:
            temperature: Average temperature in Celsius
            humidity: Average humidity percentage
            rainfall: Total rainfall in mm
            days_since_rain: Days since last rainfall
        
        Returns:
            risk_score: Score from 0-100
            risk_factors: List of contributing factors
        """
        risk_score = 0
        risk_factors = []
        
        thresholds = self.thresholds['vector_borne']
        
        # Temperature risk (mosquito breeding)
        if thresholds['temperature_optimal_low'] <= temperature <= thresholds['temperature_optimal_high']:
            risk_score += 30
            risk_factors.append(f"Optimal temperature for vectors ({temperature}°C)")
        elif temperature > thresholds['temperature_optimal_high']:
            risk_score += 25
            risk_factors.append(f"Very high temperature ({temperature}°C)")
        
        # Humidity risk (mosquito survival)
        if humidity > thresholds['humidity_high']:
            risk_score += 25
            risk_factors.append(f"High humidity ({humidity}%)")
        
        # Rainfall creates breeding grounds
        if rainfall > thresholds['rainfall_high']:
            risk_score += 20
            risk_factors.append(f"Significant rainfall ({rainfall}mm)")
        
        # Stagnant water conditions (perfect for breeding)
        if 3 <= days_since_rain <= self.thresholds['vector_borne']['stagnant_water_days']:
            risk_score += 20
            risk_factors.append(f"Stagnant water conditions ({days_since_rain} days)")
        
        return min(risk_score, 100), risk_factors


class AlertSystem:
    """Generate and manage disease alerts"""
    
    def __init__(self, predictor=None):
        """
        Initialize alert system
        
        Args:
            predictor: DiseasePredictor model instance
        """
        self.predictor = predictor
        self.weather_analyzer = WeatherRiskAnalyzer()
        self.active_alerts = {}
        self.alert_history = []
        self.thresholds = {
            'green': 25,
            'yellow': 50,
            'orange': 75
        }
    
    def generate_alert(self, location, weather_data, predicted_cases=None, alert_type='water_borne'):
        """
        Generate alert for a specific location
        
        Args:
            location: City or region name
            weather_data: Dict with temperature, humidity, rainfall, etc.
            predicted_cases: Predicted number of cases (optional)
            alert_type: 'water_borne', 'vector_borne', or 'both'
        
        Returns:
            alert: Alert dictionary with details
        """
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'location': location,
            'alert_type': alert_type,
            'weather_data': weather_data,
            'risk_scores': {},
            'risk_factors': {},
            'alert_levels': {},
            'recommendations': {}
        }
        
        # Assess water-borne risk
        if alert_type in ['water_borne', 'both']:
            water_risk, water_factors = self.weather_analyzer.assess_water_borne_risk(
                weather_data.get('temperature', 25),
                weather_data.get('humidity', 60),
                weather_data.get('rainfall', 0),
                weather_data.get('is_monsoon', False)
            )
            alert_data['risk_scores']['water_borne'] = water_risk
            alert_data['risk_factors']['water_borne'] = water_factors
            alert_data['alert_levels']['water_borne'] = self._risk_to_alert_level(water_risk)
        
        # Assess vector-borne risk
        if alert_type in ['vector_borne', 'both']:
            vector_risk, vector_factors = self.weather_analyzer.assess_vector_borne_risk(
                weather_data.get('temperature', 25),
                weather_data.get('humidity', 60),
                weather_data.get('rainfall', 0),
                weather_data.get('days_since_rain', 7)
            )
            alert_data['risk_scores']['vector_borne'] = vector_risk
            alert_data['risk_factors']['vector_borne'] = vector_factors
            alert_data['alert_levels']['vector_borne'] = self._risk_to_alert_level(vector_risk)
        
        # Use model predictions if available
        if predicted_cases is not None:
            alert_data['predicted_cases'] = predicted_cases
            prediction_risk = min((predicted_cases / 1000) * 100, 100)
            alert_data['risk_scores']['prediction'] = prediction_risk
            alert_data['alert_levels']['prediction'] = self._risk_to_alert_level(prediction_risk)
        
        # Determine overall alert level
        alert_data['overall_alert_level'] = self._determine_overall_alert(alert_data['alert_levels'])
        
        # Get recommendations (city-specific)
        alert_data['recommendations'] = self._get_recommendations(alert_data['overall_alert_level'], location)
        self.alert_history.append(alert_data)
        
        return alert_data
    
    def _risk_to_alert_level(self, risk_score):
        """Convert risk score to alert level"""
        if risk_score < self.thresholds['green']:
            return AlertLevel.GREEN.value
        elif risk_score < self.thresholds['yellow']:
            return AlertLevel.YELLOW.value
        elif risk_score < self.thresholds['orange']:
            return AlertLevel.ORANGE.value
        else:
            return AlertLevel.RED.value
    
    def _determine_overall_alert(self, alert_levels):
        """Determine overall alert from multiple alert levels"""
        if not alert_levels:
            return AlertLevel.GREEN.value
        
        # Get highest alert level
        max_level = max([v['level'] for v in alert_levels.values()])
        
        for alert_level in AlertLevel:
            if alert_level.value['level'] == max_level:
                return alert_level.value
        
        return AlertLevel.GREEN.value
    
    def _get_recommendations(self, alert_level, location):
        """Get health recommendations based on alert level and location"""
        recommendations_map = {
            'Safe': [
                '✓ Continue routine health surveillance',
                '✓ Maintain standard hygiene practices',
                '✓ Regular monitoring of water quality',
                '✓ Monthly health check-ups recommended'
            ],
            'Warning': [
                '⚠ Increase surveillance frequency to weekly',
                '⚠ Distribute health awareness materials',
                '⚠ Increase water quality testing',
                '⚠ Monitor symptoms in community',
                '⚠ Prepare healthcare resources'
            ],
            'Danger': [
                '🔶 Activate early warning protocols',
                '🔶 Daily health surveillance',
                '🔶 Issue community health advisory',
                '🔶 Intensify water testing (every 2-3 days)',
                '🔶 Set up screening camps in communities',
                '🔶 Prepare isolation facilities'
            ],
            'Critical': [
                '🔴 EMERGENCY: Activate crisis management',
                '🔴 Deploy mobile health clinics immediately',
                '🔴 Launch mass awareness campaign',
                '🔴 Implement quarantine measures if needed',
                '🔴 Daily water supply testing',
                '🔴 Hospital emergency preparedness',
                '🔴 Contact tracing and surveillance'
            ]
        }
        
        base_recommendations = recommendations_map.get(alert_level.get('name', 'Safe'), [])

        # City-specific unique actions
        city_actions = {
            'Mumbai': '🏙️ Mumbai: Increase coastal neighborhood water drainage and public pump station checks.',
            'Chennai': '🏙️ Chennai: Prioritize monsoon rainwater clearance in low-lying wards and community alert broadcasts.',
            'Kolkata': '🏙️ Kolkata: Ramp up riverbank sanitization and floating market hygiene checkpoints.',
            'Delhi': '🏙️ Delhi: Increase urban heat monitoring and street-level drinking water testing.'
        }

        location_note = f"🔹 {location}: Follow city-specific outbreak mitigation actions and liaise with local health authorities."
        location_action = city_actions.get(location, f"🏙️ {location}: Execute local community health coordination and area-specific surveillance.")

        # Preserve uniqueness across cities by giving two city-specific lines plus level-based recommendations
        return [location_note, location_action] + base_recommendations
    
    def get_location_alert(self, location):
        """Get current alert for a location"""
        return self.active_alerts.get(location, None)
    
    def get_all_active_alerts(self):
        """Get all active alerts"""
        return self.active_alerts
    
    def escalate_alert(self, location, reason=''):
        """Manually escalate alert for a location"""
        if location in self.active_alerts:
            alert = self.active_alerts[location]
            current_level = alert['overall_alert_level']['level']
            
            if current_level < 3:  # Can escalate to max level 3
                new_level = current_level + 1
                alert['overall_alert_level'] = AlertLevel[list(AlertLevel)[new_level]].value
                alert['escalation_reason'] = reason
                alert['escalated_at'] = datetime.now().isoformat()
                logger.warning(f"Alert escalated for {location}: {reason}")
    
    def get_alert_summary(self):
        """Get summary of all active alerts"""
        summary = {
            'total_active_alerts': len(self.active_alerts),
            'green_alerts': sum(1 for a in self.active_alerts.values() if a['overall_alert_level']['level'] == 0),
            'yellow_alerts': sum(1 for a in self.active_alerts.values() if a['overall_alert_level']['level'] == 1),
            'orange_alerts': sum(1 for a in self.active_alerts.values() if a['overall_alert_level']['level'] == 2),
            'red_alerts': sum(1 for a in self.active_alerts.values() if a['overall_alert_level']['level'] == 3),
            'timestamp': datetime.now().isoformat()
        }
        return summary
    
    def export_alerts_to_json(self, filepath):
        """Export all alerts to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump({
                    'active_alerts': self.active_alerts,
                    'summary': self.get_alert_summary()
                }, f, indent=2)
            logger.info(f"Alerts exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting alerts: {str(e)}")
            return False


def main():
    """Test alert system"""
    alert_system = AlertSystem()
    
    # Simulate weather data for different locations
    weather_scenarios = {
        'Mumbai': {
            'temperature': 32,
            'humidity': 85,
            'rainfall': 120,
            'is_monsoon': True,
            'days_since_rain': 2
        },
        'Delhi': {
            'temperature': 38,
            'humidity': 40,
            'rainfall': 5,
            'is_monsoon': False,
            'days_since_rain': 15
        },
        'Kolkata': {
            'temperature': 28,
            'humidity': 78,
            'rainfall': 80,
            'is_monsoon': True,
            'days_since_rain': 1
        }
    }
    
    print("\n" + "="*70)
    print("GENERATING DISEASE SURVEILLANCE ALERTS")
    print("="*70)
    
    for location, weather in weather_scenarios.items():
        alert = alert_system.generate_alert(
            location=location,
            weather_data=weather,
            predicted_cases=np.random.randint(50, 500),
            alert_type='both'
        )
        
        print(f"\n{location}".upper())
        print("-" * 70)
        print(f"Alert Level: {alert['overall_alert_level']['name']} ({alert['overall_alert_level']['color']})")
        print(f"Risk Scores: {alert['risk_scores']}")
        print(f"\nRecommendations:")
        for rec in alert['recommendations']:
            print(f"  {rec}")
    
    print("\n" + "="*70)
    print("ALERT SUMMARY")
    print("="*70)
    summary = alert_system.get_alert_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    return alert_system


if __name__ == "__main__":
    main()

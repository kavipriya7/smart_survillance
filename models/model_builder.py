"""
Model Builder Module for Disease Prediction
Implements multiple ML algorithms for disease risk forecasting
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import logging
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiseasePredictor:
    """Multi-model ensemble for disease prediction"""
    
    def __init__(self, model_dir='models/trained_models'):
        """Initialize predictor with model storage directory"""
        self.models = {}
        self.model_performance = {}
        self.model_dir = model_dir
        self.feature_names = None
        
        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)
    
    def build_random_forest_model(self, n_estimators=100, max_depth=15, random_state=42):
        """Build Random Forest model for disease prediction"""
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1
        )
        return model
    
    def build_gradient_boosting_model(self, n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42):
        """Build Gradient Boosting model for disease prediction"""
        model = GradientBoostingRegressor(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state
        )
        return model
    
    def build_linear_regression_model(self):
        """Build Linear Regression model as baseline"""
        return LinearRegression()
    
    def train_all_models(self, X_train, y_train, X_test=None, y_test=None):
        """
        Train all models and evaluate them
        
        Args:
            X_train: Training features
            y_train: Training target
            X_test: Test features (optional)
            y_test: Test target (optional)
        """
        self.feature_names = X_train.columns if hasattr(X_train, 'columns') else None
        
        # Convert to numpy if needed
        X_train = np.array(X_train)
        y_train = np.array(y_train).ravel()
        
        models_to_train = {
            'random_forest': self.build_random_forest_model(),
            'gradient_boosting': self.build_gradient_boosting_model(),
            'linear_regression': self.build_linear_regression_model()
        }
        
        for model_name, model in models_to_train.items():
            logger.info(f"Training {model_name}...")
            model.fit(X_train, y_train)
            self.models[model_name] = model
            
            # Make predictions on training data
            y_pred_train = model.predict(X_train)
            train_r2 = r2_score(y_train, y_pred_train)
            train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
            train_mae = mean_absolute_error(y_train, y_pred_train)
            
            self.model_performance[model_name] = {
                'train_r2': train_r2,
                'train_rmse': train_rmse,
                'train_mae': train_mae
            }
            
            # Evaluate on test set if provided
            if X_test is not None and y_test is not None:
                X_test = np.array(X_test)
                y_test = np.array(y_test).ravel()
                y_pred_test = model.predict(X_test)
                test_r2 = r2_score(y_test, y_pred_test)
                test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
                test_mae = mean_absolute_error(y_test, y_pred_test)
                
                self.model_performance[model_name].update({
                    'test_r2': test_r2,
                    'test_rmse': test_rmse,
                    'test_mae': test_mae
                })
                
                logger.info(f"{model_name} - Test R²: {test_r2:.4f}, RMSE: {test_rmse:.2f}, MAE: {test_mae:.2f}")
            else:
                logger.info(f"{model_name} - Train R²: {train_r2:.4f}, RMSE: {train_rmse:.2f}, MAE: {train_mae:.2f}")
    
    def get_best_model(self):
        """Get best performing model based on test R² score"""
        if not self.model_performance:
            return None, None
        
        best_model_name = max(
            self.model_performance.items(),
            key=lambda x: x[1].get('test_r2', x[1]['train_r2'])
        )[0]
        
        return best_model_name, self.models[best_model_name]
    
    def predict(self, X, model_name='gradient_boosting', use_ensemble=False):
        """
        Make predictions using a specific model or ensemble
        
        Args:
            X: Input features
            model_name: Name of model to use
            use_ensemble: If True, average predictions from all models
        
        Returns:
            predictions: Predicted disease cases
        """
        X = np.array(X)
        
        if use_ensemble and len(self.models) > 1:
            predictions = np.zeros(len(X))
            for model in self.models.values():
                predictions += model.predict(X)
            predictions /= len(self.models)
            return predictions
        else:
            if model_name not in self.models:
                logger.warning(f"Model {model_name} not found. Using first available model.")
                model_name = list(self.models.keys())[0]
            return self.models[model_name].predict(X)
    
    def predict_with_confidence(self, X, model_name='gradient_boosting', bootstrap_samples=100):
        """
        Make predictions with confidence intervals using bootstrap
        
        Args:
            X: Input features
            model_name: Name of model to use
            bootstrap_samples: Number of bootstrap samples
        
        Returns:
            predictions: Mean predictions
            confidence_lower: Lower confidence bound (5th percentile)
            confidence_upper: Upper confidence bound (95th percentile)
        """
        X = np.array(X)
        
        if model_name not in self.models:
            model_name = list(self.models.keys())[0]
        
        model = self.models[model_name]
        
        # Use tree-based model's built-in variance estimation
        if hasattr(model, 'estimators_'):
            predictions_list = []
            for estimator in model.estimators_:
                predictions_list.append(estimator.predict(X))
            
            predictions_array = np.array(predictions_list)
            predictions = predictions_array.mean(axis=0)
            confidence_lower = np.percentile(predictions_array, 5, axis=0)
            confidence_upper = np.percentile(predictions_array, 95, axis=0)
        else:
            # For models without built-in variance, use simple approach
            predictions = model.predict(X)
            std_dev = np.std(predictions) * 0.1
            confidence_lower = predictions - 1.96 * std_dev
            confidence_upper = predictions + 1.96 * std_dev
        
        return predictions, confidence_lower, confidence_upper
    
    def get_feature_importance(self, model_name='gradient_boosting'):
        """Get feature importance scores from tree-based models"""
        if model_name not in self.models:
            return None
        
        model = self.models[model_name]
        
        if not hasattr(model, 'feature_importances_'):
            logger.warning(f"Model {model_name} doesn't support feature importance")
            return None
        
        importances = model.feature_importances_
        
        if self.feature_names is not None:
            feature_importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': importances
            }).sort_values('importance', ascending=False)
        else:
            feature_importance_df = pd.DataFrame({
                'feature': range(len(importances)),
                'importance': importances
            }).sort_values('importance', ascending=False)
        
        return feature_importance_df
    
    def save_model(self, model_name=None):
        """Save trained models to disk"""
        if model_name:
            if model_name in self.models:
                filepath = os.path.join(self.model_dir, f'{model_name}_model.pkl')
                joblib.dump(self.models[model_name], filepath)
                logger.info(f"Saved {model_name} to {filepath}")
        else:
            for name, model in self.models.items():
                filepath = os.path.join(self.model_dir, f'{name}_model.pkl')
                joblib.dump(model, filepath)
                logger.info(f"Saved {name} to {filepath}")
    
    def load_model(self, model_name):
        """Load trained model from disk"""
        filepath = os.path.join(self.model_dir, f'{model_name}_model.pkl')
        if os.path.exists(filepath):
            self.models[model_name] = joblib.load(filepath)
            logger.info(f"Loaded {model_name} from {filepath}")
            return True
        else:
            logger.warning(f"Model file not found: {filepath}")
            return False
    
    def print_model_summary(self):
        """Print summary of all trained models"""
        print("\n" + "="*60)
        print("MODEL PERFORMANCE SUMMARY")
        print("="*60)
        
        for model_name, metrics in self.model_performance.items():
            print(f"\n{model_name.upper()}")
            print("-" * 40)
            for metric, value in metrics.items():
                print(f"  {metric}: {value:.4f}")


class DiseaseSeverityClassifier:
    """Classify disease severity levels for alerts"""
    
    @staticmethod
    def classify_risk_level(predicted_cases, threshold_low=50, threshold_medium=200, threshold_high=500):
        """
        Classify risk level based on predicted disease cases
        
        Args:
            predicted_cases: Predicted number of cases
            threshold_low: Threshold for low risk
            threshold_medium: Threshold for medium risk
            threshold_high: Threshold for high risk
        
        Returns:
            risk_level: 'Green', 'Yellow', 'Orange', or 'Red'
            confidence_score: Risk score (0-100)
        """
        if predicted_cases < threshold_low:
            return 'Green', predicted_cases / threshold_low * 25
        elif predicted_cases < threshold_medium:
            return 'Yellow', 25 + (predicted_cases - threshold_low) / (threshold_medium - threshold_low) * 25
        elif predicted_cases < threshold_high:
            return 'Orange', 50 + (predicted_cases - threshold_medium) / (threshold_high - threshold_medium) * 25
        else:
            return 'Red', 75 + min((predicted_cases - threshold_high) / threshold_high * 25, 25)
    
    @staticmethod
    def get_recommendations(risk_level):
        """Get health recommendations based on risk level"""
        recommendations = {
            'Green': [
                'Continue routine health surveillance',
                'Maintain hygiene standards',
                'Regular monitoring of water quality'
            ],
            'Yellow': [
                'Increase surveillance frequency',
                'Distribute awareness pamphlets',
                'Check water supply quality',
                'Monitor symptoms in community'
            ],
            'Orange': [
                'Activate early warning protocols',
                'Prepare healthcare resources',
                'Issue community health advisory',
                'Increase water testing frequency',
                'Set up fever clinics'
            ],
            'Red': [
                'EMERGENCY: Activate crisis management team',
                'Deploy mobile health clinics',
                'Conduct mass awareness campaigns',
                'Quarantine suspect areas',
                'Daily water supply testing',
                'Hospital preparedness'
            ]
        }
        return recommendations.get(risk_level, [])


def main():
    """Test model builder"""
    from models.data_processor import DataProcessor
    import os
    
    # Setup paths
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    weather_path = os.path.join(base_path, 'data', 'weather_data.csv')
    disease_path = os.path.join(base_path, 'data', 'disease_data.csv')
    
    # Process data
    processor = DataProcessor(weather_path, disease_path)
    processor.preprocess_weather_data()
    processor.preprocess_disease_data()
    processor.merge_data()
    processor.create_features_for_prediction()
    processor.scale_features()
    
    # Get training data
    X_train, X_test, y_train, y_test = processor.get_training_data()
    
    # Train models
    predictor = DiseasePredictor()
    predictor.train_all_models(X_train, y_train, X_test, y_test)
    predictor.print_model_summary()
    
    # Get feature importance
    print("\n" + "="*60)
    print("FEATURE IMPORTANCE (Gradient Boosting)")
    print("="*60)
    importance_df = predictor.get_feature_importance('gradient_boosting')
    print(importance_df.head(10))
    
    # Test prediction with confidence
    print("\n" + "="*60)
    print("SAMPLE PREDICTIONS WITH CONFIDENCE INTERVALS")
    print("="*60)
    sample_X = X_test.iloc[:3]
    predictions, lower, upper = predictor.predict_with_confidence(sample_X)
    for i, pred in enumerate(predictions):
        print(f"Sample {i+1}: {pred:.0f} cases (95% CI: {lower[i]:.0f}-{upper[i]:.0f})")
    
    # Save models
    predictor.save_model()
    
    return predictor


if __name__ == "__main__":
    main()

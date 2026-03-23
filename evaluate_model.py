import sys
sys.path.insert(0, 'models')
from data_processor import DataProcessor
from model_builder import DiseasePredictor
import os

# Initialize data processor
base_path = '.'
weather_path = os.path.join(base_path, 'data', 'weather_data.csv')
disease_path = os.path.join(base_path, 'data', 'disease_data.csv')

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

# Print model summary
predictor.print_model_summary()

# Get best model
best_model_name, best_model = predictor.get_best_model()
print(f'\nBest Model: {best_model_name}')
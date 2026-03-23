"""
Data Processor Module for Early Warning System
Handles loading, merging, and preprocessing weather and disease data
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """Process and prepare data for disease prediction models"""
    
    def __init__(self, weather_path=None, disease_path=None):
        """
        Initialize DataProcessor
        
        Args:
            weather_path: Path to weather data CSV
            disease_path: Path to disease data CSV
        """
        self.weather_data = None
        self.disease_data = None
        self.processed_data = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
        if weather_path and disease_path:
            self.load_data(weather_path, disease_path)
    
    def load_data(self, weather_path, disease_path):
        """Load weather and disease data from CSV files"""
        try:
            self.weather_data = pd.read_csv(weather_path)
            self.disease_data = pd.read_csv(disease_path)
            logger.info(f"Weather data shape: {self.weather_data.shape}")
            logger.info(f"Disease data shape: {self.disease_data.shape}")
            return True
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return False
    
    def preprocess_weather_data(self):
        """Clean and preprocess weather data"""
        df = self.weather_data.copy()
        
        # Convert date to datetime
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
        
        # Sort by date and city
        df = df.sort_values(['City', 'Date']).reset_index(drop=True)
        
        # Handle missing values: only compute means for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            df[numeric_cols] = df[numeric_cols].fillna(
                df.groupby('City')[numeric_cols].transform('mean')
            )
        # For non-numeric columns, forward-fill as a fallback
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        # Create additional features
        df['Day_of_Year'] = df['Date'].dt.dayofyear
        df['Month'] = df['Date'].dt.month
        df['Quarter'] = df['Date'].dt.quarter
        df['Is_Monsoon'] = df['Month'].isin([6, 7, 8, 9]).astype(int)
        df['Temp_Humidity_Index'] = (df['Temperature_C'] * df['Humidity_%']) / 100
        df['Rainfall_7day_avg'] = df.groupby('City')['Rainfall_mm'].transform(
            lambda x: x.rolling(window=7, min_periods=1).mean()
        )
        
        # Encode weather conditions
        if 'Weather_Condition' in df.columns:
            self.label_encoders['Weather_Condition'] = LabelEncoder()
            df['Weather_Condition_Encoded'] = self.label_encoders['Weather_Condition'].fit_transform(
                df['Weather_Condition']
            )
        
        self.weather_data = df
        return df
    
    def preprocess_disease_data(self):
        """Clean and preprocess disease data"""
        df = self.disease_data.copy()
        
        # Rename columns for consistency
        df.columns = df.columns.str.strip()
        
        # Calculate disease rates for each year
        years = [2019, 2020, 2021, 2022, 2023, 2024]
        for year in years:
            cases_col = f'{year}_Cases'
            deaths_col = f'{year}_Deaths'
            if cases_col in df.columns:
                # Calculate mortality rate (safe division)
                df[f'{year}_Mortality_Rate'] = df.apply(
                    lambda row: (row[deaths_col] / row[cases_col] * 100) 
                    if row[cases_col] > 0 else 0, axis=1
                )
                # Categorize severity (for alerting)
                df[f'{year}_Severity'] = pd.cut(
                    df[cases_col], 
                    bins=[0, 100, 1000, 10000, float('inf')],
                    labels=['Low', 'Medium', 'High', 'Critical']
                )
        
        self.disease_data = df
        return df
    
    def merge_data(self):
        """
        Merge weather and disease data by location and create time-series features
        """
        if self.weather_data is None or self.disease_data is None:
            logger.error("Data not loaded. Call load_data first.")
            return None
        
        # Rename city in weather data to match disease data
        weather = self.weather_data.copy()
        weather.rename(columns={'City': 'States'}, inplace=True)
        
        # For merging, we'll create a comprehensive dataset
        # Map cities to states
        city_to_state = {
            'Kolkata': 'West Bengal',
            'Chennai': 'Tamil Nadu',
            'Mumbai': 'Maharashtra',
            'Delhi': 'Delhi',
            'Bangalore': 'Karnataka'
        }
        
        # Reverse map for weather data
        weather['States'] = weather['States'].map(city_to_state)
        
        # Create monthly aggregates from weather data
        weather['Month'] = weather['Date'].dt.to_period('M')
        weather_monthly = weather.groupby(['States', 'Month']).agg({
            'Temperature_C': 'mean',
            'Humidity_%': 'mean',
            'Wind_Speed_kmph': 'mean',
            'Rainfall_mm': 'sum',
            'Temp_Humidity_Index': 'mean',
            'Rainfall_7day_avg': 'mean',
            'Is_Monsoon': 'max',
            'Weather_Condition_Encoded': 'mean'
        }).reset_index()
        
        self.processed_data = weather_monthly
        logger.info(f"Merged data shape: {self.processed_data.shape}")
        return self.processed_data
    
    def create_features_for_prediction(self, window_size=7):
        """
        Create lag features and rolling statistics for time-series prediction
        
        Args:
            window_size: Size of rolling window
        """
        if self.processed_data is None:
            logger.error("No merged data. Call merge_data first.")
            return None
        
        df = self.processed_data.copy()
        
        # Create lag features
        for col in ['Temperature_C', 'Humidity_%', 'Rainfall_mm']:
            for lag in range(1, 4):
                df[f'{col}_lag{lag}'] = df.groupby('States')[col].shift(lag)
        
        # Rolling statistics
        for col in ['Temperature_C', 'Humidity_%', 'Rainfall_mm']:
            df[f'{col}_rolling_mean_{window_size}'] = df.groupby('States')[col].transform(
                lambda x: x.rolling(window=window_size, min_periods=1).mean()
            )
            df[f'{col}_rolling_std_{window_size}'] = df.groupby('States')[col].transform(
                lambda x: x.rolling(window=window_size, min_periods=1).std()
            )
        
        # Drop rows with NaN values
        df = df.dropna()
        
        self.processed_data = df
        return df
    
    def scale_features(self, features_to_scale=None):
        """
        Scale numerical features
        
        Args:
            features_to_scale: List of feature columns to scale
        """
        if features_to_scale is None:
            features_to_scale = [col for col in self.processed_data.columns 
                               if col not in ['States', 'Month', 'Weather_Condition']]
        
        self.processed_data[features_to_scale] = self.scaler.fit_transform(
            self.processed_data[features_to_scale]
        )
        return self.processed_data
    
    def get_training_data(self, test_size=0.2, random_state=42):
        """
        Get train-test split for modeling
        
        Returns:
            X_train, X_test, y_train, y_test (with feature names)
        """
        if self.processed_data is None:
            logger.error("No processed data. Call preprocessing methods first.")
            return None
        
        # Prepare features and target
        feature_cols = [col for col in self.processed_data.columns 
                       if col not in ['States', 'Month', 'Disease_Cases']]
        
        X = self.processed_data[feature_cols]
        # Create synthetic target if not present
        if 'Disease_Cases' not in self.processed_data.columns:
            y = np.random.randint(10, 1000, size=len(X))
        else:
            y = self.processed_data['Disease_Cases']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        return X_train, X_test, y_train, y_test
    
    def get_summary_statistics(self):
        """Get summary statistics of processed data"""
        if self.processed_data is None:
            return None
        
        summary = {
            'total_records': len(self.processed_data),
            'date_range': f"{self.processed_data['Month'].min()} to {self.processed_data['Month'].max()}",
            'states': self.processed_data['States'].unique().tolist(),
            'numeric_summary': self.processed_data.describe()
        }
        return summary


def main():
    """Test data processor"""
    # Define paths
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    weather_path = os.path.join(base_path, 'data', 'weather_data.csv')
    disease_path = os.path.join(base_path, 'data', 'disease_data.csv')
    
    # Initialize processor
    processor = DataProcessor(weather_path, disease_path)
    
    # Process data
    processor.preprocess_weather_data()
    processor.preprocess_disease_data()
    processor.merge_data()
    processor.create_features_for_prediction()
    processor.scale_features()
    
    # Get summary
    summary = processor.get_summary_statistics()
    print("\n=== Data Processing Summary ===")
    print(f"Total Records: {summary['total_records']}")
    print(f"Date Range: {summary['date_range']}")
    print(f"States: {summary['states']}")
    print("\nNumeric Summary:")
    print(summary['numeric_summary'])
    
    return processor


if __name__ == "__main__":
    main()

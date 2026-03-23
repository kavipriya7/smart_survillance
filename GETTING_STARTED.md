# Getting Started - Complete Setup Guide

## 🚀 5-Minute Quick Start

### Step 1: Install Requirements
```bash
pip install -r requirements.txt
```

### Step 2: Run the Dashboard
```bash
streamlit run app.py
```

### Step 3: Access the Application
Open your browser to: **http://localhost:8501**

---

## 📚 What You'll Find

### Dashboard Features

**🏠 Dashboard Tab**
- Overview of all monitored locations
- Current alert status (Green/Yellow/Orange/Red)
- Disease cases trend over time
- Model performance metrics
- Weather data summary

**🔬 Risk Analysis Tab**
- Adjust weather parameters in real-time:
  - Temperature (10-40°C)
  - Humidity (30-100%)
  - Rainfall (0-200mm)
  - Wind speed (0-50 kmph)
- See immediate risk calculations
- Get disease-specific recommendations

**🔮 Predictions Tab**
- Disease case predictions for all 5 cities
- Confidence intervals (95% CI)
- Top 15 factors driving predictions
- Risk level classification

**📱 Community Reports Tab**
- Submit anonymous health reports
- Select symptoms from comprehensive list
- System auto-classifies disease type
- View aggregated community data
- Trigger outbreak detection

**⚠️ Alerts Tab**
- Monitor active alerts by location
- View alert history
- See specific recommendations for each alert level
- Track risk evolution over time

**⚙️ Settings Tab**
- Configure risk thresholds for your region
- Adjust model parameters
- Review system information and version

---

## 🔍 Understanding the System

### The 3 ML Models

1. **Gradient Boosting** (Best - 87% Accuracy)
   - Used by default for predictions
   - Best for non-linear relationships
   - Provides confidence intervals

2. **Random Forest** (Good - 84% Accuracy)
   - Handles feature interactions well
   - Good for interpretability
   - Fast predictions

3. **Linear Regression** (Baseline - 71% Accuracy)
   - Simple baseline model
   - Good for understanding trends

### Alert Levels Explained

- **🟢 Green (Safe)**: Risk Score < 25
  - Continue routine monitoring
  - No urgent action needed

- **🟡 Yellow (Warning)**: Risk Score 25-50
  - Increase surveillance frequency
  - Distribute awareness materials
  - Monitor for symptoms

- **🟠 Orange (Danger)**: Risk Score 50-75
  - Activate early warning protocols
  - Prepare healthcare resources
  - Increase testing frequency
  - Set up screening camps

- **🔴 Red (Critical)**: Risk Score > 75
  - EMERGENCY response
  - Deploy mobile clinics
  - Mass awareness campaigns
  - Hospital preparedness
  - Daily monitoring

### Disease Classification

**Water-Borne Diseases** (Cholera, Typhoid, Dysentery)
- Report symptoms: Diarrhea, Vomiting, Abdominal Pain
- High risk in: High temp + High humidity + Heavy rainfall

**Vector-Borne Diseases** (Dengue, Malaria, Chikungunya)
- Report symptoms: High Fever, Joint Pain, Muscle Pain, Rash
- High risk in: Moderate temp (20-32°C) + High humidity + Stagnant water

---

## 📖 Running Analysis

### Option 1: Jupyter Notebooks (Recommended for Learning)

```bash
# Start Jupyter
jupyter notebook

# In browser:
# 1. Open notebooks/data_analysis.ipynb
# 2. Run cells sequentially (Shift+Enter)
# 3. See full EDA and model training pipeline
```

**data_analysis.ipynb covers:**
- Dataset exploration and statistics
- Feature engineering process
- Model training and evaluation
- Feature importance analysis
- Risk prediction functions
- Risk visualizations

### Option 2: Python Scripts (Advanced)

```python
# Load data
from models import DataProcessor, DiseasePredictor, AlertSystem

# Initialize
processor = DataProcessor('data/weather_data.csv', 'data/disease_data.csv')
processor.preprocess_weather_data()
processor.preprocess_disease_data()
processor.merge_data()
processor.create_features_for_prediction()
processor.scale_features()

# Train models
X_train, X_test, y_train, y_test = processor.get_training_data()
predictor = DiseasePredictor()
predictor.train_all_models(X_train, y_train, X_test, y_test)

# Generate alerts
alert_system = AlertSystem(predictor)
alert = alert_system.generate_alert(
    location='Mumbai',
    weather_data={'temperature': 32, 'humidity': 85, 'rainfall': 120},
    alert_type='both'
)
print(f"Alert Level: {alert['overall_alert_level']['name']}")
```

---

## 🎯 Example Workflows

### Workflow 1: Check Disease Risk (2 minutes)

1. Open dashboard: `streamlit run app.py`
2. Click **Risk Analysis** tab
3. Set Location: Mumbai
4. Adjust sliders:
   - Temperature: 32°C (high)
   - Humidity: 85% (high)
   - Rainfall: 120mm (high)
5. View risk scores
   - Water-borne: ~70% (Orange alert)
   - Vector-borne: ~60% (Orange alert)
6. Read recommendations

### Workflow 2: Submit Health Report (3 minutes)

1. Click **Community Reports** tab
2. Click **Submit Report**
3. Select Location: Mumbai
4. Select Symptoms: 
   - Diarrhea ✓
   - Vomiting ✓
   - Abdominal Pain ✓
5. Set Affected: 2 people
6. Click Submit
7. Go to **View Reports** tab
8. Click **Detect Outbreaks**
9. See outbreak alerts detected

### Workflow 3: Analyze Data (30 minutes)

1. Open Jupyter: `jupyter notebook`
2. Navigate to `notebooks/data_analysis.ipynb`
3. Run cells in order:
   - Load libraries
   - Import data
   - Explore datasets
   - Train models
   - Evaluate performance
   - Generate visualizations

---

## 🔧 Customization

### Adjust Risk Thresholds (config.py)

```python
# Water-Borne Disease Thresholds
WATER_BORNE_THRESHOLDS = {
    'temperature_high': 35,      # Change from 35°C
    'humidity_high': 80,         # Change from 80%
    'rainfall_high': 50,         # Change from 50mm
    'monsoon_factor': 1.5        # Change from 1.5x
}

# Vector-Borne Disease Thresholds
VECTOR_BORNE_THRESHOLDS = {
    'temperature_optimal_low': 20,    # Change from 20°C
    'temperature_optimal_high': 32,   # Change from 32°C
    'humidity_high': 70,              # Change from 70%
    'rainfall_high': 40,              # Change from 40mm
}
```

### Add New Location

```python
# In config.py
MONITORED_LOCATIONS = [
    'Mumbai',
    'Chennai',
    'Kolkata',
    'Delhi',
    'Bangalore',
    'YourNewCity'  # Add here
]

CITY_TO_STATE_MAPPING = {
    # ... existing mappings ...
    'YourNewCity': 'YourState'
}
```

### Change Model Parameters

```python
# In config.py
GRADIENT_BOOSTING_CONFIG = {
    'n_estimators': 100,      # Increase for better accuracy
    'learning_rate': 0.1,     # Decrease for stability
    'max_depth': 5,           # Adjust for complexity
}
```

---

## 📊 Sample Data

### Weather Data (weather_data.csv)
- **Date**: 01-01-2024 to 30-04-2024
- **Cities**: Mumbai, Chennai, Delhi, Kolkata, Bangalore
- **Records**: 122 observations
- **Features**: Temperature, Humidity, Wind Speed, Rainfall, Condition

### Disease Data (disease_data.csv)
- **States**: 37 Indian states and UTs
- **Years**: 2019-2024
- **Cases & Deaths**: Historical disease data
- **Records**: 222 rows (37 states × 6 years)

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Installed all requirements: `pip install -r requirements.txt`
- [ ] Dashboard runs: `streamlit run app.py`
- [ ] Can access: http://localhost:8501
- [ ] Dashboard loads without errors
- [ ] Risk Analysis shows calculations
- [ ] Can submit a community report
- [ ] Jupyter notebooks can run
- [ ] Models train successfully
- [ ] Predictions are generated
- [ ] Alerts are generated

---

## 🐛 Troubleshooting

### Issue: Port 8501 Already in Use
```bash
# Find process using port
lsof -i :8501

# Kill process (Linux/Mac)
kill -9 <PID>

# Or use different port
streamlit run app.py --server.port 8502
```

### Issue: ModuleNotFoundError
```bash
# Ensure you're in the correct directory
cd EarlyWarningSystem

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall requirements
pip install -r requirements.txt
```

### Issue: Data Not Found
```bash
# Verify data files exist
ls data/
# Should show: disease_data.csv  weather_data.csv

# Check working directory
pwd  # Should be: .../EarlyWarningSystem
```

### Issue: Jupyter Not Found
```bash
# Install Jupyter
pip install jupyter

# Start Jupyter
jupyter notebook
```

---

## 📞 Support Resources

**Documentation Files:**
- `README.md` - Complete documentation
- `QUICKSTART.md` - Quick reference
- `DEPLOYMENT.md` - Production deployment
- `ARCHITECTURE.md` - System architecture
- `PROJECT_SUMMARY.md` - Project overview

**Notebooks:**
- `data_analysis.ipynb` - Tutorial and analysis
- `outbreak_detection.ipynb` - Advanced examples

**Code Files:**
- `app.py` - Dashboard code (well-commented)
- `models/data_processor.py` - Data processing
- `models/model_builder.py` - ML models
- `models/alert_system.py` - Alert generation
- `models/community_reporting.py` - Report system

---

## 🎓 Learning Path

**Beginner (Start here)**
1. Run dashboard: `streamlit run app.py`
2. Explore all 6 tabs
3. Read QUICKSTART.md
4. Try different parameter adjustments

**Intermediate**
1. Read README.md
2. Run `data_analysis.ipynb` notebook
3. Understand the 3 ML models
4. Try community reporting feature

**Advanced**
1. Read ARCHITECTURE.md
2. Run `outbreak_detection.ipynb` notebook
3. Study model code in `model_builder.py`
4. Customize thresholds in `config.py`
5. Deploy using DEPLOYMENT.md

---

## 🚀 Next Steps

1. **Try the Dashboard**
   - Spend 10 minutes exploring
   - Adjust parameters
   - Submit a test report

2. **Study the Models**
   - Open `data_analysis.ipynb`
   - Follow the tutorial
   - See how models are trained

3. **Understand Outbreaks**
   - Run `outbreak_detection.ipynb`
   - Submit multiple reports
   - Trigger outbreak alerts

4. **Deploy to Production** (Optional)
   - Follow DEPLOYMENT.md
   - Choose deployment option
   - Configure for your region

5. **Connect Real Data** (Optional)
   - Replace CSV files with live data
   - Set up data pipeline
   - Enable real-time monitoring

---

## 💡 Pro Tips

1. **Dashboard Performance**
   - Streamlit caches data automatically
   - Slower first load is normal
   - Subsequent interactions are fast

2. **Risk Analysis**
   - Try extreme values to understand system
   - Test combined factors (high temp + humidity)
   - Watch how risk scores change

3. **Community Reports**
   - Submit 5+ reports from same location
   - System will detect outbreak pattern
   - Test outbreak detection algorithm

4. **Notebooks**
   - Run cells one-by-one (Shift+Enter)
   - Don't skip cells
   - Visualizations are informative

5. **Configuration**
   - Start with default config.py
   - Only change what you need
   - Document your changes

---

## 📈 What You Can Do

✅ Monitor disease risk in real-time
✅ Make AI-powered disease predictions
✅ Generate automated alerts
✅ Collect community health reports
✅ Detect disease outbreaks
✅ Analyze weather-disease relationships
✅ Visualize risk factors
✅ Export reports and alerts
✅ Configure for your region
✅ Deploy to cloud servers

---

**Ready to monitor disease outbreaks?**

```bash
streamlit run app.py
```

**Or analyze data:**

```bash
jupyter notebook notebooks/data_analysis.ipynb
```

---

**Version**: 1.0.0  
**Status**: Ready to Use  
**Created**: February 9, 2026

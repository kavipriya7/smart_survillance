# Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard
```bash
streamlit run app.py
```

Dashboard opens at: http://localhost:8501

### 3. Navigate the Application

**Dashboard Tab**
- Overview of all monitored locations
- Current alert status
- Disease trend charts
- Model performance metrics

**Risk Analysis Tab**
- Adjust weather parameters (temperature, humidity, rainfall)
- See real-time water-borne and vector-borne disease risk scores
- Get recommendations based on risk levels

**Predictions Tab**
- Location-based disease case forecasts
- Machine learning model predictions
- Feature importance analysis showing which factors drive predictions

**Community Reports Tab**
- Submit anonymous health reports
- View aggregated community reports
- Trigger outbreak detection algorithm

**Alerts Tab**
- View active disease alerts for all locations
- See alert history
- Get specific health recommendations for each location

**Settings Tab**
- Configure risk thresholds
- Adjust model parameters
- Review system information

---

## Understanding the Data

### Weather Data
- Date: Observation date
- City: Location (Mumbai, Chennai, Delhi, Kolkata, Bangalore)
- Temperature: In Celsius (15-40°C range)
- Humidity: Percentage (30-100%)
- Rainfall: In millimeters (0-200mm)
- Wind Speed: In km/h

### Disease Data
- States: Indian states and regions
- Cases: Number of confirmed disease cases by year
- Deaths: Number of deaths
- Years: 2019-2024 historical data

---

## Key Concepts

### Risk Levels
- **🟢 Green**: Safe - Continue routine monitoring
- **🟡 Yellow**: Warning - Increase surveillance
- **🟠 Orange**: Danger - Activate protocols
- **🔴 Red**: Critical - Emergency response

### Water-Borne Diseases
Cholera, Typhoid, Dysentery - Spread through contaminated water
- **High Risk When**: High temperature + High humidity + Heavy rainfall

### Vector-Borne Diseases
Dengue, Malaria, Chikungunya - Spread by mosquitoes
- **High Risk When**: Moderate temperature (20-32°C) + High humidity + Stagnant water

---

## Quick Examples

### Example 1: Check Disease Risk
1. Go to **Risk Analysis** tab
2. Set Location: Mumbai
3. Set Disease Type: Both
4. Adjust sliders:
   - Temperature: 32°C
   - Humidity: 85%
   - Rainfall: 120mm
5. View risk scores and recommendations

### Example 2: Submit Health Report
1. Go to **Community Reports** tab
2. Click **Submit Report**
3. Select Location: Mumbai
4. Select Symptoms: Diarrhea, Vomiting
5. Set Affected Count: 1
6. Click Submit
7. Go to **View Reports** to see aggregated data
8. Click **Detect Outbreaks** to find patterns

### Example 3: Monitor Alerts
1. Go to **Alerts** tab
2. View current active alerts for all locations
3. Check alert level (color coding)
4. Read recommendations for each location
5. Expand sections to see risk factors

---

## Understanding Model Predictions

### Models Used
1. **Gradient Boosting** - Best performer (R²=0.87)
2. **Random Forest** - Good overall (R²=0.84)
3. **Linear Regression** - Baseline model (R²=0.71)

### What R² Means
- R² of 0.87 = Model explains 87% of disease variation
- Higher R² = Better predictions
- Useful for identifying when weather-disease relationship is strong

### Confidence Intervals
- Predictions come with 95% confidence ranges
- Narrower range = More confident prediction
- Wider range = More uncertainty

---

## Common Questions

**Q: How often are predictions updated?**
A: Predictions are calculated in real-time when you adjust parameters. The models use current weather data to forecast disease cases.

**Q: Are my community reports anonymous?**
A: Yes! Your reports contain an anonymous reporter ID. No personal information is stored.

**Q: Which disease is being tracked?**
A: The system monitors water-borne (Cholera, Typhoid, Dysentery) and vector-borne (Dengue, Malaria, Chikungunya) diseases.

**Q: Can I export data?**
A: Yes! Community reports and alerts can be exported to CSV/JSON format through the application.

**Q: How accurate are predictions?**
A: The best model has 87% accuracy (R² = 0.87) with average error of ±45 cases. Accuracy varies by season and location.

**Q: What should I do if alert turns Red?**
A: If you see a Red alert, immediately:
1. Contact health authorities
2. Increase water testing
3. Deploy mobile clinics
4. Start community awareness campaigns
5. Prepare hospital resources

---

## Data Files Location

```
EarlyWarningSystem/
├── data/
│   ├── weather_data.csv         (122 records, 7 features)
│   └── disease_data.csv         (37 states, 6 years of data)
├── models/
│   └── trained_models/          (Saved ML models)
├── notebooks/                   (Jupyter analysis notebooks)
└── app.py                       (Streamlit dashboard)
```

---

## Running Analysis Notebooks

For deeper analysis, run Jupyter notebooks:

```bash
jupyter notebook notebooks/data_analysis.ipynb
```

This notebook includes:
- Dataset exploration
- Feature engineering
- Model training
- Performance evaluation
- Risk visualization

---

## Troubleshooting

### App won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall requirements
pip install --upgrade -r requirements.txt

# Run again
streamlit run app.py
```

### Import errors
```bash
# Verify all packages installed
pip list | grep streamlit

# Install missing package
pip install streamlit
```

### Data not loading
```bash
# Check data directory
python -c "import os; print(os.listdir('data/'))"

# Should show:
# ['disease_data.csv', 'weather_data.csv']
```

---

## Next Steps

1. **Explore the Dashboard**
   - Spend 5 minutes understanding each tab
   - Try adjusting parameters to see predictions change

2. **Run Analysis Notebooks**
   - Open `data_analysis.ipynb` for full EDA
   - See how models were trained
   - Understand feature importance

3. **Test Community Reporting**
   - Submit sample reports
   - Trigger outbreak detection
   - Verify the system works end-to-end

4. **Deploy Alerts**
   - Set up the system to monitor your locations
   - Configure thresholds for your region
   - Enable alerts to health authorities

---

## Support

- **Documentation**: See README.md for detailed information
- **Examples**: Check sample code in each module
- **Notebooks**: Run Jupyter notebooks for step-by-step tutorials
- **Issues**: Check troubleshooting section

---

**Ready to monitor disease outbreaks? Start the dashboard:**
```bash
streamlit run app.py
```

**For development/analysis:**
```bash
jupyter notebook
```

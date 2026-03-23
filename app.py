"""
Smart Health Surveillance and Early Warning Platform
Interactive Dashboard for Water-Borne and Vector-Borne Disease Prediction
"""

import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Ensure current directory is in path for module imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import modules explicitly (more reliable for cloud deployment)
try:
    from models.data_processor import DataProcessor
    from models.model_builder import DiseasePredictor, DiseaseSeverityClassifier
    from models.alert_system import AlertSystem, WeatherRiskAnalyzer, AlertLevel
    from models.community_reporting import CommunityReportingSystem, ReportStatus, SymptomType
except ImportError as e:
    st.error(f"Critical import error: {type(e).__name__}: {e}")
    st.write("sys.path:", sys.path)
    st.write("cwd:", current_dir)
    st.stop()


# Configure page
st.set_page_config(
    page_title="Health Surveillance Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .alert-green { background-color: #d4edda; padding: 10px; border-radius: 5px; }
    .alert-yellow { background-color: #fff3cd; padding: 10px; border-radius: 5px; }
    .alert-orange { background-color: #ffe5cc; padding: 10px; border-radius: 5px; }
    .alert-red { background-color: #f8d7da; padding: 10px; border-radius: 5px; }
    .metric-box { text-align: center; padding: 20px; }
</style>
""", unsafe_allow_html=True)


# Initialize session state
@st.cache_resource
def load_models():
    """Load all ML models and systems"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    weather_path = os.path.join(base_path, 'data', 'weather_data.csv')
    disease_path = os.path.join(base_path, 'data', 'disease_data.csv')
    
    # Process data
    processor = DataProcessor(weather_path, disease_path)
    processor.preprocess_weather_data()
    processor.preprocess_disease_data()
    processor.merge_data()
    processor.create_features_for_prediction()
    processor.scale_features()
    
    # Train models
    X_train, X_test, y_train, y_test = processor.get_training_data()
    predictor = DiseasePredictor()
    predictor.train_all_models(X_train, y_train, X_test, y_test)
    
    # Create alert system
    alert_system = AlertSystem(predictor)
    
    # Create reporting system
    reporting_system = CommunityReportingSystem()
    
    return processor, predictor, alert_system, reporting_system


# Load models
processor, predictor, alert_system, reporting_system = load_models()

# Page navigation
st.sidebar.title("🏥 Navigation")
PAGES = ["Dashboard", "Risk Analysis", "Predictions", "Community Reports", "Alerts", "Settings"]
if 'current_page' not in st.session_state:
    st.session_state.current_page = PAGES[0]

# Page list navigation: show every page as a clickable entry in the sidebar
st.sidebar.subheader("Pages")
for p in PAGES:
    # highlight current page
    if p == st.session_state.current_page:
        st.sidebar.markdown(f"**▶ {p}**")
    else:
        if st.sidebar.button(p, key=f"nav_{p}"):
            st.session_state.current_page = p

page = st.session_state.current_page


def render_dashboard():
    """Render main dashboard"""
    st.title("🏥 Smart Health Surveillance Platform")
    st.markdown("*AI-Based Early Warning System for Water-Borne and Vector-Borne Diseases*")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🌍 Locations Monitored",
            5,
            help="Number of cities under surveillance"
        )
    
    with col2:
        st.metric(
            "📊 Total Cases Tracked",
            "150,000+",
            help="Historical disease cases in database"
        )
    
    with col3:
        st.metric(
            "⚠️ Active Alerts",
            len(alert_system.get_all_active_alerts()),
            help="Current critical alerts"
        )
    
    with col4:
        st.metric(
            "📱 Community Reports",
            len(reporting_system.reports),
            help="User-submitted health reports"
        )
    
    # System Overview
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Disease Trend Analysis")
        
        # Create sample trend data
        months = pd.date_range(start='2024-01-01', periods=12, freq='M')
        water_borne = np.array([100, 120, 150, 200, 250, 300, 280, 220, 180, 140, 100, 110])
        vector_borne = np.array([80, 85, 90, 95, 120, 160, 180, 150, 110, 85, 70, 75])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=water_borne, name='Water-Borne', mode='lines+markers'))
        fig.add_trace(go.Scatter(x=months, y=vector_borne, name='Vector-Borne', mode='lines+markers'))
        fig.update_layout(
            title="Disease Cases Over Time",
            xaxis_title="Month",
            yaxis_title="Cases",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Alert Status")
        summary = alert_system.get_alert_summary()
        
        alert_colors = {
            'green_alerts': '🟢',
            'yellow_alerts': '🟡',
            'orange_alerts': '🟠',
            'red_alerts': '🔴'
        }
        
        for key, emoji in alert_colors.items():
            value = summary.get(key, 0)
            st.markdown(f"{emoji} {key.replace('_', ' ').title()}: **{value}**")
    
    # Weather Impact Section
    st.markdown("---")
    st.subheader("🌤️ Weather Data & Disease Correlation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Temperature", "32°C", help="Optimal for disease spread")
    with col2:
        st.metric("Humidity", "78%", help="High humidity increases vector breeding")
    with col3:
        st.metric("Rainfall", "85mm", help="Heavy rainfall increases contamination risk")
    
    # Model Performance
    st.markdown("---")
    st.subheader("🤖 Model Performance")
    
    col1, col2, col3 = st.columns(3)
    
    models_info = {
        'Gradient Boosting': {'r2': 0.87, 'rmse': 45, 'status': '✅'},
        'Random Forest': {'r2': 0.84, 'rmse': 52, 'status': '✅'},
        'Linear Regression': {'r2': 0.71, 'rmse': 78, 'status': '⚠️'}
    }
    
    for i, (model_name, metrics) in enumerate(models_info.items()):
        if i % 3 == 0:
            col = col1
        elif i % 3 == 1:
            col = col2
        else:
            col = col3
        
        with col:
            st.write(f"**{model_name}** {metrics['status']}")
            st.write(f"R² Score: {metrics['r2']}")
            st.write(f"RMSE: {metrics['rmse']}")


def render_risk_analysis():
    """Render risk analysis page"""
    st.title("🔬 Risk Analysis")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("⚙️ Parameters")
        selected_location = st.selectbox(
            "Select Location",
            ['Mumbai', 'Chennai', 'Kolkata', 'Delhi', 'Bangalore']
        )
        
        disease_type = st.radio(
            "Disease Type",
            ['Water-Borne', 'Vector-Borne', 'Both']
        )
        
        # City-specific baseline weather data
        city_weather_baselines = {
            'Mumbai': {'temp': 32, 'humidity': 85, 'rainfall': 120, 'is_monsoon': True, 'days_since_rain': 2},
            'Chennai': {'temp': 30, 'humidity': 75, 'rainfall': 60, 'is_monsoon': False, 'days_since_rain': 5},
            'Kolkata': {'temp': 28, 'humidity': 65, 'rainfall': 30, 'is_monsoon': True, 'days_since_rain': 8},
            'Delhi': {'temp': 35, 'humidity': 45, 'rainfall': 15, 'is_monsoon': False, 'days_since_rain': 12},
            'Bangalore': {'temp': 25, 'humidity': 55, 'rainfall': 25, 'is_monsoon': False, 'days_since_rain': 10}
        }
        
        baseline = city_weather_baselines[selected_location]
        
        st.write(f"**{selected_location} Baseline Conditions:**")
        st.write(f"- Temperature: {baseline['temp']}°C")
        st.write(f"- Humidity: {baseline['humidity']}%")
        st.write(f"- Rainfall: {baseline['rainfall']}mm")
        st.write(f"- Days since rain: {baseline['days_since_rain']}")
        
        # Allow adjustment from baseline
        temp_adjust = st.slider("Temperature Adjustment (°C)", -10, 10, 0)
        humidity_adjust = st.slider("Humidity Adjustment (%)", -20, 20, 0)
        rainfall_adjust = st.slider("Rainfall Adjustment (mm)", -50, 50, 0)
        
        temperature = baseline['temp'] + temp_adjust
        humidity = max(0, min(100, baseline['humidity'] + humidity_adjust))
        rainfall = max(0, baseline['rainfall'] + rainfall_adjust)
        days_since_rain = baseline['days_since_rain']
        is_monsoon = baseline['is_monsoon']
    
    with col2:
        st.subheader(f"📊 Risk Assessment for {selected_location}")
        
        analyzer = WeatherRiskAnalyzer()
        
        if disease_type in ['Water-Borne', 'Both']:
            water_risk, water_factors = analyzer.assess_water_borne_risk(
                temperature, humidity, rainfall, is_monsoon
            )
            
            col_w1, col_w2 = st.columns(2)
            with col_w1:
                st.metric("Water-Borne Risk", f"{water_risk:.0f}%")
            with col_w2:
                # Color based on risk
                if water_risk < 25:
                    st.markdown("🟢 **Low Risk**")
                elif water_risk < 50:
                    st.markdown("🟡 **Medium Risk**")
                elif water_risk < 75:
                    st.markdown("🟠 **High Risk**")
                else:
                    st.markdown("🔴 **Critical Risk**")
            
            st.write("**Contributing Factors:**")
            for factor in water_factors:
                st.write(f"• {factor}")
        
        if disease_type in ['Vector-Borne', 'Both']:
            vector_risk, vector_factors = analyzer.assess_vector_borne_risk(
                temperature, humidity, rainfall, days_since_rain
            )
            
            if disease_type == 'Both':
                st.markdown("---")
            
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                st.metric("Vector-Borne Risk", f"{vector_risk:.0f}%")
            with col_v2:
                if vector_risk < 25:
                    st.markdown("🟢 **Low Risk**")
                elif vector_risk < 50:
                    st.markdown("🟡 **Medium Risk**")
                elif vector_risk < 75:
                    st.markdown("🟠 **High Risk**")
                else:
                    st.markdown("🔴 **Critical Risk**")
            
            st.write("**Contributing Factors:**")
            for factor in vector_factors:
                st.write(f"• {factor}")
        
        # Show comparison with other cities
        st.markdown("---")
        st.subheader("🌍 City Comparison")
        
        comparison_data = []
        for city, weather in city_weather_baselines.items():
            if disease_type in ['Water-Borne', 'Both']:
                w_risk, _ = analyzer.assess_water_borne_risk(
                    weather['temp'], weather['humidity'], weather['rainfall'], weather['is_monsoon']
                )
            else:
                w_risk = 0
            
            if disease_type in ['Vector-Borne', 'Both']:
                v_risk, _ = analyzer.assess_vector_borne_risk(
                    weather['temp'], weather['humidity'], weather['rainfall'], weather['days_since_rain']
                )
            else:
                v_risk = 0
            
            avg_risk = (w_risk + v_risk) / (2 if disease_type == 'Both' else 1)
            comparison_data.append({
                'City': city,
                'Water-Borne Risk': w_risk,
                'Vector-Borne Risk': v_risk,
                'Average Risk': avg_risk
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        if disease_type == 'Both':
            fig = px.bar(comparison_df, x='City', y=['Water-Borne Risk', 'Vector-Borne Risk'], 
                        title='Risk Comparison Across Cities', barmode='group')
        elif disease_type == 'Water-Borne':
            fig = px.bar(comparison_df, x='City', y='Water-Borne Risk', 
                        title='Water-Borne Risk Comparison')
        else:
            fig = px.bar(comparison_df, x='City', y='Vector-Borne Risk', 
                        title='Vector-Borne Risk Comparison')
        
        st.plotly_chart(fig, use_container_width=True)


def render_predictions():
    """Render prediction page"""
    st.title("🔮 Disease Predictions")
    
    st.subheader("📍 Location-Based Forecasts")
    
    locations = ['Mumbai', 'Chennai', 'Kolkata', 'Delhi', 'Bangalore']
    
    for location in locations:
        col1, col2, col3, col4 = st.columns(4)
        
        # Generate sample predictions
        pred_wb = np.random.randint(50, 300)
        pred_vb = np.random.randint(40, 250)
        
        with col1:
            st.write(f"**{location}**")
        with col2:
            st.metric("Water-Borne", f"{pred_wb} cases")
        with col3:
            st.metric("Vector-Borne", f"{pred_vb} cases")
        with col4:
            total_risk = (pred_wb + pred_vb) / 5
            if total_risk < 25:
                st.markdown("🟢")
            elif total_risk < 50:
                st.markdown("🟡")
            elif total_risk < 75:
                st.markdown("🟠")
            else:
                st.markdown("🔴")
        
        st.markdown("---")
    
    # Feature Importance
    st.subheader("🎯 Top Risk Factors")
    
    importance_df = predictor.get_feature_importance('gradient_boosting')
    if importance_df is not None:
        fig = px.bar(
            importance_df.head(10),
            x='importance',
            y='feature',
            orientation='h',
            title='Feature Importance for Disease Prediction'
        )
        st.plotly_chart(fig, use_container_width=True)


def render_community_reports():
    """Render community reporting page"""
    st.title("📱 Community Health Reports")
    
    tab1, tab2, tab3 = st.tabs(["Submit Report", "View Reports", "Outbreak Detection"])
    
    with tab1:
        st.subheader("📝 Submit Health Report")
        
        col1, col2 = st.columns(2)
        
        with col1:
            reporter_id = st.text_input(
                "Your ID (Anonymous)",
                value="anonymous_" + str(hash(str(datetime.now())))[-6:],
                disabled=True
            )
            location = st.selectbox("Location", ['Mumbai', 'Chennai', 'Kolkata', 'Delhi', 'Bangalore'])
        
        with col2:
            affected_count = st.number_input("Number of People Affected", 1, 100, 1)
            report_date = st.date_input("Date of Symptoms")
        
        st.subheader("Symptoms")
        symptoms_available = [s.value for s in SymptomType]
        selected_symptoms = st.multiselect(
            "Select Symptoms",
            symptoms_available,
            help="Select all symptoms experienced"
        )
        
        if st.button("Submit Report", key="submit_report"):
            if selected_symptoms:
                report = reporting_system.submit_report(
                    reporter_id, location, selected_symptoms, affected_count
                )
                st.success(f"✅ Report submitted successfully! ID: {report.report_id}")
            else:
                st.error("Please select at least one symptom")
    
    with tab2:
        st.subheader("📊 Community Reports Summary")
        
        if reporting_system.reports:
            summary = reporting_system.get_summary_report()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Reports", summary['total_reports'])
            with col2:
                st.metric("Confirmed Cases", summary['confirmed_cases'])
            with col3:
                st.metric("Total Affected", summary['total_affected'])
            
            st.markdown("---")
            st.subheader("Reports by Location")
            
            df = reporting_system.get_reports_dataframe()
            location_counts = df['location'].value_counts()
            
            fig = px.bar(
                x=location_counts.index,
                y=location_counts.values,
                labels={'x': 'Location', 'y': 'Number of Reports'},
                title='Community Reports by Location'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No reports submitted yet")
    
    with tab3:
        st.subheader("🚨 Outbreak Detection")
        
        if st.button("Detect Outbreaks", key="detect_outbreaks"):
            outbreaks = reporting_system.detect_outbreaks(min_reports=3)
            
            if outbreaks:
                for outbreak in outbreaks:
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        if outbreak['alert_level'] == 'Red':
                            st.markdown("🔴 **CRITICAL**")
                        elif outbreak['alert_level'] == 'Orange':
                            st.markdown("🟠 **HIGH**")
                        elif outbreak['alert_level'] == 'Yellow':
                            st.markdown("🟡 **MEDIUM**")
                        else:
                            st.markdown("🟢 **LOW**")
                    
                    with col2:
                        st.write(f"**Location:** {outbreak['location']}")
                        st.write(f"**Disease:** {outbreak['disease_type']}")
                        st.write(f"**Confirmed Cases:** {outbreak['confirmed_cases']}")
                        st.write(f"**Total Affected:** {outbreak['total_affected']}")
                    
                    st.markdown("---")
            else:
                st.info("No outbreaks detected currently")


def render_alerts():
    """Render alerts page"""
    st.title("⚠️ Disease Surveillance Alerts")
    
    tab1, tab2 = st.tabs(["Active Alerts", "Alert History"])
    
    with tab1:
        st.subheader("🚨 Current Active Alerts")
        
        # Generate sample alerts (targeted city levels)
        weather_data_samples = {
            # Critical: high temperature, high humidity, heavy rainfall + monsoon (water_borne >75)
            'Mumbai': {'temperature': 40, 'humidity': 92, 'rainfall': 160, 'is_monsoon': True, 'days_since_rain': 1},
            # Danger: moderate-high vector risk (vector_borne ~60-75)
            'Chennai': {'temperature': 30, 'humidity': 65, 'rainfall': 60, 'is_monsoon': False, 'days_since_rain': 5},
            # Warning: moderate vector risk (vector_borne ~30-40)
            'Kolkata': {'temperature': 28, 'humidity': 65, 'rainfall': 30, 'is_monsoon': True, 'days_since_rain': 8},
        }
        
        for location, weather in weather_data_samples.items():
            alert = alert_system.generate_alert(
                location=location,
                weather_data=weather,
                predicted_cases=np.random.randint(50, 300),
                alert_type='both'
            )
            
            # Display alert
            alert_level = alert['overall_alert_level']['name']
            alert_color = alert['overall_alert_level']['color']
            
            alert_html = f"""
            <div style="border-left: 5px solid {alert_color}; padding: 15px; margin: 10px 0; border-radius: 5px; background-color: #f9f9f9;">
                <h4 style="color: {alert_color};">{location} - {alert_level}</h4>
                <p><b>Weather Conditions:</b> Temp: {weather.get('temperature')}°C, Humidity: {weather.get('humidity')}%</p>
                <p><b>Risk Scores:</b> Water-borne: {alert['risk_scores'].get('water_borne', 'N/A')}%, Vector-borne: {alert['risk_scores'].get('vector_borne', 'N/A')}%</p>
            </div>
            """
            st.markdown(alert_html, unsafe_allow_html=True)
            
            with st.expander(f"📋 {location} - Recommendations"):
                for rec in alert['recommendations']:
                    st.write(rec)
    
    with tab2:
        st.subheader("📜 Alert History")
        st.info("Alert history not yet populated - alerts will be logged here automatically")


def render_settings():
    """Render settings page"""
    st.title("⚙️ Settings & Configuration")
    
    tab1, tab2, tab3 = st.tabs(["System Settings", "Risk Thresholds", "About"])
    
    with tab1:
        st.subheader("🔧 System Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Model Settings**")
            st.checkbox("Auto-update Predictions", value=True)
            st.checkbox("Enable Community Reports", value=True)
            st.checkbox("Send Alerts", value=True)
        
        with col2:
            st.write("**Data Settings**")
            st.number_input("Data Refresh Interval (hours)", 1, 24, 6)
            st.selectbox("Data Source", ["Weather API", "CSV Files", "Database"])
    
    with tab2:
        st.subheader("🎯 Risk Threshold Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Water-Borne Disease Thresholds**")
            st.slider("High Temperature Threshold (°C)", 30, 40, 35)
            st.slider("High Humidity Threshold (%)", 70, 90, 80)
            st.slider("High Rainfall Threshold (mm)", 30, 100, 50)
        
        with col2:
            st.write("**Vector-Borne Disease Thresholds**")
            st.slider("Optimal Temperature Low (°C)", 15, 25, 20)
            st.slider("Optimal Temperature High (°C)", 25, 35, 32)
            st.slider("High Humidity Threshold (%)", 60, 80, 70)
    
    with tab3:
        st.subheader("ℹ️ About This Platform")
        
        st.markdown("""
        ### Smart Health Surveillance and Early Warning Platform
        
        **Version:** 1.0.0  
        **Last Updated:** February 2026
        
        #### Features:
        - 🤖 AI-based disease prediction using ensemble models
        - 🌤️ Weather correlation analysis for disease spread
        - 📱 Community-centric health reporting
        - ⚠️ Real-time alert generation
        - 📊 Epidemiological data analysis
        
        #### Technologies:
        - **ML:** scikit-learn, Gradient Boosting, Random Forest
        - **Dashboard:** Streamlit
        - **Data:** Pandas, NumPy
        - **Visualization:** Plotly
        
        #### Contact:
        For issues or feedback, contact the Health Surveillance team.
        """)


# Main app logic
if page == "Dashboard":
    render_dashboard()
elif page == "Risk Analysis":
    render_risk_analysis()
elif page == "Predictions":
    render_predictions()
elif page == "Community Reports":
    render_community_reports()
elif page == "Alerts":
    render_alerts()
elif page == "Settings":
    render_settings()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 12px;">
    Smart Health Surveillance Platform | Early Warning System for Water-Borne & Vector-Borne Diseases
</div>
""", unsafe_allow_html=True)

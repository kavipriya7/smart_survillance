"""
Community-Centric Reporting System
Collects, validates, and aggregates community health reports
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from enum import Enum
import json
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SymptomType(Enum):
    """Water-borne and Vector-borne disease symptoms"""
    # Water-borne
    DIARRHEA = "Diarrhea"
    VOMITING = "Vomiting"
    ABDOMINAL_PAIN = "Abdominal Pain"
    DEHYDRATION = "Dehydration"
    FEVER_WITH_GI = "Fever with GI symptoms"
    
    # Vector-borne
    HIGH_FEVER = "High Fever"
    JOINT_PAIN = "Joint Pain"
    MUSCLE_PAIN = "Muscle Pain"
    RASH = "Rash"
    HEADACHE = "Headache"
    BODY_ACHE = "Body Ache"
    NAUSEA = "Nausea"


class ReportStatus(Enum):
    """Status of community reports"""
    SUBMITTED = "submitted"
    VERIFIED = "verified"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    UNDER_INVESTIGATION = "under_investigation"


class CommunityReport:
    """Individual community health report"""
    
    def __init__(self, reporter_id, location, symptoms, report_date=None):
        """
        Create a community report
        
        Args:
            reporter_id: Anonymous ID of reporter
            location: Location of report (city/area)
            symptoms: List of symptoms reported
            report_date: Date of report (default: today)
        """
        self.report_id = self._generate_report_id(reporter_id)
        self.reporter_id = reporter_id
        self.location = location
        self.symptoms = symptoms
        self.report_date = report_date or datetime.now().date().isoformat()
        self.submission_timestamp = datetime.now().isoformat()
        self.status = ReportStatus.SUBMITTED.value
        self.verification_score = 0
        self.confirmed_by_health_worker = False
        self.notes = ""
        self.affected_count = 1  # Single person or family size
    
    def _generate_report_id(self, reporter_id):
        """Generate unique report ID"""
        timestamp = datetime.now().isoformat()
        hash_input = f"{reporter_id}{timestamp}".encode()
        return hashlib.md5(hash_input).hexdigest()[:12]
    
    def set_affected_count(self, count):
        """Set number of people affected by this illness"""
        self.affected_count = max(1, count)
    
    def set_status(self, status, notes=""):
        """Update report status"""
        self.status = status
        self.notes = notes
    
    def calculate_verification_score(self):
        """
        Calculate verification score based on symptom credibility
        Higher score = more credible report
        """
        score = 0
        
        # Check for symptom consistency
        water_borne_symptoms = {
            'Diarrhea', 'Vomiting', 'Abdominal Pain', 
            'Dehydration', 'Fever with GI symptoms'
        }
        vector_borne_symptoms = {
            'High Fever', 'Joint Pain', 'Muscle Pain', 
            'Rash', 'Headache', 'Body Ache', 'Nausea'
        }
        
        symptom_set = set(self.symptoms)
        water_match = len(symptom_set & water_borne_symptoms) / max(len(water_borne_symptoms), 1)
        vector_match = len(symptom_set & vector_borne_symptoms) / max(len(vector_borne_symptoms), 1)
        
        # Higher score if symptoms match a disease pattern
        score += max(water_match, vector_match) * 50
        
        # Bonus for detailed reporting
        if len(self.symptoms) >= 3:
            score += 20
        
        # Penalty for vague symptoms
        if any('other' in s.lower() for s in self.symptoms):
            score -= 10
        
        self.verification_score = max(0, min(100, score))
        return self.verification_score
    
    def to_dict(self):
        """Convert report to dictionary"""
        return {
            'report_id': self.report_id,
            'reporter_id': self.reporter_id,
            'location': self.location,
            'symptoms': self.symptoms,
            'report_date': self.report_date,
            'submission_timestamp': self.submission_timestamp,
            'status': self.status,
            'verification_score': self.verification_score,
            'confirmed_by_health_worker': self.confirmed_by_health_worker,
            'affected_count': self.affected_count,
            'notes': self.notes
        }


class CommunityReportingSystem:
    """Manage community health reports and outbreak detection"""
    
    def __init__(self):
        """Initialize reporting system"""
        self.reports = []
        self.report_dataframe = None
        self.outbreak_signals = []
        self.analysis_cache = {}
    
    def submit_report(self, reporter_id, location, symptoms, affected_count=1):
        """
        Submit a new community report
        
        Args:
            reporter_id: Anonymous reporter ID
            location: Location of report
            symptoms: List of symptoms
            affected_count: Number of people affected
        
        Returns:
            report: CommunityReport object
        """
        # Validate symptoms
        valid_symptoms = [s.value for s in SymptomType]
        symptoms = [s for s in symptoms if s in valid_symptoms]
        
        if not symptoms:
            logger.warning(f"Invalid symptoms provided by {reporter_id}")
            return None
        
        # Create report
        report = CommunityReport(reporter_id, location, symptoms)
        report.set_affected_count(affected_count)
        report.calculate_verification_score()
        
        # Store report
        self.reports.append(report)
        logger.info(f"Report submitted: {report.report_id} from {location}")
        
        return report
    
    def verify_report(self, report_id, status, health_worker_id, notes=""):
        """
        Health worker verification of report
        
        Args:
            report_id: ID of report to verify
            status: Verification status
            health_worker_id: ID of health worker
            notes: Verification notes
        """
        for report in self.reports:
            if report.report_id == report_id:
                report.set_status(status, notes)
                if status == ReportStatus.CONFIRMED.value:
                    report.confirmed_by_health_worker = True
                logger.info(f"Report {report_id} verified as {status}")
                return True
        return False
    
    def get_reports_dataframe(self):
        """Convert reports to pandas DataFrame"""
        if not self.reports:
            return pd.DataFrame()
        
        data = [r.to_dict() for r in self.reports]
        self.report_dataframe = pd.DataFrame(data)
        return self.report_dataframe
    
    def detect_outbreaks(self, location=None, lookback_days=7, min_reports=5):
        """
        Detect potential disease outbreaks
        
        Args:
            location: Specific location to analyze (None for all)
            lookback_days: Days to look back
            min_reports: Minimum reports to trigger alert
        
        Returns:
            outbreak_signals: List of detected outbreak patterns
        """
        self.get_reports_dataframe()
        
        if self.report_dataframe.empty:
            return []
        
        df = self.report_dataframe.copy()
        
        # Filter by date
        cutoff_date = (datetime.now() - timedelta(days=lookback_days)).isoformat()
        df['report_date'] = pd.to_datetime(df['report_date'])
        df = df[df['report_date'] >= cutoff_date]
        
        # Filter by location if specified
        if location:
            df = df[df['location'] == location]
        
        # Filter by confirmed reports
        df = df[df['status'] == ReportStatus.CONFIRMED.value]
        
        outbreaks = []
        
        # Analyze by location
        for loc in df['location'].unique():
            loc_data = df[df['location'] == loc]
            
            report_count = len(loc_data)
            total_affected = loc_data['affected_count'].sum()
            
            if report_count >= min_reports:
                # Detect disease type
                disease_type = self._detect_disease_type(loc_data)
                
                outbreak = {
                    'location': loc,
                    'disease_type': disease_type,
                    'confirmed_cases': report_count,
                    'total_affected': total_affected,
                    'detection_date': datetime.now().isoformat(),
                    'severity': self._calculate_severity(report_count, total_affected),
                    'alert_level': self._determine_alert_level(report_count, total_affected),
                    'recent_reports': loc_data['report_date'].max()
                }
                outbreaks.append(outbreak)
                logger.warning(f"Outbreak signal detected in {loc}: {disease_type}")
        
        self.outbreak_signals = outbreaks
        return outbreaks
    
    def _detect_disease_type(self, location_reports):
        """Detect water-borne or vector-borne disease"""
        water_borne_symptoms = {
            'Diarrhea', 'Vomiting', 'Abdominal Pain', 
            'Dehydration', 'Fever with GI symptoms'
        }
        vector_borne_symptoms = {
            'High Fever', 'Joint Pain', 'Muscle Pain', 
            'Rash', 'Headache', 'Body Ache', 'Nausea'
        }
        
        all_symptoms = []
        for symptoms in location_reports['symptoms']:
            all_symptoms.extend(symptoms)
        
        water_score = sum(1 for s in all_symptoms if s in water_borne_symptoms)
        vector_score = sum(1 for s in all_symptoms if s in vector_borne_symptoms)
        
        if water_score > vector_score:
            return 'Water-borne (Cholera/Typhoid/Dysentery)'
        elif vector_score > water_score:
            return 'Vector-borne (Dengue/Malaria/Chikungunya)'
        else:
            return 'Unknown'
    
    def _calculate_severity(self, report_count, total_affected):
        """Calculate severity on 0-100 scale"""
        # Exponential scaling
        severity = min(100, (report_count + total_affected) / 2)
        return severity
    
    def _determine_alert_level(self, report_count, total_affected):
        """Determine alert level"""
        if report_count < 5:
            return 'Green'
        elif report_count < 15:
            return 'Yellow'
        elif report_count < 30:
            return 'Orange'
        else:
            return 'Red'
    
    def get_location_statistics(self, location):
        """Get statistics for a location"""
        self.get_reports_dataframe()
        
        if self.report_dataframe.empty:
            return None
        
        loc_data = self.report_dataframe[self.report_dataframe['location'] == location]
        
        if loc_data.empty:
            return None
        
        # Count reports by status
        status_counts = loc_data['status'].value_counts().to_dict()
        
        # Get common symptoms
        all_symptoms = []
        for symptoms in loc_data['symptoms']:
            all_symptoms.extend(symptoms)
        
        symptom_counts = pd.Series(all_symptoms).value_counts().to_dict()
        
        return {
            'location': location,
            'total_reports': len(loc_data),
            'confirmed_cases': len(loc_data[loc_data['status'] == ReportStatus.CONFIRMED.value]),
            'total_affected': loc_data['affected_count'].sum(),
            'avg_verification_score': loc_data['verification_score'].mean(),
            'status_distribution': status_counts,
            'most_common_symptoms': symptom_counts,
            'date_range': {
                'from': loc_data['report_date'].min(),
                'to': loc_data['report_date'].max()
            }
        }
    
    def get_summary_report(self):
        """Get system-wide summary"""
        self.get_reports_dataframe()
        
        if self.report_dataframe.empty:
            return {
                'total_reports': 0,
                'confirmed_cases': 0,
                'outbreak_signals': 0
            }
        
        df = self.report_dataframe
        
        return {
            'total_reports': len(df),
            'confirmed_cases': len(df[df['status'] == ReportStatus.CONFIRMED.value]),
            'avg_verification_score': df['verification_score'].mean(),
            'total_affected': df['affected_count'].sum(),
            'locations_with_reports': df['location'].nunique(),
            'outbreak_signals': len(self.outbreak_signals),
            'status_distribution': df['status'].value_counts().to_dict(),
            'timestamp': datetime.now().isoformat()
        }
    
    def export_reports_csv(self, filepath):
        """Export reports to CSV"""
        try:
            df = self.get_reports_dataframe()
            df.to_csv(filepath, index=False)
            logger.info(f"Reports exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting reports: {str(e)}")
            return False
    
    def export_outbreak_signals_json(self, filepath):
        """Export outbreak signals to JSON"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.outbreak_signals, f, indent=2)
            logger.info(f"Outbreak signals exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting outbreak signals: {str(e)}")
            return False


def main():
    """Test community reporting system"""
    system = CommunityReportingSystem()
    
    # Simulate community reports
    test_scenarios = [
        # Mumbai water-borne outbreak
        ('reporter_001', 'Mumbai', ['Diarrhea', 'Vomiting', 'Fever with GI symptoms'], 1),
        ('reporter_002', 'Mumbai', ['Diarrhea', 'Abdominal Pain', 'Dehydration'], 2),
        ('reporter_003', 'Mumbai', ['Vomiting', 'Diarrhea', 'Abdominal Pain'], 1),
        ('reporter_004', 'Mumbai', ['Fever with GI symptoms', 'Diarrhea'], 3),
        ('reporter_005', 'Mumbai', ['Diarrhea', 'Abdominal Pain'], 1),
        
        # Chennai vector-borne outbreak
        ('reporter_006', 'Chennai', ['High Fever', 'Joint Pain', 'Rash'], 1),
        ('reporter_007', 'Chennai', ['High Fever', 'Muscle Pain', 'Headache'], 1),
        ('reporter_008', 'Chennai', ['Joint Pain', 'Body Ache', 'Rash'], 2),
        ('reporter_009', 'Chennai', ['High Fever', 'Headache', 'Nausea'], 1),
    ]
    
    print("\n" + "="*70)
    print("COMMUNITY HEALTH REPORTING SYSTEM")
    print("="*70)
    
    # Submit reports
    for reporter_id, location, symptoms, affected in test_scenarios:
        report = system.submit_report(reporter_id, location, symptoms, affected)
        if report:
            print(f"✓ Report {report.report_id} submitted from {location}")
    
    # Verify some reports
    for i, report in enumerate(system.reports[:6]):
        if i % 2 == 0:
            system.verify_report(report.report_id, ReportStatus.CONFIRMED.value, 'hw_001')
    
    # Detect outbreaks
    print("\n" + "="*70)
    print("OUTBREAK DETECTION")
    print("="*70)
    outbreaks = system.detect_outbreaks(min_reports=3)
    
    for outbreak in outbreaks:
        print(f"\n🚨 OUTBREAK ALERT")
        print(f"  Location: {outbreak['location']}")
        print(f"  Disease Type: {outbreak['disease_type']}")
        print(f"  Confirmed Cases: {outbreak['confirmed_cases']}")
        print(f"  Total Affected: {outbreak['total_affected']}")
        print(f"  Severity: {outbreak['severity']:.0f}/100")
        print(f"  Alert Level: {outbreak['alert_level']}")
    
    # Get location statistics
    print("\n" + "="*70)
    print("LOCATION STATISTICS")
    print("="*70)
    for location in ['Mumbai', 'Chennai']:
        stats = system.get_location_statistics(location)
        if stats:
            print(f"\n{location}:")
            print(f"  Total Reports: {stats['total_reports']}")
            print(f"  Confirmed Cases: {stats['confirmed_cases']}")
            print(f"  Total Affected: {stats['total_affected']}")
            print(f"  Top Symptoms: {dict(list(stats['most_common_symptoms'].items())[:3])}")
    
    # Summary
    print("\n" + "="*70)
    print("SYSTEM SUMMARY")
    print("="*70)
    summary = system.get_summary_report()
    for key, value in summary.items():
        if key != 'status_distribution':
            print(f"{key}: {value}")
    
    return system


if __name__ == "__main__":
    main()

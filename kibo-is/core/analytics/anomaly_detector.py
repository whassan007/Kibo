import numpy as np
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """
    Detects statistical anomalies in compliance risk telemetry.
    """
    def __init__(self, db_session: Session):
        self.db = db_session

    def detect_risk_spikes(self, org_id: str, current_risk: float) -> dict:
        """
        Flags if today's risk score is an anomaly (> 2 std dev from 30-day mean).
        """
        query = text("""
            SELECT risk_avg 
            FROM analytics_daily_metrics
            WHERE org_id = :org_id 
              AND date >= current_date - interval '30 days'
            ORDER BY date DESC
        """)
        
        results = self.db.execute(query, {"org_id": org_id}).fetchall()
        
        if len(results) < 14:
            # Not enough data for statistical significance
            return {"is_anomaly": False, "reason": "Insufficient historical data (need >= 14 days)"}
            
        historical_risks = [row.risk_avg for row in results if row.risk_avg is not None]
        
        mean_risk = np.mean(historical_risks)
        std_dev = np.std(historical_risks)
        
        z_score = (current_risk - mean_risk) / std_dev if std_dev > 0 else 0
        
        is_anomaly = abs(z_score) > 2.0
        
        return {
            "is_anomaly": is_anomaly,
            "z_score": float(z_score),
            "mean_risk": float(mean_risk),
            "std_dev": float(std_dev),
            "threshold_exceeded": is_anomaly and z_score > 0
        }

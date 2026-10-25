from datetime import date, timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Dict, Any

class TrendingService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_risk_trending(self, org_id: str) -> Dict[str, Any]:
        """
        Calculates 30, 90, and 365-day risk score trends.
        Uses TimescaleDB hypertable for efficient querying.
        """
        today = date.today()
        intervals = {
            "30_days": today - timedelta(days=30),
            "90_days": today - timedelta(days=90),
            "365_days": today - timedelta(days=365)
        }
        
        trends = {}
        
        for label, start_date in intervals.items():
            query = text("""
                SELECT 
                    AVG(risk_avg) as avg_risk,
                    AVG(compliance_percent) as avg_compliance
                FROM analytics_daily_metrics
                WHERE org_id = :org_id 
                  AND date >= :start_date 
                  AND date <= :today
            """)
            
            result = self.db.execute(query, {
                "org_id": org_id,
                "start_date": start_date,
                "today": today
            }).fetchone()
            
            trends[label] = {
                "avg_risk": float(result.avg_risk) if result and result.avg_risk else 0.0,
                "avg_compliance": float(result.avg_compliance) if result and result.avg_compliance else 0.0
            }
            
        # Calculate velocity (change over the last 30 days compared to previous 30 days)
        d30 = today - timedelta(days=30)
        d60 = today - timedelta(days=60)
        velocity_query = text("""
            WITH current_period AS (
                SELECT AVG(risk_avg) as val FROM analytics_daily_metrics
                WHERE org_id = :org_id AND date >= :d30
            ),
            previous_period AS (
                SELECT AVG(risk_avg) as val FROM analytics_daily_metrics
                WHERE org_id = :org_id AND date >= :d60 
                  AND date < :d30
            )
            SELECT current_period.val - previous_period.val as risk_velocity
            FROM current_period, previous_period
        """)
        
        velocity_result = self.db.execute(velocity_query, {"org_id": org_id, "d30": d30, "d60": d60}).fetchone()
        
        trends["risk_velocity"] = float(velocity_result.risk_velocity) if velocity_result and velocity_result.risk_velocity else 0.0
        
        return trends

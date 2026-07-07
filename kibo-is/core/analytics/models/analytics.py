from datetime import date, datetime
from sqlalchemy import Column, String, Float, Integer, Date, DateTime, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class DailyMetrics(Base):
    __tablename__ = 'analytics_daily_metrics'

    id = Column(String, primary_key=True)
    date = Column(Date, index=True)
    org_id = Column(String, index=True)
    risk_avg = Column(Float)
    risk_critical_count = Column(Integer)
    assessment_count = Column(Integer)
    compliance_percent = Column(Float)


class WeeklyForecast(Base):
    __tablename__ = 'analytics_weekly_forecast'

    id = Column(String, primary_key=True)
    week = Column(Date, index=True)
    org_id = Column(String, index=True)
    predicted_risks = Column(Integer)
    predicted_gaps = Column(Integer)
    confidence = Column(Float)


class BenchmarkScore(Base):
    __tablename__ = 'analytics_benchmark_score'

    id = Column(String, primary_key=True)
    org_id = Column(String, index=True)
    peer_group = Column(String)
    risk_percentile = Column(Float)
    compliance_percentile = Column(Float)


class ExecutiveReport(Base):
    __tablename__ = 'analytics_executive_report'

    id = Column(String, primary_key=True)
    org_id = Column(String, index=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    content = Column(JSON)
    file_path = Column(String)
    delivery_status = Column(String)

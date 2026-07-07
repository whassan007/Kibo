import os
import pandas as pd
from sqlalchemy import create_engine
from typing import Tuple, Dict

def get_engine():
    # Use standard local postgres credentials
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/kibo_is")
    return create_engine(db_url)

def fetch_telemetry_data() -> pd.DataFrame:
    """Fetch 30-day sliding window of telemetry."""
    query = """
    SELECT timestamp, metric_name, value, tenant_id 
    FROM telemetry_logs 
    WHERE timestamp >= NOW() - INTERVAL '30 days'
    ORDER BY timestamp ASC
    """
    engine = get_engine()
    try:
        return pd.read_sql(query, engine)
    except Exception as e:
        print(f"Warning: Telemetry fetch failed. {e}")
        return pd.DataFrame()

def fetch_risk_history() -> pd.DataFrame:
    """Fetch 90-day risk history for forecasting."""
    query = """
    SELECT created_at as date, risk_score 
    FROM vendor_risk_assessments 
    WHERE created_at >= NOW() - INTERVAL '90 days'
    ORDER BY created_at ASC
    """
    engine = get_engine()
    try:
        return pd.read_sql(query, engine)
    except Exception as e:
        print(f"Warning: Risk history fetch failed. {e}")
        return pd.DataFrame()

def fetch_historical_controls() -> pd.DataFrame:
    """Fetch mitigating controls for semantic search."""
    query = """
    SELECT id, title, description, domain 
    FROM mitigating_controls
    """
    engine = get_engine()
    try:
        return pd.read_sql(query, engine)
    except Exception as e:
        print(f"Warning: Controls fetch failed. {e}")
        return pd.DataFrame()

def generate_mock_data():
    """Fallback if DB is empty."""
    import numpy as np
    from datetime import datetime, timedelta
    
    now = datetime.now()
    telemetry = pd.DataFrame({
        'timestamp': [now - timedelta(days=x) for x in range(30)],
        'metric_name': ['cpu_usage'] * 30,
        'value': np.random.normal(50, 10, 30),
        'tenant_id': ['tenant-1'] * 30
    })
    
    # Introduce anomalies
    telemetry.loc[5, 'value'] = 99.9
    telemetry.loc[15, 'value'] = 5.0
    
    risk_history = pd.DataFrame({
        'date': [now - timedelta(days=x) for x in range(90)],
        'risk_score': np.random.normal(65, 5, 90)
    })
    
    controls = pd.DataFrame({
        'id': ['c1', 'c2', 'c3'],
        'title': ['Encryption at Rest', 'MFA', 'Access Logging'],
        'description': [
            'All databases must use AES-256 encryption at rest.',
            'Multi-factor authentication is required for all administrative access.',
            'All access to production systems must be logged centrally.'
        ],
        'domain': ['Data Security', 'Identity', 'Monitoring']
    })
    
    return telemetry, risk_history, controls

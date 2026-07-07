import logging
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class WarehouseSync:
    """
    Handles synchronization and optimization of metrics into TimescaleDB hypertables.
    """
    def __init__(self, db_session: Session):
        self.db = db_session

    def setup_hypertable(self):
        """
        Converts the daily_metrics table into a TimescaleDB hypertable
        partitioned by the 'date' column.
        """
        try:
            # Check if timescaledb extension exists
            self.db.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
            
            # Convert to hypertable if not already
            query = text("""
                SELECT create_hypertable('analytics_daily_metrics', 'date', if_not_exists => TRUE);
            """)
            self.db.execute(query)
            self.db.commit()
            logger.info("TimescaleDB hypertable 'analytics_daily_metrics' configured successfully.")
        except Exception as e:
            logger.error(f"Failed to configure TimescaleDB hypertable: {str(e)}")
            self.db.rollback()

    def create_continuous_aggregates(self):
        """
        Sets up continuous aggregates for weekly and monthly rollups.
        """
        try:
            # Monthly rollup view
            monthly_query = text("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS analytics_monthly_metrics
                WITH (timescaledb.continuous) AS
                SELECT time_bucket('1 month', date) AS bucket,
                       org_id,
                       AVG(risk_avg) as avg_risk,
                       MAX(risk_critical_count) as max_critical_risks,
                       AVG(compliance_percent) as avg_compliance
                FROM analytics_daily_metrics
                GROUP BY bucket, org_id;
            """)
            self.db.execute(monthly_query)
            self.db.commit()
            logger.info("Continuous aggregates configured successfully.")
        except Exception as e:
            logger.error(f"Failed to configure continuous aggregates: {str(e)}")
            self.db.rollback()

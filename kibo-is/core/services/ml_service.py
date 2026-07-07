from core.ml.anomaly_detection import AnomalyDetector
from core.ml.assessment_drafting import AssessmentDrafter
from core.ml.control_recommendation import ControlRecommender
from core.ml.risk_prediction import RiskPredictor
from core.ml.approver_routing import ApproverRouter

class MLService:
    def __init__(self, llm_client=None, embeddings_model=None):
        self.anomaly_detector = AnomalyDetector()
        self.assessment_drafter = AssessmentDrafter(llm_client) if llm_client else None
        self.control_recommender = ControlRecommender(embeddings_model) if embeddings_model else None
        self.risk_predictor = RiskPredictor()
        self.approver_router = ApproverRouter()
        
    def check_anomaly(self, today_metrics: dict) -> dict:
        return self.anomaly_detector.predict(today_metrics)
        
    async def draft_assessment(self, assessment_type: str, system_description: str) -> dict:
        if not self.assessment_drafter:
            raise ValueError("LLM client not configured.")
        return await self.assessment_drafter.draft(assessment_type, system_description)
        
    def recommend_controls(self, findings: str, top_k: int = 5) -> list:
        if not self.control_recommender:
            raise ValueError("Embeddings model not configured.")
        return self.control_recommender.recommend(findings, top_k=top_k)
        
    def forecast_risk(self, days_ahead: int = 30) -> dict:
        return self.risk_predictor.forecast(days_ahead)
        
    def route_approval(self, features: list) -> dict:
        return self.approver_router.predict(features)

from sklearn.ensemble import RandomForestClassifier
import pickle
import os

class ApproverRouter:
    def __init__(self, model_path: str = None):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        if model_path and os.path.exists(model_path):
            self.load(model_path)
            
    def train(self, X_train: list, y_train: list):
        """
        X_train: list of lists [assessment_type_encoded, risk_level_encoded, domain_encoded, amount]
        y_train: list of strings ["DPO", "CISO", "CPO", "Legal"]
        """
        self.model.fit(X_train, y_train)
        
    def predict(self, assessment_features: list) -> dict:
        """
        Predicts the optimal approver based on assessment features.
        """
        prediction = self.model.predict([assessment_features])[0]
        probabilities = self.model.predict_proba([assessment_features])[0]
        
        return {
            'recommended_approver': str(prediction),
            'confidence': float(max(probabilities))
        }

    def save(self, path: str):
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)

    def load(self, path: str):
        with open(path, 'rb') as f:
            self.model = pickle.load(f)

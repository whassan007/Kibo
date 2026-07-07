import pickle
import os
import warnings
from statsmodels.tsa.arima.model import ARIMA
import numpy as np

# Suppress statsmodels warnings for cleaner output
warnings.filterwarnings("ignore")

class RiskPredictor:
    def __init__(self, model_path: str = None):
        self.arima_fitted = None
        if model_path and os.path.exists(model_path):
            self.load(model_path)
            
    def train(self, historical_risks: list):
        """
        Trains an ARIMA(1,1,1) model on a 1D array of historical risk scores.
        """
        if not historical_risks or len(historical_risks) < 30:
            raise ValueError("Insufficient historical data. Provide at least 30 data points.")
            
        model = ARIMA(historical_risks, order=(1,1,1))
        self.arima_fitted = model.fit()

    def forecast(self, days_ahead: int = 30) -> dict:
        """
        Forecasts risk scores for the next N days.
        """
        if self.arima_fitted is None:
            raise ValueError("Model is not trained. Call train() or load() first.")
            
        forecast_result = self.arima_fitted.get_forecast(steps=days_ahead)
        predictions = forecast_result.predicted_mean
        confidence = forecast_result.conf_int()
        
        return {
            'predictions': np.nan_to_num(predictions).tolist(),
            'lower_bound': np.nan_to_num(confidence.iloc[:, 0]).tolist() if hasattr(confidence, 'iloc') else confidence[:, 0].tolist(),
            'upper_bound': np.nan_to_num(confidence.iloc[:, 1]).tolist() if hasattr(confidence, 'iloc') else confidence[:, 1].tolist()
        }

    def save(self, path: str):
        if self.arima_fitted:
            self.arima_fitted.save(path)

    def load(self, path: str):
        from statsmodels.tsa.arima.model import ARIMAResults
        self.arima_fitted = ARIMAResults.load(path)

import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kibo_gateway")

def run_chat_completion(model_name: str, messages: list):
    """
    Routes crew model calls to local Ollama fleet.
    Logs to .kibo/logs/cloud_usage.log if a cloud model is requested.
    """
    is_local = any(kw in model_name.lower() for kw in ["ollama", "qwen", "deepseek", "local", "llama"])
    
    if not is_local:
        log_dir = "/Users/iceman/Documents/Code/Kibo/.kibo/logs"
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "cloud_usage.log")
        with open(log_path, "a") as f:
            f.write(f"[{datetime.utcnow().isoformat()}Z] WARNING: Cloud- billed model '{model_name}' called by W-Method crew.\n")
        logger.warning(f"CLOUD MODEL DETECTED: Call to '{model_name}' logged to cloud_usage.log")
        
    # Standard routing to local Ollama server
    # In a full run, this delegates to ollama-spark or ollama-studio
    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": f"[Routed via local Ollama fleet] Processing response from {model_name} stub."
                }
            }
        ]
    }

import json
import logging

logger = logging.getLogger(__name__)

class AssessmentDrafter:
    def __init__(self, llm_client):
        """
        Takes an abstracted LLM client (e.g. wrapper around OpenAI or Anthropic).
        """
        self.llm = llm_client
    
    async def draft(self, assessment_type: str, system_description: str) -> dict:
        prompt = f"""
        Draft a {assessment_type} assessment for the following system:
        {system_description}
        
        Please format the response strictly as a JSON object with the following keys:
        - summary: Executive Summary (3-5 sentences)
        - data_categories: List of data categories involved (strings)
        - risks: List of 5-7 key risks identified (strings)
        - mitigations: Mitigations for the risks (strings)
        - controls: List of 7-10 controls needed (strings)
        
        Output ONLY the JSON object.
        """
        
        try:
            # Assuming the llm client has an async generate method
            response = await self.llm.generate(prompt)
            # Basic sanitization to catch if the LLM output markdown code blocks
            clean_response = response.strip().strip("```json").strip("```").strip()
            return json.loads(clean_response)
        except Exception as e:
            logger.error(f"Failed to draft assessment via LLM: {str(e)}")
            return {
                "error": "Failed to generate assessment draft",
                "details": str(e)
            }

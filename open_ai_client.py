import json
import re
from typing import Optional, Dict, Any

from openai import OpenAI

from conf import Config
from logger_config import get_logger

logger = get_logger('OpenAIClient')

class OpenAIClient:
    """Client per interagire con OpenAI."""

    SYSTEM_PROMPT = """
    You are a virtual dealer, an expert second-hand retailer. 
    Your task is to rate products based on the provided context, assigning a score from 0 (bad deal) to 10 (excellent deal).
    Be strict with the score.
    """

    @staticmethod
    def invoke(context: Dict[str, Any], product: Dict[str, Any]) -> Optional[str]:
        """Invoca OpenAI per valutare un prodotto."""

        user_prompt = f"""
        Score the informations inside <product> using the informations provided inside the <context>.

        Here is the context:
        <context>{context}</context>

        Here is the ad:
        <product>{product}</product>

        Your answer should in JSON format. The JSON should contain the following fields:
        - "score": a float between 0 and 10
        - "reasoning": a string explaining why you gave the score you did
        - "product_feature": an array of strings, each string describing the product features that influenced your decision
        """
        logger.info(f"Invoking OpenAI with prompt: {user_prompt}")

        client = OpenAI(api_key=Config.OPEN_AI_API_KEY)
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": OpenAIClient.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )
        return completion.choices[0].message.content

    @staticmethod
    def parse_response(response: str) -> Optional[Dict[str, Any]]:
        """Parsa la risposta JSON di OpenAI e restituisce un dizionario."""
        match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
        if match:
            try:
                parsed_json = json.loads(match.group(1).strip())
                logger.info(f"OpenAI response parsed correctly: {parsed_json}")
                return parsed_json
            except json.JSONDecodeError as e:
                logger.error(f"OpenAI parsing error: {e}")
        else:
            logger.error("No JSON found in OpenAI response.")
        return None
import json
import re
from typing import Optional, Dict, Any

from httpx import Response

from conf import Config
from http_client import HttpClient
from logger_config import get_logger

logger = get_logger('DeepSeekClient')


class DeepSeekClient:
    """Client per interagire con il servizio DeepSeek."""

    @staticmethod
    def create_input_prompt(object_title: str, object_description: str) -> dict:
        """Crea un prompt per interrogare DeepSeek."""
        prompt = (
            f"Find the average price of similar objects with this charateristics: title: {object_title}, description: {object_description}. "
            f"Refine the comparison by using the description to ensure that comparisons are made between "
            f"similar products (same model, condition, included accessories, limited editions, etc.). "
            f"Return the response in JSON format with clear details and links to the sources used. "
            f"Expected JSON Output: \"mean_price\": \"mean price found (float)\", "
            "\"std_price\": \"standard deviation from mean price (float)\", "
            "\"context_description\": \"description_text\" "
        )

        data = {
            "messages": [
                {"role": "system",
                 "content": "You are a virtual assistant capable of scraping the web to find the average price of a used object from multiple reliable sources, including: second-hand marketplaces, completed sales databases, e-commerce sites and online auctions but exclude wikipedia. Ensure to response in json format"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": Config.deep_seek_max_tokens,
            "temperature": Config.deep_seek_temperature,
            "top_p": Config.deep_seek_top_p,
            "search_web": Config.deep_seek_search_web
        }
        logger.info(f"Creating DeepSeek input prompt: {data}")
        return data

    @staticmethod
    def invoke(body: dict) -> Response | None:
        """Effettua una richiesta a DeepSeek e restituisce la risposta."""
        headers = {
            'Content-Type': 'application/json',
            'x-rapidapi-host': 'deepseek-v3-websearch.p.rapidapi.com',
            'x-rapidapi-key': Config.DEEP_SEEK_API_KEY
        }
        logger.info(f"Invoking DeepSeek with prompt: {body}")
        response = HttpClient.fetch_with_backoff(
            url=Config.deep_seek_endpoint_v3,
            method='POST',
            headers=headers,
            json=body
        )

        logger.info(f"DeepSeek response: {response.text}")
        return response

    @staticmethod
    def extract_json(response: str) -> Optional[Dict[str, Any]]:
        """Parsa la risposta JSON di DeepSeek e restituisce un dizionario."""
        match = re.search(r"```json\s*\n(.*?)(?:\n```|$)", response, re.DOTALL)

        if not match:
            logger.error("No JSON found in DeepSeek response.")
            return None

        try:
            parsed_json = json.loads(match.group(1).strip())

            for key in ["mean_price", "std_price"]:
                if key in parsed_json:
                    parsed_json[key] = re.sub(r"[^\d.]", "", str(parsed_json.get(key, "")))

            logger.info(f"DeepSeek response parsed correctly: {parsed_json}")
            return parsed_json

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing DeepSeek JSON: {e}")

        return None

    @staticmethod
    def extract_json_from_string(text):
        """
        Estrae il JSON contenuto all'interno di una stringa e lo converte in un dizionario.

        Args:
            text (str): La stringa contenente il JSON formattato.

        Returns:
            dict | None: Il dizionario estratto se il parsing ha successo, altrimenti None.
        """
        try:
            # Prima prova a estrarre direttamente un JSON valido
            json_data = None
            try:
                json_data = json.loads(text)
                return json_data
            except json.JSONDecodeError:
                pass  # Se fallisce, procedi con l'estrazione tramite regex

            # Trova il JSON all'interno della stringa usando un pattern più tollerante
            match = re.search(r'```json\n(.*?)```', text, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
                return json.loads(json_str)
            else:
                print("Nessun JSON trovato nella stringa.")
        except (json.JSONDecodeError, re.error) as e:
            print(f"Errore durante l'estrazione o il parsing del JSON: {e}")
        return None



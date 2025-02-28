import json

from deep_seek_client import DeepSeekClient
from domain import InputProduct, OutputResult
from open_ai_client import OpenAIClient
from logger_config import get_logger

logger = get_logger('LLM')

class LLM:

    @staticmethod
    def compute_score(
            object_title: str,
            object_description: str,
            object_price: float
    ) -> json:
        """Flusso principale di esecuzione del programma."""

        ds_prompt = DeepSeekClient.create_input_prompt(object_title, object_description)
        ds_response = DeepSeekClient.invoke(ds_prompt)

        if ds_response.status_code == 200:
            ds_parsed = DeepSeekClient.extract_json_from_string(ds_response.text)
            logger.info(f"Parsed response: {ds_parsed}")

            if ds_parsed is None:
                logger.error("Failed to parse response from DeepSeekClient.")
                return None

            p = ds_parsed.get("model_response", {}).get("choices", [{}])[0].get("message", {}).get("content")
            if p is None:
                logger.error("DeepSeek response does not contain valid content.")
                return None

            c = DeepSeekClient.extract_json(p)

            if c is None:
                logger.error("Failed to extract JSON from DeepSeek content.")
                return None

            output_object = OutputResult(
                mean_price=float(c['mean_price']),
                std_price=float(c['std_price']),
                context_description=c['context_description'],
            )

            if c:
                input_product = InputProduct(product_title=object_title, product_description=object_description,
                                             product_price=object_price)
                oa_response = OpenAIClient.invoke(output_object.to_json(), input_product.to_json())
                oa_parsed = OpenAIClient.parse_response(oa_response)
                logger.info(f"OpenAI evaluation: {oa_parsed}")

                if oa_parsed is None:
                    logger.error("OpenAI evaluation returned None.")
                    return None

                return oa_parsed


if __name__ == "__main__":
    object_title = "Nintendo Switch Lite"
    object_description = "Vendo Nintendo Switch Lite pari al nuovo, completa di scatola, caricabatterie, cover e gommini."
    object_price = 70

    object_score = LLM.compute_score(object_title, object_description, object_price)
    print(object_score)

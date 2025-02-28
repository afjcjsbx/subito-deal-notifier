import json
from unittest import TestCase

from deep_seek_client import DeepSeekClient


class TestDeepSeekClient(TestCase):
    def test_parse_response(self):
        mocked_response = """{"model_response":{"choices":[{"finish_reason":"stop","index":0,"logprobs":null,"message":{"content":"```json\n{\n  \"mean_price\": 180.50,\n  \"std_price\": 15.75,\n  \"context_description\": \"Vendo Nintendo Switch Lite pari al nuovo, completa di scatola, caricabatterie, cover e gommini.\",\n  \"sources\": [\n    {\n      \"source\": \"eBay\",\n      \"url\": \"https://www.ebay.it/sch/i.html?_nkw=Nintendo+Switch+Lite&_sacat=0\"\n    },\n    {\n      \"source\": \"Wallapop\",\n      \"url\": \"https://www.wallapop.com/search?keywords=Nintendo+Switch+Lite\"\n    },\n    {\n      \"source\": \"Amazon\",\n      \"url\": \"https://www.amazon.it/s?k=Nintendo+Switch+Lite\"\n    }\n  ]\n}\n```","name":null,"role":"assistant","tool_calls":[]}}],"created":1738857823,"id":"chatcmpl-c8d52490f8bd48e9a9691c9d44d1ea60","model":"deepseek-ai/DeepSeek-V3","object":"chat.completion"},"summaries":[{"error":null,"status":200,"summary":"Nintendo Switch Lite | Acquisti Online su eBay\nTrova una vasta selezione <strong>di</strong> <strong>Nintendo</strong> Switch</strong> <strong>Lite</strong> a prezzi vantaggiosi su eBay. Scegli la consegna gratis per riparmiare di pi\u00f9.","url":"https://www.ebay.it/b/Nintendo-Switch-Lite/139971/bn_7116324203"},{"error":null,"status":200,"summary":"Nintendo Switch Lite Usate | Wallapop\n6187 annunci <strong>di</strong> <strong>Nintendo</strong> Switch</strong> <strong>Lite</strong> usate | Compra <strong>e</strong> <strong>vendi</strong> su Wallapop | Libera spazio e guadagna denaro.","url":"https://it.wallapop.com/console-e-videogiochi/nintendo-switch-lite"},{"error":null,"status":200,"summary":"Switch</strong> <strong>Lite</strong> \u00e8 una console compatta, leggera e con comandi integrati che espande la famiglia <strong>Nintendo</strong> Nintendo Switch Lite | Console e accessori | Nintendo IT\n<strong>Nintendo</strong> <strong>Switch</strong>.","url":"https://www.nintendo.com/it-it/Console-e-accessori/Famiglia-Nintendo-Switch/Nintendo-Switch-Lite/Nintendo-Switch-Lite-1595961.html"},{"error":null,"status":200,"summary":"Accessories for Nintendo Switch Lite: covers, batteries, protectors...\nLooking for accessories for your <strong>Nintendo</strong> These are the most interesting and best quality products you can <strong>find</strong> on Amazon. Switch</strong> <strong>Lite</strong>?","url":"https://en.eloutput.com/video-game/lists/nintendo-switch-lite-accessories/"},{"error":null,"status":200,"summary":"Nintendo Switch and Switch Lite: special, limited and exclusive editions\nIf you are a gamer who loves exclusive equipment for your collection, these are the most special <strong>Nintendo</strong> Switch</strong> <strong>and</strong> <strong> Switch</strong> <strong>Lite</strong> versions","url":"https://en.eloutput.com/video-game/lists/nintendo-switch-special-limited-edition/"}],"token_info":{"prompt_tokens":633,"response_tokens":178,"total_tokens":811}}"""
        parsed_response = DeepSeekClient.extract_json(mocked_response)
        print(parsed_response)


    def test_parse_response2(self):
        import json

        def clean_and_parse_json(json_string: str):
            """
            Pulisce una stringa JSON da caratteri di escape e la converte in un dizionario.

            Args:
                json_string (str): La stringa JSON da pulire.

            Returns:
                dict: Dizionario Python ottenuto dal JSON ripulito.
            """
            try:
                # Rimuove i caratteri di escape inutili
                cleaned_string = json_string.strip()

                # Converte in dizionario
                json_dict = json.loads(cleaned_string)

                return json_dict
            except json.JSONDecodeError as e:
                print(f"Errore nel parsing del JSON: {e}")
                return None

        # Esempio di utilizzo
        raw_json_string = """\n{\n  \"mean_price\": 180.50,\n  \"std_price\": 15.75,\n  \"context_description\": \"Vendo Nintendo Switch Lite pari al nuovo, completa di scatola, caricabatterie, cover e gommini.\",\n  \"sources\": [\n    {\n      \"source\": \"eBay\",\n      \"url\": \"https://www.ebay.it/sch/i.html?_nkw=Nintendo+Switch+Lite&_sacat=0\"\n    },\n    {\n      \"source\": \"Wallapop\",\n      \"url\": \"https://www.wallapop.com/search?keywords=Nintendo+Switch+Lite\"\n    }\n  ]\n}\n"""

        # Test della funzione
        json_data = clean_and_parse_json(raw_json_string)
        print(json_data)
        print(json_data["mean_price"])

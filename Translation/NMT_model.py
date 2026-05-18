from deepl import DeepLClient, Translator, Language

from os import getenv
from dotenv import load_dotenv


class DeepLService:
    load_dotenv()
    def __init__(self):
        api_key = getenv("DEEPL_AUTHORIZATION_KEY")

        if not api_key:
            raise ValueError("DeepL API key not set.")
        self.client = DeepLClient(api_key)

    def is_connected(self) -> bool:
        return self.client is not None

    def supported_languages(self) -> tuple[list[Language], list[Language]]:
        source_languages = self.client.get_source_languages()
        target_languages = self.client.get_target_languages()
        return source_languages, target_languages

    def client_information(self) -> dict:
        return \
            {
                "client": self.client,
                "translator": self.client,
            }

    def translate(self, text: str, source_language: str, target_language: str):
        result = self.client.translate_text(text, source_lang=source_language, target_lang=target_language)
        return result

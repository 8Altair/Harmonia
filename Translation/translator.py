from Translation.NMT_model import DeepLService


class Translator:
    def __init__(self):
        self.service = DeepLService()
        if not self.service.is_connected():
            raise ValueError("DeepL client is not set.")

    def translate_raw_text(self, text: str, source_language: str, target_language: str) -> str:
        translated_text = self.service.translate(text, source_language, target_language)
        return translated_text.text

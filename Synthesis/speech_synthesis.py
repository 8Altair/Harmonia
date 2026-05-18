from Synthesis.TTS_model import TTSService

from logging_configuration import speech_synthesis_logger


class SpeechSynthesizer:
    def __init__(self):
        speech_synthesis_logger.debug("Initializing SpeechSynthesizer.")
        try:
            model_name = "tts_models/en/jenny/jenny"
            self.service = TTSService(model_name, "cuda")
            speech_synthesis_logger.debug(f"Speech synthesis service initialized through {model_name} model.")
        except Exception:
            speech_synthesis_logger.exception("Failed to initialize speech synthesis service.")
            raise

    def synthesize(self, spoken_text: str, file_path: str):
        speech_synthesis_logger.debug("Attempting to synthesize speech.")
        try:
            speech_synthesis_logger.info(f"Synthesizing text: {spoken_text}")
            self.service.model.tts_to_file(text=spoken_text, file_path=file_path)
            speech_synthesis_logger.debug("Speech synthesized successfully.")
        except Exception:
            speech_synthesis_logger.exception("Failed to synthesize speech.")
            raise

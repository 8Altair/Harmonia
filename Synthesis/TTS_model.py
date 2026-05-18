from TTS.api import TTS

from torch.cuda import is_available

from logging_configuration import tts_model_logger


def tts_models():
    try:
        available_models = TTS.list_models()
        tts_model_logger.info(f"Available TTS models: {available_models}")
    except Exception:
        tts_model_logger.exception("Failed to retrieve available TTS models.")
        raise

    return available_models

class TTSService:
    def __init__(self, model_name="tts_models/en/jenny/jenny", device_name="cpu"):
        tts_model_logger.debug("Initializing TTSService.")

        if model_name not in tts_models():
            tts_model_logger.error(f"The {model_name} is not listed among TTS models.")
            raise ValueError(f"Invalid TTS model: {model_name}")
        self.model_name = model_name
        tts_model_logger.info(f"Model name: {model_name}")

        if device_name not in ("cpu", "cuda"):
            tts_model_logger.error(f"Invalid device: {device_name}")
            raise ValueError(f"Invalid device: {device_name}")

        if device_name == "cuda" and not is_available():
            tts_model_logger.warning("CUDA is not available. Falling back to CPU.")
            device_name = "cpu"
        self.device_name = device_name
        tts_model_logger.info(f"Device name: {self.device_name}")

        try:
            tts_model_logger.debug(f"Loading model {model_name}.")
            self.model = TTS(model_name).to(device_name)
            tts_model_logger.debug(f"Model loaded.")
        except Exception as e:
            tts_model_logger.critical(f"Loading model {model_name} failed. System unusable.")
            raise RuntimeError(f"TTS model could not be loaded: {model_name}.") from e

        tts_model_logger.info("TTSService initialized.")

    def is_loaded(self) -> bool:
        loaded = self.model is not None
        tts_model_logger.debug(f"Model is {'loaded' if loaded else 'not loaded'}.")
        return loaded

    def model_information(self) -> dict:
        tts_model_logger.debug(f"Returning model information for {self.model_name}.")
        return \
            {
                "name": self.model_name,
                "device": str(self.device_name),
            }

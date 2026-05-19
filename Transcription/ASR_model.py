from whisper import tokenizer, load_model, available_models
from torch.cuda import is_available

from logging_configuration import asr_model_logger


def available_languages() -> dict[str, str]:
    """
        Retrieve all languages supported by the Whisper tokenizer.

        Returns:
            dict[str, str]:
                Dictionary mapping Whisper language codes to their corresponding
                language names.

        Raises:
            Exception:
                Raised if the Whisper tokenizer languages cannot be accessed.

        Notes:
            The returned dictionary uses ISO-like language codes as keys and
            human-readable language names as values.
    """
    try:
        asr_model_logger.debug("Accessing available languages.")
        languages = tokenizer.LANGUAGES
        asr_model_logger.debug("Available languages returned.")
        asr_model_logger.info(f"Available languages: {', '.join(languages.values())}")
        return languages

    except Exception:
        asr_model_logger.exception("Failed to access available languages.")
        raise

def whisper_models() -> list[str]:
    """
        Retrieve all available Whisper model names.

        Returns:
            list[str]:
                List of Whisper model names supported by the local Whisper package.

        Raises:
            Exception:
                Raised if the available Whisper models cannot be retrieved.
    """
    try:
        asr_model_logger.debug("Accessing Whisper models.")
        models = available_models()
        asr_model_logger.debug("Available Whisper models returned.")
        asr_model_logger.info(f"Available Whisper models: {models}")
        return models

    except Exception:
        asr_model_logger.exception("Failed to access Whisper models.")
        raise


class WhisperService:
    """
        Service wrapper responsible for Whisper model initialization,
        validation, loading, and metadata access.

        The service validates the requested model and device configuration,
        handles CUDA fallback behavior, and exposes utility methods for
        inspecting the loaded model.

        Attributes:
            model_name (str):
                Name of the loaded Whisper model.

            model:
                Loaded Whisper model instance.
    """
    def __init__(self, model_name="base", device_name="cpu"):
        """
            Initialize and load a Whisper model.

            Args:
                model_name (str, optional):
                    Name of the Whisper model to load.
                    Defaults to "base".

                device_name (str, optional):
                    Target device used for model inference.
                    Supported values are "cpu" and "cuda".
                    Defaults to "cpu".

            Raises:
                ValueError:
                    Raised if the provided model name is invalid.

                ValueError:
                    Raised if the provided device name is invalid.

                RuntimeError:
                    Raised if the Whisper model cannot be loaded.
        """
        asr_model_logger.debug("Initializing WhisperService.")

        self.available_languages = available_languages()

        if model_name not in whisper_models():
            asr_model_logger.error(f"The {model_name} is not listed among Whisper models.")
            raise ValueError(f"Invalid Whisper model: {model_name}")
        self.model_name = model_name
        asr_model_logger.info(f"Model name: {model_name}")

        if device_name not in ("cpu", "cuda"):
            asr_model_logger.error(f"Invalid device: {device_name}")
            raise ValueError(f"Invalid device: {device_name}")

        if device_name == "cuda" and not is_available():
            asr_model_logger.warning("CUDA is not available. Falling back to CPU.")
            device_name = "cpu"
        asr_model_logger.info(f"Device name: {device_name}")

        try:
            asr_model_logger.debug(f"Loading model {model_name}.")
            self.model = load_model(model_name, device_name)
            asr_model_logger.debug(f"Model loaded.")
        except Exception as e:
            asr_model_logger.critical(f"Loading model {model_name} failed. System unusable.")
            raise RuntimeError(f"Whisper model could not be loaded: {model_name}.") from e

        asr_model_logger.info("WhisperService initialized.")

    def is_loaded(self) -> bool:
        """
            Check whether the Whisper model is successfully loaded.

            Returns:
                bool:
                    True if the model instance exists, otherwise False.
        """
        loaded = self.model is not None
        asr_model_logger.debug(f"Model is {'laoded' if loaded else 'not loaded'}.")
        return loaded

    def model_information(self) -> dict:
        """
            Retrieve metadata about the currently loaded Whisper model.

            Returns:
                dict:
                    Dictionary containing:
                        - name:
                            Whisper model name.
                        - device:
                            Device currently used by the model.
                        - parameters:
                            Total number of model parameters.
        """
        asr_model_logger.debug(f"Returning model information for {self.model_name}.")
        return \
            {
                "name": self.model_name,
                "device": str(self.model.device),
                "parameters": sum(parameters.numel() for parameters in self.model.parameters()),
            }

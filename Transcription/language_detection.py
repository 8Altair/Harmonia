from whisper import pad_or_trim, log_mel_spectrogram

from Transcription.ASR_model import WhisperService

from logging_configuration import language_detection_logger
from numpy import ndarray


class LanguageDetector:
    """
        Service class responsible for detecting the spoken language in an audio file
        using a dedicated Whisper model.

        The detector loads a Whisper model through `WhisperService`, preprocesses
        the input audio into a mel spectrogram, and returns the probability
        distribution over supported languages.

        Attributes:
            service (WhisperService):
                Whisper service instance used for language detection.
    """
    def __init__(self):
        """
            Initialize the language detector and load the Whisper model used for
            language identification.

            Raises:
                Exception:
                    Propagates any exception raised during Whisper service
                    initialization.
        """
        language_detection_logger.debug(f"Initializing LanguageDetector.")
        try:
            model_name = "large-v3"
            self.service = WhisperService(model_name, "cuda")
            language_detection_logger.debug(f"Language detection service loaded through {model_name} model.")
        except Exception:
            language_detection_logger.critical("Failed to initialize language detection service.")
            raise
        language_detection_logger.info(f"LanguageDetector initialized.")

    def detect(self, original_audio: ndarray) -> dict[str, float]:
        """
            Detect the spoken language probabilities for an audio file.

            Args:
                original_audio (ndarray):
                    Audio array used for language detection.

            Returns:
                dict[str, float]:
                    Dictionary mapping Whisper language codes to their detected
                    probabilities.

            Raises:
                Exception:
                    Raised if the audio cannot be preprocessed.

                Exception:
                    Raised if the mel spectrogram cannot be initialized.

                Exception:
                    Raised if Whisper language detection fails.
        """
        language_detection_logger.debug("Starting language detection.")
        try:
            language_detection_logger.debug("Starting padding/trimming of the audio.")
            audio = pad_or_trim(original_audio)
            language_detection_logger.debug("Padding/trimming successful.")
        except Exception:
            language_detection_logger.exception(f"Failed to pad/trim audio.")
            raise

        try:
            language_detection_logger.debug(f"Initializing mel spectrogram.")
            mel_spectrogram = (log_mel_spectrogram(audio, n_mels=self.service.model.dims.n_mels).
                               to(self.service.model.device))
            language_detection_logger.debug("Mel spectrogram initialized.")
        except Exception:
            language_detection_logger.exception("Failed to initialize mel spectrogram.")
            raise

        try:
            language_detection_logger.debug("Getting detected language probabilities.")
            _, probabilities = self.service.model.detect_language(mel_spectrogram)
            detected_languages: dict[str, float] = probabilities
            language_detection_logger.debug(f"Language probabilities retrieved.")
            language_detection_logger.info(f"Language probabilities: {detected_languages}")
            return detected_languages

        except Exception:
            language_detection_logger.exception("Failed to detect language.")
            raise

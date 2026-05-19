from Transcription.ASR_model import WhisperService

from logging_configuration import live_transcription_logger

from numpy import ndarray


class LiveTranscriptor:
    """
        Service class responsible for live audio transcription using a Whisper model.

        The transcriptor initializes a dedicated Whisper transcription model
        through `WhisperService` and exposes functionality for converting
        spoken audio into text.

        Attributes:
            service (WhisperService):
                Whisper service instance used for audio transcription.
    """
    def __init__(self):
        """
            Initialize the live transcription service and load the Whisper
            transcription model.

            Raises:
                Exception:
                    Propagates any exception raised during Whisper service
                    initialization.
        """
        live_transcription_logger.debug("Initializing LiveTranscriptor.")
        try:
            model_name = "turbo"
            self.service = WhisperService(model_name, "cuda")
            live_transcription_logger.debug(f"Live transcription service initialized through {model_name} model.")
        except Exception:
            live_transcription_logger.exception("Failed to initialize live transcription service.")
            raise

    def transcribe_audio(self, audio_input: ndarray, language: str, prompt: str = "") -> str:
        """
            Transcribe live spoken audio from an audio file into text.

            Args:
                audio_input (ndarray):
                    Audio array used for transcription.

                language (str):
                    Language code used to guide Whisper transcription.

                prompt (str, optional):
                    Optional initial prompt provided to Whisper to improve
                    transcription context and accuracy.
                    If not provided, a default transcription prompt is generated.

            Returns:
                str:
                    Transcribed text extracted from the audio file.

            Raises:
                ValueError:
                    Raised if the transcription result text is empty.

                RuntimeError:
                    Raised if the transcription process fails.
        """
        live_transcription_logger.debug(f"Starting transcription.")
        language_name = self.service.available_languages[language].capitalize()
        live_transcription_logger.info(f"Transcription language: {language_name}.")
        prompt = f"Transcribe the audio of human speech from {language_name} language." if not prompt else prompt
        live_transcription_logger.info(f"Transcription prompt: {prompt}")

        try:
            live_transcription_logger.debug("Transcribing audio.")
            result = self.service.model.transcribe(audio_input, verbose=True, condition_on_previous_text=False,
                                                   initial_prompt=prompt, language=language)
            transcribed_text = result["text"]
            if not transcribed_text:
                live_transcription_logger.error("Result text is empty.")
                raise ValueError("Result text is empty.")
            live_transcription_logger.debug(f"Transcribed result: {transcribed_text}")
            return transcribed_text

        except ValueError:
            raise
        except Exception as e:
            live_transcription_logger.exception("Failed to transcribe the audio. Cannot return the result.")
            raise RuntimeError("Failed to transcribe the audio.") from e

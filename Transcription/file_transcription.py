from Transcription.ASR_model import WhisperService

from logging_configuration import file_transcription_logger

from numpy import ndarray


class FileTranscriptor:
    """
        Service class responsible for audio transcription using a Whisper model.

        The transcriptor initializes a dedicated Whisper transcription model
        through `WhisperService` and exposes functionality for converting
        spoken audio into text.

        Attributes:
            service (WhisperService):
                Whisper service instance used for audio transcription.
    """
    def __init__(self):
        """
            Initialize the file transcription service and load the Whisper
            transcription model.

            Raises:
                Exception:
                    Propagates any exception raised during Whisper service
                    initialization.
        """
        file_transcription_logger.debug("Initializing FileTranscriptor.")
        try:
            model_name = "large-v3-turbo"
            self.service = WhisperService(model_name, "cuda")
            file_transcription_logger.debug(f"File transcription service initialized through {model_name} model.")
        except Exception:
            file_transcription_logger.exception("Failed to initialize file transcription service.")
            raise

    def transcribe_audio(self, audio_input: str | ndarray, language: str, prompt: str = "") -> str:
        """
            Transcribe spoken audio from an audio file or audio array into text.

            Args:
                audio_input (str | ndarray):
                    Path to an audio file or standardized audio array.

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
        file_transcription_logger.debug(f"Starting transcription.")
        language_name = self.service.available_languages[language].capitalize()
        file_transcription_logger.info(f"Transcription language: {language_name}.")
        prompt = f"Transcribe the audio of human speech from {language_name} language." if not prompt else prompt
        file_transcription_logger.info(f"Transcription prompt: {prompt}")

        try:
            file_transcription_logger.debug("Transcribing audio.")
            result = self.service.model.transcribe(audio_input, verbose=True, condition_on_previous_text=True,
                                                   initial_prompt=prompt, language=language,
                                                   fp16=(self.service.model.device.type == "cuda"))

            transcribed_text = result["text"]
            if not transcribed_text:
                file_transcription_logger.error("Result text is empty.")
                raise ValueError("Result text is empty.")
            file_transcription_logger.debug(f"Transcribed result: {transcribed_text}")
            return transcribed_text

        except ValueError:
            raise
        except Exception as e:
            file_transcription_logger.exception("Failed to transcribe the audio. Cannot return the result.")
            raise RuntimeError("Failed to transcribe the audio.") from e

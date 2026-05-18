from silero_vad import load_silero_vad, read_audio, get_speech_timestamps, VADIterator

from logging_configuration import vad_logger


try:    # Load voice activity detection model from Silero only once
    vad_logger.debug("Loading silero voice activity detection model.")
    voice_detection_model = load_silero_vad()
    vad_logger.debug("Silero model loaded.")
except Exception:
    vad_logger.exception("Failed to load silero voice activity detection model.")
    raise

class VADSession:
    """
        Manage file-based and streaming voice activity detection for one a session.

        This class provides:
        - File-level voice activity detection.
        - Live-streaming voice activity detection.

        Each session maintains its own:
        - VAD iterator.
        - Speech accumulation buffer.
        - Speech collection state.

        The session shares the globally loaded Silero VAD model.

        Parameters
        ----------
        model : object, optional
            Loaded Silero VAD model instance.
            Defaults to the globally loaded `voice_detection_model`.

        sampling_rate : int, optional
            Audio sampling rate used for voice activity detection.
            Defaults to 16000 Hz.

        Attributes
        ----------
        model : object
            Loaded Silero VAD model instance.

        sampling_rate : int
            Audio sampling rate used for processing.

        vad_iterator : VADIterator
            Streaming VAD iterator used for live speech detection.

        speech_buffer : list
            Buffer containing accumulated speech chunks during live detection.

        currently_collecting : bool
            Indicates whether speech is currently being accumulated.
    """
    def __init__(self, model=voice_detection_model, sampling_rate=16000):
        vad_logger.debug("Initializing LiveVADSession.")
        self.model = model
        vad_logger.info(f"Model: {self.model}")
        self.sampling_rate = sampling_rate
        vad_logger.info(f"Sampling rate: {self.sampling_rate}")

        try:
            vad_logger.debug("Initializing VADIterator.")
            self.vad_iterator = VADIterator(model, sampling_rate=self.sampling_rate)
            vad_logger.debug("Vad iterator initialized.")
        except Exception:
            vad_logger.exception("Failed to initialize VADIterator.")
            raise

        self.speech_buffer = []
        self.currently_collecting = False
        vad_logger.debug("LiveVADSession initialized.")

    def reset(self):
        """
            Reset the current live VAD session state.

            This method:
            - Resets internal Silero VAD iterator state.
            - Clears the accumulated speech buffer.
            - Disables active speech collection state.

            Notes
            -----
            Call this method when:
            - A live session ends.
            - Microphone streaming stops.
            - The current session must be reinitialized.
        """
        vad_logger.debug("Resetting LiveVADSession.")
        try:
            vad_logger.debug("Resetting VADIterator.")
            self.vad_iterator.reset_states()
            vad_logger.debug("VADIterator reset.")
        except Exception:
            vad_logger.exception("Failed to reset VADIterator.")
            raise

        self.speech_buffer.clear()
        self.currently_collecting = False

        vad_logger.debug("LiveVADSession reset.")

    def file_voice_detection(self, audio) -> list:
        """
            Perform voice activity detection on a complete audio array.

            Parameters
            ----------
            audio : np.ndarray
                Audio to analyze.

            Returns
            -------
            list
                Speech timestamp dictionaries returned by Silero VAD.

            Raises
            ------
            Exception
                If audio loading or speech timestamp extraction fails.
        """
        vad_logger.debug(f"Voice detection from standardized audio array.")

        try:
            vad_logger.debug("Attempting to retrieve speech timestamps.")
            speech_timestamps = get_speech_timestamps(
                audio,
                self.model,
                sampling_rate=self.sampling_rate,
                return_seconds=True)
            vad_logger.debug("Speech timestamps retrieved.")

        except Exception:
            vad_logger.exception("Failed to read speech timestamps.")
            raise

        vad_logger.info(f"Speech timestamps: {speech_timestamps}")
        return speech_timestamps

    def live_voice_detection(self, audio_chunk) -> None | list:
        """
            Perform live voice activity detection on streaming audio chunks.

            The method processes incoming audio data with the Silero VAD iterator
            and accumulates speech chunks until speech-end detection occurs.

            Parameters
            ----------
            audio_chunk : array-like
                Streaming audio chunk represented as audio sample data.

            Returns
            -------
            list | None
                Returns a finalized speech buffer when speech end is detected.
                Returns ``None`` while speech collection is still ongoing or when
                no speech activity is detected.

            Notes
            -----
            - Audio chunks are internally divided into smaller VAD windows.
            - Speech accumulation begins after speech-start detection.
            - Speech accumulation ends after speech-end detection.
        """
        vad_logger.debug(f"Voice detection from a chunk.")
        window_size_samples = 512 if self.sampling_rate == 16000 else 256
        vad_logger.debug(f"Window size samples: {window_size_samples}")
        for i in range(0, len(audio_chunk), window_size_samples):
            chunk = audio_chunk[i: i + window_size_samples]
            if len(chunk) < window_size_samples:
                break

            try:
                speech: None | dict[str, float] = self.vad_iterator(chunk, return_seconds=True)
            except Exception:
                vad_logger.exception("Failed to iterate over speech data.")
                raise

            if speech:
                vad_logger.debug("Speech is existent.")
                if "start" in speech.keys():
                    vad_logger.debug("Start of the speech detected.")
                    self.currently_collecting = True
                    self.speech_buffer = []
                elif "end" in speech.keys():
                    vad_logger.debug("End of the speech detected.")
                    self.currently_collecting = False
                    self.speech_buffer.append(chunk)
                    buffer = self.speech_buffer.copy()
                    self.speech_buffer = []

                    vad_logger.debug("Returning current speech buffer.")
                    return buffer

            if self.currently_collecting:
                self.speech_buffer.append(chunk)

        vad_logger.debug("Returning None voice activity.")
        return None

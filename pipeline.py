from typing import Any

from numpy import concatenate, ndarray

from Transcription.language_detection import LanguageDetector
from Transcription.file_transcription import FileTranscriptor
from Transcription.live_transcription import LiveTranscriptor
from Translation.translator import Translator
from Synthesis.speech_synthesis import SpeechSynthesizer

from utility import standardize_audio, is_empty_audio, duration_validation, silence_validation
from voice_activity_detection import VADSession


class LiveSessionState:
    def __init__(self):
        self.vad: VADSession = VADSession()
        self.pending_speech_chunks: list[ndarray] = []
        self.trailing_silence_chunks: list[ndarray] = []
        self.trailing_silence_seconds: float = 0.0


class Pipeline:
    live_speech_end_silence_seconds = 5.0

    def __init__(self):
        self.vad = VADSession()

        self.language_detector = LanguageDetector()
        self.file_transcriptor = FileTranscriptor()
        self.translator = Translator()
        self.speech_synthesizer = SpeechSynthesizer()

        self.live_sessions: dict[str, LiveSessionState] = {}
        self.live_transcriptor = LiveTranscriptor()

    @staticmethod
    def _clear_live_session_state(session: LiveSessionState) -> None:
        session.vad.reset()
        session.pending_speech_chunks.clear()
        session.trailing_silence_chunks.clear()
        session.trailing_silence_seconds = 0.0

    def _build_success_result(self, audio: ndarray, audio_language: str,
                              chosen_target_language: str, live: bool) -> dict[str, Any]:
        if audio_language == "Detect":
            audio_language = max(self.language_detector.detect(audio).items(), key=lambda item: item[1])[0]

        transcriptor = self.live_transcriptor if live else self.file_transcriptor
        transcription_result = transcriptor.transcribe_audio(audio_input=audio, language=audio_language)
        translated_text = self.translator.translate_raw_text(text=transcription_result, source_language=audio_language,
                                                             target_language=chosen_target_language,)
        synthesized_audio_path = "Synthesis/Output/test.wav"
        self.speech_synthesizer.synthesize(spoken_text=translated_text, file_path=synthesized_audio_path)

        return\
            {
                "status": "success",
                "source_language": audio_language,
                "target_language": chosen_target_language,
                "transcribed_text": transcription_result,
                "translated_text": translated_text,
                "synthesized_audio_path": synthesized_audio_path,
            }

    def _finalize_live_segment(self, session_id: str, speech_buffer: list[ndarray], audio_language: str,
                               chosen_target_language: str) -> dict[str, Any]:
        full_audio = concatenate(speech_buffer)
        session = self.live_sessions[session_id]

        speech_timestamps = session.vad.file_voice_detection(full_audio)
        if not speech_timestamps:
            self._clear_live_session_state(session)
            del self.live_sessions[session_id]
            return {"status": "rejected", "reason": "No voice detected."}

        padding_seconds = 0.5
        start_sample = max(0, int((speech_timestamps[0]["start"] - padding_seconds) * session.vad.sampling_rate))
        end_sample = min(len(full_audio), int((speech_timestamps[-1]["end"] + padding_seconds) * session.vad.sampling_rate))
        absolute_speech_part = full_audio[start_sample:end_sample]

        result = self._build_success_result(audio=absolute_speech_part, audio_language=audio_language,
                                            chosen_target_language=chosen_target_language, live=True,)

        self._clear_live_session_state(session)
        del self.live_sessions[session_id]
        return result

    def process_file(self, audio_file_path: str, audio_language: str = "en",
                     chosen_target_language: str = "en") -> dict[str, Any]:
        audio = standardize_audio(audio_file_path)
        if is_empty_audio(audio):
            return {"status": "rejected", "reason": "Audio is empty."}
        if not duration_validation(audio):
            return {"status": "rejected", "reason": "Audio duration is not valid."}

        speech_timestamps = self.vad.file_voice_detection(audio)
        if not speech_timestamps:
            return {"status": "rejected", "reason": "No voice detected."}

        padding_seconds = 0.5
        start_sample = max(0, int((speech_timestamps[0]["start"] - padding_seconds) * self.vad.sampling_rate))
        end_sample = min(len(audio), int((speech_timestamps[-1]["end"] + padding_seconds) * self.vad.sampling_rate))
        absolute_speech_part = audio[start_sample:end_sample]
        if not silence_validation(absolute_speech_part):
            return \
                {
                    "status": "rejected",
                    "reason": "Audio is too silent, which can cause hallucinations during transcription."
                }

        return self._build_success_result(audio=absolute_speech_part, audio_language=audio_language,
                                          chosen_target_language=chosen_target_language, live=False,)

    def process_live_speech(self, session_id: str, audio_chunk: str | ndarray | None = None,
                            sampling_rate: int = 16000, audio_language: str = "Detect",
                            chosen_target_language: str = "en", finalize: bool = False) -> dict[str, Any]:
        if session_id not in self.live_sessions:
            if audio_chunk is None and finalize:
                return {"status": "idle", "reason": "No pending live speech segment."}
            self.live_sessions[session_id] = LiveSessionState()

        session = self.live_sessions[session_id]

        if audio_chunk is not None:
            audio = standardize_audio(audio_chunk, sampling_rate)
            if is_empty_audio(audio):
                return {"status": "rejected", "reason": "Audio chunk is empty."}

            was_collecting = session.vad.currently_collecting
            speech_buffer = session.vad.live_voice_detection(audio)
            is_collecting = session.vad.currently_collecting

            if speech_buffer:
                if session.pending_speech_chunks:
                    session.pending_speech_chunks.extend(session.trailing_silence_chunks)
                session.pending_speech_chunks.extend(speech_buffer)
                session.trailing_silence_chunks.clear()
                session.trailing_silence_seconds = 0.0
                return \
                    {
                        "status": "listening",
                        "reason": f"Speech end detected. Waiting for more than "
                                  f"{self.live_speech_end_silence_seconds:.0f} seconds of silence before finalizing.",
                    }

            if session.pending_speech_chunks:
                if not was_collecting and is_collecting:
                    session.pending_speech_chunks.extend(session.trailing_silence_chunks)
                    session.trailing_silence_chunks.clear()
                    session.trailing_silence_seconds = 0.0
                elif not is_collecting:
                    session.trailing_silence_chunks.append(audio)
                    session.trailing_silence_seconds += len(audio) / session.vad.sampling_rate

                    if session.trailing_silence_seconds > self.live_speech_end_silence_seconds:
                        finalized_speech_buffer = session.pending_speech_chunks.copy()
                        session.pending_speech_chunks.clear()
                        session.trailing_silence_chunks.clear()
                        session.trailing_silence_seconds = 0.0
                        return self._finalize_live_segment(session_id=session_id,
                                                           speech_buffer=finalized_speech_buffer,
                                                           audio_language=audio_language,
                                                           chosen_target_language=chosen_target_language,)

        if finalize:
            buffered_speech = session.pending_speech_chunks.copy()
            if session.vad.speech_buffer:
                if session.pending_speech_chunks:
                    buffered_speech.extend(session.trailing_silence_chunks)
                buffered_speech.extend(session.vad.speech_buffer.copy())

            if buffered_speech:
                return self._finalize_live_segment(session_id=session_id, speech_buffer=buffered_speech,
                                                   audio_language=audio_language,
                                                   chosen_target_language=chosen_target_language,)

            self._clear_live_session_state(session)
            del self.live_sessions[session_id]
            return {"status": "idle", "reason": "No pending live speech segment."}

        return {"status": "listening", "reason": "No completed speech segment yet."}

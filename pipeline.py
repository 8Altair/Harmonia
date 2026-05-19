from Transcription.language_detection import LanguageDetector
from Transcription.file_transcription import FileTranscriptor
from Translation.translator import Translator
from Synthesis.speech_synthesis import SpeechSynthesizer

from utility import standardize_audio, is_empty_audio, duration_validation, silence_validation, decider
from voice_activity_detection import VADSession


class FilePipeline:
    def __init__(self):
        self.vad = VADSession()
        self.language_detector = LanguageDetector()
        self.file_transcriptor = FileTranscriptor()
        self.translator = Translator()
        self.speech_synthesizer = SpeechSynthesizer()

    def process_file(self, audio_file_path: str, audio_language: str = "en", chosen_target_language: str = "en") -> dict:
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
            return {"status": "rejected", "reason": "Audio is too silent, which can cause hallucinations during transcription."}

        if audio_language == "Detect":
            audio_language = max(self.language_detector.detect(absolute_speech_part).items(),
                                 key=lambda x: x[1])[0]

        transcription_result = self.file_transcriptor.transcribe_audio(audio_input=absolute_speech_part,
                                                                       language=audio_language)
        translated_text = self.translator.translate_raw_text(text=transcription_result,
                                                             source_language=audio_language,
                                                             target_language=chosen_target_language)
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

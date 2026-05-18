import tempfile, os

from flask import Flask, request, jsonify

from pipeline import FilePipeline


pipeline = FilePipeline()

app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return 'Hello World!'
#
#
# @app.route('/transcription', methods=['POST'])
# def transcription():
#     audio_file = request.files.get("audio_file")
#
#     if audio_file is None:
#         return jsonify({"error": "No audio file provided."}), 400
#
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as tmp:
#         audio_file.save(tmp.name)
#         file_path = tmp.name
#
#     try:
#         detected_languages = decider(language_detector.detect(file_path))
#
#         if isinstance(detected_languages, str):
#             language = detected_languages
#         elif isinstance(detected_languages, tuple) and detected_languages[-1] is True:
#             language = detected_languages[0]
#         else:
#             return jsonify({"error": "No language detected confidently."}), 400
#
#         transcription_result = file_transcriptor.transcribe_audio(audio_file_path=file_path, language=language)
#
#         return jsonify(
#             {
#                 "text": transcription_result,
#                 "language": language
#             }), 200
#
#     finally:  # ALWAYS runs, even if error happens
#         if os.path.exists(file_path):
#             os.remove(file_path)
#
#
# @app.route("/translate", methods=["POST"])
# def translate():
#     data = request.get_json()
#
#     text = data.get("text")
#     target_language = data.get("target_language")
#     source_language = data.get("source_language")
#
#     if not text or not target_language:
#         return jsonify({"error": "Missing text or target language"}), 400
#
#     translated_text = translator.translate_raw_text(text, source_language, target_language)
#     return jsonify({"text": translated_text, "language": target_language}), 200
#
#
# @app.route("/test-local")
# def test_local():
#     file_path = r"C:\Users\dinoa\OneDrive - Univerza v Mariboru\Dokumenti\Sound Recordings\Test.m4a"
#     target_language = "bs"  # Change as needed
#
#     detected_languages = decider(language_detector.detect(file_path))
#
#     if isinstance(detected_languages, str):
#         language = detected_languages
#     elif isinstance(detected_languages, tuple) and detected_languages[-1] is True:
#         language = detected_languages[0]
#     else:
#         return jsonify(
#             {
#                 "error": "Language detection uncertain.",
#                 "candidates": detected_languages
#             }), 400
#
#     transcription_result = file_transcriptor.transcribe_audio(audio_file_path=file_path, language=language)
#
#     translated_text = translator.translate_raw_text(transcription_result, language, target_language)
#
#     return jsonify(
#         {
#             "source_language": language,
#             "target_language": target_language,
#             "original_text": transcription_result,
#             "translated_text": translated_text
#         })

@app.route("/process-file", methods=["GET"])
def process_file():
    test_audio_path = r"C:\Users\dinoa\OneDrive - Univerza v Mariboru\Dokumenti\Sound Recordings\Test_2.flac"

    result = pipeline.process_file(audio_file_path=test_audio_path)

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

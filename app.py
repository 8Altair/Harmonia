import tempfile, os

from flask import Flask, jsonify, request, send_file, send_from_directory

from pathlib import Path
from functools import lru_cache

from pipeline import Pipeline


app = Flask(__name__)   # Flask application instance

project_root = Path(__file__).resolve().parent  # Get the absolute path of the current file, then its parent directory
frontend_build_directory = project_root / "static" / "app"  # Define the path for the frontend build directory
synthesis_output_directory = project_root / "Synthesis" / "Output"  # Define the path for the synthesized speech output

pipeline = Pipeline()   # Create a pipeline instance

@app.route("/process-file", methods=["GET"])

@lru_cache(maxsize=1)
def get_frontend_configuration_payload() -> dict:
    whisper_languages = pipeline.language_detector.service.available_languages
    source_languages, target_languages = pipeline.translator.service.supported_languages()

    source_language_map =\
        {
            language.code.lower(): language.name
            for language in source_languages
        }
    target_language_map = \
        {
            language.code.lower(): language.name
            for language in target_languages
        }

    compatible_source_codes = sorted(set(whisper_languages).intersection(source_language_map),
                                     key=lambda code: source_language_map[code].lower(),)

    source_language_options = \
        [
            {
                "value": "Detect",
                "label": "Detect automatically"
            }
        ]
    source_language_options.extend(
        {
            "value": code,
            "label": f"{source_language_map[code]} ({code})",
        }
        for code in compatible_source_codes)

    target_language_options = \
        [
            {
                "value": code,
                "label": f"{name} ({code})",
            }
            for code, name in sorted(target_language_map.items(), key=lambda item: item[1].lower())
        ]

    default_target_language = "en"
    if default_target_language not in target_language_map:
        default_target_language = next((code for code in target_language_map if code.startswith("en")),
                                       target_language_options[0]["value"] if target_language_options else "",)

    return \
        {
            "source_languages": source_language_options,
            "target_languages": target_language_options,
            "default_source_language": "Detect",
            "default_target_language": default_target_language,
            "voice_label": "English voice",
            "live_chunk_duration_seconds": 3,
        }


def process_file():
    test_audio_path = r"C:\Users\dinoa\OneDrive - Univerza v Mariboru\Dokumenti\Sound Recordings\Test_2.flac"

    result = pipeline.process_file(audio_file_path=test_audio_path)

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

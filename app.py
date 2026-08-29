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


@app.route("/", methods=["GET"])
def serve_frontend():
    index_path = frontend_build_directory / "index.html"
    if index_path.exists():
        return send_from_directory(frontend_build_directory, "index.html")

    return jsonify(
        {
            "status": "frontend_not_built",
            "reason": "The React frontend has not been built yet. Run `npm install` and `npm run dev` inside `frontend`, or `npm run build` to serve it from Flask.",
        }), 503


@app.route("/assets/<path:file_name>", methods=["GET"])
def serve_frontend_assets(file_name: str):
    return send_from_directory(frontend_build_directory / "assets", file_name)


@app.route("/frontend-config", methods=["GET"])
def frontend_config():
    return jsonify(get_frontend_configuration_payload())


@app.route("/generated-audio/<path:file_name>", methods=["GET"])
def generated_audio(file_name: str):
    return send_from_directory(synthesis_output_directory, os.path.basename(file_name))


@app.route("/test-file", methods=["GET"])
def process_test_file():
    test_audio_path = r"C:\Users\dinoa\OneDrive - Univerza v Mariboru\Dokumenti\Sound Recordings\Test_2.flac"

    result = pipeline.process_file(audio_file_path=test_audio_path)
    if result.get("synthesized_audio_path"):
        result["synthesized_audio_url"] = f"/generated-audio/{Path(result['synthesized_audio_path']).name}"

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

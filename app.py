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
def process_file():
    test_audio_path = r"C:\Users\dinoa\OneDrive - Univerza v Mariboru\Dokumenti\Sound Recordings\Test_2.flac"

    result = pipeline.process_file(audio_file_path=test_audio_path)

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

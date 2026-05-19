import tempfile, os

from flask import Flask, request, jsonify

from pipeline import FilePipeline


pipeline = FilePipeline()

app = Flask(__name__)

@app.route("/process-file", methods=["GET"])
def process_file():
    test_audio_path = r"C:\Users\dinoa\OneDrive - Univerza v Mariboru\Dokumenti\Sound Recordings\Test_2.flac"

    result = pipeline.process_file(audio_file_path=test_audio_path)

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

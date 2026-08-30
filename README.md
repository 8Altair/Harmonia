# Harmonia

> **Development status:** Harmonia is in active development and is not yet finalized. File-based transcription is operational, while live transcription remains experimental and requires further work.

Harmonia is a web application built around an NLP pipeline that converts spoken content into text, translates it, and synthesizes the translated text as speech.

## Current Functionality

- Process uploaded audio and video files.
- Detect the source language or use a selected language.
- Transcribe speech from files.
- Translate transcribed text into a selected target language.
- Convert translated text into synthesized speech.
- Capture live microphone audio through the frontend. The live-processing workflow is still under development.
- Display pipeline status, recent activity, and processing results in the web interface.

## Project Structure

```text
Harmonia/
|-- app.py                 Flask application and HTTP endpoints
|-- pipeline.py            NLP pipeline orchestration
|-- Transcription/         Language detection and speech recognition
|-- Translation/           Machine translation integration
|-- Synthesis/             Text-to-speech processing
|-- frontend/              React user interface
|   `-- src/
|       |-- components/
|       |-- services/
|       `-- styles/
|-- static/                Generated frontend build served by Flask
|-- Logs/                  Application runtime logs
|-- Start-Harmonia.ps1     Full application startup
|-- Stop-Harmonia.ps1      Full application shutdown
|-- requirements.txt       Python dependencies
`-- LICENSE                Repository license
```

## Technologies

- **Backend:** Python and Flask
- **Frontend:** React, Vite, and Lucide React
- **Speech recognition and language detection:** OpenAI Whisper
- **Voice activity detection:** Silero VAD
- **Translation:** DeepL API
- **Speech synthesis:** Coqui TTS
- **Audio and ML processing:** PyTorch, NumPy, Librosa, and SoundFile
- **Local tooling:** PowerShell startup and shutdown scripts

## Running the Application

On Windows, the complete application can be started and stopped with:

```powershell
.\Start-Harmonia.ps1
.\Stop-Harmonia.ps1
```

For frontend-only visual testing:

```powershell
.\Start-Harmonia-Frontend.ps1
.\Stop-Harmonia-Frontend.ps1
```

The full application requires the Python environment and frontend dependencies to be installed. Translation also requires a valid DeepL authorization key in the local environment configuration.

## License

Harmonia is licensed under the [PolyForm Noncommercial License 1.0.0](LICENSE).

This README is intentionally brief and will be expanded as the project approaches a finalized release.

---

*Note: The Harmonia frontend was built entirely with AI assistance.*

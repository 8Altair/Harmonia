import { LoaderCircle, Mic, MicOff, UploadCloud } from "lucide-react";
import { useRef, useState } from "react";

function UploadPanel({
  mode,
  onModeChange,
  selectedFile,
  onFileSelect,
  onSubmit,
  loading,
  disabled,
  isRecording,
  onRecordToggle,
  liveMessage,
}) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  function handleDrop(event) {
    event.preventDefault();
    setIsDragging(false);

    const file = event.dataTransfer.files?.[0];
    if (file) {
      onFileSelect(file);
    }
  }

  return (
    <section className={`upload-panel${isDragging ? " upload-panel--active" : ""}`}>
      <div className="mode-switcher" role="tablist" aria-label="Transcription mode">
        <button
          type="button"
          className={`mode-switcher__button${mode === "file" ? " mode-switcher__button--active" : ""}`}
          onClick={() => onModeChange("file")}
          disabled={isRecording}
        >
          File transcription
        </button>
        <button
          type="button"
          className={`mode-switcher__button${mode === "live" ? " mode-switcher__button--active" : ""}`}
          onClick={() => onModeChange("live")}
          disabled={isRecording}
        >
          Live transcription
        </button>
      </div>

      <div
        className="upload-dropzone"
        onDragEnter={
          mode === "file"
            ? (event) => {
                event.preventDefault();
                setIsDragging(true);
              }
            : undefined
        }
        onDragLeave={
          mode === "file"
            ? (event) => {
                event.preventDefault();
                setIsDragging(false);
              }
            : undefined
        }
        onDragOver={mode === "file" ? (event) => event.preventDefault() : undefined}
        onDrop={mode === "file" ? handleDrop : undefined}
      >
        {mode === "file" ? (
          <>
            <div className="upload-dropzone__icon" aria-hidden="true">
              <UploadCloud size={28} />
            </div>

            <div className="upload-dropzone__copy">
              <h3>Upload audio file</h3>
              <p>Drag and drop a recording here, or browse from disk.</p>
              <span>Supports WAV, MP3, FLAC, M4A, OGG, AAC and similar audio formats.</span>
            </div>

            <div className="upload-dropzone__actions">
              <input
                ref={inputRef}
                type="file"
                accept="audio/*"
                hidden
                onChange={(event) => {
                  const file = event.target.files?.[0];
                  if (file) {
                    onFileSelect(file);
                  }
                }}
              />
              <button type="button" className="button-secondary" onClick={() => inputRef.current?.click()}>
                Browse Files
              </button>
              <button type="button" className="button-primary" onClick={onSubmit} disabled={disabled}>
                {loading ? <LoaderCircle className="spin" size={18} /> : null}
                <span>{loading ? "Processing..." : "Process File"}</span>
              </button>
            </div>
          </>
        ) : (
          <>
            <div className={`upload-dropzone__icon${isRecording ? " upload-dropzone__icon--recording" : ""}`} aria-hidden="true">
              {isRecording ? <Mic size={28} /> : <MicOff size={28} />}
            </div>

            <div className="upload-dropzone__copy">
              <h3>Live microphone stream</h3>
              <p>Capture speech from your microphone and send chunks to the live pipeline.</p>
              <span>{liveMessage}</span>
            </div>

            <div className="upload-dropzone__actions">
              <button
                type="button"
                className={isRecording ? "button-danger" : "button-primary"}
                onClick={onRecordToggle}
                disabled={loading}
              >
                {loading ? <LoaderCircle className="spin" size={18} /> : null}
                <span>{isRecording ? "Stop microphone" : "Start microphone"}</span>
              </button>
            </div>
          </>
        )}
      </div>

      {selectedFile || mode === "live" ? (
        <div className="upload-meta">
          <div>
            <span className="upload-meta__label">{mode === "file" ? "Selected file" : "Microphone"}</span>
            <strong>{mode === "file" ? selectedFile.name : (isRecording ? "Active" : "Stopped")}</strong>
          </div>
          <div>
            <span className="upload-meta__label">{mode === "file" ? "Size" : "Capture mode"}</span>
            <strong>
              {mode === "file"
                ? `${(selectedFile.size / (1024 * 1024)).toFixed(2)} MB`
                : "3 second chunk upload"}
            </strong>
          </div>
        </div>
      ) : null}
    </section>
  );
}

export default UploadPanel;

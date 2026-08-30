import { AlertTriangle, CheckCircle2, FileAudio, LoaderCircle, Mic } from "lucide-react";

import { PipelineIcon } from "./PipelineVisuals";

function StatusIcon({ phase }) {
  if (phase === "loading") {
    return <LoaderCircle className="spin" size={18} />;
  }
  if (phase === "success") {
    return <CheckCircle2 size={18} />;
  }
  if (phase === "rejected" || phase === "error") {
    return <AlertTriangle size={18} />;
  }
  return <CheckCircle2 size={18} />;
}

function statusLabelForPhase(phase) {
  if (phase === "listening") {
    return "Listening";
  }
  if (phase === "loading") {
    return "Processing";
  }
  if (phase === "success") {
    return "Complete";
  }
  if (phase === "rejected") {
    return "Rejected";
  }
  if (phase === "error") {
    return "Failed";
  }
  return "Ready";
}

function StatusPanel({ phase, sourceLanguage, targetLanguage, selectedFile, message, mode, isRecording }) {
  const items = [
    { key: "transcription", title: "Transcription" },
    { key: "translation", title: "Translation" },
    { key: "synthesis", title: "Speech Synthesis" },
  ];

  return (
    <div className="side-stack">
      <section className="side-card">
        <div className="side-card__header">
          <div>
            <h3>Pipeline Status</h3>
          </div>
          <span className={`status-pill status-pill--${phase}`}>{statusLabelForPhase(phase)}</span>
        </div>

        <p className="side-card__operational">
          <span className="operational-dot" />
          {phase === "error" || phase === "rejected" ? "Pipeline needs attention" : "All systems operational"}
        </p>

        <p className="side-card__message">{message}</p>

        <div className="status-list">
          {items.map((item) => {
            return (
              <div key={item.key} className="status-row">
                <div className="status-row__meta">
                  <span className={`status-row__icon status-row__icon--${item.key}`}>
                    <PipelineIcon kind={item.key} />
                  </span>
                  <div>
                    <strong>{item.title}</strong>
                    <span>{statusLabelForPhase(phase)}</span>
                  </div>
                </div>
                <span className={`status-row__state status-row__state--${phase}`}>
                  <StatusIcon phase={phase} />
                </span>
              </div>
            );
          })}
        </div>
      </section>

      <section className="side-card">
        <div className="side-card__header">
          <h3>Recent Activity</h3>
          <span className="side-card__link">Current</span>
        </div>

        <div className="activity-row">
          <span className="activity-row__icon">
            {mode === "file" ? <FileAudio size={20} /> : <Mic size={20} />}
          </span>
          <div className="activity-row__copy">
            <strong>
              {mode === "file"
                ? (selectedFile?.name || "No file selected")
                : (isRecording ? "Live microphone" : "Microphone stopped")}
            </strong>
            <span>{sourceLanguage || "Detect"}{" -> "}{targetLanguage || "-"}</span>
            <small>{statusLabelForPhase(phase)}</small>
          </div>
          <span className={`activity-row__state activity-row__state--${phase}`}>
            <StatusIcon phase={phase} />
          </span>
        </div>
      </section>
    </div>
  );
}

export default StatusPanel;

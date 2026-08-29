function ResultSection({ title, body }) {
  return (
    <article className="result-card">
      <div className="result-card__header">
        <p>{title}</p>
      </div>
      <div className="result-card__body">{body || "No content returned yet."}</div>
    </article>
  );
}

function ResultsPanel({ phase, result, audioUrl }) {
  if (!result && (phase === "idle" || phase === "listening" || phase === "loading")) {
    return null;
  }

  if (phase === "rejected" || phase === "error") {
    return (
      <section className="results-grid">
        <ResultSection title="Pipeline response" body={result?.reason || "The backend did not provide a reason."} />
      </section>
    );
  }

  return (
    <section className="results-grid">
      <ResultSection title="Transcribed text" body={result?.transcribed_text} />
      <ResultSection title="Translated text" body={result?.translated_text} />
      <article className="result-card result-card--audio">
        <div className="result-card__header">
          <p>Synthesized audio</p>
        </div>
        <div className="result-card__body result-card__body--audio">
          {audioUrl ? (
            <>
              <audio controls src={audioUrl} className="audio-player">
                Your browser does not support audio playback.
              </audio>
              <a className="button-secondary button-secondary--inline" href={audioUrl} download>
                Download audio
              </a>
            </>
          ) : (
            "The backend did not return a playable synthesized audio URL."
          )}
        </div>
      </article>
    </section>
  );
}

export default ResultsPanel;

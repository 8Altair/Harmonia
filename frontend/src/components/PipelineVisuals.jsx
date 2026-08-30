import PipelineConnectorArtwork from "./PipelineConnectorArtwork";
import MicrophoneArtwork from "./MicrophoneArtwork";
import SpeechSynthesisArtwork from "./SpeechSynthesisArtwork";
import TranslationArtwork from "./TranslationArtwork";

function PipelineIcon({ kind, className = "" }) {
  const classNames = `pipeline-art pipeline-art--${kind} ${className}`.trim();

  if (kind === "transcription") {
    return <MicrophoneArtwork className={classNames} />;
  }

  if (kind === "translation") {
    return <TranslationArtwork className={classNames} />;
  }

  return <SpeechSynthesisArtwork className={classNames} />;
}

function PipelineConnector({ className = "" }) {
  return <PipelineConnectorArtwork className={className} />;
}

export { PipelineConnector, PipelineIcon };

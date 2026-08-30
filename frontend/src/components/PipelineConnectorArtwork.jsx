function PipelineConnectorArtwork({ className = "" }) {
  return (
    <svg className={`pipeline-connector ${className}`.trim()} viewBox="0 0 120 48" fill="none" aria-hidden="true">
      <circle cx="91" cy="24" r="18" fill="var(--connector-panel, #07162e)" stroke="currentColor" strokeWidth="2" />
      <path d="M28 24h62" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
      <path d="m87 17 7 7-7 7" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default PipelineConnectorArtwork;

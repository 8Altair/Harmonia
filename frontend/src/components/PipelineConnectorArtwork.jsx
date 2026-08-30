function PipelineConnectorArtwork({ className = "" }) {
  return (
    <svg className={`pipeline-connector ${className}`.trim()} viewBox="0 0 120 48" fill="none" aria-hidden="true">
      <path d="M0 24h73" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
      <circle cx="91" cy="24" r="18" fill="var(--connector-panel, #07162e)" stroke="currentColor" strokeWidth="2" />
      <path d="m84 17 7 7-7 7" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default PipelineConnectorArtwork;

function PipelineWaveform({ mirrored = false, className = "" }) {
  const classNames = `pipeline-waveform${mirrored ? " pipeline-waveform--mirrored" : ""} ${className}`.trim();

  return (
    <svg className={classNames} viewBox="0 0 160 92" fill="none" aria-hidden="true">
      <g stroke="currentColor" strokeLinecap="round">
        <path d="M0 46c19 0 22-25 43-25s23 25 44 25 22-25 43-25 18 25 30 25" strokeWidth="2.4" />
        <path d="M0 53c19 0 22-18 43-18s23 18 44 18 22-18 43-18 18 18 30 18" strokeWidth="1.8" opacity=".78" />
        <path d="M0 60c19 0 22-11 43-11s23 11 44 11 22-11 43-11 18 11 30 11" strokeWidth="1.3" opacity=".52" />
        <path d="M22 23v46M30 29v34M38 35v22M130 29v34M138 35v22" strokeWidth="1" opacity=".35" />
      </g>
    </svg>
  );
}

export default PipelineWaveform;

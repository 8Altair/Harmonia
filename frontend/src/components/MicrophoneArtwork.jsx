function MicrophoneArtwork({ className = "" }) {
  return (
    <svg className={className} viewBox="0 0 120 120" fill="none" aria-hidden="true">
      <g stroke="currentColor" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M15 51v18M25 42v36M35 49v22M85 49v22M95 42v36M105 51v18" opacity=".82" />
        <rect x="45" y="19" width="30" height="51" rx="15" />
        <path d="M37 55v4a23 23 0 0 0 46 0v-4M60 82V99M48 99h24" />
        <path d="M54 34h12M54 45h12M54 56h12" opacity=".78" />
      </g>
    </svg>
  );
}

export default MicrophoneArtwork;

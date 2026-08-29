function TranslationArtwork({ className = "" }) {
  return (
    <svg className={className} viewBox="0 0 120 120" fill="none" aria-hidden="true">
      <g stroke="currentColor" strokeWidth="4.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="54" cy="54" r="35" />
        <path d="M19 54h70M54 19c11 10 17 22 17 35s-6 25-17 35c-11-10-17-22-17-35s6-25 17-35ZM26 32c8 5 18 8 28 8s20-3 28-8M26 76c8-5 18-8 28-8s20 3 28 8" />
        <rect x="72" y="68" width="31" height="29" rx="4" fill="var(--art-panel, #071426)" />
        <path d="M80 76h14M87 76v12M82 85h10M95 87l3 4" />
      </g>
    </svg>
  );
}

export default TranslationArtwork;

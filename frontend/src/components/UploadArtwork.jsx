function UploadArtwork({ className = "" }) {
  return (
    <svg className={`upload-art ${className}`.trim()} viewBox="0 0 120 120" fill="none" aria-hidden="true">
      <g stroke="currentColor" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M35 91H28a20 20 0 1 1 4-39 29 29 0 0 1 56 8 16 16 0 1 1 5 31H83" />
        <path d="M60 94V58M45 73l15-15 15 15" />
      </g>
    </svg>
  );
}

export default UploadArtwork;

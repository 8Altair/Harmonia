export async function fetchFrontendConfig() {
  const response = await fetch("/frontend-config");
  if (!response.ok) {
    throw new Error("Unable to load frontend configuration from the backend.");
  }

  return response.json();
}

async function parseApiResponse(response) {
  const payload = await response.json().catch(() => ({
    status: "error",
    reason: "The backend returned an unreadable response.",
  }));

  if (!response.ok) {
    throw new Error(payload.reason || "The backend rejected the request.");
  }

  return payload;
}

export async function submitFileProcessing({ file, sourceLanguage, targetLanguage }) {
  const formData = new FormData();
  formData.append("audio_file", file);
  formData.append("source_language", sourceLanguage);
  formData.append("target_language", targetLanguage);

  const response = await fetch("/process-file", {
    method: "POST",
    body: formData,
  });

  return parseApiResponse(response);
}

export async function submitLiveChunk({
  sessionId,
  chunk,
  sourceLanguage,
  targetLanguage,
  samplingRate,
  finalize = false,
}) {
  const formData = new FormData();
  formData.append("session_id", sessionId);
  formData.append("source_language", sourceLanguage);
  formData.append("target_language", targetLanguage);
  formData.append("sampling_rate", String(samplingRate || 16000));
  formData.append("finalize", String(finalize));

  if (chunk) {
    formData.append("audio_chunk", chunk, chunk.name || "live_chunk.webm");
  }

  const response = await fetch("/process-live-speech", {
    method: "POST",
    body: formData,
  });

  return parseApiResponse(response);
}

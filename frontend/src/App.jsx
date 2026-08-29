import { Globe2, Languages, MoveRight, Volume2 } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import HeaderBar from "./components/HeaderBar";
import MicrophoneArtwork from "./components/MicrophoneArtwork";
import ResultsPanel from "./components/ResultsPanel";
import Sidebar from "./components/Sidebar";
import StageCircle from "./components/StageCircle";
import StatusPanel from "./components/StatusPanel";
import UploadPanel from "./components/UploadPanel";
import { fetchFrontendConfig, submitFileProcessing, submitLiveChunk } from "./services/api";

const isFrontendPreview = import.meta.env.VITE_FRONTEND_ONLY === "true";
const previewConfig = {
  source_languages: [
    { value: "Detect", label: "Detect automatically" },
    { value: "English", label: "English" },
    { value: "Spanish", label: "Spanish" },
  ],
  target_languages: [
    { value: "English", label: "English" },
    { value: "Spanish", label: "Spanish" },
  ],
  default_source_language: "Detect",
  default_target_language: "English",
  voice_label: "English voice",
  live_chunk_duration_seconds: 3,
};

const defaultConfig = {
  source_languages: [{ value: "Detect", label: "Detect automatically" }],
  target_languages: [],
  default_source_language: "Detect",
  default_target_language: "",
  voice_label: "English voice",
  live_chunk_duration_seconds: 3,
};

function deriveAudioUrl(result) {
  if (!result) {
    return "";
  }

  if (result.synthesized_audio_url) {
    return result.synthesized_audio_url;
  }

  if (result.synthesized_audio_path) {
    const normalizedPath = result.synthesized_audio_path.split(/[\\/]/).pop();
    return `/generated-audio/${normalizedPath}`;
  }

  return "";
}

function statusMessageForPhase(phase, result, mode, isRecording, statusReason) {
  if (statusReason) {
    return statusReason;
  }
  if (mode === "live" && isRecording && phase !== "error" && phase !== "rejected") {
    return "The microphone is active. Harmonia is listening for a completed speech segment.";
  }
  if (phase === "listening") {
    return "Listening for speech boundaries in the live stream.";
  }
  if (phase === "loading") {
    return mode === "live"
      ? "Finalizing the live stream and processing the last captured speech."
      : "The Flask pipeline is processing the uploaded file.";
  }
  if (phase === "success") {
    return "All three stages completed successfully.";
  }
  if (phase === "rejected") {
    return result?.reason || "The backend rejected the file.";
  }
  if (phase === "error") {
    return result?.reason || "The request failed before a valid result was returned.";
  }
  return "Ready to submit a file for processing";
}

function createSessionId() {
  if (window.crypto?.randomUUID) {
    return window.crypto.randomUUID();
  }

  return `harmonia-live-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function consumeFloat32Samples(chunks, sampleCount) {
  const extracted = new Float32Array(sampleCount);
  let offset = 0;

  while (offset < sampleCount && chunks.length > 0) {
    const chunk = chunks[0];
    const availableSamples = Math.min(chunk.length, sampleCount - offset);
    extracted.set(chunk.subarray(0, availableSamples), offset);
    offset += availableSamples;

    if (availableSamples === chunk.length) {
      chunks.shift();
    } else {
      chunks[0] = chunk.subarray(availableSamples);
    }
  }

  return extracted;
}

function mergeFloat32Samples(chunks) {
  const totalSamples = chunks.reduce((sampleCount, chunk) => sampleCount + chunk.length, 0);
  const merged = new Float32Array(totalSamples);
  let offset = 0;

  for (const chunk of chunks) {
    merged.set(chunk, offset);
    offset += chunk.length;
  }

  return merged;
}

function encodeWavFile(samples, sampleRate) {
  const bytesPerSample = 2;
  const wavBuffer = new ArrayBuffer(44 + samples.length * bytesPerSample);
  const view = new DataView(wavBuffer);
  const channelCount = 1;
  const blockAlign = channelCount * bytesPerSample;
  const byteRate = sampleRate * blockAlign;

  const writeAscii = (offset, value) => {
    for (let index = 0; index < value.length; index += 1) {
      view.setUint8(offset + index, value.charCodeAt(index));
    }
  };

  writeAscii(0, "RIFF");
  view.setUint32(4, 36 + samples.length * bytesPerSample, true);
  writeAscii(8, "WAVE");
  writeAscii(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, channelCount, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, byteRate, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, 16, true);
  writeAscii(36, "data");
  view.setUint32(40, samples.length * bytesPerSample, true);

  let offset = 44;
  for (const sample of samples) {
    const clampedSample = Math.max(-1, Math.min(1, sample));
    view.setInt16(offset, clampedSample < 0 ? clampedSample * 0x8000 : clampedSample * 0x7fff, true);
    offset += bytesPerSample;
  }

  return new File([wavBuffer], "live_chunk.wav", { type: "audio/wav" });
}

function App() {
  const [theme, setTheme] = useState(() =>
    window.localStorage.getItem("harmonia-theme") === "light" ? "light" : "dark",
  );
  const [config, setConfig] = useState(isFrontendPreview ? previewConfig : defaultConfig);
  const [configError, setConfigError] = useState("");
  const [mode, setMode] = useState("file");
  const [selectedFile, setSelectedFile] = useState(null);
  const [sourceLanguage, setSourceLanguage] = useState("Detect");
  const [targetLanguage, setTargetLanguage] = useState("");
  const [phase, setPhase] = useState("idle");
  const [result, setResult] = useState(null);
  const [statusReason, setStatusReason] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const latestResultRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const audioContextRef = useRef(null);
  const sourceNodeRef = useRef(null);
  const processorNodeRef = useRef(null);
  const pcmChunkBufferRef = useRef([]);
  const bufferedSampleCountRef = useRef(0);
  const liveSampleRateRef = useRef(16000);
  const liveSessionIdRef = useRef(null);
  const liveQueueRef = useRef(Promise.resolve());
  const stopRequestedRef = useRef(false);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.colorScheme = theme;
    window.localStorage.setItem("harmonia-theme", theme);
  }, [theme]);

  useEffect(() => {
    if (isFrontendPreview) {
      return undefined;
    }

    let ignore = false;

    async function loadConfig() {
      try {
        const payload = await fetchFrontendConfig();
        if (ignore) {
          return;
        }

        setConfig(payload);
        setSourceLanguage(payload.default_source_language || "Detect");
        setTargetLanguage(payload.default_target_language || payload.target_languages?.[0]?.value || "");
      } catch (error) {
        if (ignore) {
          return;
        }

        setConfigError(error.message);
      }
    }

    loadConfig();

    return () => {
      ignore = true;
    };
  }, []);

  useEffect(() => () => {
    mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
    processorNodeRef.current?.disconnect();
    sourceNodeRef.current?.disconnect();
    audioContextRef.current?.close();
  }, []);

  useEffect(() => {
    latestResultRef.current = result;
  }, [result]);

  function applyBackendPayload(payload, options = {}) {
    const { keepListening = false, ignoreIdle = false } = options;

    if (payload.status === "success") {
      setResult(payload);
      setStatusReason(keepListening ? "Live segment processed. Harmonia is still listening." : "");
      setPhase(keepListening ? "listening" : "success");
      return;
    }

    if (payload.status === "listening") {
      setStatusReason(payload.reason || "");
      setPhase("listening");
      return;
    }

    if (payload.status === "idle" && ignoreIdle) {
      if (!latestResultRef.current) {
        setPhase("idle");
      }
      setStatusReason("");
      return;
    }

    if (payload.status === "rejected" || payload.status === "error") {
      setResult((currentResult) => currentResult ?? payload);
      setStatusReason(payload.reason || "");
      setPhase(payload.status);
      return;
    }

    setStatusReason(payload.reason || "");
    setPhase(payload.status || "idle");
  }

  function enqueueLiveRequest(task) {
    liveQueueRef.current = liveQueueRef.current
      .then(task)
      .catch((error) => {
        setPhase("error");
        setStatusReason(error.message || "The live pipeline request failed.");
        setIsRecording(false);
      });

    return liveQueueRef.current;
  }

  function resetLiveAudioResources() {
    processorNodeRef.current?.disconnect();
    sourceNodeRef.current?.disconnect();
    mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
    audioContextRef.current?.close();

    processorNodeRef.current = null;
    sourceNodeRef.current = null;
    mediaStreamRef.current = null;
    audioContextRef.current = null;
    pcmChunkBufferRef.current = [];
    bufferedSampleCountRef.current = 0;
    liveSessionIdRef.current = null;
    stopRequestedRef.current = false;
  }

  async function handleSubmit() {
    if (!selectedFile || !targetLanguage) {
      return;
    }

    setPhase("loading");
    setResult(null);
    setStatusReason("");

    try {
      const payload = await submitFileProcessing({
        file: selectedFile,
        sourceLanguage,
        targetLanguage,
      });

      setResult(payload);
      setPhase(payload.status || "success");
    } catch (error) {
      setPhase("error");
      setResult({
        status: "error",
        reason: error.message,
      });
      setStatusReason(error.message);
    }
  }

  async function startLiveRecording() {
    const AudioContextCtor = window.AudioContext || window.webkitAudioContext;
    if (!navigator.mediaDevices?.getUserMedia || !AudioContextCtor) {
      setPhase("error");
      setStatusReason("This browser does not support live microphone capture.");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const audioContext = new AudioContextCtor();
      const sourceNode = audioContext.createMediaStreamSource(stream);
      const processorNode = audioContext.createScriptProcessor(4096, 1, 1);
      const sessionId = createSessionId();
      const chunkSizeInSamples = Math.max(1, Math.floor(audioContext.sampleRate * (config.live_chunk_duration_seconds || 3)));

      mediaStreamRef.current = stream;
      audioContextRef.current = audioContext;
      sourceNodeRef.current = sourceNode;
      processorNodeRef.current = processorNode;
      liveSessionIdRef.current = sessionId;
      liveSampleRateRef.current = audioContext.sampleRate;
      stopRequestedRef.current = false;
      pcmChunkBufferRef.current = [];
      bufferedSampleCountRef.current = 0;

      setResult(null);
      setStatusReason("Microphone enabled. Harmonia is listening.");
      setPhase("listening");
      setIsRecording(true);

      processorNode.onaudioprocess = (event) => {
        if (stopRequestedRef.current) {
          return;
        }

        const monoChunk = new Float32Array(event.inputBuffer.getChannelData(0));
        pcmChunkBufferRef.current.push(monoChunk);
        bufferedSampleCountRef.current += monoChunk.length;

        while (bufferedSampleCountRef.current >= chunkSizeInSamples) {
          const chunkSamples = consumeFloat32Samples(pcmChunkBufferRef.current, chunkSizeInSamples);
          bufferedSampleCountRef.current -= chunkSamples.length;
          const wavChunk = encodeWavFile(chunkSamples, liveSampleRateRef.current);

          enqueueLiveRequest(async () => {
            const payload = await submitLiveChunk({
              sessionId,
              chunk: wavChunk,
              sourceLanguage,
              targetLanguage,
              samplingRate: liveSampleRateRef.current,
            });
            applyBackendPayload(payload, { keepListening: !stopRequestedRef.current });
          });
        }
      };

      sourceNode.connect(processorNode);
      processorNode.connect(audioContext.destination);
    } catch (error) {
      setPhase("error");
      setStatusReason(error.message || "Failed to access the microphone.");
      resetLiveAudioResources();
      setIsRecording(false);
    }
  }

  function stopLiveRecording() {
    if (!audioContextRef.current || !liveSessionIdRef.current) {
      return;
    }

    stopRequestedRef.current = true;
    setPhase("loading");
    setStatusReason("Stopping microphone and flushing the last live segment.");
    processorNodeRef.current?.disconnect();
    sourceNodeRef.current?.disconnect();

    const remainingSamples = mergeFloat32Samples(pcmChunkBufferRef.current);
    pcmChunkBufferRef.current = [];
    bufferedSampleCountRef.current = 0;

    enqueueLiveRequest(async () => {
      const payload = await submitLiveChunk({
        sessionId: liveSessionIdRef.current,
        chunk: remainingSamples.length > 0 ? encodeWavFile(remainingSamples, liveSampleRateRef.current) : null,
        sourceLanguage,
        targetLanguage,
        samplingRate: liveSampleRateRef.current,
        finalize: true,
      });
      applyBackendPayload(payload, { ignoreIdle: true });
    }).finally(() => {
      resetLiveAudioResources();
      setIsRecording(false);
      setPhase((currentPhase) =>
        currentPhase === "listening" ? (latestResultRef.current ? "success" : "idle") : currentPhase,
      );
    });
  }

  function handleRecordToggle() {
    if (isRecording) {
      stopLiveRecording();
      return;
    }

    startLiveRecording();
  }

  const audioUrl = deriveAudioUrl(result);
  const canSubmit = Boolean(selectedFile && targetLanguage) && phase !== "loading";
  const pipelineMessage = configError || statusMessageForPhase(phase, result, mode, isRecording, statusReason);

  return (
    <div className="app-shell">
      <Sidebar theme={theme} onThemeChange={setTheme} />

      <main className="main-panel">
        <HeaderBar />

        <section className="hero-panel">
          <div className="hero-backdrop" aria-hidden="true" />

          <div className="hero-heading">
            <h2>Create. Translate. Speak.</h2>
            <p>End-to-end language processing pipeline</p>
          </div>

          <div className="pipeline-row">
            <StageCircle
              accent="blue"
              icon={<MicrophoneArtwork className="stage-icon stage-icon--transcription" />}
              index="1"
              title="Transcription"
              description="Convert speech to text"
              controlLabel="Source language"
              options={config.source_languages}
              value={sourceLanguage}
              onChange={setSourceLanguage}
            />

            <div className="pipeline-link" aria-hidden="true">
              <MoveRight size={24} />
            </div>

            <StageCircle
              accent="cyan"
              icon={
                <span className="stage-icon stage-icon--translation">
                  <Globe2 className="stage-icon__globe" size={88} strokeWidth={1.8} />
                  <span className="stage-icon__language-badge">
                    <Languages size={34} strokeWidth={1.8} />
                  </span>
                </span>
              }
              index="2"
              title="Translation"
              description="Translate text to the selected target language"
              controlLabel="Target language"
              options={config.target_languages}
              value={targetLanguage}
              onChange={setTargetLanguage}
            />

            <div className="pipeline-link pipeline-link--violet" aria-hidden="true">
              <MoveRight size={24} />
            </div>

            <StageCircle
              accent="violet"
              icon={<Volume2 size={92} strokeWidth={1.8} />}
              index="3"
              title="Speech Synthesis"
              description="Convert translated text to speech output"
              controlLabel="Voice profile"
              badge={config.voice_label}
            />
          </div>

          <UploadPanel
            mode={mode}
            onModeChange={setMode}
            selectedFile={selectedFile}
            onFileSelect={setSelectedFile}
            onSubmit={handleSubmit}
            loading={phase === "loading"}
            disabled={!canSubmit || mode !== "file"}
            isRecording={isRecording}
            onRecordToggle={handleRecordToggle}
            liveMessage={
              isRecording
                ? "The browser is streaming 3 second WAV chunks to the live pipeline."
                : "Enable the microphone to stream 3 second WAV chunks to the backend."
            }
          />

          {(configError || phase === "rejected" || phase === "error") ? (
            <div className={`message-banner message-banner--${phase === "idle" ? "error" : phase}`}>
              {pipelineMessage}
            </div>
          ) : null}
        </section>

        <ResultsPanel phase={phase} result={result} audioUrl={audioUrl} />
      </main>

      <StatusPanel
        phase={phase}
        sourceLanguage={sourceLanguage}
        targetLanguage={targetLanguage}
        selectedFile={selectedFile}
        message={pipelineMessage}
        mode={mode}
        isRecording={isRecording}
      />
    </div>
  );
}

export default App;

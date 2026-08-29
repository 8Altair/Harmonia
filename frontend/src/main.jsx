import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles/index.css";
import "./styles/app.css";
import "./styles/header-layout.css";
import "./styles/pipeline-waveform.css";
import "./styles/stage-circles.css";
import "./styles/upload-art.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

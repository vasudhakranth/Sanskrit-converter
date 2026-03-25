import React, { useState, useRef, useEffect } from "react";
import "./App.css";

const modes = ["USR-JSON", "JSON-NLG", "USR-NLG"];

export default function App() {
  const [activeMode, setActiveMode] = useState("USR-JSON");
  const [inputText, setInputText] = useState("");
  const [output, setOutput] = useState("");
  const [language, setLanguage] = useState("english");
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFileName, setSelectedFileName] = useState("");
  const fileInputRef = useRef(null);

// Handle Mode Switching - Always clear for fresh start
const handleModeChange = (newMode) => {
    setInputText("");
    setOutput("");
    setSelectedFileName("");
    setActiveMode(newMode);
  };

const handleFileUpload = async (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setSelectedFileName(selectedFile.name);
      setOutput("");
      const text = await selectedFile.text();
      setInputText(text);
    }
  };

  const handleConvert = async () => {
    const input = inputText.trim();
    if (!input) return;

    setIsLoading(true);
    setOutput("");

    try {
      const response = await fetch("http://localhost:5000/api/convert", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mode: activeMode,
          text: input,
          language: language,
        }),
      });

      const data = await response.json();
      
      if (response.ok) {
        setOutput(data.output);
      } else {
        setOutput(`Error: ${data.error}`);
      }
    } catch (error) {
      setOutput(`Failed to connect to server: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(output);
    alert("Copied to clipboard!");
  };

  const handleDownload = () => {
    const blob = new Blob([output], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    // Name the file based on the mode
    a.download = `sanskrit_${activeMode.toLowerCase()}_output.${activeMode === 'USR-JSON' ? 'json' : 'txt'}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="app">
      <div className="navbar">
        <h2 className="logo">Sanskrit Converter</h2>
        <div className="nav-buttons">
          {modes.map((mode) => (
            <button
              key={mode}
              className={activeMode === mode ? "active" : ""}
              onClick={() => handleModeChange(mode)}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>

      <div className="container">
        {/* INPUT PANEL */}
        <div className="panel">
          <h3>Input ({activeMode})</h3>
          
          {(activeMode === "JSON-NLG" || activeMode === "USR-NLG") && (
            <div className="dropdown-section">
              <label>Language:</label>
              <select value={language} onChange={(e) => setLanguage(e.target.value)}>
                <option value="english">English</option>
                <option value="hindi">Hindi</option>
              </select>
            </div>
          )}

          <textarea
            placeholder={`Paste data or upload file for ${activeMode}...`}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
          />

          <div className="file-upload">
            <input 
              ref={fileInputRef}
              type="file" 
              onChange={handleFileUpload} 
              accept=".json,.txt,.usr" 
              style={{ display: 'none' }} 
              id="file-upload"
            />
            <label htmlFor="file-upload" className="file-btn">
              📁 Choose File
            </label>
            {selectedFileName && (
              <div className="file-name">Selected: {selectedFileName}</div>
            )}
          </div>
        </div>

        {/* CONVERT BUTTON */}
        <div className="middle-button">
          <button 
            className="convert-btn middle-convert-btn" 
            onClick={handleConvert}
            disabled={isLoading || !inputText.trim()}
          >
            {isLoading ? "Processing..." : "Convert"}
          </button>
        </div>

        {/* OUTPUT PANEL */}
        <div className="panel output">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <h3 style={{ margin: 0 }}>Output</h3>
            {output && (
              <div style={{ display: 'flex', gap: '8px' }}>
                <button className="clear-btn" style={{ background: '#17a2b8' }} onClick={handleCopy}>Copy</button>
                <button className="clear-btn" style={{ background: '#28a745' }} onClick={handleDownload}>Download</button>
                <button className="clear-btn" onClick={() => setOutput("")}>Clear</button>
              </div>
            )}
          </div>
          
          <div className="output-box" style={{ whiteSpace: 'pre-wrap' }}>
             {output || "Generated output will appear here..."}
          </div>
        </div>
      </div>
    </div>
  );
}
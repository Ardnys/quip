import { useState } from "react";
import AppGrid from "./AppGrid";
import AudioDeviceList from "./AudioDeviceList";
import ExtraOptions from "./ExtraOptions";
import StreamView from "./StreamView";
import { useWebRTC } from "../hooks/useWebRTC";
import styles from "./ShareScreen.module.css";
import { useEffect } from "react";

const DEFAULT_OPTIONS = {
  videoCodec: "AV1",
  audioCodec: "OPUS",
  captureCursor: true,
  drawBorder: false,
  randomlyFart: false,
  useStun: false,
};

export default function ShareScreen({ onBack }) {
  const [selectedHwnd, setSelectedHwnd] = useState(null);
  const [selectedWindowTitle, setSelectedWindowTitle] = useState(null);
  const [selectedAudioDevice, setSelectedAudioDevice] = useState(null);
  const [options, setOptions] = useState(DEFAULT_OPTIONS);
  const [windows, setWindows] = useState([]);
  const [windowsLoading, setWindowsLoading] = useState(true);
  const [audioDevies, setAudioDevices] = useState([]);
  // TODO: audio loading state

  // 'setup' | 'streaming'
  const [view, setView] = useState("setup");

  const { start, stop, toggleMute, videoRef, connectionState, muted, error } =
    useWebRTC();

  const canShare = selectedHwnd !== null && selectedAudioDevice !== null;

  useEffect(() => {
    async function loadAudio() {
      try {
        const res = await fetch("/api/audio_devices");
        const data = await res.json();
        setAudioDevices(data);
      } catch (e) {
        console.error("Failed to load audio devices", e);
      }
    }
    async function loadWindows() {
      setWindowsLoading(true);
      try {
        const res = await fetch("/api/windows");
        const data = await res.json();
        setWindows(data.windows);
      } catch (e) {
        console.error("Failed to load windows", e);
      } finally {
        setWindowsLoading(false);
      }
    }
    loadWindows();
    loadAudio();
  }, []);

  function handleWindowSelect(hwnd, title) {
    setSelectedHwnd(hwnd);
    setSelectedWindowTitle(title);
  }

  async function handleShare() {
    if (!canShare) return;
    setView("streaming");
    await start({
      hwnd: selectedHwnd,
      windowTitle: selectedWindowTitle,
      audioDevice: selectedAudioDevice,
      ...options,
    });
  }

  function handleStop() {
    stop();
    setView("setup");
  }

  // Keep the PC alive, just go back to setup so user can pick a different app
  function handleReselect() {
    stop();
    setView("setup");
  }

  // ── Streaming view ────────────────────────────────────────────────────────
  if (view === "streaming") {
    return (
      <div className={styles.root} style={{ height: "100%" }}>
        <div className={styles.bg} aria-hidden="true" />
        <StreamView
          videoRef={videoRef}
          connectionState={connectionState}
          muted={muted}
          error={error}
          windowTitle={selectedWindowTitle}
          onToggleMute={toggleMute}
          onStop={handleStop}
          onReselect={handleReselect}
        />
      </div>
    );
  }

  // ── Setup view ────────────────────────────────────────────────────────────
  return (
    <div className={styles.root}>
      <div className={styles.bg} aria-hidden="true" />

      <header className={styles.topBar}>
        <button className={styles.backBtn} onClick={onBack}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path
              d="M10 3L5 8l5 5"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          back
        </button>
        <h1 className={styles.logo}>quip</h1>
        <div style={{ width: 70 }} />
      </header>

      <div className={styles.content}>
        {/* App selection */}
        <section className={`${styles.card} ${styles.cardAppSelect}`}>
          <div className={styles.cardHeader}>
            <h2 className={styles.sectionTitle}>Select app to share</h2>
            <span className={styles.hint}>click to select</span>
          </div>
          <AppGrid
            windows={windows}
            loading={windowsLoading}
            selectedHwnd={selectedHwnd}
            onSelect={handleWindowSelect}
          />
        </section>

        {/* Bottom row */}
        <div className={styles.bottomRow}>
          {/* Audio devices */}
          <section className={styles.card}>
            <div className={styles.cardHeader}>
              <h2 className={styles.sectionTitle}>Audio device</h2>
              {selectedAudioDevice !== null && (
                <span className={styles.selectedTag}>1 selected</span>
              )}
            </div>
            <AudioDeviceList
              devices={audioDevies}
              selectedIndex={selectedAudioDevice}
              onSelect={setSelectedAudioDevice}
            />
          </section>

          {/* Options + share */}
          <div className={styles.rightCol}>
            <section className={styles.card} style={{ flex: 1 }}>
              <div className={styles.cardHeader}>
                <h2 className={styles.sectionTitle}>Extra options</h2>
              </div>
              <ExtraOptions options={options} onChange={setOptions} />
            </section>

            <div className={styles.shareRow}>
              {!canShare && (
                <p className={styles.shareHint}>
                  {!selectedHwnd && !selectedAudioDevice
                    ? "select an app and audio device"
                    : !selectedHwnd
                      ? "select an app to share"
                      : "select an audio device"}
                </p>
              )}
              <button
                className={`${styles.shareBtn} ${canShare ? styles.shareBtnReady : ""}`}
                onClick={handleShare}
                disabled={!canShare}
              >
                share
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path
                    d="M3 8h10M8.5 3.5l4.5 4.5-4.5 4.5"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

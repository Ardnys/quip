import {
  Mic,
  MicOff,
  MonitorX,
  LayoutGrid,
  Maximize2,
  Minimize2,
  Loader2,
  Volume2,
  VolumeOff,
} from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import styles from "./StreamView.module.css";

/**
 * Fullscreen-capable video player with a controls bar that auto-hides.
 *
 * Props:
 *   videoRef          — ref forwarded from useWebRTC, attached to <video>
 *   connectionState   — 'connecting' | 'connected' | 'disconnected' | 'failed'
 *   muted             — bool
 *   error             — string | null
 *   windowTitle       — string, shown in the control bar
 *   onToggleMute      — () => void
 *   onStop            — () => void  (closes the PC and returns to setup)
 *   onReselect        — () => void  (keeps the PC alive, back to app selection)
 */
export default function StreamView({
  videoRef,
  connectionState,
  muted,
  error,
  windowTitle,
  onToggleMute,
  onStop,
  onReselect,
}) {
  const containerRef = useRef(null);
  const hideTimer = useRef(null);
  const [controlsVisible, setControlsVisible] = useState(true);
  const [fullscreen, setFullscreen] = useState(false);

  // Show controls + reset the hide timer — called from mouse events
  const showControls = useCallback(() => {
    setControlsVisible(true);
    clearTimeout(hideTimer.current);
    hideTimer.current = setTimeout(() => {
      setControlsVisible(false);
    }, 3000);
  }, []);

  // Cleanup timer on unmount
  useEffect(() => {
    return () => clearTimeout(hideTimer.current);
  }, []);

  // When not yet connected, cancel any pending hide and keep controls visible
  // via the connectionState-derived render path — don't force setState here
  useEffect(() => {
    if (connectionState !== "connected") {
      clearTimeout(hideTimer.current);
    }
  }, [connectionState]);

  // Track fullscreen state
  useEffect(() => {
    const onFsChange = () => setFullscreen(!!document.fullscreenElement);
    document.addEventListener("fullscreenchange", onFsChange);
    return () => document.removeEventListener("fullscreenchange", onFsChange);
  }, []);

  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  }

  const isConnecting = connectionState === "connecting";
  const isFailed = connectionState === "failed" || !!error;
  // Controls are always visible while not streaming; auto-hide only when connected
  const showingControls = controlsVisible || connectionState !== "connected";

  return (
    <div
      ref={containerRef}
      className={styles.root}
      onMouseMove={showControls}
      onMouseLeave={() => {
        // Let the existing timer run out naturally — no need to force-hide here
        // When connected, the 3s timer from showControls will hide them
      }}
    >
      {/* Video element */}
      <video
        ref={videoRef}
        className={styles.video}
        autoPlay
        playsInline
        muted={muted}
      />

      {/* Connecting overlay */}
      {isConnecting && (
        <div className={styles.overlay}>
          <Loader2 className={styles.spinner} size={36} />
          <p className={styles.overlayText}>
            connecting to {windowTitle || "application"}…
          </p>
        </div>
      )}

      {/* Error overlay */}
      {isFailed && (
        <div className={styles.overlay}>
          <MonitorX size={36} color="var(--red)" />
          <p className={styles.overlayText}>{error || "Stream failed"}</p>
          <button className={styles.retryBtn} onClick={onStop}>
            go back
          </button>
        </div>
      )}

      {/* Controls bar — auto-hides when connected */}
      <div
        className={`${styles.controls} ${showingControls ? styles.controlsVisible : ""}`}
      >
        {/* Left: app info */}
        <div className={styles.ctrlLeft}>
          <span className={styles.windowBadge}>
            <span className={styles.liveDot} />
            {windowTitle || "sharing"}
          </span>
        </div>

        {/* Center: transport controls */}
        <div className={styles.ctrlCenter}>
          <ControlBtn
            onClick={onToggleMute}
            active={muted}
            title={muted ? "Unmute" : "Mute"}
          >
            {muted ? <VolumeOff size={18} /> : <Volume2 size={18} />}
          </ControlBtn>

          <ControlBtn onClick={onReselect} title="Select a different app">
            <LayoutGrid size={18} />
          </ControlBtn>

          <ControlBtn onClick={onStop} danger title="Stop sharing">
            <MonitorX size={18} />
          </ControlBtn>
        </div>

        {/* Right: fullscreen */}
        <div className={styles.ctrlRight}>
          <ControlBtn
            onClick={toggleFullscreen}
            title={fullscreen ? "Exit fullscreen" : "Fullscreen"}
          >
            {fullscreen ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
          </ControlBtn>
        </div>
      </div>
    </div>
  );
}

function ControlBtn({ children, onClick, active, danger, title }) {
  return (
    <button
      className={[
        styles.ctrlBtn,
        active ? styles.ctrlBtnActive : "",
        danger ? styles.ctrlBtnDanger : "",
      ].join(" ")}
      onClick={onClick}
      title={title}
    >
      {children}
    </button>
  );
}

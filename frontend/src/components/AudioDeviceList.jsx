import { useState, useRef } from "react";
import styles from "./AudioDeviceList.module.css";

const PLACEHOLDER_DEVICES = [
  { index: 0, name: "CABLE Output (VB-Audio Virtual Cable)", channels: 16 },
  { index: 1, name: "Microphone (Realtek Audio)", channels: 1 },
  { index: 2, name: "Headset Microphone (WH-1000XM4)", channels: 1 },
  { index: 3, name: "HDMI Audio (Monitor)", channels: 2 },
  { index: 4, name: "Same Audio Again", channels: 2 },
  { index: 5, name: "Expensive Audio Equipment", channels: 999 },
];

function guessIcon(name) {
  const n = name.toLowerCase();
  if (n.includes("cable") || n.includes("virtual")) return "🔌";
  if (
    n.includes("headset") ||
    n.includes("headphone") ||
    n.includes("wh-") ||
    n.includes("wf-")
  )
    return "🎧";
  if (n.includes("mic")) return "🎙️";
  if (n.includes("hdmi") || n.includes("display") || n.includes("monitor"))
    return "🖥️";
  if (n.includes("usb")) return "🔊";
  return "🎵";
}

export default function AudioDeviceList({
  devices = PLACEHOLDER_DEVICES,
  selectedIndex,
  onSelect,
}) {
  const [listenState, setListenState] = useState("idle"); // idle | listening | stopping
  const streamRef = useRef(null);
  const ctxRef = useRef(null);
  const timerRef = useRef(null);

  async function handleListen() {
    if (listenState === "listening") {
      stopListen();
      return;
    }
    if (selectedIndex === null) return;

    setListenState("listening");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const ctx = new AudioContext();
      ctxRef.current = ctx;
      const src = ctx.createMediaStreamSource(stream);
      src.connect(ctx.destination);
      timerRef.current = setTimeout(stopListen, 7000);
    } catch {
      setListenState("idle");
    }
  }

  function stopListen() {
    if (timerRef.current) clearTimeout(timerRef.current);
    streamRef.current?.getTracks().forEach((t) => t.stop());
    ctxRef.current?.close();
    streamRef.current = null;
    ctxRef.current = null;
    setListenState("idle");
  }

  const canListen = false;

  return (
    <div className={styles.root}>
      <div className={styles.list}>
        {devices.map((d) => (
          <button
            key={d.index}
            className={`${styles.device} ${selectedIndex === d.index ? styles.selected : ""}`}
            onClick={() => onSelect(d.index)}
          >
            <span className={styles.icon}>{guessIcon(d.name)}</span>
            <div className={styles.info}>
              <span className={styles.name}>{d.name}</span>
              <span className={styles.channels}>
                {d.max_input_channels === 1 ? "mono" : `stereo`}
              </span>
            </div>
            {selectedIndex === d.index && <div className={styles.selDot} />}
          </button>
        ))}
      </div>

      <button
        className={`${styles.listenBtn} ${listenState === "listening" ? styles.active : ""}`}
        onClick={handleListen}
        disabled={!canListen}
      >
        {listenState === "listening" ? (
          <>
            <span className={styles.listenDots}>
              <span />
              <span />
              <span />
            </span>
            stop listening
          </>
        ) : (
          <>
            <svg
              width="14"
              height="14"
              viewBox="0 0 14 14"
              fill="none"
              style={{ marginRight: 5, verticalAlign: "middle" }}
            >
              <path
                d="M7 1v12M4 3.5v7M1 5.5v3M10 3.5v7M13 5.5v3"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
              />
            </svg>
            listen (🚧 UNDER CONSTRUCTION 🚧)
          </>
        )}
      </button>
    </div>
  );
}

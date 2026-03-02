import { useCallback, useRef, useState } from "react";

/**
 * Encapsulates RTCPeerConnection lifecycle.
 *
 * Usage:
 *   const { start, stop, muted, toggleMute, connectionState, error } = useWebRTC()
 *
 * `start(payload)` kicks off ICE gathering + offer/answer and resolves when
 * the remote description is set. The video element is wired up internally
 * via the ref returned by the hook.
 */
export function useWebRTC() {
  const pcRef = useRef(null);
  const videoRef = useRef(null); // attach this ref to <video>

  const [connectionState, setConnectionState] = useState("idle");
  // idle | connecting | connected | disconnected | failed
  const [muted, setMuted] = useState(false);
  const [error, setError] = useState(null);

  // ── helpers ──────────────────────────────────────────────────────────────

  function waitForIceGathering(pc) {
    return new Promise((resolve) => {
      if (pc.iceGatheringState === "complete") return resolve();
      const check = () => {
        if (pc.iceGatheringState === "complete") {
          pc.removeEventListener("icegatheringstatechange", check);
          resolve();
        }
      };
      pc.addEventListener("icegatheringstatechange", check);
    });
  }

  async function sendOffer(pc, payload) {
    const res = await fetch("/api/offer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sdp: pc.localDescription.sdp,
        type: pc.localDescription.type,
        // window identity — backend accepts hwnd; title kept for fallback
        hwnd: payload.hwnd,
        windowTitle: payload.windowTitle,
        audioDevice: payload.audioDevice,
        videoCodec: payload.videoCodec,
        audioCodec: payload.audioCodec,
        captureCursor: payload.captureCursor,
        drawBorder: payload.drawBorder,
        randomlyFart: payload.randomlyFart,
      }),
    });
    if (!res.ok)
      throw new Error(`Offer rejected: ${res.status} ${res.statusText}`);
    return res.json();
  }

  // ── public API ────────────────────────────────────────────────────────────

  const start = useCallback(async (payload) => {
    setError(null);
    setConnectionState("connecting");

    const iceServers = payload.useStun
      ? [{ urls: ["stun:stun.l.google.com:19302"] }]
      : [];

    const pc = new RTCPeerConnection({
      sdpSemantics: "unified-plan",
      iceServers,
    });
    pcRef.current = pc;

    // Wire connection state changes to UI state
    pc.addEventListener("connectionstatechange", () => {
      setConnectionState(pc.connectionState);
      if (pc.connectionState === "failed") {
        setError("Connection failed. Check that the server is running.");
      }
    });

    // Attach incoming tracks to the video element
    pc.addEventListener("track", (evt) => {
      if (!evt.streams?.[0]) return;
      const video = videoRef.current;
      if (!video) return;
      if (video.srcObject !== evt.streams[0]) {
        video.srcObject = evt.streams[0];
      }
    });

    try {
      pc.addTransceiver("video", { direction: "recvonly" });
      pc.addTransceiver("audio", { direction: "recvonly" });

      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      await waitForIceGathering(pc);

      const answer = await sendOffer(pc, payload);
      await pc.setRemoteDescription(answer);
    } catch (err) {
      setError(err.message);
      setConnectionState("failed");
      pc.close();
      pcRef.current = null;
    }
  }, []);

  const stop = useCallback(() => {
    const pc = pcRef.current;
    if (!pc) return;
    setTimeout(() => {
      pc.close();
      pcRef.current = null;
    }, 300);
    const video = videoRef.current;
    if (video) {
      video.srcObject = null;
    }
    setConnectionState("idle");
    setMuted(false);
    setError(null);
  }, []);

  const toggleMute = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;
    video.muted = !video.muted;
    setMuted(video.muted);
  }, []);

  return { start, stop, toggleMute, videoRef, connectionState, muted, error };
}

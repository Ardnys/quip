import styles from "./AppGrid.module.css";
import { useMemo } from "react";

// Placeholder windows for development
const PLACEHOLDER_WINDOWS = [
  { hwnd: 1, title: "Visual Studio Code", thumbnail: null, color: "#1e1e2e" },
  { hwnd: 2, title: "Google Chrome", thumbnail: null, color: "#1a1a2e" },
  { hwnd: 3, title: "Discord", thumbnail: null, color: "#1e1428" },
  { hwnd: 4, title: "Spotify", thumbnail: null, color: "#0d1f14" },
  { hwnd: 5, title: "Windows Terminal", thumbnail: null, color: "#0c0c1a" },
  { hwnd: 6, title: "Zed Editor", thumbnail: null, color: "#0c1c1b" },
  { hwnd: 7, title: "Zen Browser", thumbnail: null, color: "#2c0f2a" },
];

/** Simple 32-bit string -> seed hash */
function hashStringToUint32(str) {
  let h = 2166136261 >>> 0;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619) >>> 0;
  }
  return h >>> 0;
}

/** mulberry32 PRNG (deterministic given seed) */
function mulberry32(seed) {
  let t = seed >>> 0;
  return function () {
    t += 0x6d2b79f5;
    t = Math.imul(t ^ (t >>> 15), t | 1) >>> 0;
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const AppIcon = ({ title }) => {
  const initials = title
    .split(" ")
    .map((w) => w[0] || "")
    .join("")
    .slice(0, 2)
    .toUpperCase();

  // compute deterministic color + widths from title
  const { color, lineWidths } = useMemo(() => {
    const seed = hashStringToUint32(title || ""); // stable seed
    const rng = mulberry32(seed);

    // deterministic hex color
    const hex = Math.floor(rng() * 0xffffff)
      .toString(16)
      .padStart(6, "0");
    const color = `#${hex}`;

    // five deterministic widths (matching your original formula-ish)
    const widths = Array.from({ length: 5 }, (_, i) => {
      const base = 30 + Math.sin(i * 2.5) * 25; // deterministic
      const jitter = rng() * 20; // deterministic jitter
      const w = Math.max(5, Math.min(95, base + jitter));
      return w;
    });

    return { color, lineWidths: widths };
  }, [title]);

  return (
    <div className={styles.placeholder} style={{ background: color }}>
      <span className={styles.placeholderInitials}>{initials}</span>
      <div className={styles.placeholderLines}>
        {lineWidths.map((w, i) => (
          <div
            key={i}
            className={styles.placeholderLine}
            style={{
              width: `${w}%`,
              opacity: 0.06 + i * 0.02,
            }}
          />
        ))}
      </div>
    </div>
  );
};

export default function AppGrid({
  windows = PLACEHOLDER_WINDOWS,
  loading,
  selectedHwnd,
  onSelect,
}) {
  return (
    <div className={styles.grid}>
      {loading ? (
        <div className={styles.card}>
          <AppIcon title={"Loading"} />
        </div>
      ) : (
        windows.map((w) => (
          <button
            key={w.hwnd}
            className={`${styles.card} ${selectedHwnd === w.hwnd ? styles.selected : ""}`}
            onClick={() => onSelect(w.hwnd, w.title)}
          >
            {w.thumbnail ? (
              <img
                src={`data:image/jpeg;base64,${w.thumbnail}`}
                alt={w.title}
                className={styles.thumb}
              />
            ) : (
              <AppIcon title={w.title} />
            )}
            <div className={styles.cardLabel}>
              <span className={styles.cardLabelText}>{w.title}</span>
              {selectedHwnd === w.hwnd && (
                <span className={styles.selectedBadge}>selected</span>
              )}
            </div>
            {selectedHwnd === w.hwnd && (
              <div className={styles.selectedCorner} aria-hidden="true">
                <svg width="20" height="20" viewBox="0 0 20 20">
                  <path
                    d="M5 10.5l3.5 3.5 7-7"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    fill="none"
                  />
                </svg>
              </div>
            )}
          </button>
        ))
      )}
    </div>
  );
}

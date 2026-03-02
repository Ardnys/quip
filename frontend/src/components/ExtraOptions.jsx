import styles from "./ExtraOptions.module.css";

const VIDEO_CODECS = ["AV1", "VP9", "VP8", "H264"];
const AUDIO_CODECS = ["OPUS", "PCMU", "PCMA"];

function Select({ id, value, onChange, options }) {
  return (
    <select
      id={id}
      className={styles.select}
      value={value}
      onChange={(e) => onChange(e.target.value)}
    >
      {options.map((o) => (
        <option key={o} value={o}>
          {o}
        </option>
      ))}
    </select>
  );
}

function Checkbox({ id, checked, onChange, label }) {
  return (
    <label className={styles.checkLabel} htmlFor={id}>
      <input
        id={id}
        type="checkbox"
        className={styles.checkbox}
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
      />
      <span className={styles.checkMark} aria-hidden="true">
        {checked && (
          <svg width="10" height="8" viewBox="0 0 10 8" fill="none">
            <path
              d="M1 4l3 3 5-6"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
      </span>
      <span className={styles.checkText}>{label}</span>
    </label>
  );
}

export default function ExtraOptions({ options, onChange }) {
  const set = (key, val) => onChange({ ...options, [key]: val });

  return (
    <div className={styles.root}>
      <div className={styles.cols}>
        {/* Video codec column */}
        <div className={styles.col}>
          <label className={styles.label} htmlFor="video-codec">
            video codec
          </label>
          <Select
            id="video-codec"
            value={options.videoCodec}
            onChange={(v) => set("videoCodec", v)}
            options={VIDEO_CODECS}
          />
          <div className={styles.checks}>
            <Checkbox
              id="capture-cursor"
              checked={options.captureCursor}
              onChange={(v) => set("captureCursor", v)}
              label="capture cursor"
            />
            <Checkbox
              id="draw-border"
              checked={options.drawBorder}
              onChange={(v) => set("drawBorder", v)}
              label="draw border"
            />
          </div>
        </div>

        {/* Audio codec column */}
        <div className={styles.col}>
          <label className={styles.label} htmlFor="audio-codec">
            audio codec
          </label>
          <Select
            id="audio-codec"
            value={options.audioCodec}
            onChange={(v) => set("audioCodec", v)}
            options={AUDIO_CODECS}
          />
          <div className={styles.checks}>
            <Checkbox
              id="randomly-fart"
              checked={options.randomlyFart}
              onChange={(v) => set("randomlyFart", v)}
              label="randomly fart"
            />
            <Checkbox
              id="use-stun"
              checked={options.useStun}
              onChange={(v) => set("useStun", v)}
              label="use STUN server"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

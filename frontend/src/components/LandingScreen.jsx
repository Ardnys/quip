import { useState } from "react";
import ChecklistModal from "./ChecklistModal";
import styles from "./LandingScreen.module.css";

export default function LandingScreen({ onStart }) {
  const [showChecklist, setShowChecklist] = useState(false);

  return (
    <div className={styles.root}>
      {/* Background mesh */}
      <div className={styles.meshBg} aria-hidden="true" />

      <main className={styles.main}>
        <div className={styles.titleWrap}>
          <h1 className={styles.title}>quip</h1>
          <div className={styles.titleUnderline} />
        </div>

        <p className={styles.tagline}>
          streaming an application with audio in a video conference in browser
          should not be this difficult. but it is
        </p>

        <button className={styles.startBtn} onClick={onStart}>
          <span className={styles.startBtnInner}>
            <span>share application</span>
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path
                d="M3.75 9h10.5M9.75 4.5l4.5 4.5-4.5 4.5"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </span>
        </button>

        <button
          className={styles.checklistBtn}
          onClick={() => setShowChecklist(true)}
        >
          pre-share checklist
        </button>
      </main>

      <footer className={styles.footer}>
        <a
          href="https://github.com/Ardnys/quip"
          target="_blank"
          rel="noreferrer"
          className={styles.footerLink}
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="currentColor"
            style={{ marginRight: 5, verticalAlign: "middle", marginTop: -2 }}
          >
            <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0 1 12 6.844a9.59 9.59 0 0 1 2.504.337c1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.02 10.02 0 0 0 22 12.017C22 6.484 17.522 2 12 2z" />
          </svg>
          github
        </a>
        <span className={styles.footerDot}>·</span>
        <a href="#" className={styles.footerLink}>
          project's tragic development story
        </a>
      </footer>

      {showChecklist && (
        <ChecklistModal onClose={() => setShowChecklist(false)} />
      )}
    </div>
  );
}

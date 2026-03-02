import { useEffect, useRef } from 'react'
import styles from './ChecklistModal.module.css'

const steps = [
  {
    n: '01',
    title: 'Install a virtual audio device',
    body: <>Download and install <a href="https://vb-audio.com/Cable/" target="_blank" rel="noreferrer">VB-Cable</a> (free) or <a href="https://existential.audio/blackhole/" target="_blank" rel="noreferrer">BlackHole</a>. This creates a virtual audio cable on your system.</>
  },
  {
    n: '02',
    title: 'Route your app\'s audio',
    body: 'Open the target application\'s audio settings and set its output device to "CABLE Input" (or your virtual device). This pipes its audio into the virtual cable.'
  },
  {
    n: '03',
    title: 'Select the capture device in quip',
    body: 'On the sharing screen, pick "CABLE Output" from the audio device list. quip will read from this and stream it to the receiver.'
  },
  {
    n: '04',
    title: 'Verify before sharing',
    body: 'Use the Listen button to confirm audio is flowing through the virtual device before starting the stream.'
  },
  {
    n: '05',
    title: 'Keep the app visible',
    body: 'Windows Capture requires the application window to be visible (not minimized) for capture to work correctly.'
  },
]

export default function ChecklistModal({ onClose }) {
  const overlayRef = useRef(null)

  useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <div
      className={styles.overlay}
      ref={overlayRef}
      onClick={(e) => { if (e.target === overlayRef.current) onClose() }}
    >
      <div className={styles.modal}>
        <div className={styles.header}>
          <span className={styles.tag}>pre-share checklist</span>
          <button className={styles.closeBtn} onClick={onClose} aria-label="Close">✕</button>
        </div>

        <div className={styles.steps}>
          {steps.map((s) => (
            <div key={s.n} className={styles.step}>
              <span className={styles.stepNum}>{s.n}</span>
              <div className={styles.stepContent}>
                <p className={styles.stepTitle}>{s.title}</p>
                <p className={styles.stepBody}>{s.body}</p>
              </div>
            </div>
          ))}
        </div>

        <button className={styles.gotItBtn} onClick={onClose}>got it</button>
      </div>
    </div>
  )
}

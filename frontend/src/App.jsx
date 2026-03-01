import { useState } from 'react'
import LandingScreen from './components/LandingScreen'
import ShareScreen from './components/ShareScreen'

export default function App() {
  const [screen, setScreen] = useState('landing')

  return (
    <div style={{ height: '100%' }}>
      {screen === 'landing' && (
        <LandingScreen onStart={() => setScreen('share')} />
      )}
      {screen === 'share' && (
        <ShareScreen onBack={() => setScreen('landing')} />
      )}
    </div>
  )
}

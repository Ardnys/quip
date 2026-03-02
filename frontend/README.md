# quip — frontend

React/Vite SPA for quip. Handles window and audio device selection, WebRTC negotiation, and displays the incoming stream with playback controls.

## Stack

- **React 19** with CSS Modules
- **Vite 7** for dev server and production builds
- **lucide-react** for icons
- **motion** for animations

## Structure

- **`src/components/LandingScreen`** — entry screen with a link to the sharing setup and a pre-share checklist modal.
- **`src/components/ShareScreen`** — main setup screen: window picker, audio device selector, codec/option controls, and the share button.
- **`src/components/StreamView`** — fullscreen video player shown during an active stream, with auto-hiding controls for mute, stop, and fullscreen.
- **`src/components/AppGrid`** — grid of capturable window previews with thumbnails.
- **`src/components/AudioDeviceList`** — list of audio input devices with a listen preview button.
- **`src/components/ExtraOptions`** — codec dropdowns and miscellaneous checkboxes.
- **`src/hooks/useWebRTC.js`** — encapsulates the `RTCPeerConnection` lifecycle: ICE gathering, offer/answer exchange, track attachment, and cleanup.

## Development

Requires [Node.js](https://nodejs.org/) and the backend running on `http://127.0.0.1:9119`. See backend README.

```bash
npm install
npm run dev
```

API calls are proxied from `/api/*` to the backend dev server via the Vite proxy config.

## Production build

```bash
npm run build
```

Output goes to `dist/`. The build script at the project root (`uv run build.py`) runs this automatically and copies the output into the backend's static directory.

## Contributing

Contributions are welcome. **Audio previews**, **minimized streams**, **random farts in audio stream** or any other fun stuff are good first issues to start. Open an issue and I will hapilly respond!

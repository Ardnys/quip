var pc = null;

const getVisibleWindows = async () => {
  const response = await fetch("/visible_windows", {
    method: "GET",
  });
  const windows = await response.json();
  return windows["visibleWindows"];
};

function iceGathering() {
  // wait for ICE gathering to complete
  return new Promise((resolve) => {
    if (pc.iceGatheringState === "complete") {
      resolve();
    } else {
      const checkState = () => {
        if (pc.iceGatheringState === "complete") {
          pc.removeEventListener("icegatheringstatechange", checkState);
          resolve();
        }
      };
      pc.addEventListener("icegatheringstatechange", checkState);
    }
  });
}

function initiateOffer() {
  var offer = pc.localDescription;
  return fetch("/offer", {
    body: JSON.stringify({
      sdp: offer.sdp,
      type: offer.type,
      selectedWindow: selectedWindow,
    }),
    headers: {
      "Content-Type": "application/json",
    },
    method: "POST",
  });
}

function negotiate() {
  selectedWindow = document.getElementById("selected-window-button").innerText;
  pc.addTransceiver("video", { direction: "recvonly" });
  pc.addTransceiver("audio", { direction: "recvonly" });
  return pc
    .createOffer()
    .then((offer) => {
      return pc.setLocalDescription(offer);
    })
    .then(iceGathering)
    .then(initiateOffer)
    .then((response) => {
      return response.json();
    })
    .then((answer) => {
      return pc.setRemoteDescription(answer);
    })
    .catch((e) => {
      alert(e);
    });
}

function start(conf) {
  // selected window should be sent to server
  var config = {
    sdpSemantics: "unified-plan",
    iceServers: [{ urls: ["stun:stun.l.google.com:19302"] }],
  };

  console.log(conf);

  pc = new RTCPeerConnection(config);

  // connect audio / video
  pc.addEventListener("track", (evt) => {
    // Always attach to the video element — it carries both tracks
    const videoEl = document.getElementById("video");
    if (evt.streams && evt.streams[0]) {
      videoEl.srcObject = evt.streams[0];
    }
  });

  negotiate();
}

const unmuteButton = document.getElementById("unmute-button");
unmuteButton.addEventListener("click", () => {
  const v = document.getElementById("video");
  if (v.muted) {
    console.log("SPEAK");
    v.muted = false;
  }
});

function stop() {
  // close peer connection
  setTimeout(() => {
    pc.close();
  }, 500);
}

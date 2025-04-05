var pc = null;

const getVisibleWindows = async () => {
	const response = await fetch("/visible_windows", {
		method: "GET",
	});
	const windows = await response.json();
	return windows["visibleWindows"];
};

function negotiate() {
	selectedWindow = document.getElementById("selected-window-button").innerText;
	pc.addTransceiver("video", { direction: "recvonly" });
	pc.addTransceiver("audio", { direction: "recvonly" });
	return pc
		.createOffer()
		.then((offer) => {
			return pc.setLocalDescription(offer);
		})
		.then(() => {
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
		})
		.then(() => {
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
		})
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

function start() {
	// selected window should be sent to server
	var config = {
		sdpSemantics: "unified-plan",
	};

	pc = new RTCPeerConnection(config);

	// connect audio / video
	pc.addEventListener("track", (evt) => {
		if (evt.track.kind == "video") {
			document.getElementById("video").srcObject = evt.streams[0];
		} else {
			document.getElementById("audio").srcObject = evt.streams[0];
		}
	});
	negotiate();
}

function stop() {
	// close peer connection
	setTimeout(() => {
		pc.close();
	}, 500);
}

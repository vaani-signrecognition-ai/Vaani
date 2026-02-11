// recognize.js
// Uses MediaPipe Hands in the browser to draw hand landmarks and bounding boxes on webcam feed
// and displays the predicted label from the backend

let mpHands, hands, camera, canvasElement, canvasCtx;

async function setupHandDetection() {
    // Load MediaPipe Hands
    if (!window.Hands) {
        await loadMediaPipeHands();
    }
    mpHands = window.Hands;
    hands = new mpHands({
        locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
    });
    hands.setOptions({
        maxNumHands: 2,
        modelComplexity: 1,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
    });
    hands.onResults(onResults);

    // Setup camera
    camera = new Camera(document.getElementById('webcamVideo'), {
        onFrame: async () => {
            await hands.send({image: document.getElementById('webcamVideo')});
        },
        width: 640,
        height: 480
    });
    camera.start();

    // Setup canvas
    canvasElement = document.getElementById('webcamCanvas');
    canvasCtx = canvasElement.getContext('2d');
}

function onResults(results) {
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);
    if (results.multiHandLandmarks) {
        for (const landmarks of results.multiHandLandmarks) {
            drawConnectors(canvasCtx, landmarks, window.HAND_CONNECTIONS, {color: '#00FF00', lineWidth: 2});
            drawLandmarks(canvasCtx, landmarks, {color: '#FF0000', lineWidth: 1});
        }
    }
    canvasCtx.restore();
}

async function loadMediaPipeHands() {
    // Load MediaPipe Hands and drawing utils from CDN
    await Promise.all([
        loadScript('https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js'),
        loadScript('https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils/drawing_utils.js'),
        loadScript('https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js')
    ]);
    window.HAND_CONNECTIONS = HAND_CONNECTIONS;
}

function loadScript(src) {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

window.setupHandDetection = setupHandDetection;

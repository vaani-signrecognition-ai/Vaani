let video = document.getElementById("video");
let canvas = document.getElementById("canvas");
let currentPrediction = "---";

// Utility function to convert snake_case to human-readable text
function prettifyLabel(label) {
    return label
        .replaceAll("_", " ")
        .replace(/\s+/g, " ")
        .trim();
}

function startCamera() {
  navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } })
    .then(stream => {
      video.srcObject = stream;
      document.getElementById("result").innerText = "Camera started! Ready to predict.";
      document.getElementById("confidence").innerText = "";
    })
    .catch(err => {
      alert("Error accessing camera: " + err.message);
      console.error(err);
    });
}

function captureImage() {
  const ctx = canvas.getContext("2d");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  ctx.drawImage(video, 0, 0);
  
  return new Promise((resolve) => {
    canvas.toBlob(blob => resolve(blob), 'image/jpeg', 0.95);
  });
}

async function predictWord() {
  if (!video.srcObject) {
    alert("Please start the camera first!");
    return;
  }

  document.getElementById("result").innerText = "Predicting word...";
  document.getElementById("confidence").innerText = "";
  
  try {
    const blob = await captureImage();
    let formData = new FormData();
    formData.append("image", blob);

    const response = await fetch("/api/predict/word", {
      method: "POST",
      body: formData
    });
    
    const data = await response.json();
    
    if (data.error) {
      document.getElementById("result").innerText = "Error: " + data.error;
      document.getElementById("predictionType").style.display = "none";
    } else {
      currentPrediction = data.word;
      
      // Handle unknown/low confidence predictions
      if (data.word === "unknown") {
        document.getElementById("result").innerText = "Please try again";
        document.getElementById("confidence").innerText = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;
        document.getElementById("predictionType").style.display = "none";
      } else {
        const cleanText = prettifyLabel(data.word);
        document.getElementById("result").innerText = cleanText;
        document.getElementById("confidence").innerText = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;
        document.getElementById("predictionType").innerText = "Word Prediction";
        document.getElementById("predictionType").style.display = "inline-block";
      }
    }
  } catch (error) {
    console.error("Prediction error:", error);
    document.getElementById("result").innerText = "Error: " + error.message;
    document.getElementById("predictionType").style.display = "none";
  }
}

async function predictAlphabet() {
  if (!video.srcObject) {
    alert("Please start the camera first!");
    return;
  }

  document.getElementById("result").innerText = "Predicting letter/number...";
  document.getElementById("confidence").innerText = "";
  
  try {
    const blob = await captureImage();
    let formData = new FormData();
    formData.append("image", blob);

    const response = await fetch("/api/predict/alphabet", {
      method: "POST",
      body: formData
    });
    
    const data = await response.json();
    
    if (data.error) {
      document.getElementById("result").innerText = "Error: " + data.error;
      document.getElementById("predictionType").style.display = "none";
    } else {
      currentPrediction = data.letter;
      document.getElementById("result").innerText = data.letter;
      document.getElementById("confidence").innerText = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;
      document.getElementById("predictionType").innerText = "Letter/Number Prediction";
      document.getElementById("predictionType").style.display = "inline-block";
    }
  } catch (error) {
    console.error("Prediction error:", error);
    document.getElementById("result").innerText = "Error: " + error.message;
    document.getElementById("predictionType").style.display = "none";
  }
}

function speak() {
  let text = currentPrediction;
  if (text === "---" || text === "Predicting..." || text === "unknown") {
    alert("Please make a prediction first!");
    return;
  }
  
  // Speak the prettified version (without underscores)
  const cleanText = prettifyLabel(text);
  let utter = new SpeechSynthesisUtterance(cleanText);
  utter.lang = 'en-IN';
  utter.rate = 0.9;
  window.speechSynthesis.speak(utter);
}

let video = document.getElementById("video");
let canvas = document.getElementById("canvas");

function startCamera() {
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => video.srcObject = stream);
}

function predictSign() {
  const ctx = canvas.getContext("2d");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  ctx.drawImage(video, 0, 0);

  canvas.toBlob(blob => {
    let formData = new FormData();
    formData.append("image", blob);

    fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      document.getElementById("result").innerText = data.prediction;
    });
  });
}

function speak() {
  let text = document.getElementById("result").innerText;
  let utter = new SpeechSynthesisUtterance(text);
  window.speechSynthesis.speak(utter);
}

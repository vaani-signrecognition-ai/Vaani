fetch("http://127.0.0.1:5000/api/ngos")
  .then(res => res.json())
  .then(data => {
    const container = document.getElementById("ngoContainer");
    container.innerHTML = "";

    data.forEach(ngo => {
      container.innerHTML += `
        <div class="ngo-card">
          <h5>${ngo.ngo_name}</h5>
          <p>${ngo.email}</p>
        </div>
      `;
    });
  })
  .catch(err => console.error("NGO fetch error:", err));

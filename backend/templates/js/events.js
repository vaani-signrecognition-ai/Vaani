fetch("http://127.0.0.1:5000/api/events")
  .then(res => res.json())
  .then(data => {
    const list = document.getElementById("eventsList");
    list.innerHTML = "";

    data.forEach(event => {
      list.innerHTML += `
        <div class="event-card">
          <h5>${event.title}</h5>
          <p><b>NGO:</b> ${event.ngo_name}</p>
          <p><b>Date:</b> ${event.event_date}</p>
          <p><b>Location:</b> ${event.location}</p>
          <p>${event.description}</p>
        </div>
      `;
    });
  })
  .catch(err => console.error("Event fetch error:", err));

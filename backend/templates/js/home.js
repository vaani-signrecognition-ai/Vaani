fetch("http://127.0.0.1:5000/api/events?limit=3")
  .then(res => res.json())
  .then(data => {
    const container = document.getElementById("eventsContainer");
    data.forEach(e => {
      container.innerHTML += `<p><b>${e.event_title}</b> - ${e.event_date}</p>`;
    });
  });

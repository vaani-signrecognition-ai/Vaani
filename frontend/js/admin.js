async function loadNGORequests() {
  const res = await fetch("http://127.0.0.1:5000/api/admin/ngo-requests");
  const data = await res.json();

  const table = document.getElementById("ngoTable");
  table.innerHTML = "";

  data.forEach(req => {
    table.innerHTML += `
    <tr>
    <td>${req.org_name}</td>
    <td>${req.contact_person}</td>
    <td>${req.phone}</td>
    <td>${req.email}</td>
    <td>${req.city}</td>
    <td>${req.purpose}</td>
    <td>${req.description}</td>
    <td>
      <span class="status ${req.status}">
        ${req.status}
      </span>
    </td>
    <td>${new Date(req.submitted_at).toLocaleString()}</td>
    <td>
      ${
        req.status === "PENDING"
          ? `
            <button class="approve" onclick="updateRequest(${req.request_id}, 'APPROVED')">
              Approve
            </button>
            <button class="reject" onclick="updateRequest(${req.request_id}, 'REJECTED')">
              Reject
            </button>
          `
          : "—"
      }
    </td>
  </tr>
  
    `;
  });
}

async function updateRequest(requestId, action) {
  await fetch(
    "http://127.0.0.1:5000/api/admin/ngo-request/action",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        request_id: requestId,
        action: action
      })
    }
  );

  loadNGORequests(); // refresh table
}

loadNGORequests();

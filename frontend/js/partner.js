document.getElementById("partnerForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  // clear previous errors
  document.querySelectorAll(".error").forEach(el => {
    el.innerText = "";
  });

  const payload = {
    org_name: org_name.value.trim(),
    contact_person: contact_person.value.trim(),
    phone: phone.value.trim(),
    email: email.value.trim(),
    purpose: purpose.value.trim(),
    city: city.value.trim(),
    description: description.value.trim()
  };

  const res = await fetch("http://127.0.0.1:5000/api/ngo/request", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const data = await res.json();

  // ❌ backend validation failed → show instantly
  if (!res.ok) {
    for (let field in data.errors) {
      const errorEl = document.getElementById(field + "_error");
      if (errorEl) {
        errorEl.innerText = data.errors[field];
      }
    }
    return;
  }

  // ✅ success
  alert("Application submitted successfully!");
  e.target.reset();
});

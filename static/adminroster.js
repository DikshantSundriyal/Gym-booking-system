const session_select = document.getElementById("roster_session_select");
const roster_container = document.getElementById("roster_container");
const roster_message = document.getElementById("roster_message");
const backbutton = document.getElementById("back_admin_btn");

const token = localStorage.getItem("token");
const role = localStorage.getItem("role");

if (!token || role !== "admin") {
    alert("Admins only.");
    window.location.replace("/login");
}

backbutton.addEventListener("click", function() {
    window.location.href = "/admin";
});

async function loadSessions() {
    try {
        const response = await fetch("/api/sessions", {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + token
            }
        });
        const result = await response.json();

        session_select.innerHTML = '<option value="">Select session</option>';
        result.forEach(session => {
            const opt = document.createElement("option");
            opt.value = session.session_id;
            opt.textContent = session.date + " " + session.time + " (" + session.mats_left + " mats left)";
            session_select.appendChild(opt);
        });
    } catch (error) {
        roster_message.textContent = "Could not load sessions";
    }
}
session_select.addEventListener("change", async function() {
    const session_id = session_select.value;
    if (session_id === "") {
        roster_container.innerHTML = "";
        roster_message.textContent = "";
        return;
    }
    roster_message.textContent = "Loading attendees...";
    roster_container.innerHTML = "";
    try {
        const response = await fetch("/admin/session/" + session_id + "/bookings", {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + token
            }
        });
        const result = await response.json();
        roster_message.textContent = "";
        if (result.length === 0) {
            roster_message.textContent = "No bookings for this session.";
            return;
        }
        result.forEach(b => {
            const card = document.createElement("div");
            card.classList.add("session-card");
            card.style.margin = "8px 0";
            const name = document.createElement("p");
            name.textContent = "Member: " + b.name + " (" + b.email + ")";
            const code = document.createElement("p");
            code.textContent = "Code: " + b.booking_code;
            const status = document.createElement("p");
            status.textContent = "Status: " + (b.checked_in ? "Checked In" : "Pending");
            card.append(name, code, status);
            roster_container.appendChild(card);
        });
    } catch (error) {
        roster_message.textContent = "Server connection failed";
    }
});

loadSessions();
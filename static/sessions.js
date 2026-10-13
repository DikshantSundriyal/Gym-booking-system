
const session_container = document.getElementById("sessions");
const session_message = document.getElementById("sessions-message");
const filter_date = document.getElementById("filter_date");
const clear_filter_btn = document.getElementById("clear_filter_btn");

session_container.innerHTML = "";

async function loadSessions() {
    const token = localStorage.getItem("token");
    if (!token) {
        session_message.textContent = "Please login first";
        return;
    }
    let url = "/api/sessions";
    const selected_date = filter_date.value;
    if (selected_date !== "") {
        url = url + "?date=" + selected_date;
    }
    try {
        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const result = await response.json();
        if (!response.ok) {
            session_message.textContent = result.message || "Could not load sessions";
            return;
        }
        session_container.innerHTML = "";
        if (result.length === 0) {
            session_message.textContent = "No sessions are currently available.";
            return;
        }
        session_message.textContent = "";
        result.forEach(session => {
            const card = document.createElement("div");
            card.classList.add("session-card");

            const date = document.createElement("h2");
            date.textContent = session.date;

            const time = document.createElement("p");
            time.textContent = "Time: " + session.time;

            const mats = document.createElement("p");
            mats.textContent = "Mats left: " + session.mats_left;

            const button = document.createElement("button");
            if (session.mats_left === 0) {
                button.textContent = "Join Waitlist";
                button.addEventListener("click", function() {
                    joinwaitlist(session.session_id, button);
                });
            } else {
                button.textContent = "Book Session";
                button.addEventListener("click", function() {
                    createbooking(session.session_id, button);
                });
            }
            card.appendChild(date);
            card.appendChild(time);
            card.appendChild(mats);
            card.appendChild(button);
            session_container.appendChild(card);
        });
    } catch (error) {
        session_message.textContent = "Something went wrong.";
        console.error(error);
    }
}

async function createbooking(session_id, button) {
    const token = localStorage.getItem("token");

    if (!token) {
        session_message.textContent = "Please login again";
        return;
    }

    button.disabled = true;
    button.textContent = "Booking...";
    try {
        const response = await fetch("/sessions/book/" + session_id, {
            method: "POST",
            headers: {
                "Authorization": "Bearer " + token,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ "sessionid": session_id })
        });
        const result = await response.json();
        if (response.ok) {
            session_message.textContent =
                result.message + ". Booking code: " + result.booking_code;
            await loadSessions();
        } else {
            session_message.textContent =
                result.message || "Could not make booking";

            await loadSessions();
        }
    } catch (error) {
        session_message.textContent = "Could not connect to the server";
        button.disabled = false;
        button.textContent = "Book Session";
    }
}

async function joinwaitlist(session_id, button) {
    const token = localStorage.getItem("token");

    if (!token) {
        session_message.textContent = "Please login again";
        return;
    }

    button.disabled = true;
    button.textContent = "Joining...";
    try {
        const response = await fetch("/sessions/waitlist/" + session_id, {
            method: "POST",
            headers: {
                "Authorization": "Bearer " + token,
                "Content-Type": "application/json"
            }
        });
        const result = await response.json();
        if (response.ok) {
            session_message.textContent =
                result.message + ". Your waitlist number is " +
                result.waitlist_number;

            await loadSessions();
        } else {
            session_message.textContent =
                result.message || "Could not join waitlist";

            await loadSessions();
        }
    } catch (error) {
        session_message.textContent = "Could not connect to the server";
        button.disabled = false;
        button.textContent = "Join Waitlist";
    }
}
filter_date.addEventListener("change", function() {
    loadSessions();
});
clear_filter_btn.addEventListener("click", function() {
    filter_date.value = "";
    loadSessions();
});

loadSessions();
setInterval(function(){loadSessions();}, 5000);
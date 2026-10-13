const Session_button=document.getElementById("Session-creating-button");
const Checkin_button=document.getElementById("Check_in-button");
const Roster_button=document.getElementById("Session_roster-button");

const token = localStorage.getItem("token");
const role = localStorage.getItem("role");

if (!token || role !== "admin") {
    alert("Admins only.");
    window.location.replace("/login");
}

Session_button.addEventListener('click',
    function(){
        window.location.href='/admin/sessions/create';
    }
);
Checkin_button.addEventListener('click',
    function(){
        window.location.href='/admin/check-in';
    }
);
Roster_button.addEventListener('click',
    function(){
        window.location.href='/admin/roster';
    }
);


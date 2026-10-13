const session_create_form=document.getElementById("create_session");
const session_time=document.getElementById("session_time");
const session_date=document.getElementById("session_date");
const session_text=document.getElementById("session_message");

const token = localStorage.getItem("token");
const role = localStorage.getItem("role");

if (!token || role !== "admin") {
    alert("Admins only.");
    window.location.replace("/login");
}

session_create_form.addEventListener("submit",
    async function(event){
        event.preventDefault();

        const sessiontime=session_time.value;
        const sessiondate=session_date.value;


        if (sessiontime==="" || sessiondate===""){
            session_text.textContent="Please choose all options"
            return
        }

        const data={
            'date':sessiondate,'time':sessiontime
        };
        const response= await fetch("/api/admin/sessions/create",
            {method:"POST",
            headers: {"Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body:JSON.stringify(data)
        });
        const result= await response.json();

        if (result.success){
            session_text.textContent="Session created succesfully";
        }
        else{
        session_text.textContent="Error "+ response.status + ": "+result.message;
        }

    }
);

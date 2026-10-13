const checkin_form=document.getElementById("admin_checkin");
const booking_code=document.getElementById("booking_code");
const message=document.getElementById("checkin_message");
const button=document.getElementById("checkin_button");

const token = localStorage.getItem("token");
const role = localStorage.getItem("role");

if (!token || role !== "admin") {
    alert("Admins only.");
    window.location.replace("/login");
}


checkin_form.addEventListener("submit",
    async function (event){
        event.preventDefault();

        const token = localStorage.getItem("token");
        if (!token) {
            message.textContent = "Please log in again.";
            return;
        }
        const bcode=booking_code.value;

        if (bcode === ""){
        message.textContent ="Please enter the booking code";
        return;
    }
    const data={
        'bookingcode':bcode
    };
    button.disabled = true;
    message.textContent = "Checking booking...";
    try{
        const response= await fetch("/api/admin/check-in",
            {method:"POST",
            headers: {"Content-Type": "application/json",
                "Authorization":`Bearer ${token}`
            },
            body:JSON.stringify(data)
        });
        const result= await response.json();

        if (result.success){
            message.textContent=result.name+"("+result.email+")"+result.message;
            checkin_form.reset();
        }
        else{
            message.textContent="Error "+ response.status + ": "+result.message;
        }
    }   
    catch(error){
        message.textContent="Server connection failed";
    }
    finally{
        button.disabled=false;
    }

});
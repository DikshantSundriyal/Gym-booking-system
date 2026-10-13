const message=document.getElementById("messagecontent")
const container=document.getElementById("booking_container")

async function history(){
    const token=localStorage.getItem("token")

    if (!token){
        container.textContent="Please login first";
        return;
    }
    try{
        const response= await fetch("/my_bookings",
            {headers:{
                "Authorization": `Bearer ${token}`
            }}
        );

        const result = await response.json();
        if(!response.ok){
            container.textContent="Unable to load bookings"
            return;
        }
        const history=result;

        container.innerHTML="";
        if(result.length===0){
            container.textContent="No bookings yet";
            return;
        }
        container.innerHTML="";
        history.forEach(i => {
            const panel= document.createElement("div");
            panel.className="booking_details"

            const title= document.createElement("h1");
            title.textContent="Session"+i.session_id;

            const date= document.createElement("p");
            date.textContent="Session date: "+i.date;

            const time= document.createElement("p");
            time.textContent="Session time: "+i.time;

            panel.append(title,date,time)
            
            if(i.type==="booked"){
                const status= document.createElement("p");
                status.textContent="Status: "+i.type;
                const bookingid= document.createElement("p");
                bookingid.textContent="Booking id: "+i.booking_id;
                const bookingcode= document.createElement("p");
                bookingcode.textContent="Booking code: "+i.booking_code;
                const bcancelbutton=document.createElement("button");
                bcancelbutton.textContent="Cancel Booking";
                bcancelbutton.className="cancel-button";
                bcancelbutton.addEventListener("click", function(){
                    cancelbooking(i.booking_id,bcancelbutton)
                });
                panel.append(status, bookingid, bookingcode, bcancelbutton);
            }
            if(i.type==="waitlisted"){
                const status= document.createElement("p");
                status.textContent="Status: "+i.type;
                const waitlistid= document.createElement("p");
                waitlistid.textContent="Waitlist number: "+i.waitlist_number;
                const wcancelbutton=document.createElement("button");
                wcancelbutton.textContent="Cancel Waitlist";
                wcancelbutton.className="cancel-button";
                wcancelbutton.addEventListener("click", function(){
                    cancelwaitlist(i.waitlist_id,wcancelbutton)
                });
                panel.append(status,waitlistid,wcancelbutton);
            }
            container.appendChild(panel);
        });
    }
    catch(error){
            container.textContent="Something went wrong";
        }
}


async function cancelbooking(bookingid,button){
    const confirmation=confirm("You  sure you want to delete?");
    if (!confirmation){
        return;
    }
    button.disabled=true;
    button.textContent="Cancelling...";

    const token=localStorage.getItem("token");
    if (!token){
        message.textContent="Please login again";
        return;
    }
    try{
        const response= await fetch("/booking/del/"+ bookingid, {method: "DELETE",
             headers:{"Authorization": `Bearer ${token}`}
        });
        const result= await response.json();

        if (response.ok){
            message.textContent=result.message;
            await history();
        }
        else{
            message.textContent=result.message || "Could not cancel booking";
            button.disabled=false;
            button.textContent="Cancel booking";
        }
    }
    catch(error){
        message.textContent="Could not connect to the server";
        button.disabled=false;
        button.textContent="Cancel booking";
    }
}



async function cancelwaitlist(waitlistid,button){
    const confirmation=confirm("You  sure you want to cancel?");
    if (!confirmation){
        return;
    }
    button.disabled=true;
    button.textContent="Cancelling...";

    const token=localStorage.getItem("token");
    if (!token){
        message.textContent="Please login again";
        return;
    }
    try{
        const response= await fetch("/waitlist/del/"+ waitlistid, {method: "DELETE",
             headers:{"Authorization": `Bearer ${token}`}
        });
        const result= await response.json();

        if (response.ok){
            message.textContent=result.message;
            await history();
        }
        else{
            message.textContent=result.message || "Could not cancel waitlist";
            button.disabled=false;
            button.textContent="Cancel Waitlist";
        }
    }
    catch(error){
        message.textContent="Could not connect to the server";
        button.disabled=false;
        button.textContent="Cancel Waitlist";
    }
}
history();
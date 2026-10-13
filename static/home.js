const login_button=document.getElementById("Login-button");
const Session_button=document.getElementById("Session-booking-button");
const Session_history_button=document.getElementById("Session-history-button");
const message=document.getElementById("Home-message");


const token=localStorage.getItem("token");

if(!token){
        login_button.addEventListener('click',
        function(){
            window.location.href='/login';
        }
    );
    Session_button.addEventListener('click',
        function(){
            window.location.href='/login';
        }
    );
    Session_history_button.addEventListener('click',
        function(){
            window.location.href='/login';
        }
    );

}
else{
    login_button.addEventListener('click',
        function(){
            message.textContent="You are alreagy login";
        }
    );
    Session_button.addEventListener('click',
        function(){
            window.location.href='/sessions';
        }
    );
    Session_history_button.addEventListener('click',
        function(){
            window.location.href='/booking_history';
        }
    );
}
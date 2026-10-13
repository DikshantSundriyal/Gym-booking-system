const login_form=document.getElementById("login");
const login_name=document.getElementById("login_name");
const login_email=document.getElementById("login_email");
const login_password=document.getElementById("login_password");
const loginMessage =document.getElementById("login_Message");


login_form.addEventListener("submit",
    async function (event){
        event.preventDefault();

        const name=login_name.value;
        const email=login_email.value;
        const password=login_password.value;

        if (name === "" || email === "" || password === "") {
        loginMessage.textContent ="Please fill in all fields";
        return;
    }
    const data={
        'name':name,'email':email,'password':password
    };
    const response= await fetch("/login",
        {method:"POST",
        headers: {"Content-Type": "application/json"},
        body:JSON.stringify(data)
    });
    const result= await response.json();

    if (result.success){
        localStorage.setItem("token",result.access_token);
        localStorage.setItem("role",result.role);
        if(result.role==="admin"){
            window.location.replace('/admin');
        }
        if(result.role==="user"){
            window.location.replace('/');;
        }
        
    }
    else{
        loginMessage.textContent="Error "+ response.status + ": "+result.message;
    }

});
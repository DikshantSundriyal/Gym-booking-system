const register_form=document.getElementById("registeration");
const register_name=document.getElementById("registeration_name");
const register_email=document.getElementById("registeration_email");
const register_password=document.getElementById("registeration_password");
const registerMessage =document.getElementById("register_message");


register_form.addEventListener("submit",
    async function (event){
        event.preventDefault();

        const name=register_name.value;
        const email=register_email.value;
        const password=register_password.value;

        if (name === "" || email === "" || password === "") {
        registerMessage.textContent ="Please fill in all fields";
        return;
    }
    const data={
        'name':name,'email':email,'password':password
    };
    const response= await fetch("/register",
        {method:"POST",
        headers: {"Content-Type": "application/json"},
        body:JSON.stringify(data)
    });
    const result= await response.json();

    if (result.success){
        window.location.replace('/login');
    }
    else{
        registerMessage.textContent="Error "+ response.status + ": "+result.message;
    }

});
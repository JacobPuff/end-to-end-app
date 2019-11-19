import React from 'react';
import ReactDOM from 'react-dom';
import {postRequest} from '../utilities.js'

const ENTER_KEYCODE = 13;

function LoginSignup(props) {
    //Login state
    const [UsernameEmail, setUsernameEmail] = React.useState("");

    //Sign up state
    const [Username, setUsername] = React.useState("");
    const [Email, setEmail] = React.useState("");
    const [PasswordAgain, setPasswordAgain] = React.useState("");

    //Shared
    const [Password, setPassword] = React.useState("");
    const [sendingRequest, setSendingRequest] = React.useState(false)

    const [displayError, setDisplayError] = React.useState(false);
    const [errorValue, setErrorValue] = React.useState("error: this is shown before being set")

    const [displaySuccess, setDisplaySuccess] = React.useState(false);
    const [successValue, setSuccesssValue] = React.useState("success: or is it? because this is shown before being set")

    function ValidateEmail(mail) {
        if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(mail)) {
            return (true)
        }
        return (false)
    }

    function LoginSignupErrorHandler(errorData) {
        console.log(errorData)
        console.log("error: " + errorData["d"]["errors"][0])
        var error_type = errorData["d"]["error_type"]
        var error = errorData["d"]["errors"][0]
        setErrorValue("error: " + error);
        setDisplayError(true);
        switch (error) {
            case "user doesn't exist":
                setErrorValue("error: username or password are incorrect");
                setDisplayError(true);
                break;
            case "username already in use":
                setErrorValue("error: username already in use");
                setDisplayError(true);
        }
    }

    function checkEnter(e) {
        if (e.keyCode == ENTER_KEYCODE || e.charCode == ENTER_KEYCODE) {
            console.log("YEET")
            if (document.title == "Login") {
                handleLoginSubmit();
            } else if (document.title == "Sign up") {
                handleSignupSubmit();
            }
            console.log(e.target.value)
            return;
        }
    }

    function handleInputs(e) {
        e.preventDefault();

        switch(e.target.placeholder) {
            case "Username/Email":
                setUsernameEmail(e.target.value);
                break;
            case "password":
                setPassword(e.target.value);
                break;
            case "Username":
                setUsername(e.target.value);
                break;
            case "Email":
                setEmail(e.target.value);
                break;
            case "password again":
                setPasswordAgain(e.target.value);
                break;
        }
    }

    function handleLoginSubmit() {
        if (!UsernameEmail) {
            setErrorValue("error: username is required");
            setDisplayError(true);
            return;
        }
        else if (!Password) {
            setErrorValue("error: password is required")
            setDisplayError(true);
            return;
        }
        else {
            setDisplayError(false);
        }
        if (!sendingRequest) {
            if (ValidateEmail(UsernameEmail)) {
                var loginPost = postRequest("sessions", {"user_email": UsernameEmail,
                                                            "user_pass": Password,
                                                            "token": localStorage.getItem("token")})
                setSendingRequest(true)
            }
            else {
                var loginPost = postRequest("sessions", {"user_name": UsernameEmail,
                                                            "user_pass": Password,
                                                            "token": localStorage.getItem("token")})
                setSendingRequest(true)
            }

            loginPost.then(function(result){
                setSendingRequest(false)
                localStorage.setItem("token", result.d.token)
                setSuccesssValue("successfully logged in");
                setDisplaySuccess(true);
            }).catch(function(errorData){
                setSendingRequest(false);
                LoginSignupErrorHandler(errorData);
            })
        }
    }

    function handleSignupSubmit() {
        if (!Username) {
            setErrorValue("error: username is required");
            setDisplayError(true);
            return;
        } else if (ValidateEmail(Username)) {
            setErrorValue("error: you put your email in the wrong field")
            setDisplayError(true);
            return;
        }
        else if (!Email || !ValidateEmail(Email)) {
            setErrorValue("error: valid email is required");
            setDisplayError(true);
            return;
        }
        else if (!Password) {
            setErrorValue("error: password is required")
            setDisplayError(true);
            return;
        }
        else if (PasswordAgain != Password) {
            setErrorValue("error: passwords do not match");
            setDisplayError(true);
            return;
        }
        else {
            setDisplayError(false);
        }
        if (!sendingRequest) {
            var signupRequest = postRequest("users", {"user_name": Username, "user_email": Email, "user_pass": Password})
            setSendingRequest(true)

            signupRequest.then(function(result){
                setSendingRequest(false)
                setSuccessValue("successfully signed up");
                setDisplaySuccess(true);
            }).catch(function(errorData){
                setSendingRequest(false);
                LoginSignupErrorHandler(errorData);
            });
        }
    }

    if (window.location.pathname == "/login/") {
        document.title = "Login"
        return (
            React.createElement('div', {className:"centerContainer"},
                React.createElement('h1', {className:"inputName"}, "Login"),
                React.createElement('input', {className:"customInput", placeholder:"Username/Email", onChange: handleInputs, onKeyDown: checkEnter}),
                React.createElement('input', {className:"customInput", placeholder:"password", type:"password", onChange: handleInputs, onKeyDown: checkEnter}),
                (displayError && React.createElement('p', {className:"error"}, errorValue)),
                (displaySuccess && React.createElement('p', {className:"success"}, successValue)),
                React.createElement('div', {className:"inputButtonContainer"},
                    React.createElement('div', {className:"miniButton"},
                        React.createElement('button', {className:"inputButton", onClick:() => {window.location.href="/forgotpassword"}},
                            "Forgot Password?"),
                        React.createElement('button', {className:"inputButton", onClick:() => {window.location.href="/signup"}},
                            "Sign Up")
                    ),
                    React.createElement('button', {className:"inputButton", onClick: handleLoginSubmit},
                            "Submit")
                )
            )
        );
    }
    else if (window.location.pathname == "/signup/") {
        document.title = "Sign up"
        return (
            React.createElement('div', {className:"centerContainer"},
                React.createElement('h1', {className:"inputName"}, "Sign up"),
                React.createElement('input', {className:"customInput", placeholder:"Username", onChange: handleInputs, onKeyDown: checkEnter}),
                React.createElement('input', {className:"customInput", placeholder:"Email", onChange: handleInputs, onKeyDown: checkEnter}),
                React.createElement('input', {className:"customInput", placeholder:"password", type:"password", onChange: handleInputs, onKeyDown: checkEnter}),
                React.createElement('input', {className:"customInput", placeholder:"password again", type:"password", onChange: handleInputs, onKeyDown: checkEnter}),
                (displayError && React.createElement('p', {className:"error"}, errorValue)),
                (displaySuccess && React.createElement('p', {className:"success"}, successValue)),
                React.createElement('div', {className:"inputButtonContainer"},
                    React.createElement('button', {className:"inputButton", onClick:() => {window.location.href="/login"}},
                        "Login"),
                    React.createElement('button', {className:"inputButton", onClick: handleSignupSubmit},
                        "Submit")
                )
            )
        );
    }
}

ReactDOM.render(
    React.createElement(LoginSignup),
    document.getElementById('root')
);
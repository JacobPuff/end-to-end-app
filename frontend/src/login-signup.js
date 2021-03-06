import React from 'react';
import ReactDOM from 'react-dom';
import Reaptcha from 'reaptcha';
import {postRequest, validateEmail} from './utilities.js'

const ENTER_KEYCODE = 13;

function LoginSignup() {
    //Login state
    const [UsernameEmail, setUsernameEmail] = React.useState("");

    //Sign up state
    const [Username, setUsername] = React.useState("");
    const [Email, setEmail] = React.useState("");
    const [PasswordAgain, setPasswordAgain] = React.useState("");
    const [recaptchaToken, setRecaptchaToken] = React.useState("");
    var recaptchaRef = React.useRef();

    //Shared
    const [Password, setPassword] = React.useState("");
    const [sendingRequest, setSendingRequest] = React.useState(false);

    const [displayError, setDisplayError] = React.useState(false);
    const [errorValue, setErrorValue] = React.useState("error: this is shown before being set")

    const [displaySuccess, setDisplaySuccess] = React.useState(false);
    const [successValue, setSuccessValue] = React.useState("success: or is it? because this is shown before being set")

    function LoginSignupErrorHandler(errorData) {
        var error_type = errorData["d"]["error_type"];
        var error = errorData["d"]["errors"][0]
        console.log("error_type: " + error_type, "\nerror: ", error);
        switch (error) {
            case "user doesnt exist":
                setErrorValue("error: username/email or password are incorrect");
                setDisplayError(true);
                break;
            case "email is blacklisted":            
                setErrorValue("Email has been blacklisted. Use contact section on the home page " + 
                    "if you need anything.");
                setDisplayError(true);
                break;
            case "recaptcha token is invalid":
                setErrorValue("Nupe. Yous got a bad recaptcha token. Yous a bot.");
                setDisplayError(true);
                break;
            default:
                setErrorValue("error: " + error);
                setDisplayError(true);
        }
    }

    function checkEnter(e) {
        if (e.keyCode == ENTER_KEYCODE || e.charCode == ENTER_KEYCODE) {
            if (document.title == "Login") {
                handleLoginSubmit();
            } else if (document.title == "Sign up") {
                handleSignupSubmit();
            }
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
        setDisplaySuccess(false);
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
        else if (Password.length < 8) {
            setErrorValue("error: password must be at least 8 characters");
            setDisplayError(true);
            return;
        }
        else {
            setDisplayError(false);
        }

        if (!sendingRequest) {
            if (validateEmail(UsernameEmail)) {
                var loginPost = postRequest("sessions", {"user_email": UsernameEmail,
                                                            "user_pass": Password})
                setSendingRequest(true)
            }
            else {
                var loginPost = postRequest("sessions", {"user_name": UsernameEmail,
                                                            "user_pass": Password})
                setSendingRequest(true)
            }

            loginPost.then(function(result){
                setSendingRequest(false)
                localStorage.setItem("localLastActive", new Date());
                localStorage.setItem("token", result.d.token)
                setSuccessValue("successfully logged in");
                setDisplaySuccess(true);
            }).catch(function(errorData){
                setSendingRequest(false);
                LoginSignupErrorHandler(errorData);
            })
        }
    }

    function handleVerifyReCaptcha(e) {
        setRecaptchaToken(e);
    }

    function handleExpireReCaptcha() {
        setRecaptchaToken("");
        recaptchaRef.current.reset();
    }

    function handleSignupSubmit() {
        setDisplaySuccess(false);
        if (!Username) {
            setErrorValue("error: username is required");
            setDisplayError(true);
            return;
        }
        else if (validateEmail(Username)) {
            setErrorValue("error: you put your email in the wrong field")
            setDisplayError(true);
            return;
        }
        else if (!Email || !validateEmail(Email)) {
            setErrorValue("error: valid email is required");
            setDisplayError(true);
            return;
        }
        else if (Password.length < 8) {
            setErrorValue("error: password must be at least 8 characters");
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
        else if (!recaptchaToken) {
            setErrorValue("Please verify you are not a bot");
            setDisplayError(true);
            return;
        }
        else {
            setDisplayError(false);
        }

        if (!sendingRequest) {
            var signupRequest = postRequest("users", {"user_name": Username, "user_email": Email,
                                                    "user_pass": Password, "recaptcha_token": recaptchaToken})
            setSendingRequest(true)

            signupRequest.then(function(result){
                setSendingRequest(false)
                localStorage.setItem("localLastActive", new Date());
                localStorage.setItem("token", result.d.session.token);
                setSuccessValue("successfully signed up! check your email to verify it!");
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
                    React.createElement('div', {},
                        React.createElement('button', {className:"inputButton miniButton", onClick:() => {window.location.href="/forgotpassword"}},
                            "Forgot Password?"),
                        React.createElement('button', {className:"inputButton miniButton", onClick:() => {window.location.href="/signup"}},
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
                    React.createElement('button', {className:"inputButton miniButton", onClick:() => {window.location.href="/login"}},
                        "Login"),
                    React.createElement(Reaptcha, {sitekey: "6LerI8YUAAAAAL4tpU_V5_PyEXjRsnsfE_jRrozx",
                        theme: "dark",
                        ref: recaptchaRef,
                        onVerify: (e) => {handleVerifyReCaptcha(e)},
                        onExpire: (e) => {handleExpireReCaptcha(e)}}),
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
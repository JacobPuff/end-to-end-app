import React from 'react';
import ReactDOM from 'react-dom';
import Reaptcha from 'reaptcha';
import { validateEmail, postRequest } from './utilities';

const ENTER_KEYCODE = 13;

function ForgotPassword() {
    const [Email, setEmail] = React.useState("");
    const [sendingRequest, setSendingRequest] = React.useState(false);
    const [recaptchaToken, setRecaptchaToken] = React.useState("");
    var recaptchaRef = React.useRef();

    const [displayError, setDisplayError] = React.useState(false);
    const [displaySuccess, setDisplaySuccess] = React.useState(false);
    const [errorValue, setErrorValue] = React.useState("error: this is displayed before being set");
    const [successValue, setSuccessValue] = React.useState("success: or is it? because this is shown before being set");

    function checkEnter(e) {
        if (e.keyCode == ENTER_KEYCODE || e.charCode == ENTER_KEYCODE) {
            handleSubmit();
            return;
        }
    }

    function changeEmail(e) {
        e.preventDefault();
        setEmail(e.target.value);
    }

    function handleVerifyReCaptcha(e) {
        setRecaptchaToken(e);
    }

    function handleExpireReCaptcha() {
        setRecaptchaToken("");
        recaptchaRef.current.reset();
    }

    function handleSubmit() {
        setDisplayError(false);
        setDisplaySuccess(false);
        if (!recaptchaToken) {
            setErrorValue("Please verify you are not a bot");
            setDisplayError(true);
            return;
        }
        if (!sendingRequest) {
            if (validateEmail(Email)) {
                setSendingRequest(true);
                const resetEmailRequest = postRequest("resettokens", {"user_email": Email,
                                                                    "recaptcha_token": recaptchaToken});
                resetEmailRequest.then(function() {
                    setSendingRequest(false);
                    setSuccessValue("If there is a user with that email, you'll receive a password reset link!");
                    setDisplaySuccess(true);
                }).catch(function(errorData) {
                    setSendingRequest(false);
                    var error_type = errorData.d.error_type
                    var error = errorData.d.errors[0]
                    console.log(errorData)
                    console.log("error_type: ", error_type,
                                "\nerror: ", error);
                    switch (error) {
                        case "email is blacklisted":
                            setErrorValue("Email has been blacklisted. Use contact section on the home page" +
                                "if you need anything.");
                            setDisplayError(true);
                            break;
                        case "recaptcha token is invalid":
                            setErrorValue("Nupe. Yous got a bad recaptcha token. Yous a bot.")
                            setDisplayError(true)
                            break;
                    }
                });

            } else {
                setErrorValue("Please enter a valid email address");
                setDisplayError(true);
            }
        }
    }

    return (
        React.createElement('div', {className: "centerContainer"},
            React.createElement('h1', {className: "inputName"}, "Forgot Password"),
            React.createElement('p', {}, "You can send yourself a password reset link here"),
            React.createElement('input', {className:"customInput", placeholder: "Email",
                                            onChange: changeEmail, onKeyDown: checkEnter}),
            (displayError && React.createElement('p', {className:"error"}, errorValue)),
            (displaySuccess && React.createElement('p', {className:"success"}, successValue)),
            React.createElement('div', {className: "inputButtonContainer"},
                React.createElement(Reaptcha, {sitekey: "6LerI8YUAAAAAL4tpU_V5_PyEXjRsnsfE_jRrozx",
                    theme: "dark",
                    ref: recaptchaRef,
                    onVerify: (e) => {handleVerifyReCaptcha(e)},
                    onExpire: (e) => {handleExpireReCaptcha(e)}}),
                React.createElement('div', {className: "inputButton miniButton", onClick: handleSubmit}, "Submit")
            )
        )
    );
}

ReactDOM.render(
    React.createElement(ForgotPassword),
    document.getElementById('root')
);
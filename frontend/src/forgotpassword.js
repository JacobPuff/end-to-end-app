import React from 'react';
import ReactDOM from 'react-dom';
import { validateEmail, postRequest } from './utilities';

const ENTER_KEYCODE = 13;

function ForgotPassword() {
    const [Email, setEmail] = React.useState("");
    const [sendingRequest, setSendingRequest] = React.useState(false);

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

    function handleSubmit() {
        setDisplayError(false);
        setDisplaySuccess(false);
        if (!sendingRequest) {
            if (validateEmail(Email)) {
                setSendingRequest(true);
                const resetEmailRequest = postRequest("resettokens", {"user_email": Email});
                resetEmailRequest.then(function() {
                    setSendingRequest(false);
                    setSuccessValue("If there is a user with that email, you'lll receive a password reset link!");
                    setDisplaySuccess(true);
                }).catch(function(errorData) {
                    setSendingRequest(false);
                    console.log(errorData)
                    console.log("error_type: ", errorData.d.error_type,
                                "\nerror: ", errorData.d.errors[0]);
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
            React.createElement('div', {className: "inputButton", onClick: handleSubmit}, "Submit")
        )
    );
}

ReactDOM.render(
    React.createElement(ForgotPassword),
    document.getElementById('root')
);
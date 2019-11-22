import React from 'react';
import ReactDOM from 'react-dom';
import {putRequest, postRequest} from './utilities.js';

function Verify() {
    const verifyToken = new URL(window.location.href).searchParams.get("verifytoken");
    const [smolMessage, setSmolMessage] = React.useState(true);

    const [inputNameState, setInputNameState] = React.useState("Loading");
    const [messageValue, setMessageValue] = React.useState("just a sec");
    const [sentEmail, setSentEmail] = React.useState(false);
    const [sendingRequest, setSendingRequest] = React.useState(false);

    const [displayError, setDisplayError] = React.useState(false);
    const [errorValue, setErrorValue] = React.useState("error: this is shown before being set")

    const [displaySuccess, setDisplaySuccess] = React.useState(false);
    const [successValue, setSuccessValue] = React.useState("success: or is it? because this is shown before being set")

    React.useEffect(() => {
        if (verifyToken) {
            const verifyRequest = putRequest("verifytokens", {"verifytoken": verifyToken});
            verifyRequest.then(function() {
                setInputNameState("Verified email!")
                setMessageValue("Your email has successfully been verified! How neat is that?");
            }).catch(function(errorData) {
                verifyErrorHandler(errorData);
            });
        } else {
            setInputNameState("Verify email")
            setMessageValue("You need to use the link in your verification email for this page to work");
        }
    }, []);

    function verifyErrorHandler(errorData) {
        var error_type = errorData["d"]["error_type"];
        var error = errorData["d"]["errors"][0]
        console.log("error_type: " + error_type, "\nerror: ", error);
        switch (error) {
            case "user already verified":
                setErrorValue("error: youve already verified your email")
                setDisplayError(true);
                break;
            case "verify token is expired":
                setInputNameState("Verify email")
                setMessageValue("Your verification email has expired, but you can send another one!");
                setSmolMessage(false);
                break;
            case "verify token doesnt exist":
                setInputNameState("Verify email")
                setMessageValue("The token used doesnt exist. If you used the link in your verification email, you've already verified your email");
                break;
            default:
                setErrorValue("error: " + error);
                setDisplayError(true);
        }
    }

    function handleSubmit() {
        setDisplayError(false);
        setDisplaySuccess(false);
        if (!sendingRequest) {
            setSendingRequest(true);
            const sendVerificationEmailRequest = postRequest("verifytokens", {"verifytoken": verifyToken});

            sendVerificationEmailRequest.then(function() {
                setSendingRequest(false);
                setSentEmail(true);
                setSuccessValue("success! you have been sent a verification email")
                setDisplaySuccess(true);
            }).catch(function(errorData) {
                setSendingRequest(false);
                verifyErrorHandler(errorData);
            })
        }
    }

    return (
        React.createElement('div', {className: "centerContainer"},
            React.createElement('h1', {className: "inputName"}, inputNameState),
            React.createElement('p', {}, messageValue),

            (displayError && React.createElement('p', {className:"error"}, errorValue)),
            (displaySuccess && React.createElement('p', {className:"success"}, successValue)),
            
            React.createElement('div', {className: "inputButtonContainer"},
                React.createElement('button', {className: "inputButton miniButton", onClick: () => {window.location.href = "/"}},
                    "To home page"),
                    ((!smolMessage && !sentEmail)&& React.createElement('button', {className: "inputButton", onClick: handleSubmit},
                    "Send another!"))
            )
        )
    );
}

ReactDOM.render(
    React.createElement(Verify),
    document.getElementById('root')
);
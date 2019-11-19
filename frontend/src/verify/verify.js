import React from 'react';
import ReactDOM from 'react-dom';
import {putRequest, postRequest, validateEmail} from '../utilities.js';

function Verify(props) {
    const [verifyToken, setVerifyToken] = React.useState(new URL(window.location.href).searchParams.get("verifytoken"));
    const [smolMessage, setSmolMessage] = React.useState(false);

    const [inputNameState, setInputNameState] = React.useState("Loading");
    const [messageValue, setMessageValue] = React.useState("just a sec");

    const [displayError, setDisplayError] = React.useState(false);
    const [errorValue, setErrorValue] = React.useState(false);
    
    const [displaySuccess, setDisplaySuccess] = React.useState(false);
    const [successValue, setSuccessValue] = React.useState(false);

    React.useEffect(() => {
        if (verifyToken) {
            setSmolMessage(true);
            const verifyRequest = putRequest("verifytokens", {"verifytoken": verifyToken});
            verifyRequest.then(function() {
                setInputNameState("Verified email!")
                setMessageValue("Your email has successfully been verified");
            }).catch(function(errorData) {
                console.log(errorData)
                setInputNameState("Verify email")
                setMessageValue("Your verification email has expired, but you can send another one!");
                setSmolMessage(false);
            });
        } else {
            setSmolMessage(false)
            setInputNameState("Verify email")
            setMessageValue("You can send yourself a verification email here!");
        }
    }, []);

    return (
        React.createElement('div', {className: "centerContainer"},
            React.createElement('h1', {className: "inputName"}, inputNameState),
            React.createElement('p', {}, messageValue),
            (!smolMessage && React.createElement('input', {className: "customInput", placeholder: "Email"})),

            (displayError && React.createElement('p', {className:"error"}, errorValue)),
            (displaySuccess && React.createElement('p', {className:"success"}, successValue)),
            
            (!smolMessage && React.createElement('div', {className: "inputButtonContainer"},
                React.createElement('button', {className: "inputButton miniButton", onClick: () => {window.location.href = "/"}},
                    "To home page"),
                React.createElement('button', {className: "inputButton"},
                    "Submit")
            )),

            (smolMessage && React.createElement('button', {className: "inputButton miniButton", onClick: () => {window.location.href = "/"}},
                "To home page"))
        )
    );
}

ReactDOM.render(
    React.createElement(Verify),
    document.getElementById('root')
);
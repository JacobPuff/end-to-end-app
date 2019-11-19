import React from 'react';
import ReactDOM from 'react-dom';
import {putRequest, postRequest, validateEmail} from '../utilities.js';

function Verify(props) {
    const [verified, setVerified] = React.useState(false);
    const [verifyToken, setVerifyToken] = React.useState(new URL(window.location.href).searchParams.get("verifytoken"));

    const [displayError, setDisplayError] = React.useState(false);
    const [errorValue, setErrorValue] = React.useState(false);
    
    const [displaySuccess, setDisplaySuccess] = React.useState(false);
    const [successValue, setSuccessValue] = React.useState(false);

    //Should probably make things state so that I can have errors and successes

    React.useEffect(() => {
        if (verifyToken) {
            const verifyRequest = putRequest("verifytokens", {"verifytoken": verifyToken});
            verifyRequest.then(function(){
                setVerified = true;
            }).catch(function(errorData){
                console.log(errorData)
            });
        }
    }, []);
    if (verified) {
        return (
            React.createElement('div', {className: "centerContainer"},
                React.createElement('h1', {className: "inputName"}, "Verify email"),
                React.createElement('p', {}, "Your email has successfully been verified!"),
                React.createElement('button', {className: "inputButton miniButton", onClick: () => {window.location.href = "/"}}, "To home page")
            )
        );
    }
    else {
        return (
            React.createElement('div', {className: "centerContainer"},
                React.createElement('h1', {className: "inputName"}, "Verify email"),
                React.createElement('p', {}, "Your verification email has expired, but you can send another one!"),
                React.createElement('input', {className: "customInput", placeholder: "Email"}),
                React.createElement('div', {className: "inputButtonContainer"},
                    React.createElement('button', {className: "inputButton miniButton", onClick: () => {window.location.href = "/"}},
                        "To home page"),
                    React.createElement('button', {className: "inputButton"},
                        "Submit")
                )
            )
        );
    }
}

ReactDOM.render(
    React.createElement(Verify),
    document.getElementById('root')
);
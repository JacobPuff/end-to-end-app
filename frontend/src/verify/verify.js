import React from 'react';
import ReactDOM from 'react-dom';
import {putRequest, postRequest, validateEmail} from '../utilities.js';

function Verify(props) {
    var verified = false;
    var verifyToken = new URL(window.location.href).searchParams.get("verifytoken");

    React.useEffect(() => {
        if (verifyToken) {
            const verifyRequest = putRequest("verifytoken", {"verifytokens": verifyToken});
            verifyRequest.then(function(){
                verified = true;
            }).catch(function(errorData){
                console.log(errorData)
            });
        }
    }, []);
    if (verified) {
        return (
            React.createElement('div', {className: "centerContainer"},
                React.createElement('h1', {className: "inputName"}, "Verify email"),
                React.createElement('p', {}, "Your email has successfully been verified!")
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
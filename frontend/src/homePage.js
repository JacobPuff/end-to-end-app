import React from 'react';
import ReactDOM from 'react-dom';
import {putRequest, deleteRequest} from './utilities.js';

function userActionButton() {
    const [loggedIn, setLoggedIn] = React.useState(false);
    const [buttonValue, setButtonValue] = React.useState("login");

    React.useEffect(() => {
        if(localStorage.getItem("token")){
            setLoggedIn(true);
            setButtonValue("sign out");
            const checkLoggedInRequest = putRequest("sessions", {"token": localStorage.getItem("token")});
            checkLoggedInRequest.then(function() {
                //empty now because if there is a token, it should already be sign out. This is just checking.
                //If there isn't a token its already login.
                //I could probably make this check a lot faster by also including the last-active value.
            }).catch(function() {
                localStorage.removeItem("token");
                setLoggedIn(false);
                setButtonValue("login");
            });
        }
    }, []);

    function handleButton() {
        if (loggedIn) {
            setLoggedIn(false);
            setButtonValue("login");
            const deleteSessionRequest = deleteRequest("sessions", {"token": localStorage.getItem("token")});
            localStorage.removeItem("token");
        } else {
            window.location.href = "/login";
        }
    }

    return (
        React.createElement('div', {className: "userActionButton", onClick: handleButton}, buttonValue)
    );
}

ReactDOM.render(
    React.createElement(userActionButton),
    document.getElementById("userActionButton")
);
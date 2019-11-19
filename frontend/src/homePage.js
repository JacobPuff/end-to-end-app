import React from 'react';
import ReactDOM from 'react-dom';
import {putRequest, deleteRequest} from './utilities.js';

function userActionButton() {
    const [loggedIn, setLoggedIn] = React.useState(false);
    const [buttonValue, setButtonValue] = React.useState("login");

    React.useEffect(() => {
        const checkLoggedInRequest = putRequest("sessions", {"token": localStorage.getItem("token")});
        checkLoggedInRequest.then(function() {
            setLoggedIn(true);
            setButtonValue("sign out");
        }).catch(function() {
            localStorage.removeItem("token");
        });
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
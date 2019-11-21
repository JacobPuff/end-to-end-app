import React from 'react';
import ReactDOM from 'react-dom';
import {putRequest, deleteRequest} from './utilities.js';

function userActionButton() {
    const [loggedIn, setLoggedIn] = React.useState(false);
    const [buttonValue, setButtonValue] = React.useState("login");

    React.useEffect(() => {
        if(localStorage.getItem("token")){
            var expiration = new Date();
            expiration.setDate(new Date().getDate() - 7)
            var localLastActive = new Date(localStorage.getItem("localLastActive"));
            if (localLastActive > expiration) {
                setLoggedIn(true);
                setButtonValue("sign out");
            }
            const checkLoggedInRequest = putRequest("sessions", {"token": localStorage.getItem("token")});
            checkLoggedInRequest.then(function() {
                localStorage.setItem("localLastActive", new Date());
                setLoggedIn(true);
                setButtonValue("sign out");
            }).catch(function() {
                localStorage.removeItem("localLastActive");
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
            localStorage.removeItem("localLastActive");
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
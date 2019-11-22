import React from 'react';
import ReactDOM from 'react-dom';
import {getRequest} from './utilities.js';

function UserProfile() {
    const [loggedIn, setLoggedIn] = React.useState(false);
    const [user_id, setUser_id] = React.useState(null);
    const [user_name, setUser_name] = React.useState("");
    const [user_email, setUser_email] = React.useState("");

    const [inputNameState, setInputNameState] = React.useState("Loading");
    const [messageValue, setMessageValue] = React.useState("just a sec");

    React.useEffect(()=>{
        const getUserRequest = getRequest("users?token=" + localStorage.getItem("token"));
        getUserRequest.then(function(userData) {
            setLoggedIn(true);
            setUser_id(userData.d.user_id);
            setUser_name(userData.d.user_name);
            setUser_email(userData.d.user_email);
        }).catch(function(errorData) {
            setInputNameState("Not logged in");
            setMessageValue("Gotta be logged in to edit your account");
        });
    },[]);

    if (loggedIn) {

    } else {
        return (
            React.createElement('div', {className: "centerContainer"},
                React.createElement('h1', {className: "inputName"}, inputNameState),
                React.createElement('p', {}, messageValue)
            )
        )
    }
}

ReactDOM.render(
    React.createElement(UserProfile),
    document.getElementById('root')
);
import React from 'react';
import ReactDOM from 'react-dom';
import TextareaAutosize from 'react-autosize-textarea';
import {TaskList} from './tasklists.js';
import { getRequest } from '../utilities.js';
import { CustomAlert } from './customAlert.js';

function miniList(props) {
    const [editing, setEditing] = React.useState(false);
    const [listName, setListName] = React.useState(props.list_name)

    function changEditing() {
        setEditing(!editing)
    }

    function handleSave() {

    }

    if (editing) {
        return (
            React.createElement('div', {className: "miniListContainer"},
                React.createElement(TextareaAutosize, {className: "editMiniList"}, listName),
                React.createElement('button', {className: "customButton", onClick: handleSave}, "Save"),
                React.createElement('button', {className: "customButton"}, "x")
            )
        )
    } else {
        return (
            React.createElement('div', {className: "miniListContainer"},
                React.createElement('div', {className: "miniList"}, listName),
                React.createElement('button', {className: "customButton", onClick: changEditing}, "Edit"),
                React.createElement('button', {className: "customButton"}, "x")
            )
        );
    }
}

function ListOfLists() {
    const [loggedIn, setLoggedIn] = React.useState(false);
    const [demoMode, setDemoMode] = React.useState(false);

    const [allListsName, setAllListsName] = React.useState("Loading");

    //This could be split up, but it shouldnt change, so its fine if its in a dictionary.
    //We only really need the user_id anyways.
    //I just might want to have a "{username}'s lists" title or something later.
    const [userData, setUserData] = React.useState({});
    const [adding, setAdding] = React.useState(true);

    //Alert
    const [alertValue, setAlertValue] = React.useState("");
    const [displayAlert, setDisplayAlert] = React.useState(false);
    const [alertType, setAlertType] = React.useState("ok");

    //Get user data
    React.useEffect(()=> {
        const getUserDataRequest = getRequest("users?token=" + localStorage.getItem("token"));
        getUserDataRequest.then(function(result) {
            setUserData(result.d);
            setLoggedIn(true);
            
            var username = result.d["user_name"];
            username = username[0].toUpperCase() + username.substring(1);
            setAllListsName(username + "'s lists");
        }).catch(function(errorData) {
            if (errorData.d.errors[0] == "not authenticated for this request") {
                setAlertType("yes/no");
                setAlertValue("You arent logged in. Continue in demo mode?");
                setDisplayAlert(true);
            }
        });
    }, []);

    function handleAlertButtons(buttonValue) {
        if (alertType == "yes/no") {
            if(buttonValue) {
                setDemoMode(true);
            } else {
                window.location.href = '/';
            }
        }
        setDisplayAlert(false);
    }

    function changeAdding() {
        setAdding(!adding);
    }

    return (
        React.createElement('div', {className: "listOfLists"},
            React.createElement('div', {className: "listOfListsName"}, allListsName),
            React.createElement(miniList, {list_name: "Le Yeet"}),
            React.createElement(miniList, {list_name: "Le Haw"}),
            React.createElement(miniList, {list_name: "Le Yeethaw"}),
            (!adding && React.createElement('div', {className: "wideButton", onClick: changeAdding}, "Add list")),
            (adding && React.createElement('div', {className: "addListContainer"},
                React.createElement(TextareaAutosize, {className: "addList", rows: 1, type: "text"}),
                React.createElement('button', {className: "customButton", onClick: changeAdding}, "Done")
            )),
            (displayAlert && React.createElement(CustomAlert, {type: alertType, alert: alertValue, handleButtons: handleAlertButtons}))
        )
    );
}

ReactDOM.render(
    React.createElement(ListOfLists),
    document.getElementById('root')
);
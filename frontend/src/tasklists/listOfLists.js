import React from 'react';
import ReactDOM from 'react-dom';
import TextareaAutosize from 'react-autosize-textarea';
import {TaskList} from './tasklists.js';
import { getRequest, postRequest } from '../utilities.js';
import { CustomAlert } from './customAlert.js';

const ENTER_KEYCODE = 13;
const RETRY_UNICODE = "\u21BB"; //↻ 

function MiniList(props) {
    const [editing, setEditing] = React.useState(false);
    const [listName, setListName] = React.useState(props.list_name)
    const [isAdded, setIsAdded] = React.useState(false);

    React.useState(() => {
        if (props.list_id[0] == 't') {
            setIsAdded(false);
        } else {
            setIsAdded(true);
        }
    }, [])

    function checkEnterMiniList(e) {
        if (e.keyCode == ENTER_KEYCODE || e.charCode == ENTER_KEYCODE) {
            e.preventDefault();
            handleSave();
        }
    }

    function changeListName(e) {
        e.preventDefault();
        setListName(e.target.value);
    }

    function toggleEditing() {
        setEditing(!editing)
    }

    function retryAddingList() {
        props.retryAddList(props.list_id);
    }

    function handleSave() {
        toggleEditing()

    }

    if (editing) {
        return (
            React.createElement('div', {className: "miniListContainer"},
                React.createElement(TextareaAutosize, {className: "editMiniList", defaultValue: listName,
                    onChange: changeListName, onKeyDown: checkEnterMiniList}),
                React.createElement('button', {className: "customButton", onClick: handleSave}, "Save"),
                React.createElement('button', {className: "customButton"}, "x")
            )
        )
    } else {
        return (
            React.createElement('div', {className: "miniListContainer"},
                (isAdded && React.createElement('div', {className: "miniList"}, listName)),
                (!isAdded && React.createElement('div', {className: "miniList adding"}, listName)),
                (!props.canRetry && React.createElement('button', {className: "customButton",
                    onClick: toggleEditing}, "Edit")),
                (props.canRetry && React.createElement('button', {className: "customButton",
                    onClick: retryAddingList}, RETRY_UNICODE)),
                React.createElement('button', {className: "customButton"}, "x")
            )
        );
    }
}

function ListOfLists() {
    const [demoMode, setDemoMode] = React.useState(false);
    const [canRetryGetLists, setCanRetryGetlists] = React.useState(false);

    const [allListsName, setAllListsName] = React.useState("Loading");
    const [listToAdd, setListToAdd] = React.useState("");

    //This could be split up, but it shouldnt change, so its fine if its in a dictionary.
    //We use this for the user_id, and to have user_name in allListsName.
    //Needs to be a state because its set with a request.
    const [userData, setUserData] = React.useState({});
    const [adding, setAdding] = React.useState(false);

    //Asynchronous states
    const [allLists, setAllLists] = React.useState([]);
    const [asyncDeleteList, setAsyncDeleteList] = React.useState([]);
    const [currentTempId, setCurrentTempId] = React.useState(0);
    const [updateHappened, setUpdateHappened] = React.useState(false);

    //Asynchronous variables
    var tempAllLists = [];
    var tempDeleteList = [];
    var getting = false;
    //This one is here because state doesn't update immediately and I want to use it in initialGetLists.
    var tempUserData = {};

    //Alert
    const [alertValue, setAlertValue] = React.useState("");
    const [displayAlert, setDisplayAlert] = React.useState(false);
    const [alertType, setAlertType] = React.useState("ok");

    //Get user data
    React.useEffect(() => {
        initialGetLists()
    }, []);

    React.useEffect(() => {
        tempAllLists = allLists;
        tempDeleteList = asyncDeleteList;
        if (updateHappened == true) {
            setUpdateHappened(false);
        }
    });

    function initialGetLists() {
        if (!getting) {
            getting = true;
            const getUserDataRequest = getRequest("users?token=" + localStorage.getItem("token"));
            getUserDataRequest.then(function(result) {
                getting = false;

                tempUserData = result.d
                setUserData(tempUserData);

                //Second request
                const getAllListsForUser = getRequest("tasklists?token=" + localStorage.getItem("token"));
                getAllListsForUser.then(function(result) {
                    getting = false;
                    var username = tempUserData["user_name"];

                    username = username[0].toUpperCase() + username.substring(1);
                    setAllListsName(username + "'s lists");

                    tempAllLists = result.d
                    setAllLists(tempAllLists);
                }).catch(function(errorData) {
                    getting = false;
                    initialErrorHandler(errorData)
                });

            }).catch(function(errorData) {
                getting = false;
                initialErrorHandler(errorData)
            });
        }
    }

    function initialErrorHandler(errorData) {
        if (errorData.d.errors[0] == "not authenticated for this request") {
            setAlertType("yes/no");
            setAlertValue("You arent logged in. Continue in demo mode?");
            setDisplayAlert(true);
        } else if (errorData.d.errors[0] == "a connection error occured") {
            setAlertType("ok");
            setAlertValue("There appears to be a connection problem, please try again in a bit");
            setDisplayAlert(true);

            setAllListsName("Couldn't get your lists. Please press the retry button in a bit");

            setCanRetryGetlists(true);
        } else {
            listOfListsErrorHandler(errorData);
        }
    }

    function listOfListsErrorHandler(errorData) {
        var error_type = errorData.d.error_type;
        var error = errorData.d.errors[0];
        console.log("error_type: " + error_type, "\nerror: " +  error);

        switch (error) {
            case "a connection error occured":
                setAlertType("ok");
                setAlertValue("There appears to be a connection problem, please try again in a bit");
                setDisplayAlert(true);
                break;
        }
    }

    function handleAlertButtons(buttonValue) {
        setDisplayAlert(false);
        if (alertType == "yes/no") {
            //Demo mode is currently the only yes/no type alert
            if(buttonValue) {
                setDemoMode(true);
                if (localStorage.getItem("allLists")) {
                    tempAllLists = JSON.parse(localStorage.getItem("allLists"))
                    setAllLists(tempAllLists);
                    if (tempAllLists.length > 0) {
                        var newCurrentTempId = tempAllLists[tempAllLists.length - 1].list_id + 1;
                        setCurrentTempId(newCurrentTempId);
                    }

                }
                setAllListsName("Demo mode");

                setAlertType("ok");
                setAlertValue("Now in demo mode. Do not use sensitive information in this mode. " + 
                                "Data is stored in your browser, so its not secure.");
                setDisplayAlert(true);
            } else {
                window.location.href = '/';
            }
        }
    }

    function checkEnterListOfLists(e) {
        if (e.keyCode == ENTER_KEYCODE || e.charCode == ENTER_KEYCODE) {
            e.preventDefault();
            addList();
        }
    }

    function changeListToAdd(e) {
        e.preventDefault();
        if(!displayAlert){
            setListToAdd(e.target.value);
        }
    }

    function toggleAdding() {
        setListToAdd("");
        setAdding(!adding);
    }

    function addList() {
        if (displayAlert) {
            return;
        }

        if (!listToAdd) {
            setAlertType("ok");
            setAlertValue("You cant add an empty list");
            setDisplayAlert(true);
            return;
        }
        
        if (demoMode) {
            tempAllLists.push({list_id: currentTempId, list_name: listToAdd});
            localStorage.setItem("allLists", JSON.stringify(tempAllLists));
            setAllLists(tempAllLists);
            setListToAdd("");
            setCurrentTempId(currentTempId + 1);
        } else {
            var localTempId = "temp" + currentTempId;
            tempAllLists.push({list_id: localTempId, list_name: listToAdd});
            setAllLists(tempAllLists);

            const addListRequest = postRequest("tasklists", {"list_name": listToAdd,
                                                "token": localStorage.getItem("token")});
            addListRequest.then(function(result) {
                var index = tempAllLists.findIndex(i => i.list_id == localTempId);
                tempAllLists[index]["list_id"] = result.d.list_id;
                
                if(tempAllLists[index]["canRetry"]) {
                    tempAllLists[index]["canRetry"] = false;
                }

                setAllLists(tempAllLists);
                setUpdateHappened(true);
            }).catch(function(errorData) {
                listOfListsErrorHandler(errorData);
                var index = tempAllLists.findIndex(i => i.list_id == localTempId);
                tempAllLists[index]["canRetry"] = true;

                setAllLists(tempAllLists);
                setUpdateHappened(true);
            });
            
            setCurrentTempId(currentTempId + 1);
            setListToAdd("");
        }
    }

    function retryAddList(temp_id) {
        var index = tempAllLists.findIndex(i => i.list_id == temp_id);
        var listToRetry = tempAllLists[index]
        var retryAddListRequest = postRequest("tasklists", {"list_name": listToRetry.list_name,
                                                            "token": localStorage.getItem("token")});
        retryAddListRequest.then(function(result) {
            listToRetry.list_id = result.d.list_id;
            listToRetry.canRetry = false;
            
            setAllLists(tempAllLists);
            setUpdateHappened(true);
        }).catch(function(errorData) {
            listOfListsErrorHandler(errorData)
        });
    }
    
    function deleteList(list_id) {
        var index = tempAllLists.findIndex(i => i.list_id == list_id);
    }

    function renderAllLists() {
        var lists = allLists.map((list) => {
            return (React.createElement(MiniList, {key: list["list_id"],
                                                    list_id: list["list_id"],
                                                    list_name: list["list_name"],
                                                    canRetry: list["canRetry"],
                                                    retryAddList: retryAddList}));
        });
        return lists;
    }

    function renderButton() {
        if (canRetryGetLists) {
            return (
                React.createElement('div', {className: "wideButton", onClick: initialGetLists}, "Retry")
            )
        }

        if (adding) {
            return (
                React.createElement('div', {className: "addListContainer"},
                    React.createElement(TextareaAutosize, {className: "addList", rows: 1, type: "text",
                        onChange: changeListToAdd, onKeyDown: checkEnterListOfLists, value: listToAdd}),
                    React.createElement('input',
                        {className: "customButton", type: "button", onClick: addList, value: "Add list"}
                    ),
                    React.createElement('button', {className: "customButton", onClick: toggleAdding}, "Done")
                )
            )
        }

        if (!adding) {
            return (
                React.createElement('div', {className: "wideButton", onClick: toggleAdding}, "Add list")
            );
        }
    }

    return (
        React.createElement('div', {className: "listOfLists"},
            React.createElement('div', {className: "listOfListsName"}, allListsName),
            renderAllLists(),
            renderButton(),
            (displayAlert && React.createElement(CustomAlert, {type: alertType, alert: alertValue, handleButtons: handleAlertButtons}))
        )
    );
}

ReactDOM.render(
    React.createElement(ListOfLists),
    document.getElementById('root')
);
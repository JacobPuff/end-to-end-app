import React from 'react';
import ReactDOM from 'react-dom';
import TextareaAutosize from 'react-autosize-textarea';
import {TaskList} from './tasklists.js';
import { getRequest, postRequest, deleteRequest, putRequest } from '../utilities.js';
import { CustomAlert } from './customAlert.js';

const ENTER_KEYCODE = 13;
const RETRY_UNICODE = "\u21BB"; //↻ 

function MiniList(props) {
    const [editing, setEditing] = React.useState(false);
    const [listName, setListName] = React.useState(props.list_name);
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
        setListName(props.list_name);
        setEditing(!editing);
    }

    function retryAddingList() {
        props.retryAddList(props.list_id);
    }

    function handleDelete() {
        props.deleteList(props.list_id);
    }

    function handleSave() {
        toggleEditing();
        props.updateList(props.list_id, listName);
    }

    function toSingleView() {
        props.toSingleView(props.list_id);
    }

    if (editing) {
        return (
            React.createElement('div', {className: "miniListContainer"},
                React.createElement(TextareaAutosize, {className: "editMiniList", defaultValue: props.list_name,
                    onChange: changeListName, onKeyDown: checkEnterMiniList}),
                React.createElement('button', {className: "customButton", onClick: handleSave}, "Save"),
                React.createElement('button', {className: "customButton", onClick: handleDelete}, "x")
            )
        )
    } else {
        return (
            React.createElement('div', {className: "miniListContainer"},
                (isAdded && React.createElement('div', {className: "miniList", onClick: toSingleView},
                    props.list_name)),
                (!isAdded && React.createElement('div', {className: "miniList adding"}, props.list_name)),
                (!props.canRetry && React.createElement('button', {className: "customButton",
                    onClick: toggleEditing}, "Edit")),
                (props.canRetry && React.createElement('button', {className: "customButton",
                    onClick: retryAddingList}, RETRY_UNICODE)),
                React.createElement('button', {className: "customButton", onClick: handleDelete}, "x")
            )
        );
    }
}

function ListOfLists() {
    const [demoMode, setDemoMode] = React.useState(false);
    const [canRetryGetLists, setCanRetryGetlists] = React.useState(false);
    const [gotten, setGotten] = React.useState(false);

    const [allListsName, setAllListsName] = React.useState("Loading");
    const [listToAdd, setListToAdd] = React.useState("");

    //This could be split up, but it doesnt change, so its fine if its in a dictionary.
    //We use this for the user_id, and to have user_name in allListsName.
    //Needs to be a state because its set with a request.
    const [userData, setUserData] = React.useState({});
    const [adding, setAdding] = React.useState(false);

    //For switching between single and all list views
    const [displayAllLists, setDisplayAllLists] = React.useState(true);
    //For single list view
    const [currentTasklistId, setCurrentTasklistId] = React.useState(null);
    const [currentTasklistName, setCurrentTasklistName] = React.useState("");

    //Asynchronous states
    const [allLists, setAllLists] = React.useState([]);
    const [asyncDeletedList, setAsyncDeletedList] = React.useState([]);
    const [currentTempId, setCurrentTempId] = React.useState(0);
    const [updateHappened, setUpdateHappened] = React.useState(false);

    //Asynchronous variables
    var tempAllLists = [];
    var tempDeletedList = [];
    var tempAlertList = [];
    var getting = false;

    //Alert
    const [alertValue, setAlertValue] = React.useState("");
    const [displayAlert, setDisplayAlert] = React.useState(false);
    const [alertType, setAlertType] = React.useState("ok");
    const [alertList, setAlertList] = React.useState([]);

    //Get user data
    React.useEffect(() => {
        initialGetLists()
    }, []);

    React.useEffect(() => {
        tempAllLists = allLists;
        tempDeletedList = asyncDeletedList;
        tempAlertList = alertList;
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

                var tempUserData = result.d
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
                    setGotten(true);
                    setCanRetryGetlists(false);
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
            tempAlertList.push({type: "yes/no", value: "You arent logged in. Continue in demo mode?"})
            setAlertList(tempAlertList);
            setDisplayAlert(true);
        } else if (errorData.d.errors[0] == "a connection error occured") {
            tempAlertList.push({type: "ok", value: "There appears to be a connection problem, please try again in a bit"})
            setAlertList(tempAlertList);
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
                tempAlertList.push({type: "ok", value: "There appears to be a connection problem, please try again in a bit"})
                setAlertList(tempAlertList);
                console.log(displayAlert);
                setDisplayAlert(true);
                break;
        }
    }

    //Handles alertList so that new alerts dont overwrite old ones.
    React.useEffect(() => {
        if (tempAlertList.length > 0) {
            var currentAlert = tempAlertList.shift();
            console.log(currentAlert);
            setAlertType(currentAlert.type);
            setAlertValue(currentAlert.value);
            if (displayAlert == false) {
                setDisplayAlert(true);
            }

        }
    }, [displayAlert])

    function handleAlertButtons(buttonValue) {
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

                tempAlertList.push({type: "ok",
                    value: "Now in demo mode. Do not use sensitive information in this mode. " + 
                    "Data is stored in your browser, so its not secure."})
                setAlertList(tempAlertList);
            } else {
                window.location.href = '/';
            }
        }
        setDisplayAlert(false);
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
            setDisplayAlert(false);
            return;
        }

        if (!listToAdd) {
            tempAlertList.push({type: "ok", value: "You cant add an empty list"})
            setAlertList(tempAlertList);
            setDisplayAlert(true);
            return;
        }
        
        if (demoMode) {
            tempAllLists.push({list_id: currentTempId, list_name: listToAdd});
            localStorage.setItem("allLists", JSON.stringify(tempAllLists));
            localStorage.setItem("tasksForList" + currentTempId, JSON.stringify([]));
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
    
    function updateList(list_id, list_name) {
        var index = tempAllLists.findIndex(i => i.list_id == list_id);
        var prevListName = tempAllLists[index].list_name;

        if(list_name == prevListName) {
            return;
        }

        tempAllLists[index].list_name = list_name;
        setAllLists(tempAllLists);
        setUpdateHappened(true);

        if (demoMode) {
            localStorage.setItem("allLists", JSON.stringify(tempAllLists));
            return;
        }
        const updateListNameRequest = putRequest("tasklists/" + list_id, {"list_name": list_name, "token": localStorage.getItem("token")});
        updateListNameRequest.catch(function(errorData) {
            console.log(prevListName)
            console.log(index)
            console.log(tempAllLists[index])
            tempAllLists[index].list_name = prevListName;
            console.log(tempAllLists[index])
            setAllLists(tempAllLists);
            setUpdateHappened(true);
            listOfListsErrorHandler(errorData);
        });
    }

    function deleteList(list_id) {
        var tempAllListsIndex = tempAllLists.findIndex(i => i.list_id == list_id);
        if (list_id[0] != "t" || tempAllLists[tempAllListsIndex]["canRetry"]) {
            // Needs [0] so deletedList isnt an array
            var deletedList = tempAllLists.splice(tempAllListsIndex, 1)[0];
            setAllLists(tempAllLists);
            setUpdateHappened(true);
        }

        if (list_id[0] != "t") {
            if (demoMode) {
                localStorage.setItem("allLists", JSON.stringify(tempAllLists));
                localStorage.removeItem("tasksForList" + deletedList.list_id);
                return;
            }

            tempDeletedList.push(deleteList);
            setAsyncDeletedList(tempDeletedList);

            const deleteListRequest = deleteRequest("tasklists/" + list_id, {"token": localStorage.getItem("token")});

            deleteListRequest.then(function() {
                var deletedIndex = tempDeletedList.findIndex(i => i.list_id == list_id);
                tempDeletedList.splice(deletedIndex, 1);
                setAsyncDeletedList(tempDeletedList);
            }).catch(function(errorData) {
                listOfListsErrorHandler(errorData);
                var deletedIndex = tempDeletedList.findIndex(i => i.list_id == list_id);
                tempDeletedList.splice(deletedIndex, 1);
                setAsyncDeletedList(tempDeletedList);
                tempAllLists.push(deletedList);
                tempAllLists.sort(sortLists);
                setAllLists(tempAllLists);
                setUpdateHappened(true);
            });
        }
    }

    function sortLists(a, b) {
        if(typeof(a.list_id) == "number" && typeof(b.list_id) == "number"){
            return a.list_id - b.list_id
        } else if (typeof(a.list_id) == "string" && typeof(b.list_id) == "number") {
            return 1
        } else if (typeof(a.list_id) == "number" && typeof(b.list_id) == "string"){
            return -1
        } else if (typeof(a.list_id) == "string" && typeof(b.list_id) == "string"){
            return a.list_id.substring(4) - b.list_id.substring(4)
        }
    }

    function toggleSingleOrAllListView(list_id) {
        if(displayAllLists) {
            setDisplayAllLists(false);
            setCurrentTasklistId(list_id);
            var listNameIndex = tempAllLists.findIndex(i => i.list_id == list_id)
            setCurrentTasklistName(tempAllLists[listNameIndex].list_name);
        } else {
            setDisplayAllLists(true);
        }
    }

    function renderAllLists() {
        var lists = allLists.map((list) => {
            return (React.createElement(MiniList, {key: list["list_id"],
                                                list_id: list["list_id"],
                                                list_name: list["list_name"],
                                                canRetry: list["canRetry"],
                                                retryAddList: retryAddList,
                                                updateList: updateList,
                                                deleteList: deleteList,
                                                toSingleView: toggleSingleOrAllListView}));
    });
        return lists;
    }

    function renderButton() {
        if (canRetryGetLists) {
            return (
                React.createElement('div', {className: "wideButton", onClick: initialGetLists}, "Retry")
            )
        }

        if (adding && (gotten || demoMode)) {
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

        if (!adding && (gotten || demoMode)) {
            return (
                React.createElement('div', {className: "wideButton", onClick: toggleAdding}, "Add list")
            );
        }
    }

    if (displayAllLists) {
        return (
            React.createElement('div', {className: "listOfLists"},
                React.createElement('div', {className: "listOfListsName"}, allListsName),
                renderAllLists(),
                renderButton(),
                (displayAlert && React.createElement(CustomAlert, {type: alertType, alert: alertValue, handleButtons: handleAlertButtons}))
            )
        );
    } else if (!displayAllLists) {
        return (
            React.createElement(TaskList, {list_id: currentTasklistId, list_name: currentTasklistName,
                handleBackButton: toggleSingleOrAllListView, demoMode: demoMode})
        );
    }
}

ReactDOM.render(
    React.createElement(ListOfLists),
    document.getElementById('root')
);
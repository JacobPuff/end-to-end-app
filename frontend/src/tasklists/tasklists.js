import React from 'react';
import TextareaAutosize from 'react-autosize-textarea';
import {postRequest, getRequest, putRequest, deleteRequest} from '../utilities.js';
import {CustomAlert} from './customAlert.js';

export {TaskList}

const ENTER_KEYCODE = 13;
const RETRY_UNICODE = "\u21BB"; //↻ 

function Task(props) {
    const [editing, setEditing] = React.useState(false);
    const [isUpdating, setIsUpdating] = React.useState(false);
    const [editedTaskName, setEditedTaskName] =  React.useState(props.data.task_name);

    React.useEffect(() => {
        if (props.data["task_id"][0] == "t") {
            setIsUpdating(true);
        }
        else {
            setIsUpdating(false);
        }
    }, [props.data["task_id"]]);

    function deleteTask() {
        props.deleteTask(props.data["task_id"]);
    }

    function changeEditState() {
        setEditing(props.data.task_name);
        setEditing(!editing);
    }

    function changeToEdit(e) {
        setEditedTaskName(e.target.value);
    }

    function changeDone(e) {
        props.updateTask(props.data["task_id"], {"task_done": e.target.checked});
    }

    function saveTask() {
        props.updateTask(props.data["task_id"], {"task_name": editedTaskName});
        changeEditState();
    }

    function retryAddTask() {
        props.retryAddTask(props.data["task_id"]);
    }

    function switchDisplay() {
        if (isUpdating) {
            return (
                React.createElement('div',
                    {className: "taskUpdating"},
                    React.createElement('div', {className: "taskName"},
                        props.data["task_name"]
                    ),
                    (!props.canRetry && React.createElement('input',
                        {className: "taskCheck", type: "checkbox", checked: props.data["task_done"],
                        onChange: (e) => {e.preventDefault();}}
                    )),
                    (props.canRetry && React.createElement('button',
                        {className: "customButton taskRetryButton", onClick: retryAddTask},
                        RETRY_UNICODE
                    )),
                    React.createElement('button', {className: "customButton", onClick: deleteTask}, "x"),
                )
            )
        }
        else if (editing == true) {
            return (
                React.createElement('div',
                    {className: "task"},
                    React.createElement('div', {className:"editContainer"},
                        React.createElement(TextareaAutosize,
                            {className: "editTask", rows: 1, defaultValue: props.data["task_name"], onChange: changeToEdit,
                            onKeyDown: (e) => {if(e.keyCode == ENTER_KEYCODE || e.charCode == ENTER_KEYCODE){saveTask()}}}
                        ),
                        React.createElement('input',
                            {className: "customButton", type: "button", onClick: saveTask, value: "Save"}
                        )
                    ),
                    React.createElement('input',
                        {className: "taskCheck", type: "checkbox", checked: props.data["task_done"], onChange: changeDone}
                    ),
                    React.createElement('button', {className: "customButton", onClick: deleteTask}, "x")
                )
            )
        }

        if (editing == false) {
            return (
                React.createElement('div',
                    {className: "task"},
                    React.createElement('div', {className: "taskName", onClick: changeEditState},
                        props.data["task_name"]
                    ),
                    React.createElement('input',
                        {className: "taskCheck", type: "checkbox", checked: props.data["task_done"], onChange: changeDone}
                    ),
                    React.createElement('button', {className: "customButton", onClick: deleteTask}, "x")
                )
            )
        }
    }

    return (
        switchDisplay()
    );
}

function TaskList(props) {
        //List
        const [listName, setListName] = React.useState(props.list_name)
        const [prevListName, setPrevListName] = React.useState(props.list_name);
        const [editingListName, setEditingListName] = React.useState(false);
        const [canRetryList, setCanRetryList] = React.useState(false);
        const [gotten, setGotten] = React.useState(false);

        const [currentAlert, setCurrentAlert] = React.useState("alert");
        const [displayAlert, setDisplayAlert] = React.useState(false);

        //Adding stuff
        const [adding, setAdding] = React.useState(false);
        const [addedChecked, setAddedChecked] = React.useState(false);
        const [taskToBeAdded, setTaskToBeAdded] = React.useState("")

        //Asynchronous task stuff
        const [tasks, setTasks] = React.useState([]);
        const [deleteList, setDeleteList] = React.useState([]);
        const [currentTempId, setCurrentTempId] = React.useState(0);
        const [updateHappened, setUpdateHappened] = React.useState(false);

        //temp vars for said task stuff
        var tempTasks = [];
        var tempDeleteList = [];
        var getting = false;

    //Get tasks
    React.useEffect(() => {
        initialGetTasks();
    }, []);

    function initialGetTasks(){
        if(!getting) {
            getting = true;
            //Not using prevListName because this one is needed almost immediately and Im not trusting react.
            var tempListName = listName;
            setListName(tempListName + " (loading)");

            const gettingTasks = getRequest("tasks?list_id=" + props.list_id + "&token=" + localStorage.getItem("token"));
            var successFunction = function(tasksGotten){
                setGotten(true);
                setListName(tempListName);

                setTasks(tasksGotten["d"]);
                getting = false;
                if (canRetryList) {
                    setCanRetryList(false);
                }
            }

            var rejectFunction = function(errorData) {
                tasklistErrorHandler(errorData)
                if (errorData["d"]["error_type"] == "connection_errors"){
                    getting = false;
                    setListName(tempListName);
                    setCanRetryList(true);
                }
            }

            gettingTasks.then(function(tasksGotten){
                successFunction(tasksGotten);
            }).catch(function(errorData){rejectFunction(errorData)});
        }
    }

    //Make tasks based on data
    function returnTasks() {
        const createTasks = tasks.map((task) => {
            return (React.createElement(Task, {key: task["task_id"], data: task, updateTask: updateTask,
                            deleteTask: deleteTask, retryAddTask: retryAddTask, canRetry: task["canRetry"]}))
        });
        return createTasks
    }

    //For asynchronous stuff.
    React.useEffect(() => {
        tempTasks = tasks;
        tempDeleteList = deleteList;
        if (updateHappened == true) {
            setUpdateHappened(false);
        }
    })

    function tasklistErrorHandler(errorData) {
        var error_type = errorData["d"]["error_type"];
        var error = errorData["d"]["errors"][0]
        console.log("error_type: " + error_type, "\nerror: ", error);
        
        switch(error) {
            case "a connection error occured":
                setCurrentAlert("There appears to be a connection problem, please try again in a bit");
                setDisplayAlert(true);
                break;
            case "not authenticated for this request":
                setCurrentAlert("You are not logged in, please log in and try again");
                setDisplayAlert(true);
                break;
        }
    }

    function addTask() {
        // Dont add more tasks if not logged in.
        if (displayAlert) {
            return;
        }
        if (taskToBeAdded) {
            var localTempId = currentTempId;
            tempTasks.push({task_id: "temp" + localTempId, list_id: props.list_id, task_name: taskToBeAdded, task_done: addedChecked});
            setTasks(tempTasks);

            var successFunction = function(newTask) {
                var index = tempTasks.findIndex(i => i.task_id == "temp" + localTempId)
                tempTasks[index]["task_id"] = newTask.d.task_id
                if (tempTasks[index]["canRetry"]){
                    tempTasks[index]["canRetry"] = false;
                }
                setTasks(tempTasks);
                setUpdateHappened(true);
            }

            var rejectFunction = function(errorData) {
                tasklistErrorHandler(errorData)
                if (errorData["d"]["error_type"] == "connection_errors") {
                    var index = tempTasks.findIndex(i => i.task_id == "temp" + localTempId)
                    tempTasks[index]["canRetry"] = true;
                    setTasks(tempTasks);
                    setUpdateHappened(true);
                }
            }
            
            const addingTask = postRequest("tasks", {list_id: props.list_id, task_name: taskToBeAdded,
                task_done: addedChecked, token: localStorage.getItem("token")});

            addingTask.then(function(newTask){
                successFunction(newTask);
            }).catch(function(errorData){rejectFunction(errorData)})

            setCurrentTempId(currentTempId + 1);
            setTaskToBeAdded("");
        }
        else {
            setCurrentAlert("You can't add an empty task")
            setDisplayAlert(true);
        }
    }

    function retryAddTask(tempId){
        var index = tempTasks.findIndex(i => i.task_id == tempId);
        var retryTask = tempTasks[index]
        const retryAddingTask = postRequest("tasks", {list_id: props.list_id, task_name: retryTask["task_name"],
                                        task_done: retryTask["task_done"], token: localStorage.getItem("token")})

        retryAddingTask.then(function(newTask){
            successFunction(newTask)
        }).catch(function(errorData){
            rejectFunction(errorData);
        })

        var successFunction = function(newTask) {
            //retryTask is a reference to the task in tempTasks
            retryTask["task_id"] = newTask.d.task_id
            retryTask["canRetry"] = false;
            setTasks(tempTasks);
            setUpdateHappened(true);
        }

        var rejectFunction = function(errorData) {
            tasklistErrorHandler(errorData)
        }
    }

    function updateTask(task_id, data) {
        var tempTasksIndex = tempTasks.findIndex(i => i.task_id == task_id)

        //Copy task instead of referencing it
        var preUpdateTask = {}
        preUpdateTask.task_id = tempTasks[tempTasksIndex].task_id
        preUpdateTask.task_name = tempTasks[tempTasksIndex].task_name;
        preUpdateTask.task_done = tempTasks[tempTasksIndex].task_done;

        var dataToUpdate = {}
        var updated = false
        
        var rejectFunction = function(errorData) {
            tasklistErrorHandler(errorData)
            //Recalculate index so that tasks that already exist on the server can be deleted
            //It will return a -1 instead of reverting the wrong task if the task was deleted
            var revertIndex = tempTasks.findIndex(i => i.task_id == task_id)
            if (revertIndex != -1) {
                tempTasks[revertIndex] = preUpdateTask;
                setTasks(tempTasks);
                setUpdateHappened(true);
            }
        }

        if (data["task_done"] != null) {
            tempTasks[tempTasksIndex]["task_done"] = data["task_done"]
            dataToUpdate["task_done"] = data["task_done"]
            updated = true;
        }
        if (data["task_name"] && data["task_name"] != tempTasks[tempTasksIndex]["task_name"]) {
            tempTasks[tempTasksIndex]["task_name"] = data["task_name"]
            dataToUpdate["task_name"] = data["task_name"]
            updated = true;
        }
        if (updated) {
            setTasks(tempTasks);
            setUpdateHappened(true);
            dataToUpdate["token"] = localStorage.getItem("token")
            var updatingTask = putRequest("tasks/" + task_id, dataToUpdate)
            updatingTask.catch(function(errorData){rejectFunction(errorData)});
        }
    }

    function deleteTask(task_id) {
        var tempTasksIndex = tempTasks.findIndex(i => i.task_id == task_id);

        if(task_id[0] != "t" || tempTasks[tempTasksIndex]["canRetry"]){
            var deletedTask = tempTasks.splice(tempTasksIndex, 1)[0];
            setTasks(tempTasks);
            setUpdateHappened(true);
        }

        if (task_id[0] != "t"){
            tempDeleteList.push(deletedTask);
            setDeleteList(tempDeleteList);

            const deletingTask = deleteRequest("tasks/" + task_id, {token: localStorage.getItem("token")});
            deletingTask.then(function(){
                successFunction()
            }).catch(function(errorData){rejectFunction(errorData)})
        }

        var successFunction = function() {
            var deleteIndex = tempDeleteList.findIndex(i=> i.task_id == task_id);
            tempDeleteList.splice(deleteIndex, 1)
            setDeleteList(tempDeleteList)
        }

        var rejectFunction = function(errorData) {
            tasklistErrorHandler(errorData)
            var deleteIndex = tempDeleteList.findIndex(i=> i.task_id == task_id);
            var reAddedTask = tempDeleteList[deleteIndex];
            tempDeleteList.splice(deleteIndex, 1);
            tempTasks.push(reAddedTask);

            tempTasks.sort(sortTasks);

            console.log(tempTasks);
            setTasks(tempTasks);
            setDeleteList(tempDeleteList);
            setUpdateHappened(true);
        }
    }

    function sortTasks(a, b) {
        if(typeof(a.task_id) == "number" && typeof(b.task_id) == "number"){
            return a.task_id - b.task_id
        } else if (typeof(a.task_id) == "string" && typeof(b.task_id) == "number") {
            return 1
        } else if (typeof(a.task_id) == "number" && typeof(b.task_id) == "string"){
            return -1
        } else if (typeof(a.task_id) == "string" && typeof(b.task_id) == "string"){
            return a.task_id.substring(4) - b.task_id.substring(4)
        }
    }

    function changeListName(e) {
        setListName(e.target.value)
    }

    function changedAddTask(e) {
        if(!displayAlert){
            setTaskToBeAdded(e.target.value);
        }
    }

    function toggleEditListName() {
        setPrevListName(listName);
        setEditingListName(!editingListName);
    }
    
    function toggleAddTaskField() {
        setAdding(!adding);
        setTaskToBeAdded("");
        setAddedChecked(false);
    }

    function saveListName() {
        if(listName && listName != prevListName) {
            const updateListName = putRequest("tasklists/" + props.list_id, {"list_name": listName,
                                            token: localStorage.getItem("token")});
            updateListName.catch(function(errorData){rejectFunction(errorData);})

            var rejectFunction = function(errorData){
                tasklistErrorHandler(errorData)
                setListName(prevListName);
            }
        } else {
            setListName(prevListName);
        }
    }

    function handleAlertButtons(value) {
        if(value){
            setDisplayAlert(false)
        }
    }

    function returnListName() {
        if (canRetryList) {
            return (
                React.createElement('div', {className: "listName"}, "Couldn't get tasks. Please press the retry button")
            )
        }
        else if(editingListName) {
            return (
                React.createElement(TextareaAutosize, {className: "editingListName", defaultValue: listName, onChange: changeListName,
                    onKeyDown: (e) => {if(e.keyCode == ENTER_KEYCODE || e.charCode == ENTER_KEYCODE){saveListName(); toggleEditListName();}}})
            )
        } else {
            return (
                React.createElement('div', {className: "listName", onClick: toggleEditListName}, listName)
            )
        }
    }

    function switchDisplay() {
        if (canRetryList) {
            return (
                React.createElement('div', {className: "wideButton", onClick: initialGetTasks}, "Retry")
            )
        }
        else if (adding == false && (gotten || props.demoMode)){
            return (
                React.createElement('div', {className: "wideButton", onClick: toggleAddTaskField}, "Add Tasks")
            )
        }
        else if (adding == true && (gotten || props.demoMode)){
            return (
                React.createElement('div', {className: "addTaskContainer"},
                    React.createElement(TextareaAutosize,
                        {className: "addTask", rows: 1, type: "text", onChange: changedAddTask, value: taskToBeAdded, onKeyDown: (e) => { 
                            if(e.keyCode == ENTER_KEYCODE || e.charCode == ENTER_KEYCODE){e.preventDefault(); addTask();}}}
                    ),
                    React.createElement('input',
                        {type: "checkbox", onClick: (e) => {setAddedChecked(e.target.checked)}}
                    ),
                    React.createElement('input',
                        {className: "customButton", type: "button", onClick: addTask, value: "Add Task"}
                    ),
                    React.createElement('input',
                        {className: "customButton", type: "button", onClick: toggleAddTaskField, value: "Done"}
                    )
                )
            )
        }
    }

    return (
        React.createElement('div',
            {className: "tasklist"},
            React.createElement('div', {className: "listNameContainer"},
                React.createElement('button', {className: "customButton backButton", onClick: props.handleBackButton},
                    "back"),
                returnListName(),
            ),
            returnTasks(),
            switchDisplay(),
            (displayAlert && React.createElement(CustomAlert,
                {type: "ok", alert: currentAlert, handleButtons: handleAlertButtons}
            ))
        )
        
    );
}

import React from 'react';
import ReactDOM from 'react-dom';
import TextareaAutosize from 'react-autosize-textarea';
import {postRequest, getRequest, putRequest, deleteRequest} from '../utilities.js';

const ENTER_KEYCODE = 13;

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
        // This gets annoying if you are deleting in bulk. Find a way to select for deletion at some point or something.
        //var shouldDelete = confirm("Are you sure you want to delete\n" + "\"" + props.data["task_name"] + "\"?")
        var shouldDelete = true;
        if (shouldDelete) {
            props.deleteTask(props.data["task_id"]);
        }
    }

    function changeEditState() {
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
                        {className: "customButton retryButton", onClick: retryAddTask},
                        "\u21BB"
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
                            {type: "button", onClick: saveTask, value: "Save"}
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
        const [adding, setAdding] = React.useState(false);
        const [addedChecked, setAddedChecked] = React.useState(false);
        const [tasks, setTasks] = React.useState([]);
        const [deleteList, setDeleteList] = React.useState([]);
        const [currentTempId, setCurrentTempId] = React.useState(0);
        const [updateHappened, setUpdateHappened] = React.useState(false);
        const [taskToBeAdded, setTaskToBeAdded] = React.useState("")
        var tempTasks = [];
        var tempDeleteList = [];

    //Get tasks
    React.useEffect(() => {
        initialGetTasks();
    }, []);

    function initialGetTasks(){
        const gettingTasks = getRequest("tasks?list_id=" + props.list_id + "&token=" + localStorage.getItem("token"));
        var successFunction = function(tasksGotten){
            setTasks(tasksGotten["d"]);
        }

        var rejectFunction = function(errorData) {
            console.log(errorData)
            console.log("error: " + errorData["d"]["errors"][0])
        }

        gettingTasks.then(function(tasksGotten){
            successFunction(tasksGotten);
        }).catch(function(errorData){rejectFunction(errorData)});
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
    React.useEffect(()=>{
        console.log("useEffect")
        tempTasks = tasks;
        tempDeleteList = deleteList;
        if (updateHappened == true) {
            setUpdateHappened(false);
        }
    })

    function addTask() {
        if (taskToBeAdded) {
            var localTempId = currentTempId;
            tempTasks.push({task_id: "temp" + localTempId, list_id: props.list_id, task_name: taskToBeAdded, task_done: addedChecked});
            setTasks(tempTasks);

            var successFunction = function(newTask) {
                var index = tempTasks.findIndex(i => i.task_id == "temp" + localTempId)
                //This if statement is here because you can currently delete tasks while they are being added.
                //It should be removed when that inevitably changes.
                tempTasks[index]["task_id"] = newTask.d.task_id
                if (tempTasks[index]["canRetry"]){
                    tempTasks[index]["canRetry"] = false;
                }
                setTasks(tempTasks);
                setUpdateHappened(true);
            }

            var rejectFunction = function(errorData) {
                console.log(errorData)
                console.log("error: " + errorData["d"]["errors"][0])
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
            alert("You can't add an empty task")
        }
    }
        
    /*
        preUpdateValues = [{task_id: 12, task_name: "balhblahsblashl"},
                            {task_id:34, task_done: false},
                            {task_id: 12, task_done: false}]

        Can use scope to get data needed in the success function.       Side note: Need to check that currentTempId won't break if state
                                                                        is not updated. (Get it? Its on the side.)
        promiseFunc(URL, Data, resolveData) {
            resolve([])
        }
        
        var localVar = neededData
        scopePromiseFunc(url, data).then(function(successData){ successFunction(successData)})
        successFunction(){ does whatever using localVar }
    */

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
            console.log(errorData)
            console.log("error: " + errorData["d"]["errors"][0])

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
        
        //A task should not be able to be deleted while its being added.
        //It should be able to be deleted if it could not be sent to the server.
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
            console.log("error: " + errorData["d"]["errors"][0])
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
            console.log(errorData)
            console.log("error: " + errorData["d"]["errors"][0])
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

    function changedAddTask(e) {
        setTaskToBeAdded(e.target.value);
    }
    
    function toggleAddTaskField() {
        setAdding(!adding);
        setTaskToBeAdded("");
        setAddedChecked(false);
    }

    function switchDisplay() {
        if (adding == false){
            return (
                React.createElement('div', {className: "wideButton", onClick: toggleAddTaskField},'Add Tasks')
            )
        }
        if (adding == true){
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

    return(
        React.createElement('div',
            {className: "tasklist"},
            React.createElement('div', {className: "listName"}, props.list_name),
            returnTasks(),
            switchDisplay()
        )
        
    );
}

ReactDOM.render(
    React.createElement(TaskList, {list_id: 22, list_name: "list1"}),
    document.getElementById('root')
);

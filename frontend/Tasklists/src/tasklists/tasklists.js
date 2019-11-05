import React from 'react';
import ReactDOM from 'react-dom';
import TextareaAutosize from 'react-autosize-textarea';
import {postRequest, getRequest, putRequest, deleteRequest} from '../utilities.js';

function Task(props) {
    const [editing, setEditing] = React.useState(false);
    const [isUpdating, setIsUpdating] = React.useState(false);
    var editedTaskName = props.data.task_name;

    function changeDone(e) {
        props.updateTask(props.data["task_id"], {"task_done": e.target.checked})
    }

    React.useEffect(() => {
        if (props.data["task_id"][0] == "t") {
            setIsUpdating(true)
        }
        else {
            setIsUpdating(false)
        }
    }, [props.data["task_id"]]);
//update text, set prop is updating, then when promise resolves, set it so that its not longer updating. Then it will be accessible again.
// Maybe save what the text was before, because then it can be set back to its previous value and be set to not updating.

    function deleteTask() {
        // This gets annoying if you are deleting in bulk. Find a way to select for deletion at some point or something.
        //var shouldDelete = confirm("Are you sure you want to delete\n" + "\"" + props.data["task_name"] + "\"?")
        var shouldDelete = true;
        if (shouldDelete) {
            props.deleteTask(props.data["task_id"])
        }
    }

    function changeEditState() {
        setEditing(!editing)
    }

    function changeToEdit(e) {
        editedTaskName = e.target.value
    }

    function saveTask() {
        props.updateTask(props.data["task_id"], {"task_name": editedTaskName})
        changeEditState()
    }

    function switchDisplay() {
        if (isUpdating) {
            return (
                React.createElement('div',
                    {className: "taskUpdating"},
                    React.createElement('div', {className: "taskName"},
                        props.data["task_name"]
                    ),
                    React.createElement('input',
                        {className: "taskCheck", type: "checkbox", checked: props.data["task_done"], onChange: (e) => {e.preventDefault();}}
                    ),
                    React.createElement('button', {className: "customButton", onClick: deleteTask}, "x"),
                    //This will probably be how I handle timeouts later, but for now I just want to get asynchronous stuff going.
                    //I don't know how I will get/set the prop at the moment
                    //React.createElement('button', {className: "customButton", visiblity: props.canReload})
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
                            onKeyDown: (e) => {if(e.keyCode == 13 || e.charCode == 13){saveTask()}}}
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
        var tempDeleteList = [];
        var tempTasks = [];
        //If the checkbox is marked after the text is added, it will think its an empty task.
        //If the "Add Task" button is pressed, it won't clear the textarea.
        var taskToBeAdded = "";

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
            return (React.createElement(Task, {key: task["task_id"], data: task, updateTask: updateTask, deleteTask: deleteTask}))
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
            tempTasks.push({task_id: "temp" + currentTempId, list_id: props.list_id, task_name: taskToBeAdded, task_done: addedChecked});
            setTasks(tempTasks);

            var successFunction = function(newTask) {
                var index = tempTasks.findIndex(i => i.task_id == "temp" + currentTempId)
                if(index != -1) {
                    //A task should not be able to be deleted while its updating. It should be able to be deleted if it could not be sent to the server.
                    tempTasks[index]["task_id"] = newTask.d.task_id
                    setTasks(tempTasks);
                    setUpdateHappened(true);
                }
            }

            var rejectFunction = function(errorData) {
                console.log(errorData)
                console.log("error: " + errorData["d"]["errors"][0])
                if (errorData["d"]["error_type"] == "connection_errors") {
                    
                }
            }
            
            console.log(currentTempId)
            const addingTask = postRequest("tasks", {list_id: props.list_id, task_name: taskToBeAdded,
                task_done: addedChecked, token: localStorage.getItem("token")});

            addingTask.then(function(newTask){
                successFunction(newTask);
            }).catch(function(errorData){rejectFunction(errorData)})

            setCurrentTempId(currentTempId + 1);
            taskToBeAdded = "";
        }
        else {
            alert("You can't add an empty task")
        }
    }

    function updateTask(task_id, data) {
        const updatedTasksData = tasks.slice(0)
        const index = updatedTasksData.findIndex(i => i.task_id == task_id)
        var dataToUpdate = {}
        var updated = false
        
        var successFunction = function() {
            if (data["task_done"] != null) {
                updatedTasksData[index]["task_done"] = data["task_done"]
            }
            if (data["task_name"]) {
                updatedTasksData[index]["task_name"] = data["task_name"]
            }
            setTasks(updatedTasksData);
        }
        
        var rejectFunction = function(errorData) {
            console.log(errorData)
            console.log("error: " + errorData["d"]["errors"][0])
        }

        if (data["task_done"] != null) {
            dataToUpdate["task_done"] = data["task_done"]
            updated = true;
        }
        if (data["task_name"] && data["task_name"] != updatedTasksData[index]["task_name"]) {
            dataToUpdate["task_name"] = data["task_name"]
            updated = true;
        }
        if (updated) {
            dataToUpdate["token"] = localStorage.getItem("token")
            var updatingTask = putRequest("tasks/" + task_id, dataToUpdate)
            updatingTask.then(function(){
                successFunction()
            }).catch(function(errorData){rejectFunction(errorData)});
        }
    }

    function deleteTask(task_id) {
        var tempTasksIndex = tempTasks.findIndex(i => i.task_id == task_id);
        var deletedTask = tempTasks.splice(tempTasksIndex, 1)[0];
        setTasks(tempTasks);
        setUpdateHappened(true);

        if (task_id[0] != "t"){
            tempDeleteList.push(deletedTask);
            setDeleteList(tempDeleteList);

            const deletingTask = deleteRequest("tasks/" + task_id, {token: localStorage.getItem("token")});
            deletingTask.then(function(){
                successFunction()
            }).catch(function(errorData){rejectFunction(errorData)})
        }

        var successFunction = function() {
            tempDeleteList.splice(index, 1)
            setDeleteList(tempDeleteList)
        }

        var rejectFunction = function(errorData) {
            console.log("error: " + errorData["d"]["errors"][0])
            var index = tempDeleteList.findIndex(i=> i.task_id == task_id);
            var reAddedTask = tempDeleteList[index];
            tempDeleteList.splice(index, 1);
            tempTasks.splice(tempTasksIndex, 0, reAddedTask);

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

    function changedAddTask(e) {
        taskToBeAdded = e.target.value
    }
    
    function toggleAddTaskField() {
        setAdding(!adding);
        taskToBeAdded = "";
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
                        {className: "addTask", rows: 1, type: "text", onChange: changedAddTask, onKeyDown: (e) => { 
                            if(e.keyCode == 13 || e.charCode == 13){e.preventDefault(); e.target.value = ""; addTask()}}}
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

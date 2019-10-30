import React from 'react';
import ReactDOM from 'react-dom';
import {postRequest, getRequest, putRequest, deleteRequest} from '../utilities.js';

function Task(props) {
    const [editing, setEditing] = React.useState(false)
    //editedTaskName might be able to just be a variable because its in a function component now.
    const [editedTaskName, setEditedTaskName] = React.useState(props.data["task_name"]);
    const [isUpdating, setIsUpdating] = React.useState(false)

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
    }, [props.data]);
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
        setEditedTaskName(e.target.value)
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
                    React.createElement('button', {className: "customButton", onClick: () => {console.log(props.data["task_id"])}}, "x")
                )
            )
        }
        else if (editing == true) {
            return (
                React.createElement('div',
                    {className: "task"},
                    React.createElement('div', {className:"editContainer"},
                        React.createElement('textarea',
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
        const [taskToBeAdded, setTaskToBeAdded] = React.useState("");
        const [addedChecked, setAddedChecked] = React.useState(false);
        const [tasks, setTasks] = React.useState([]);
        const [gotten, setGotten] = React.useState(false);
        const [currentTempId, setCurrentTempId] = React.useState(0);

    //Get tasks
    function initialGetTasks(){
        const gettingTasks = getRequest("tasks?list_id=" + props.list_id + "&token=" + localStorage.getItem("token"));
        var successFunction = function(tasksGotten){
            setTasks(tasksGotten["d"]);
            setGotten(true);
        }
        gettingTasks.then(function(tasksGotten){
            successFunction(tasksGotten);
        });
    }

    //Make tasks based on data
    function returnTasks() {
        React.useEffect(() => {
            if (gotten == false) {
                initialGetTasks();
            }
        });
        
        const createTasks = tasks.map((task) => {
            return (React.createElement(Task, {key: task["task_id"], data: task, updateTask: updateTask,
                                                deleteTask: deleteTask, isUpdating: (task.task_id[0] == "t")}))
        });
        return createTasks
    }
    
    function changedAddTask(e) {
        setTaskToBeAdded(e.target.value)
    }

    function addTaskView() {
        if (adding == false){
            return (
                React.createElement('div', {className: "addTasksButton", onClick: toggleAddTaskField},'Add Tasks')
            )
        }
        if (adding == true){
            return (
                React.createElement('div', {className: "addTaskContainer"},
                    React.createElement('textarea',
                        {className: "addTask", rows: 1, type: "text", onChange: changedAddTask, onKeyDown: (e) => { 
                            if(e.keyCode == 13 || e.charCode == 13){e.preventDefault(); addTask()}}, value: taskToBeAdded}
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

    function toggleAddTaskField() {
        setAdding(!adding);
        setTaskToBeAdded("");
        setAddedChecked(false);
    }

    function addTask() {
        if (taskToBeAdded) {
            var updatedTasksData = tasks.slice(0);
            updatedTasksData.push({task_id: "temp" + currentTempId, list_id: props.list_id, task_name: taskToBeAdded, task_done: addedChecked});
            setTasks(updatedTasksData);
            setTaskToBeAdded("");

            var successFunction = function(newTask) {
                var index = updatedTasksData.findIndex(i => i.task_id == "temp" + currentTempId)
                updatedTasksData[index]["task_id"] = newTask.d.task_id
                console.log(updatedTasksData)
                setTasks(updatedTasksData);
            }

            var rejectFunction = function(errorData) {
                console.log(errorData)
                console.log("error: " + errorData)
            }
            
            console.log(currentTempId)
            const addingTask = postRequest("tasks", {list_id: props.list_id, task_name: taskToBeAdded,
                task_done: addedChecked, token: localStorage.getItem("token")});

            addingTask.then(function(newTask){
                successFunction(newTask);
            }).catch(function(errorData){rejectFunction(errorData)})
            setCurrentTempId(currentTempId + 1);
        }
        else {
            alert("You can't add an empty task")
        }
    }


    /*
        Tasklist-
            state
            addTask()-
                bar()
                Promise.then((foo) => {bar(foo)})
    */  


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
        var successFunction = function() {
            const updatedTasksData = tasks.slice(0)
            const index = updatedTasksData.findIndex(i => i.task_id == task_id);
            updatedTasksData.splice(index, 1);
            setTasks(updatedTasksData)
            
        }

        var rejectFunction = function(errorData) {
            console.log("error: " + errorData["d"]["errors"][0])
        }
        const deletingTask = deleteRequest("tasks/" + task_id, {token: localStorage.getItem("token")});
        deletingTask.then(function(){
            successFunction()
        }).catch(function(errorData){rejectFunction(errorData)})
    }

    return(
        React.createElement('div',
            {className: "tasklist"},
            React.createElement('div', {className: "listName"}, props.list_name),
            returnTasks(),
            addTaskView()
        )
        
    );
}

ReactDOM.render(
    React.createElement(TaskList, {list_id: 22, list_name: "list1"}),
    document.getElementById('root')
);

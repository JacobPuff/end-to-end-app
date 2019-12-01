import React from 'react';
import ReactDOM from 'react-dom';
import {getRequest, validateEmail, putRequest, deleteRequest} from './utilities.js';

const ENTER_KEYCODE = 13;

function UserProfile() {
    const [loggedIn, setLoggedIn] = React.useState(false);
    const [deleting, setDeleting] = React.useState(false);

    const [user_id, setUser_id] = React.useState();
    const [prevUser_name, setPrevUser_name] = React.useState("");
    const [prevUser_email, setPrevUser_email] = React.useState("");
    const [user_name, setUser_name] = React.useState("");
    const [user_email, setUser_email] = React.useState("");
    const [old_pass, setOld_pass] = React.useState("");
    const [new_pass, setNew_pass] = React.useState("");
    const [new_passAgain, setNew_passAgain] = React.useState("");

    const [inputNameState, setInputNameState] = React.useState("Loading");
    const [messageValue, setMessageValue] = React.useState("just a sec");
    const [sendingRequest, setSendingRequest] = React.useState(false);

    const [displayError, setDisplayError] = React.useState(false);
    const [errorValue, setErrorValue] = React.useState("error: this is shown before being set")

    const [displaySuccess, setDisplaySuccess] = React.useState(false);
    const [successValue, setSuccessValue] = React.useState("success: or is it? because this is shown before being set")

    React.useEffect(()=>{
        const getUserRequest = getRequest("users?token=" + localStorage.getItem("token"));
        getUserRequest.then(function(userData) {
            setLoggedIn(true);
            setInputNameState("Your profile");

            setUser_id(userData.d.user_id);
            setUser_name(userData.d.user_name);
            setUser_email(userData.d.user_email);

            setPrevUser_name(userData.d.user_name);
            setPrevUser_email(userData.d.user_email);
        }).catch(function(errorData) {
            userProfileErrorHandler(errorData);
        });
    },[]);

    function userProfileErrorHandler(errorData) {
        var error_type = errorData.d.error_type;
        var error = errorData.d.errors[0];
        console.log("error_type: " + error_type, "\nerror: " +  error);

        switch (error) {
            case "a connection error occured":
                if (loggedIn) {
                    setErrorValue("a connection error occured. please try again in a bit");
                    setDisplayError(true);
                } else {
                    setInputNameState("a connection error occured");
                    setMessageValue("please try again in a bit");
                }
                break;
            case "not authenticated for this request":
                setLoggedIn(false);
                setInputNameState("Not logged in");
                setMessageValue("Gotta be logged in to edit your account.");
                break;
            case "username already in use":
                setErrorValue("error: username already in use");
                setDisplayError(true);
                break;
            case "email already in use":
                setErrorValue("error: email already in use");
                setDisplayError(true);
                break;
            case "old_pass didnt match":
                setErrorValue("error: current password is incorrect");
                setDisplayError(true);
                return;

        }
    }

    function checkEnter(e) {
        if (e.keyCode == ENTER_KEYCODE || e.charCode == ENTER_KEYCODE) {
            handleSave();
            return;
        }
    }

    function handleInputs(e) {
        e.preventDefault();

        switch (e.target.placeholder) {
            case "username":
                setUser_name(e.target.value);
                break;
            case "email":
                setUser_email(e.target.value);
                break;
            case "current password":
                setOld_pass(e.target.value);
                break;
            case "new password":
                setNew_pass(e.target.value);
                break;
            case "new password again":
                setNew_passAgain(e.target.value);
                break;
        }
    }

    function changeDeleting() {
        setDisplayError(false);
        setDisplaySuccess(false);

        if(!deleting) {
            setInputNameState("Are you sure you want to delete your account?");
            setMessageValue("You wont be able to get it back.");
        }
        setDeleting(!deleting);
    }

    function handleDelete() {
        setDisplayError(false);
        setDisplaySuccess(false);
        if(!sendingRequest) {
            setSendingRequest(true);
            var deleteUserRequest = deleteRequest("users/" + user_id, {"token": localStorage.getItem("token")});
            deleteUserRequest.then(function() {
                setSendingRequest(false);
                setInputNameState("Deleted user");
                setMessageValue("It has been done.");

                localStorage.removeItem("localLastActive");
                localStorage.removeItem("token");

                setLoggedIn(false);
                setDeleting(false);
            }).catch(function(errorData) {
                setSendingRequest(false);
                userProfileErrorHandler(errorData);
            });
        }
    }

    function handleSave() {
        setDisplayError(false);
        setDisplaySuccess(false);
        var dataToUpdate = {};

        if (!user_name) {
            setErrorValue("error: you gotta have a username");
            setDisplayError(true);
            return;
        } else if (user_name != prevUser_name) {
            if (!validateEmail(user_name)) {
                dataToUpdate["user_name"] = user_name;
            } else {
                setErrorValue("error: you put your email in the wrong field");
                setDisplayError(true);
                return;
            }
        }

        if (!user_email) {
            setErrorValue("error: you gotta have an email");
            setDisplayError(true);
            return;
        } else if (user_email != prevUser_email) {
            if (validateEmail(user_email)) {
                dataToUpdate["user_email"] = user_email;
            } else {
                setErrorValue("error: valid email is required");
                setDisplayError(true);
                return;
            }
        }

        if ((old_pass || new_pass || new_passAgain) && !(old_pass && new_pass && new_passAgain)){
            setErrorValue("error: all password fields are required to update password");
            setDisplayError(true);
            return;
        } else if (new_pass != new_passAgain) {
            setErrorValue("error: passwords dont match");
            setDisplayError(true);
            return;
        } else if (new_pass && new_pass.length < 8) {
            setErrorValue("error: password must be at least 8 characters");
            setDisplayError(true);
            return;
        } else {
            dataToUpdate["old_pass"] = old_pass;
            dataToUpdate["user_pass"] = new_pass;
        }
// change comment again + 2 to have gitlab run build-js job
        if (dataToUpdate["user_name"] ||
            dataToUpdate["user_email"] || 
            dataToUpdate["user_pass"]) {
            if(!sendingRequest) {
                setSendingRequest(true);
                dataToUpdate["token"] = localStorage.getItem("token");
                const updateUserProfileRequest = putRequest("users/" + user_id, dataToUpdate);
                
                updateUserProfileRequest.then(function() {
                    setSendingRequest(false);
                    if (dataToUpdate["user_pass"]) {
                        setOld_pass("");
                        setNew_pass("");
                        setNew_passAgain("");
                    }
                    if (dataToUpdate["user_email"]) {
                        setSuccessValue("successfully saved changes! Check your new email to verify and change it!")
                    } else {
                        setSuccessValue("successfully saved your changes");
                    }
                    setDisplaySuccess(true);
                }).catch(function(errorData) {
                    setSendingRequest(false);
                    userProfileErrorHandler(errorData);
                });
            }
        } else {
            setSuccessValue("successfully saved no changes");
            setDisplaySuccess(true);
        }
    }

    if (loggedIn && !deleting) {
        return (
            React.createElement('div', {className: "centerContainer userProfile"},
                React.createElement('h1', {className: "inputName"}, inputNameState),
                React.createElement('p', {}, "you can edit your profile here!"),
                React.createElement('div', {className: "customInputContainer"},
                    React.createElement('h2', {className: "singleInputName"}, "Username: "),
                    React.createElement('input', {className: "customInput", placeholder: "username", onChange: handleInputs,
                            onKeyDown: checkEnter, value: user_name})
                ),
                React.createElement('div', {className: "customInputContainer"},
                    React.createElement('h2', {className: "singleInputName"}, "Email: "),
                    React.createElement('input', {className: "customInput", placeholder: "email", onChange: handleInputs,
                            onKeyDown: checkEnter, value: user_email})
                ),
                React.createElement('h2', {className: "inputName"}, "Password"),
                React.createElement('div', {className: "customInputContainer"},
                    React.createElement('h2', {className: "singleInputName"}, "Current password: "),
                    React.createElement('input', {className: "customInput", placeholder: "current password", onChange: handleInputs,
                            onKeyDown: checkEnter, value: old_pass, type: "password"})
                ),
                React.createElement('div', {className: "customInputContainer"},
                    React.createElement('h2', {className: "singleInputName"}, "New password: "),
                    React.createElement('input', {className: "customInput", placeholder: "new password", onChange: handleInputs,
                            onKeyDown: checkEnter, value: new_pass, type: "password"})
                ),
                React.createElement('div', {className: "customInputContainer"},
                    React.createElement('h2', {className: "singleInputName"}, "New password again: "),
                    React.createElement('input', {className: "customInput", placeholder: "new password again", onChange: handleInputs,
                            onKeyDown: checkEnter, value: new_passAgain, type: "password"})
                ),

                (displayError && React.createElement('p', {className: "error"}, errorValue)),
                (displaySuccess && React.createElement('p', {className: "success"}, successValue)),

                React.createElement('div', {className: "inputButtonContainer"},
                    React.createElement('button', {className:"inputButton miniButton", onClick: handleSave},
                        "Save"),
                    React.createElement('button', {className: "inputButton red deleteButton", onClick: () => {changeDeleting();}},
                        "Delete account")
                )
            )
        );
    } else if (loggedIn && deleting) {
        return (
            React.createElement('div', {className: "centerContainer"},
                React.createElement('h1', {className: "inputName"}, inputNameState),
                React.createElement('p', {}, messageValue),

                (displayError && React.createElement('p', {className: "error"}, errorValue)),
                (displaySuccess && React.createElement('p', {className: "success"}, successValue)),

                React.createElement('div', {className: "inputButtonContainer"},
                    React.createElement('button', {className:"inputButton red miniButton", onClick: handleDelete},
                        "Yes"),
                    React.createElement('button', {className:"inputButton miniButton", onClick: changeDeleting},
                        "No")
                )
            )
        );
    } else {
        return (
            React.createElement('div', {className: "centerContainer"},
                React.createElement('h1', {className: "inputName"}, inputNameState),
                React.createElement('p', {}, messageValue)
            )
        );
    }
}

ReactDOM.render(
    React.createElement(UserProfile),
    document.getElementById('root')
);
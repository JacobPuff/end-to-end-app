import React from 'react';
import ReactDOM from 'react-dom';
import { putRequest, postRequest } from './utilities';

const ENTER_KEYCODE = 13;

function PasswordReset() {
    const [resetToken, setResetToken] = React.useState(new URL(window.location.href).searchParams.get("resettoken"));
    const [smolMessage, setSmolMessage] = React.useState(true);
    const [expired, setExpired] = React.useState(false);
    const [newPassword, setNewPassword] = React.useState("");
    const [newPasswordAgain, setNewPasswordAgain] = React.useState("");

    const [inputNameState, setInputNameState] = React.useState("Loading");
    const [messageValue, setMessageValue] = React.useState("just a sec");
    const [actionWasTaken, setActionWasTaken] = React.useState(false);
    const [sendingRequest, setSendingRequest] = React.useState(false);

    const [displayError, setDisplayError] = React.useState(false);
    const [errorValue, setErrorValue] = React.useState(false);
    
    const [displaySuccess, setDisplaySuccess] = React.useState(false);
    const [successValue, setSuccessValue] = React.useState(false);

    React.useEffect(() => {
        if (resetToken) {
            const resetTokenValidRequest = putRequest("resettokens", {"resettoken": resetToken});
            resetTokenValidRequest.catch(function(errorData){
                var error = errorData.d.errors[0]
                if (error == "user_pass is required") {
                    setSmolMessage(false);
                    setInputNameState("Reset password");
                    setMessageValue("You can reset your password here");
                } else if (error == "reset token is expired") {
                    setExpired(true);
                    setInputNameState("Reset password");
                    setMessageValue("Your password reset email is expired, but you can send yourself another one!");
                } else {
                    setInputNameState("Reset password");
                    passwordResetErrorHandler(errorData);
                }
            })
        } else {
            setInputNameState("Reset Password");
            setMessageValue("You need to use the link in your password reset email for this page to work.")
        }
    }, []);

    function passwordResetErrorHandler(errorData) {
        var error_type = errorData.d.error_type;
        var error = errorData.d.errors[0];
        console.log("error_type: ", error_type, "\nerror: ", error);

        switch (error) {
            case "reset token doesnt exist":
                setMessageValue("The token used doesnt exist. If you used the link in your password reset email, you've already reset your password");
                break;
            default:
                setErrorValue("error: " + error);
                setDisplayError(true);
                break;
        }
    }
    
    function checkEnter(e) {
        if (e.keyCode == ENTER_KEYCODE || e.charCode == ENTER_KEYCODE) {
            handlePasswordSubmit();
        }
    }

    function handleInputChanges(e) {
        e.preventDefault();

        switch (e.target.placeholder) {
            case "new password":
                setNewPassword(e.target.value);
                break;
            case "new password again":
                setNewPasswordAgain(e.target.value);
                break;
        }
    }

    function handlePasswordSubmit() {
        setDisplayError(false);

        if (newPassword.length < 8) {
            setErrorValue("error: password must be at least 8 characters");
            setDisplayError(true);
            return;
        } else if (newPassword != newPasswordAgain) {
            setErrorValue("error: passwords dont match");
            setDisplayError(true);
            return;
        }

        if (!sendingRequest) {
            setSendingRequest(true);
            const resetPasswordRequest = putRequest("resettokens", {"user_pass": newPassword,
                                                                    "resettoken": resetToken});
            resetPasswordRequest.then(function() {
                setSendingRequest(false);
                setActionWasTaken(true);
                setInputNameState("Reset password!");
                setMessageValue("Successfully reset your password! Now that wasnt that hard, was it?");
            }).catch(function(errorData) {
                setSendingRequest(false);
                passwordResetErrorHandler(errorData);
            });
        }
    }

    function handleSendPasswordResetEmail() {
        if (!sendingRequest) {
            setSendingRequest(true);
            const passwordResetEmailRequest = postRequest("resettokens", {"resettoken": resetToken});
            passwordResetEmailRequest.then(function() {
                setSendingRequest(false);
                setActionWasTaken(true);
                setSuccessValue("success! you have been sent a password reset email");
                setDisplaySuccess(true);
            }).catch(function(errorData){
                setSendingRequest(false);
                passwordResetErrorHandler(errorData);
            });
        }
    }

    return (
        React.createElement('div', {className: "centerContainer"},
            React.createElement('h1', {className: "inputName"}, inputNameState),
            React.createElement('p', {}, messageValue),
            ((!smolMessage && !actionWasTaken) && React.createElement('input', {className: "customInput", placeholder: "new password",
                    type: "password", onChange: handleInputChanges, onKeyDown: checkEnter})),
            ((!smolMessage && !actionWasTaken) && React.createElement('input', {className: "customInput", placeholder: "new password again",
                    type: "password", onChange: handleInputChanges, onKeyDown: checkEnter})),
            
            (displayError && React.createElement('p', {className: "error"}, errorValue)),
            (displaySuccess && React.createElement('p', {className: "success"}, successValue)),

            React.createElement('div', {className: "inputButtonContainer"},
                React.createElement('div', {className: "inputButton miniButton", onClick: () => {window.location.href = "/"}},
                    "To home page"),
                ((!smolMessage && !actionWasTaken) && React.createElement('div', {className: "inputButton",
                    onClick: handlePasswordSubmit}, "Submit")),
                ((expired && !actionWasTaken) && React.createElement('div', {className: "inputButton",
                    onClick: handleSendPasswordResetEmail},"Send another!"))
            )
        )
    );
}

ReactDOM.render(
    React.createElement(PasswordReset),
    document.getElementById('root')
);
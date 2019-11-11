import React from 'react';

export {CustomAlert}

function CustomAlert(props) {
    function getButtons() {
        switch(props.type) {
            case "yes/no":
                return (
                    React.createElement("div", {className: "alertButtonContainer"},
                        React.createElement("div", {className: "customButton", onClick: () =>{props.handleButtons(true)}}, "yes"),
                        React.createElement("div", {className: "customRedButton", onClick: () =>{props.handleButtons(false)}}, "no")
                    )
                )
            case "ok/cancel":
            return (
                React.createElement("div", {className: "alertButtonContainer"},
                    React.createElement("div", {className: "customButton", onClick: () =>{props.handleButtons(true)}}, "ok"),
                    React.createElement("div", {className: "customRedButton", onClick: () =>{props.handleButtons(false)}}, "cancel")
                )
            )
            case "ok":
                return (
                    React.createElement("div", {className: "alertButtonContainer"},
                        React.createElement("div", {className: "customButton", onClick: () =>{props.handleButtons(true)}}, "ok")
                    )
                )
        }
    }
    return (
        React.createElement("div", {className: "alertBackgroundContainer"}, 
            React.createElement("div", {className: "customAlert"},
                React.createElement("span", {className: "customAlertText"}, props.alert),
                getButtons()
            )
        )
    )
}
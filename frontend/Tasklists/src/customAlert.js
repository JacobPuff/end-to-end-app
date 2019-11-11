import React from 'react';

export {CustomAlert}

function CustomAlert(props) {
    function singleButton(returnValue, name){
        return(
            React.createElement("div", 
                {className: returnValue ? "customButton" : "customRedButton",
                onClick: () =>{props.handleButtons(returnValue)}},
                name
            )
        )
        
    }

    function getButtons() {
        switch(props.type) {
            case "yes/no":
                return (
                    React.createElement("div", {className: "alertButtonContainer"},
                        singleButton(true, "yes"),
                        singleButton(false, "no")
                    )
                )
            case "ok/cancel":
            return (
                React.createElement("div", {className: "alertButtonContainer"},
                    singleButton(true, "ok"),
                    singleButton(false, "cancel")
                )
            )
            case "ok":
                return (
                    React.createElement("div", {className: "alertButtonContainer"},
                        singleButton(true, "ok")
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
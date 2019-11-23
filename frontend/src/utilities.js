export {getRequest, postRequest, putRequest, deleteRequest, validateEmail}

function getRequest(name) {
    return new Promise(function(resolve, reject) {
        setTimeout(function(){
        var request = new XMLHttpRequest();
        request.onreadystatechange = function() {
            if (request.readyState !== 4 || request.status !== 200) {
                if((request.status == 504 || request.status == 0) && request.readyState == 4) {
                    reject({"d": {error_type: "connection_errors", errors:["a connection error occured"]}})
                }
                else if (request.readyState == 4 && request.status !== 200) {
                    reject(JSON.parse(request.responseText));
                }
                return;
            }
            var responseBody = JSON.parse(request.responseText);
            resolve(responseBody)
        };
        request.timeout = 5000;
        request.open("GET", '/api/' + name, true);
        request.setRequestHeader("Content-type", "application/json");
        request.send();

        }, 1000)
    });
}

function postRequest(name, data) {
    return new Promise(function(resolve, reject) {
        setTimeout(function(){
        var request = new XMLHttpRequest();
        request.onreadystatechange = function() {
            if (request.readyState !== 4 || request.status !== 200) {
                if((request.status == 504 || request.status == 0) && request.readyState == 4) {
                    reject({"d": {error_type: "connection_errors", errors:["a connection error occured"]}})
                }
                else if (request.readyState == 4 && request.status !== 200) {
                    reject(JSON.parse(request.responseText));
                }
                return;
            }
            var responseBody = JSON.parse(request.responseText);
            resolve(responseBody)
        };
        request.timeout = 5000;
        request.open("POST", '/api/' + name, true);
        request.setRequestHeader("Content-type", "application/json");
        request.send(JSON.stringify(data));
        
        }, 1000)
    });
}

function putRequest(name, data) {
    return new Promise(function(resolve, reject) {
        setTimeout(function(){
        var request = new XMLHttpRequest();
        request.onreadystatechange = function() {
            if (request.readyState !== 4 || request.status !== 200) {
                if((request.status == 504 || request.status == 0) && request.readyState == 4) {
                    reject({"d": {error_type: "connection_errors", errors:["a connection error occured"]}})
                }
                else if (request.readyState == 4 && request.status !== 200) {
                    reject(JSON.parse(request.responseText));
                }
                return;
            }
            var responseBody = JSON.parse(request.responseText);
            resolve(responseBody)
        };
        request.timeout = 5000;
        request.open("PUT", '/api/' + name, true);
        request.setRequestHeader("Content-type", "application/json");
        request.send(JSON.stringify(data));

        }, 1000)
    });
}

function deleteRequest(name, data) {
    return new Promise(function(resolve, reject) {
        setTimeout(function(){
        var request = new XMLHttpRequest();
        request.onreadystatechange = function() {
            if (request.readyState !== 4 || request.status !== 200) {
                if((request.status == 504 || request.status == 0) && request.readyState == 4) {
                    reject({"d": {error_type: "connection_errors", errors:["a connection error occured"]}})
                }
                else if (request.readyState == 4 && request.status !== 200) {
                    reject(JSON.parse(request.responseText));
                }
                return;
            }
            var responseBody = JSON.parse(request.responseText);
            resolve(responseBody)
        };
        request.timeout = 5000;
        request.open("DELETE", '/api/' + name, true);
        request.setRequestHeader("Content-type", "application/json");
        request.send(JSON.stringify(data));

        }, 1000)
    });
}

function validateEmail(mail) {
    if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(mail)) {
        return (true)
    }
    return (false)
}
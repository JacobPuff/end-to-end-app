var app = angular.module('mainApp', ['ui.router']);
var user = "Null";
app.component('displayBox', {
    bindings: {
    },
    controllerAs: 'displayCtrl',
    controller: function(msgService){
        var me = this;
        window.db = me;
        me.messageCache = msgService.getCache();
    },
    template: `
        <p ng-repeat="message in displayCtrl.messageCache.messages">{{message.user}}: {{message.msg}}</p>
        `
});

app.service('userService', function($http, $q){
    var me = this;
    var userCache = {users:[]};
    var currentGet = undefined;
    me.sendUsername = function(username){
        return $http.post("/flask/users", username).then(
            function (response){
                return response.data.d;
            },

            function(error){
                console.log("Error in user service", error);
            });
    }
    me.getUsers = function(){
        var defer = $q.defer();
        if(currentGet === undefined) {
            $http.get("/flask/users",{}).then(
                function(response){
                    console.log("Got Users!")
                    userCache.users = response.data.d;
                    currentGet = undefined;
                    defer.resolve(userCache.users);
                },

                function(error){
                    console.log("Error in userget service", error);
                    currentGet = undefined;
                    defer.reject(error);
                }
            );
            currentGet = defer.promise;
        }
        return currentGet;
    }
    me.getCache = function(){
        return userCache
    }
    me.poller_for_get = setInterval(me.getUsers, 3000);
})

app.service('msgService', function($http, $q){
    var me = this;
    var messageCache = {messages:[]};
    var currentGet = undefined;
    me.sendMessage = function(messageData){
        return $http.post("/flask/messages",messageData).then(
            function(response){
                return response.data.d;
            },
            
            function(error){
                console.log("Error in send service", error);
                return error;
        });
    };
    me.getMessages = function(){
        var defer = $q.defer();
        if (currentGet === undefined) {
            $http.get("/flask/messages",{}).then(
                function(response){
                    console.log("Got Messages!")
                    messageCache.messages = response.data.d;
                    currentGet = undefined;
                    defer.resolve(messageCache.messages);
                },

                function(error){
                    console.log("Error in get service", error);
                    currentGet = undefined;
                    defer.reject(error);
                }
            );
            currentGet = defer.promise;
        }
        return currentGet;
    }

    me.getCache = function(){
        return messageCache;
    }

    me.poller_for_get = setInterval(me.getMessages, 3000);

});

app.component('messageBox', {
    bindings: {
    },
    controllerAs: 'msgCtrl',
    controller: function(msgService){
        var me = this;
        me.msgSubmit = function() {
            if(me.msg != ""){
                msgService.sendMessage({user:user, msg:me.msg})
                me.msg = "";
            }
        }
    },
    template: `
        <input placeholder="Send a message!" class="msgInput" ng-model="msgCtrl.msg" ng-keypress="$event.keyCode === 13 && msgCtrl.msgSubmit()"></input>
    `
});

app.component('usernameBox', {
    bindings: {
    },
    controllerAs: 'usernameCtrl',
    controller: function(msgService, userService) {
        var me = this;
        me.showUsername = true;
        me.showContainer = false;
        me.userSubmit = function() {
            if(me.username != ""){
                user = me.username;
                me.showUsername = false;
                me.showContainer = true;
                msgService.sendMessage({user:"Bot", msg:"Welcome!"});
                userService.sendUsername(user);
            }
        }
    },
    template: `
        <p class="userPrompt" ng-show="usernameCtrl.showUsername">Enter Username</p>
        <input class="userInput" ng-show="usernameCtrl.showUsername" ng-model="usernameCtrl.username" ng-keypress="$event.keyCode === 13 && usernameCtrl.userSubmit()"></input>
        <div class="container" ng-show="usernameCtrl.showContainer">
                <display-box></display-box>
                <message-box></message-box>
                <user-box></user-box>
        </div>
    `
});

app.component('userBox', {
    bindings: {
    },
    controllerAs: 'userCtrl',
    controller: function(userService) {
        var me = this;
        me.userDisplay = function() {
            me.users = [];
            me.user = userService.getCache();
        }
    },
    template: `
            <div class="users">
                <p ng-repeat="user in userCtrl.users">{{user}}</p>
            </div>
        `
})
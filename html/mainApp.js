var app = angular.module('mainApp', []);
app.controller('mainCtrl', function(){
    var me = this;
    me.projectPosts = projectPosts;
    me.displayPopUpToggle = true;
    me.displayPopUp = function(){
        me.displayPopUpToggle = !me.displayPopUpToggle
    }
})
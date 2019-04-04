var app = angular.module('mainApp', []);
app.controller('mainCtrl', function(){
    var me = this;
    me.projectPosts = projectPosts;
    me.udemyPosts = udemyPosts;
    me.displayPopUpToggle = true;
    me.displayPopUp = function(){
        me.displayPopUpToggle = !me.displayPopUpToggle
    }
})
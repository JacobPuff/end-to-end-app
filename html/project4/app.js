var app = angular.module('myApp', []);

app.component('parent', {
    bindings: {
    },
    controllerAs: "parent",
    controller: function (){

    },
    template: ``
});

app.component('child', {
    bindings: {
    },
    controllerAs: "child",
    controller: function(){
        var me = this;
        me.foo = Math.floor(Math.random() * 6);
        me.getRandom = function(){
            me.noun = "";
            me.verb = "";
            me.foo = Math.floor(Math.random() * 6);
            me.showStr = false;
            me.showError = false;
        }
        me.list = ['/project4/temp0.html','/project4/temp1.html','/project4/temp2.html','/project4/temp3.html','/project4/temp4.html','/project4/temp5.html'];
        me.showStr = false;
        me.showError = false;
        me.showSwitch = function(){
           if(me.noun && me.verb){
                me.tempnoun = me.noun;
                me.tempverb = me.verb;
                me.showStr = true;
                me.showError = false;
                console.log(me.foo);
            } else {
                me.showError = true;
                me.showStr = false;
            }
        }
    },
    template: '<div ng-include="child.list[child.foo]"></div>'
            
});
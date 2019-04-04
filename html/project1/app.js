
var app = angular.module("metroids",[
    'ui.router'
]);
app.config(function($stateProvider, $urlRouterProvider){
    $urlRouterProvider.otherwise("/main");
    $stateProvider
    .state('main', {
        url:'/main', 
        template:'<main></main>',
        controller: function() {
            return;
        }
    }) 
    .state('metroiding', {
        url:'/metroiding', 
        template:'<metroiding></metroiding+>',
        controller: function() {
            return;
        }
    }) 
});
app.component('helloWorld',{
    bindings: {
        newName: '@'
    },
    controllerAs: 'helloCtrl',
    template:'<div class="hello">Hello {{ helloCtrl.newName }}</div>'
});

app.component('main',{
    
    bindings: {    
    },
    controller: function($state){
        this.newPage=function(){
            $state.go('metroiding');
        };
    },
    controllerAs: 'mainCtrl',
    template:'<div class="mainsh">'+
    'main'+
    '<buttoning new-state="metroiding" label="Go to Metroiding"></buttoning>'+
    '</div>'
});

app.component('metroiding',{
    bindings: {
    },
    controllerAs: 'metroidingCtrl',
     template:'<div class="metroidingas">'+
        'metroiding'+
        '<buttoning new-state="main" label="Go to Main"></buttoning>'+
        '</div>'
});

app.component('buttoning', {
    bindings: {
        newState: '@',  
        label: '@'
    },
    controller:function($state){
        this.newPage=function(){
               $state.go(this.newState);
        };
    },
    controllerAs: 'buttonCtrl',
    template:  '<div class="buttonsr">'+
        '<button ng-click="buttonCtrl.newPage()">{{ buttonCtrl.label }}</button>'+
        '</div>'
    
        
    });

var app = angular.module("NOWAI",[
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
});

app.component ('buttoninsg', {
    bindings: {
    },
    controller:function(moreService){
      var me = this;
      me.showthingsMaybe = false;
      me.stuff = [];
      me.showthings = function(){
        me.foo = moreService.getMore();
        me.foo.then(
          function(response){
            me.showthingsMaybe = true;
            me.stuff = response.data.d;
            console.log("got that response");
            console.log(me.stuff);
          },
          function(error){
            console.log("AAAAAAH THINGS ARE BURRNING AND ON FIRE WERE ALL GOING TO DIE IN DEATH DAEJALK");
          }
        );
      }
    },
    controllerAs:'button',
    template:'<div class="Show" ng-click="button.showthings()">sh9w</div>'+
      '<div ng-show="button.showthingsMaybe">'+
      '<div ng-repeat="thing in button.stuff" class="Outline"><div class="Flopple">{{thing.thing_id}}</div><div class="Subject">{{thing.stuff}}</div><div class="Body">{{thing.value}}</div>'+
      '</div>'
});
app.component ('main',{
    bindings: {
    },
    controller:function(){
      var me = this;
    
    },
    controllerAs:'main',
    template:'<posts></posts>'
    //template:'<posts></posts> <buttoninsg></buttoninsg>'
});

app.component ('posts',{
    bindings: {
    },
    controller:function(postService){
      var me = this;
      me.posts = [];

      me.newPostAndSubmit = 'New Post';
      me.shownewPostInput = false;
      me.showSubmitError = false;
      me.newPostButton = function(){
        if(me.newPostAndSubmit == 'New Post'){
          me.newPostBody = '';
          me.newPostSubject = ''
        }
        else if(me.newPostAndSubmit == 'submit'){
          if(me.newPostBody != '' && me.newPostSubject != ''){
            postService.addPost(null,me.newPostSubject,me.newPostBody).then(function(reolution){
              postService.getPostsByParent(null).then(function(resiolution){
                me.posts = resiolution;
              })
            });
            me.showSubmitError = false;
          }else {
            me.showSubmitError = true;
          }
        }
        if(me.showSubmitError == false){
          me.newPostAndSubmit = (me.newPostAndSubmit == 'New Post') ? 'submit' : 'New Post';
          me.shownewPostInput = !me.shownewPostInput;
        }
      }

      me.cancel = function(){
        me.newPostAndSubmit = 'New Post';
        me.shownewPostInput = false;
        me.showSubmitError = false;
      }

      me.deleteChild = function(child) {
        console.log('In deleteChild of root');
        var childPost = me.posts.indexOf(child);
        postService.deletePost(child.post_id).then(function(response){
          if(response == null) {
            if (childPost != -1) {
              me.posts.splice(childPost, 1);
            }
          }
        });
      }

      postService.getPostsByParent(null).then(function(result){
        me.posts = result;
      });
    },
    controllerAs:'postsCtrl',
    template:'<div><post ng-repeat="post in postsCtrl.posts" postid="post.post_id" parentdelete="postsCtrl.deleteChild"></post></div>'+
            '<h2><div  ng-show="postsCtrl.shownewPostInput">'+
          'Subject: <input type="text" ng-model="postsCtrl.newPostSubject"></input>'+
          'Message: <input type="text" ng-model="postsCtrl.newPostBody"></input>'+
        '</div>'+
        '<div ng-click="postsCtrl.cancel()" class="Show" ng-show="postsCtrl.shownewPostInput">cancel</div>'+
        '<div ng-click="postsCtrl.newPostButton()" class="Show">{{postsCtrl.newPostAndSubmit}}</div>'+
        '<p ng-show="postsCtrl.showSubmitError">Error: Cannot submit blank message or subject</p></h2>'
        
});

app.component('post',{
  bindings:{
    postid: '<',
    parentdelete: '<'
  },
 controller:function(userService, postService){
    var me = this; 
    
    me.post = undefined;
    me.user = undefined;
    me.showDelete = false;
    me.children = [];

    postService.getPostByid(me.postid).then(function(result) {
      me.post = result;
      userService.getUserByid(me.post.poster).then(function(result){
        me.user = result;
        if(me.post.poster == userService.currentUser){
          me.showDelete = true;
        }
      });
      postService.getPostsByParent(me.postid).then(function(result){
        me.children = result;
      });
    });

    
    
    me.comments = function(){
      if(me.children.length > 1){
        return (me.children.length + ' ' + 'comments');
      }else if(me.children.length == 1){
        return (me.children.length + ' ' + 'comment');
      }
      return 'No comments';
    }
    
    me.bodyToggleSymbol = '+';
    me.showBody = false;
    me.bodyToggle = function(){
      me.showBody = !me.showBody;
      me.bodyToggleSymbol = (me.bodyToggleSymbol == '+') ? '-' : '+';
    }
    me.replyAndSubmit = 'reply';
    me.showReplyInput = false;
    me.showSubmitError = false;
    me.replyButton = function(){
      if(me.replyAndSubmit == 'reply'){
        me.replyBody = '';
        me.replySubject = 'Re: ' + me.post.subject; 
      }else if(me.replyAndSubmit == 'submit'){
        
        if( me.replyBody != '' && me.replySubject != ''){
          postService.addPost(me.postid,me.replySubject,me.replyBody).then(function(result){
            postService.getPostsByParent(me.postid).then(function(posts){me.children = posts;});
          });
          me.showSubmitError = false;
        }else {
          me.showSubmitError = true;
        }
      }
      if(me.showSubmitError == false) {
        me.replyAndSubmit = (me.replyAndSubmit == 'reply') ? 'submit' : 'reply';
        me.showReplyInput = !me.showReplyInput;
      }
    }
    
    me.deleteButton = function() {
      console.log('In deleteButton of postId: ' + me.postid)
      me.parentdelete(me.post);
    }
    
    me.deleteChild = function(child) {
      console.log('In deleteChild of postId: ' + me.postid)
      var childPost = me.children.indexOf(child);
      postService.deletePost(child.post_id).then(function(response){
        if(response == null) {
          if (childPost != -1) {
            me.children.splice(childPost, 1);
          }
        }
      });
    }

    me.cancel = function() {
      me.replyAndSubmit = 'reply';
      me.showReplyInput = false;
      me.showSubmitError = false;
    }
  },
  controllerAs:'postCtrl',
  template: '<div class="post">'+
      '<div class="Outline">'+
        '<div class="Flopple">{{ postCtrl.user.username || \'Error: No username available\'}} posted:</div>'+
        '<div class="Subject"><div class="Show" ng-click="postCtrl.bodyToggle()"> {{postCtrl.bodyToggleSymbol}} </div> Subject: {{postCtrl.post.subject}}</div>'+
        '<div class="Body" ng-show="postCtrl.showBody">{{postCtrl.post.body}}</div>'+
        '<p>{{postCtrl.comments()}}</p>'+
        '<div  ng-show="postCtrl.showReplyInput">'+
          'Subject: <input type="text" ng-model="postCtrl.replySubject"></input>'+
          'Message: <input type="text" ng-model="postCtrl.replyBody"></input>'+
        '</div>'+
        '<div ng-click="postCtrl.cancel()" class="Show" ng-show="postCtrl.showReplyInput">cancel</div>'+
        '<div ng-click="postCtrl.replyButton()" class="Show">{{postCtrl.replyAndSubmit}}<p ng-show="postCtrl.showSubmitError">Error: Cannot submit blank message or subject</p></div>'+
        '<div ng-click="postCtrl.deleteButton()" ng-show="postCtrl.showDelete" class="Show">delete</div>'+
        '<post ng-repeat="subpost in postCtrl.children" postid="subpost.post_id" parentdelete="postCtrl.deleteChild"></post>'+
      '</div>'+
    '</div>'
});

app.service('userService', function($http, $q){
  var me = this;
  me.users = [];
  me.currentUser = null;

  var findUser = function(userId) {
      var result = undefined;
      me.users.forEach(function(item){
        if (item.user_id == userId){
          result = item;
        }
      })
      return result;
  }

  this.getUserByid = function(needle){
    if (me.users.length > 0){
      var deferred = $q.defer();
      deferred.resolve(findUser(needle));
      return deferred.promise;
    }
    else {
      return $http.get("http://jacob.squizzlezig.com/api/users").then(
        function(response){
          me.users = response.data.d;
          return findUser(needle);
        },function(error){console.log('death')})
    }
  }

  me.getUserByid(1).then(function(ghhf){me.currentUser = ghhf.user_id});
})

app.service('postService', function(userService, $http, $q){
  var me = this;
  me.postData = [];

  var findPost = function(needle) {
    var result = undefined;
    me.postData.forEach(function(foo){
        if(foo.post_id == needle){
        result = foo;
        }
    })
    return result;
  }

  var findParent = function(needle) {
    var result = [];
    me.postData.forEach(function(foo){
        if(foo.parent == needle){
        result.push(foo);
        }
    })
    return result;
  }

  this.getPostByid = function(needle){
    if(me.postData.length > 0) {
      var deferred = $q.defer();
      deferred.resolve(findPost(needle));
      return deferred.promise;
    }
    else {
      return $http.get("http://jacob.squizzlezig.com/api/posts").then(
        function(response){
          me.postData = response.data.d;
          return findPost(needle);
        }, function(error){return []})
    }
  }

  this.getPostsByParent = function(parent){
    if(me.postData.length > 0) {
      var deferred = $q.defer();
      deferred.resolve(findParent(parent));
      return deferred.promise;
    }
    else {
      return $http.get("http://jacob.squizzlezig.com/api/posts").then(
        function(response){
          me.postData = response.data.d;
          return findParent(parent);
        }, function(error){return []})
    }
  }

  this.deletePost = function(postId){
    return $http.delete("http://jacob.squizzlezig.com/api/posts/" + postId).then(
      function(response){
        if(response.data.d == null){
            var thing = me.postData.indexOf(findPost(postId)); 
            if(thing != -1){
              me.postData.splice(thing,1);
              console.log("spliced!");
            }
        }else {
          editPost = findPost(postId);
          editPost.subject = response.data.d.subject;
          editPost.body = response.data.d.body;
        }
        return response.data.d;
      }
    )
  }
  

  this.addPost = function(newParent,newSubject,newBody){
    var newPost = {
      poster:userService.currentUser,
      parent:newParent,
      subject:newSubject,
      body:newBody
    }
    return $http.post("http://jacob.squizzlezig.com/api/posts",newPost).then(
      function(response){
        me.postData.push(response.data.d);
        return response.data.d;
      },
      function(error){
        console.log("error posting");
      }
    )
  }
})

app.service('moreService',function($http){

  this.getMore = function(){
    return $http.get("http://jacob.squizzlezig.com/api/more")
  }

})
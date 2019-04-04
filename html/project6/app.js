var canvas = document.getElementById('myCanvas');
var canvasContext = canvas.getContext('2d');
const crowdedRadius = 30;
const localRadius = 70;
var boids = [];
var toRadians = Math.PI/180;
var frameSkip = false;
var spriteSheet0 = new Image();
spriteSheet0.src = 'spriteSheet0.png';
var spriteSheet1 = new Image();
spriteSheet1.src = 'spriteSheet1.png';
var spriteSheetCounter = 0;
var currentSpriteSheet = spriteSheet0;
function boidClass(index){
    var me = this;
    me.index = index;
    me.speed = 1;
    me.size = 32;
    me.average = 0;
    me.acceleration = 0;
    me.x = Math.floor(Math.random() * 700);
    me.y = Math.floor(Math.random() * 700);
    me.turn = 0;
    me.rotation = Math.floor(Math.random() * 360);
    me.toRotate = null;
    me.destinationX = null;
    me.destinationY = null;
    me.colorCircle = function(centerX,centerY,radius,color) {
             canvasContext.strokeStyle = color;
             canvasContext.beginPath();
             canvasContext.arc(centerX,centerY,radius,0,Math.PI*2, false);
             canvasContext.stroke();
         }
    me.run = function(){
        me.turn = Math.floor((Math.random()*10) * (Math.PI/180));
        me.average = 0;
        me.local = [];
        boids.forEach(function(boid, index){
            if(index != me.index){
                if(inLocal(boid.x, boid.y, me.x, me.y, localRadius)){
                    me.local.push(boid);
                    me.average += boid.rotation;
                }
            }
        });
        me.average = Math.floor(me.average/me.local.length);
        for(var i = 0; i <= me.local.length - 1; i++){
            me.destinationX += me.local[i].x;
            me.destinationY += me.local[i].y;
        }
        me.local.forEach(function(boid){
            if(inLocal(boid.x, boid.y, me.x, me.y, crowdedRadius)){
                //This is the steering bit that has to do with the local group.
                /*
                    TODO
                    1. Boids need to turn towards the average direction of the rest of the group. -check, probably
                    2. If the Boids are to close it needs to turn away from the average position of all local Boids. -check, probably
                    3. Boids need to turn torwards the average position of local Boids.
                    4. 2 and 3 need certain "powers". If the Boid is really far then it has more power to steer towards the rest.
                    If its really close, then the Boid steers more away.

                    5. Determine how to set "power".
                */
                console.log("0")
                if(me.rotation < me.average){
                    me.rotation -= 5;
                }
                if(me.rotation > me.average){
                    me.rotation += 5;
                }
            } else {
                console.log("1")
                console.log(me.average)
                if(me.rotation < me.average){
                    me.rotation += 3;
                }
                if(me.rotation > me.average){
                    me.rotation -= 3;
                }
            }
        })
        //For random turning.
        //me.rotation += Math.floor(Math.random() * 2) - 1;
        if(me.rotation > 360) {
            me.rotation = 1;
        }
        if(me.rotation < 0) {
            me.rotation = 360;
        }
        me.x += Math.cos(me.rotation * toRadians)// * me.speed; what are these for?
        me.y += Math.sin(me.rotation * toRadians)// * me.speed;
        if(me.x > 732){
            me.x = -32;
        } else if(me.x < -32){
            me.x = 732;
        } else if(me.y > 732) {
            me.y = -32;
        } else if(me.y < -32) {
            me.y = 732;
        }
        drawBoid(me.x, me.y, me.size, me.rotation);
        if(window.devMode) {
            me.colorCircle(me.x, me.y, localRadius, 'white');
            me.colorCircle(me.x, me.y, crowdedRadius, 'red');
            me.colorCircle(me.x, me.y, 2, 'black');
            me.colorCircle(me.x, me.y, 1, 'green');
        }
    }
}

function drawBoid (x, y, size, rotation){
    canvasContext.save();
    canvasContext.translate(x, y);
    canvasContext.rotate(rotation * toRadians + 90 * toRadians);
    canvasContext.drawImage(currentSpriteSheet, 0, 0, size, size, -size/2, -size/2, size, size);
    canvasContext.restore();
}
function inLocal (boidX, boidY, mainX, mainY, radius){
    var dist = (boidX - mainX) * (boidX - mainX) + (boidY - mainY) * (boidY - mainY);
    return dist <= radius * radius;
}
window.onload = function(){
    for(var i = 0; i <= 50; i++){
        var rand = Math.floor(Math.random() * 100);
        if(rand == 7){
            boids[i] = new redBoidClass(i);
        } else {
            boids[i] = new boidClass(i);
        }
    }
    window.stop = false;
    window.devMode = false;
    document.addEventListener('keydown', keyPressed);
    setInterval(drawAll,1000/60);
}
function keyPressed(e) {
    if(e.keyCode == 68) {
        window.devMode = !window.devMode;
    }
    if(e.keyCode == 32) {
        window.stop = !window.stop;
    }
    if(e.keyCode == 70) {
        frameSkip = true;
        //frameSkip makes it so that I can skip 1 frame forward when paused
    }
}
function drawAll() {
    if (frameSkip == true || window.stop == false) {
        frameSkip = false;
        if(spriteSheetCounter == 7) {
            spriteSheetCounter = 0;
            if(currentSpriteSheet == spriteSheet0){
                currentSpriteSheet = spriteSheet1;
            } else {
                currentSpriteSheet = spriteSheet0;
            }
        } else {
            spriteSheetCounter += 1;
        }
        canvasContext.fillStyle = '#000';
        canvasContext.fillRect(0, 0, 1400, 700)
        boids.forEach(function (boid) {
            boid.run();
        });
    }
}
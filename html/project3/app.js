var c = document.getElementById("myCanvas");
var ctx = c.getContext("2d");
var dir = 'down';
var imageMap = {
    up: ['Images/up/m0.png','Images/up/m1.png','Images/up/m2.png','Images/up/m3.png'],
    down: ['Images/down/m0.png','Images/down/m1.png','Images/down/m2.png','Images/down/m3.png'],
    right: ['Images/right/m0.png','Images/right/m1.png','Images/right/m2.png','Images/right/m3.png'],
    left: ['Images/left/m0.png','Images/left/m1.png','Images/left/m2.png','Images/left/m3.png'],
    blocks: ['Images/b0.png','Images/b1.png','Images/b2.png','Images/b3.png','Images/b4.png','Images/b5.png'],
    chests: ['Images/c0.png','Images/c1.png','Images/c2.png','Images/c3.png','Images/c4.png','Images/coin5.png']
    }

var coin = new Image();
coin.src = imageMap['chests'][5];
var roomData = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ];
var map = {
    room: roomData,
    cols:31,
    rows:31,
    tsize:64,
    getTile: function(row,col){
        return roomData[row][col];
    },
    isSolidTileAtXY: function (x, y) {
            var col = Math.floor(x / this.tsize);
            var row = Math.floor(y / this.tsize);
            var tile = this.getTile(row,col);
            var chestCollide = false;
            chests.forEach(function(chest){
                if(col == chest.x && row == chest.y){
                    chestCollide = true;
                }
            })
            return tile == 1 || chestCollide == true;
        
    },
    getCol: function (x) {
        return Math.floor(x / this.tsize);
    },
    getRow: function (y) {
        return Math.floor(y / this.tsize);
    },
    getX: function (col) {
        return col * this.tsize;
    },
    getY: function (row) {
        return row * this.tsize;
    }

};
var deathImage = new Image();
deathImage.src = 'Images/death.png';
var playerx = 3*64;
var playery = 3*64;
var image = new Image();
image.src = imageMap[dir][0];
var player = {
    gold: 0,
    deathTimer: 0,
    death: false,
    img: image,
    width: 64,
    height: 64,
    draw: function() {
        if(this.deathTimer > 0 && this.deathTimer <= 70){
            this.deathTimer += 1;
            if(this.deathTimer >= 70){
                ctx.drawImage(deathImage,0,0,1024,640);
                ctx.font = "100px Arial";
                ctx.fillText('You Are Dead',200,290);
            }
            this.death = true;    
        }
        if(this.deathTimer <= 7){
        ctx.drawImage(this.img, playerx - camera.x, playery - camera.y, this.width, this.height);
        }
        
    },
    
    collide: function (dirx, diry) {
        var row, col;
        // -1 in right and bottom is because image ranges from 0..63
        // and not up to 64
        var left = playerx;
        var right = playerx + 64 - 1;
        var top = playery;
        var bottom = playery + 64 - 1;

        // check for collisions on sprite sides
        var collision =
            map.isSolidTileAtXY(left, top) ||
            map.isSolidTileAtXY(right, top) ||
            map.isSolidTileAtXY(right, bottom) ||
            map.isSolidTileAtXY(left, bottom);
        if (!collision) { return; }
        keyValid = false;
        if (diry > 0) {
            row = map.getRow(bottom);
            playery = -this.height + map.getY(row);
        }
        else if (diry < 0) {
            row = map.getRow(top);
            playery = this.height + map.getY(row);
        }
        else if (dirx > 0) {
            col = map.getCol(right);
            playerx = -this.width + map.getX(col);
        }
        else if (dirx < 0) {
            col = map.getCol(left);
            playerx = this.width + map.getX(col);
        }
    },
    move: function(dirx, diry) {
        // move hero
        playerx += dirx;
        playery += diry;

        

        // clamp values
        var maxX = map.room[0].length * map.tsize;
        var maxY = map.room.length * map.tsize;
        playerx = Math.max(0,Math.min(playerx, maxX-64));
        playery = Math.max(0,Math.min(playery, maxY-64));
	    this.collide(dirx, diry);
        camera.move();
    }


};
var renderFloors = function(x,y){
    for(row = Math.floor(y/map.tsize); row < Math.floor((y + 672)/map.tsize); row++){
        for(col = Math.floor(x/map.tsize); col < Math.floor((x + 1056)/map.tsize); col++){
            var blockImage = new Image();
            var tileGotten = map.getTile(row,col);
            if(tileGotten == 1){
                blockImage.src = imageMap.blocks[5];
            }
            if(tileGotten == 0){
                blockImage.src = imageMap.blocks[1];
            }
            ctx.drawImage(blockImage, col*64 - camera.x, row*64 - camera.y, 64, 64);
        }
    }
}
var Keyboard = {};

Keyboard.SPACE = 32;
Keyboard.LEFT = 37;
Keyboard.RIGHT = 39;
Keyboard.UP = 38;
Keyboard.DOWN = 40;
Keyboard._keys = {
};


Keyboard._onKeyDown = function (event) {
    var keyCode = event.keyCode;
    if (keyCode in this._keys) {
        event.preventDefault();
        this._keys[keyCode] = true;
    }
};

Keyboard._onKeyUp = function (event) {
    var keyCode = event.keyCode;
    if (keyCode in this._keys) {
        event.preventDefault();
        this._keys[keyCode] = false;
    }
};
Keyboard.listenForEvents = function (keys) {
    window.addEventListener('keydown', this._onKeyDown.bind(this));
    window.addEventListener('keyup', this._onKeyUp.bind(this));

    keys.forEach(function (key) {
        this._keys[key] = false;
    }.bind(this));
}

Keyboard.isDown = function (keyCode) {
    if (!keyCode in this._keys) {
        throw new Error('Keycode ' + keyCode + ' is not being listened to');
    }
    return this._keys[keyCode];
};



var Game = {
    update: function () {
    var dirx = 0;
        var diry = 0;
        var keyValid = false;

        // handle hero movement with arrow keys
        if (Keyboard.isDown(Keyboard.LEFT)==true) {
            dir = "left";
            dirx += -32; 
            keyValid = true;
        }
        if (Keyboard.isDown(Keyboard.RIGHT)==true) {
            dir = "right";
            dirx += 32; 
            keyValid = true;
        }
        if (Keyboard.isDown(Keyboard.UP)==true) {
            dir = "up";
            diry += -32; 
            keyValid = true;
        }
        if (Keyboard.isDown(Keyboard.DOWN)==true) {
            dir = "down";
            diry += 32; 
            keyValid = true;
        }
        
        if((dirx != 0 && diry == 0) || (dirx == 0 && diry != 0)){
            
            player.move(dirx, diry);
            if(keyValid == true && (dirx != 0 || diry != 0)){  
                if(image.src.endsWith('/m0.png')){
                    image.src = imageMap[dir][1];
                }else if(image.src.endsWith('/m1.png')){
                    image.src = imageMap[dir][2];
                }else if(image.src.endsWith('/m2.png')){
                    image.src = imageMap[dir][3];
                }else if(image.src.endsWith('/m3.png')){
                    image.src = imageMap[dir][0];
                }

            }
        }else if(image.src.endsWith('/m1.png')){
            image.src = imageMap[dir][2];
        }else if(image.src.endsWith('/m3.png')){
            image.src = imageMap[dir][0];
        }
    }
};

var camera = {
    x: 0,
    y: 0,
    minX: 1024/2-32,
    minY: 640/2-32,
    maxX: map.room[0].length*64 - 1024/2-32,
    maxY: map.room.length*64 - 640/2-32,
    inView: function(x, y){
       if(y > Math.floor(this.y/map.tsize) && y < Math.floor(this.y + 640/map.tsize)){
           if(x > Math.floor(this.x/map.tsize) && x < Math.floor(this.x + 1024/map.tsize)){
               return true;
           }
       }
       return false;
    },
    
    move: function(){
            if(playerx >= this.minX && playerx <= this.maxX){
                this.x = playerx - this.minX;
            }
            if(playery >= this.minY && playery <= this.maxY){
                this.y = playery - this.minY;
            }
    },
}
var rooms = [];
var roomAvailable = function(x,y,width,height){
    var roomsTest = true;

    rooms.forEach(function(room,index){
        if(roomsTest == false){
            return
        }
        if(x > room.x + width + 1 || x + width< room.x - 1 ||
           y > room.y + room.height + 1 || y + height <  room.y - 1){
            roomsTest = true;
        }else {
            roomsTest = false;
        }
    })
    return roomsTest
}
function makeRoom(x,y,width,height,arr){
    var me = this;
    me.x = x;
    me.y = y;
    me.bridge = false;
    me.chest = Math.round(Math.random());
    me.trap = Math.round(Math.random());
    me.width = width;
    me.height = height;
    if(roomAvailable(me.x,me.y,me.width,me.height)){
        for(var row = me.y; row < me.y + height; row ++){
            for(var col = me.x; col < me.x + width; col ++){
                roomData[row][col] = 0;
            }
        }
        if(me.chest == 1){
            if(me.trap == 1){
                new Chest(Math.floor(me.x+me.width/2),Math.floor(me.y+me.height/2),chests,2);
            }
            if(me.trap == 0){
                new Chest(Math.floor(me.x+me.width/2),Math.floor(me.y+me.height/2),chests,0);
            }
        }
    arr.push(me);
    }
}

function makeMap(unicornMagicPoops, width, height){
    new makeRoom(0,0,5,5,rooms);
    // Expand current rows to the width needed, if they aren't bigger already
    for(var rows = 0; rows <= map.rows; rows++){
        for(var cols = map.cols; cols < width; cols++){
            roomData[rows].push(1);
        }
    }

    // Add new rows for any remaining height
    for(var rows = roomData.length; rows <= height; rows++){
        var rowMake = [];
        for(var cols = 0; cols <= width; cols++){
            rowMake.push(1);
        }
        roomData.push(rowMake);

    }
    for(var trys = 0; trys <= unicornMagicPoops; trys++){
            var stuffx = Math.ceil(Math.random()* (width - 2));
            var stuffy = Math.ceil(Math.random()* (width- 2));
            var stuffwidth = Math.ceil(Math.random()*8)+2;
            var stuffheight = Math.ceil(Math.random()*8)+2;
            if(stuffx + stuffwidth > width){
                stuffwidth = 2;
            }
            if(stuffy + stuffheight > height){
                stuffheight = 2;
            }
            new makeRoom(stuffx,stuffy,stuffwidth,stuffheight,rooms);
    }
    camera.maxX = map.room[0].length*64 - 1024/2-32;
    camera.maxY = map.room.length*64 - 640/2-32;
    console.log("stuff")
    maze(0,0,width,height);

}

    var mazex = 0;
    var mazey = 0;
var maze = function(x,y,width,height){
    console.log(rooms.length)
    bridgeExtra = false;
    rooms.forEach(function(room,index){
     if(room.bridge == false){

        var otherRoom = rooms[Math.round(Math.random() * (rooms.length - 1))]
        if(otherRoom.bridge == true || otherRoom == room){
            if(otherRoom == room){
                if(rooms.indexOf(room) == 0){
                    otherRoom = rooms[rooms.indexOf(room) + 1];
                }else{
                    otherRoom = rooms[rooms.indexOf(room) - 1];
                }
            }
            if(otherRoom.bridge == true){
                if(rooms.length % 2 == 1 && bridgeExtra == false && index == rooms.length - 1){
                    otherRoom.bridge == false;
                }
            }

        }else{
            var roomx = Math.round(Math.random() * (room.x+room.width-room.x) + room.x);
            var roomy = Math.round(Math.random() * (room.y+room.width-room.y) + room.y);
            var otherRoomx = Math.round(Math.random() * (otherRoom.x+otherRoom.width-otherRoom.x) + otherRoom.x);
            var otherRoomy = Math.round(Math.random() * (otherRoom.y+otherRoom.height-otherRoom.y) + otherRoom.y);
            
            if(roomx < room.x){
                roomx = room.x + 2;
            }
            if(roomx > room.x+room.width){
                roomx = room.x+room.width - 2;
            }
            if(roomy < room.y){
                roomy = room.y + 2;
            }
            if(roomy > room.y+room.height){
                roomy = room.y+room.height - 2;
            }
            if(otherRoomx < otherRoom.x){
                otherRoomx = otherRoom.x + 2;
            }
            if(otherRoomx > otherRoom.x+otherRoom.width){
                otherRoomx = otherRoom.x+otherRoom.width - 2;
            }
            if(otherRoomy < otherRoom.y){
                otherRoomy = otherRoom.y + 2;
            }
            if(otherRoomy > otherRoom.y+otherRoom.height){
                otherRoomy = otherRoom.y+otherRoom.height - 2;
            }
            var point = {
                x: otherRoomx,
                y: roomy
            }
            console.log(point.x,point.y)
            if(roomx < point.x){
                for(var l = point.x;l >= roomx; l--){
                    roomData[point.y][l] = 0;
                }
            }
            if(roomx > point.x){
                var r = point.x
                for(var r = point.x;r <= roomx; r++){
                    roomData[point.y][r] = 0;
                }
            }
            
            if(otherRoomy < point.y){
                for(var u = point.y;u >= otherRoomy; u--){
                    roomData[u][point.x] = 0;
                }
            }
            if(otherRoomy > point.y){
                for(var d = point.y;d <= otherRoomy; d++){
                    roomData[d][point.x] = 0;
                }
            }
        }
     }
    })
}
var chests = [];
function Chest(x,y,arr,rt){
    var me = this;
    me.got = Math.ceil(Math.random()* 100);
    me.x = x;
    me.y = y;
    me.rt = rt;
    me.m = 0;
    me.ny = me.y*64 - 16;
    me.nx = me.x*64;
    me.img = new Image();
    me.img.src = imageMap['chests'][me.rt];
    me.opened = false;
    me.draw = function(){
        ctx.drawImage(me.img, me.x*64  - camera.x, me.y*64  - camera.y,64,64);
    }
    me.animation = function(){
        if(me.rt == 2 && me.img.src != imageMap['chests'][4]){
                if(me.img.src.endsWith('/c2.png')){
                    requestAnimationFrame(me.animation);
                    me.img.src = imageMap['chests'][3];
                }else if(me.img.src.endsWith('/c3.png')){
                    me.img.src = imageMap['chests'][4];
                    player.deathTimer += 1;
                }
    
        }
        if (me.rt == 0 && me.m <= 16){
            requestAnimationFrame(me.animation);
            me.m += 1;
            me.ny -= 1;
            if(me.ny <= 16){
                me.ny = 16;
            }
            if(me.nx >= map.cols*64 - 64){
                me.nx = me.x*64 - 64
            }
            ctx.fillText('+' + me.got,me.nx + 32 - camera.x,me.ny + 32 - camera.y);
            ctx.drawImage(coin,me.nx - camera.x,me.ny - camera.y,32,32);
        }

    }
    me.inRange = function(){
        if((playerx/64 == me.x - 1 && playery/64 == me.y && dir == 'right') ||
         (playerx/64 == me.x + 1 && playery /64== me.y && dir == 'left') || 
         (playery/64 == me.y - 1 && playerx/64 == me.x && dir == 'down') || 
         (playery/64 == me.y  + 1 && playerx /64== me.x && dir == 'up')){
            return true;
        }
        return false;
    }
    me.behavior = function(){
        
        if(me.rt == 0){
            if(me.opened == false && me.inRange() == true){
                player.gold += me.got;
                me.img.src = imageMap['chests'][1];
                requestAnimationFrame(me.animation);
                
                me.opened = true;
            }
        }else if(me.rt == 2){
            if(me.opened == false && me.inRange() == true){
                requestAnimationFrame(me.animation);
                me.opened = true;
            }
        }
    }
    arr.push(me);
}
var renderChests = function(){
    chests.forEach(function(chest, index){
        if(Keyboard.isDown(Keyboard.SPACE)) {
            chest.behavior();
        }
        chest.draw();
        
    })
    
}
var FPS = 30;  // lowest requirement 30 do not change except to go to 60
dostuff = function() {
    setTimeout(function(){
    window.requestAnimationFrame(dostuff);
    if(player.death == false){
            ctx.clearRect(0,0,1024,640);
            Game.update();
            renderFloors(camera.x,camera.y);
            renderChests();
            ctx.drawImage(coin, 10,20,32, 32);
            ctx.fillText(player.gold,45,50);
    }
    player.draw();
    }, 1000/FPS);
};


var Start = false;
if(Start == false){
    Keyboard.listenForEvents([Keyboard.LEFT,Keyboard.RIGHT,Keyboard.UP,Keyboard.DOWN,Keyboard.SPACE]);
    ctx.fillStyle = "white";
    ctx.font = "40px Arial";
    new makeMap(100,60,60);
    Start = true;
    window.requestAnimationFrame(dostuff);
}
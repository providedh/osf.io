var $ = require('jquery');
var TweenLite = require('TweenLite');
require('EasePack');
require('vendor/youtube');

var passwordForms = require('js/passwordForms');

// ANIMATION FOR FRONT PAGE
$( document ).ready(function() {
    $('.youtube').YouTubeModal({autoplay:1, width:640, height:480});
});

var waitForFinalEvent = (function () {
    var timers = {};
    return function (callback, ms, uniqueId) {
        if (!uniqueId) {
          uniqueId = 'Don\'t call this twice without a uniqueId';
        }
        if (timers[uniqueId]) {
          clearTimeout (timers[uniqueId]);
        }
        timers[uniqueId] = setTimeout(callback, ms);
    };
})();

(function() {

    var width;
    var height;
    var largeHeader;
    var canvas;
    var ctx;
    var points;
    var target;
    var animateHeader = true;

    // Main
    initHeader();
    initAnimation();
    addListeners();

    function initHeader() {
        width = $(window).width();
        height = 800;
        target = {
            x: width/2,
            y: 500
        };

        largeHeader = document.getElementById('home-hero');

        canvas = $('#demo-canvas')[0];
        canvas.width = width;
        canvas.height = height;
        ctx = canvas.getContext('2d');

        // create points
        points = [];
        for(var x = 0; x < width; x = x + width/10) {
            for(var y = 0; y < height; y = y + height/15) {
                var px = x + Math.random()*width/10;
                var py = y + Math.random()*height/15;
                var p = {x: px, originX: px, y: py, originY: py };
                points.push(p);
            }
        }

        // for each point find the 2 closest points
        for (var i = 0; i < points.length; i++) {
            var closest = [];
            var p1 = points[i];
            for (var j = 0; j < points.length; j++) {
                var p2 = points[j];
                if (p1 !== p2) {
                    var placed = false;
                    for (var k = 0; k < 2; k++) {
                        if (!placed) {
                            if(closest[k] === undefined) {
                                closest[k] = p2;
                                placed = true;
                            }
                        }
                    }
                    for (var m = 0; m < 2; m++) {
                        if (!placed) {
                            if (getDistance(p1, p2) < getDistance(p1, closest[m])) {
                                closest[m] = p2;
                                placed = true;
                            }
                        }
                    }
                }
            }
            p1.closest = closest;
        }

        // assign a circle to each point
        for(var n in points) {
            var c = new Circle(points[n], 2+Math.random()*3, 'rgba(255,255,255,0.3)');
            points[n].circle = c;
        }
    }

    // Event handling
    function addListeners() {
        setPos();
        window.addEventListener('scroll', scrollCheck);
        window.addEventListener('resize', resize);
    }

    function setPos(e) {
        target.x = window.innerWidth/2;
        target.y = 530;
    }

    function scrollCheck() {
        if (document.body.scrollTop > height) {
            animateHeader = false;
        } else {
            animateHeader = true;
        }
    }

    function resize() {
        if (window.innerWidth > 770) {
            waitForFinalEvent(function(){
                $('#demo-canvas').remove();
                $('#canvas-container').append('<canvas id="demo-canvas"></canvas>');
                initHeader();
                initAnimation();
            }, 300, 'resize');
        }
    }

    // animation
    function initAnimation() {
        animate();
        for(var i in points) {
            shiftPoint(points[i]);
        }
    }

    function animate() {
        if(animateHeader) {
            ctx.clearRect(0,0,width,height);
            for(var i in points) {
                // detect points in range
                if(Math.abs(getDistance(target, points[i])) < 20000) {
                    points[i].active = 0.3;
                    points[i].circle.active = 0.6;
                } else if(Math.abs(getDistance(target, points[i])) < 100000) {
                    points[i].active = 0.1;
                    points[i].circle.active = 0.3;
                } else if(Math.abs(getDistance(target, points[i])) < 200000) {
                    points[i].active = 0.02;
                    points[i].circle.active = 0.1;
                } else {
                    points[i].active = 0;
                    points[i].circle.active = 0;
                }
                drawLines(points[i]);
                points[i].circle.draw();
            }
        }
        requestAnimationFrame(animate);
    }

    function shiftPoint(p) {
        TweenLite.to(p, 1+1*Math.random(), {x:p.originX-50+Math.random()*100,
            y: p.originY-50+Math.random()*100, ease:Circ.easeInOut,
            onComplete: function() {
                shiftPoint(p);
            }});
    }

    // Canvas manipulation
    function drawLines(p) {
        if (!p.active) {
            return;
        }
        for(var i in p.closest) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p.closest[i].x, p.closest[i].y);
            ctx.strokeStyle = 'rgba(191,178,144,'+ p.active+')';
            ctx.stroke();
        }
    }

    function Circle(pos,rad,color) {
        var self = this;

        // constructor
        (function() {
            self.pos = pos || null;
            self.radius = rad || null;
            self.color = color || null;
        })();

        this.draw = function() {
            if (!self.active) {
                return;
            }
            ctx.beginPath();
            ctx.arc(self.pos.x, self.pos.y, self.radius, 0, 2 * Math.PI, false);
            ctx.fillStyle = 'rgba(191,178,144,'+ self.active+')';
            ctx.fill();
        };
    }

    // Util
    function getDistance(p1, p2) {
        return Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2);
    }

})();

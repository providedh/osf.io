'use strict';

var $ = require('jquery');
var d3 = require('d3');
var bootbox = require('bootbox');

var VisContainer = function(selector, options) {

    var self = this;
    console.log(options.node);
    self.node = options.node
    // self.options = $.extend({}, defaultOptions, options);
    var url = self.node.urls.api + 'teistats/statistics/';
    
    self.mixButton = document.getElementById("startstop-button");
    self.resetButton = document.getElementById("reset-button");

    self.mixButton.addEventListener("click", startAction);
    self.resetButton.addEventListener("click", resetStatisticsAction);

    var startAction = function() {
    	console.log("Statistics starting...");
    	self.mixButton.removeEventListener("click", startAction);
    	self.mixButton.addEventListener("click", stopAction);
    	self.mixButton.innerHTML = '<i class="fa fa-stop"></i> Stop';
    	self.fetchStatisticsPeriodically(10);
    };

    var stopAction = function() {
    	clearInterval(self.timerId);
    	console.log("Stopped");
    	self.mixButton.removeEventListener("click", stopAction);
    	self.mixButton.addEventListener("click", startAction);
    	self.mixButton.innerHTML = '<i class="fa fa-play"></i> Start';
    };

    var resetStatisticsAction = function() {
    	bootbox.confirm({
	            title: 'Reset TEI Statistics?',
	            message: 'Are you sure you want to reset statistics for this node?',
	            callback: function(result) {
	                if(result) {
	                	stopAction();
	                    $.ajax({
	                    type: 'delete',
	                    url: options.node.urls.api + 'teistats/config/reset-statistics/', 
	                    contentType: 'application/json',
	                    dataType: 'json',
	                    data: JSON.stringify({})
	                }).done(function() {
	                    console.log('Statistics were reset');
	                }).fail(function() {
	                    console.log('Error resetting statistics');
	                });
	                }
	            },
	            buttons:{
	                confirm:{
	                    label:'Remove',
	                    className:'btn-danger'
	                }
	            }
	        });
	};

	self.fetchStatisticsPeriodically = function(seconds) {
    	seconds = (typeof seconds !== 'undefined') ?  seconds : 1; 
    	var fetchStatistics = function() {
    		d3.json(url).then(function(data) {
    			console.log(data);
    		}, function(err) {
    			console.log('Error retrieving data ' + err.stack);
    		});
    	};
    	
    	fetchStatistics();
    	self.timerId = setInterval(fetchStatistics, 1000 * seconds);
    };

    d3.select('#reset-button')
    	.on('click', function (d) { 
	    	
    	});

    d3.select('#vis-svg-container')
    	.append("text")
    		.text('Hello from D3!')
	    	.attr('x', 200)
	    	.attr('y', 200);

};

module.exports = VisContainer;
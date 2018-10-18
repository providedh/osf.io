'use strict';

var d3 = require('d3');
var bootbox = require('bootbox');



var VisContainer = function(selector, options) {
    var self = this;
    console.log(options.node);
    self.node = options.node
    var url = self.node.urls.api + 'teistats/statistics/';
    
    self.mixButton = document.getElementById("startstop-button");
    self.resetButton = document.getElementById("reset-button");

    

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

	                	fetch(options.node.urls.api + 'teistats/config/reset-statistics/', {
	                		method: "DELETE"
	                	}).then(function(response) {
	                		if (response.ok) console.log('Statistics were reset');
	                		else console.log('Error resetting statistics');
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

	function isEmptyDictionary(dict) {
		for(var key in dict) {
	        if(dict.hasOwnProperty(key))
	            return false;
	    	}
    	return true;
	}



	self.mixButton.addEventListener("click", startAction);
    self.resetButton.addEventListener("click", resetStatisticsAction);

	self.fetchStatisticsPeriodically = function(seconds) {
    	seconds = (typeof seconds !== 'undefined') ?  seconds : 1;
    	var fetchStatistics = function() {
    		d3.json(url).then(self.updateVis, function(err) {
    			console.log('Error retrieving data ' + err.stack);
    		});
    	};
    	
    	fetchStatistics();
    	self.timerId = setInterval(fetchStatistics, 1000 * seconds);
    };


    self.svg = d3.select('#vis-svg-container')

    self.generateDistributionData = function(stats) {
    	var data = new Array();
    	var xpos = 12;
    	var ypos = 1;
    	var width = 12;
    	var height = 12;

    	for (var row = 0; row < stats.length; row++) {
    		data.push(new Array());
    		for (var column = 0; column < 100; column++) {
    			var value = 0;
    			if (stats[row].percentages.hasOwnProperty("" + column))
    				value = stats[row].percentages["" + column]
    			data[row].push({
	    			x: xpos,
	    			y: ypos,
	    			width: width,
	    			height: height,
	    			value: value

	    		});
	    		xpos += width; 	
    		}
    		xpos = 12;
    		ypos += height + 20;
    	}
    	return data
    }

    self.updateVis = function(statsData) {
    	console.log(statsData);
    	if (isEmptyDictionary(statsData)) return;

    	var distData = self.generateDistributionData(statsData.statistics);
    	console.log(distData);

    	var line = d3.line();

    	var groups = self.svg.append("g").selectAll(".line")
    		.data(distData)
    		.enter().append("g");

    	var lines = groups
				.append("path")
    			.attr("d", function(d) { 
    				return line([[
		    				d[0].x -12,
		    				d[0].y 
		    		],[
		    				d[d.length - 1].x -12,
		    				d[d.length - 1].y 
		    		]]);
    			})
    			.attr("stroke", "grey");

		groups.each(function(d, i) {
			console.log(d);
			d3.select(this).selectAll("circle")
						.data(d)
					.enter()
						.append("circle")
						.attr("cx", function(d) { return d.x; })
						.attr("cy", function(d) { return d.y; })
						.attr("r", function(d) { return d.value > 0 ? 5 : 0 })
						.attr("fill", function(d) { return "black"; });
		});





    	// var column = row.selectAll(".square")
    	// 	.data(function(d) { return d; })
    	// 	.enter().append("rect")
    	// 	.attr("class", "square")
    	// 	.attr("x", function(d) { return d.x; })
    	// 	.attr("y", function(d) { return d.y; })
    	// 	.attr("width", function(d) { return d.width; })
    	// 	.attr("height", function(d) { return d.height; })
    	// 	.style("fill", "#fff")
    	// 	.style("stroke", "#222");


    	// var row = self.svg.selectAll(".row")
    	// 	.data(rowData)
    	// 	.enter().append("g")
    	// 	.attr("class", "row")
	    // 		.append("rect")
	    // 		.attr("class", "square")
	    // 		.attr("x", function(d) { return 200;})
	    // 		.attr("y", function(d, i) { return 10 * i})
	    // 		.attr("width", 800)
	    // 		.attr("height", 10)
	    // 		.style("fill", function(d) {
	    // 			if (isEmptyDictionary(d)) {
		   //  			return "#fff";
		   //  		} else {
		   //  			return "#000";
		   //  		}
	    // 		})
	    // 		.style("stroke", "#222");
    };

    self.updateVis([]);
};



module.exports = VisContainer;
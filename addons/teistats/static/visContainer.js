'use strict';

var d3 = require('d3');
// var d3tip = require('d3-tip');
var bootbox = require('bootbox');



var VisContainer = function(selector, options) {
    var self = this;
    console.log(options.node);
    self.node = options.node
    var url = self.node.urls.api + 'teistats/statistics/';
    self.axisAdded = false;
    
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

    self.svg = d3.select('#vis-svg-container');

    self.generateDistributionData = function(stats) {
    	var data = new Array();
    	var width = 14;
    	var height = 14;

        self.yScale = d3.scaleLinear().domain([0,stats.length - 1]).range([51, self.containerSize[1] - 50]);

    	for (var queryIdx = 0; queryIdx < stats.length; queryIdx++) {
            if (!self.axisAdded) {
                console.log('adding axis');
                var xAxis = d3.axisBottom().scale(self.xScale);
                self.svg.append("g")
                    .attr("transform", "translate(0," + self.yScale(queryIdx) + ")")
                    .call(xAxis)
                    .append("text")
                    .text(stats[queryIdx].element)
                        .attr("fill", "black")
                        .attr("x", 225)
                        .attr("text-anchor", "end")
                        .attr("font-family", "sans-serif")
                        .attr("font-size", "10px");
            }

    		for (var percent = 0; percent < 100; percent++) {
    			var value = 0;
    			if (stats[queryIdx].percentages.hasOwnProperty("" + percent))
    				value = stats[queryIdx].percentages["" + percent]
                if (value !== 0) {
                    data.push({
                        x: self.xScale(percent),
                        y: self.yScale(queryIdx),
                        width: width,
                        height: height,
                        percent: percent,
                        value: value,
                        queryIdx: queryIdx
                    });
                }
    		}
    	}
        self.axisAdded = true;
    	return data
    }

    self.updateVis = function(statsData) {
        
        if (!statsData || statsData.statistics.length == 0) return;

        console.log(statsData);


    	var distData = self.generateDistributionData(statsData.statistics);



    	// distData = d3.nest()
    	// 			.key(function(d) { return d.queryIdx}).entries(distData);

    	console.log(distData);

    	var container = self.svg.select("#baseGrp");

    	var circle = container.selectAll("circle").data(distData, function (d) { return "" + d.queryIdx + d.percent; });


		var radiusScale = d3.scaleLinear()
						    .domain(d3.extent(distData, function(a) { return +a.value; }))
						    .range([2, 15]);

    	circle.enter().append("circle")
				.attr("cx", function(d) { return d.x; })
				.attr("cy", function(d) { return d.y; })
				.attr("r", function(d) { return radiusScale(d.value); })
				.attr("fill", 'rgba(0, 0, 0, 0.5)')
			.merge(circle)
					.transition()
					.duration(750)
	    			.ease(d3.easeLinear)
						.attr("r", function(d) { return radiusScale(d.value); });

		circle.exit().remove();


    };

    window.onload = function () { 


        var clientRect = document.getElementById('vis-svg-container').getBoundingClientRect();
        self.containerSize = [clientRect.right - clientRect.left, clientRect.bottom - clientRect.top];
        

        self.xScale = d3.scaleLinear().domain([0,100]).range([251, self.containerSize[0] - 200]);
        // console.log(self.xScale(50));

        self.svg.append("g")
                .attr("id", "baseGrp");

        

        self.updateVis()
    }
};



module.exports = VisContainer;
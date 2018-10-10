'use strict';

// var $ = require('jquery');
var d3 = require('d3');


var VisContainer = function(selector, options) {
    var self = this;
    // self.options = $.extend({}, defaultOptions, options);
    d3.select('#vis-svg-container')
    	.append("text")
    		.text('Hello from D3!')
	    	.attr('x', 200)
	    	.attr('y', 200);


    // this.viewModel = new ViewModel(self.options);
    // $osf.applyBindings(self.viewModel, selector);
};

module.exports = VisContainer;
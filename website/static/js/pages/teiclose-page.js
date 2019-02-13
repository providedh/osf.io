'use strict';
var $ = require('jquery');
var m = require('mithril');

var subnav = $("#projectSubnav");
var navbar = subnav.find('.navbar-nav');
navbar.append("<li><a href=\"" + window.contextVars.file.addon_url + "\">Close Reading</a></li>");

var CloseReadingWidget = require('closeReading');

m.mount(document.getElementById('close-reading-widget'), m.component(CloseReadingWidget.CloseReadingWidget,
    {node: window.contextVars.node, file: window.contextVars.file}));
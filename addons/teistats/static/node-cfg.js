'use strict';

var $ = require('jquery');
var TeiXPathManager = require('./teiXPathManager');
var TeiXPathTable = require('./teiXPathTable');
var $osf = require('js/osfHelpers');
var rt = require('js/responsiveTable');
require('jquery-ui');
require('js/filters');


var ctx = window.contextVars;

$(document).ready(function() {

    var nodeApiUrl = ctx.node.urls.api;

    var addUrl = nodeApiUrl + 'teistats/config/add-xpath/';
    var teiXPathManager = new TeiXPathManager('#addTeiStatXPath', addUrl);
    var tableUrl = nodeApiUrl + 'teistats/config/';
    var elementTable = $('#teiXPathTable');
    var teiXPathTable = new TeiXPathTable('#teiXPathsScope', tableUrl, elementTable);

    $(window).on('load', function() {
        if (!!teiXPathTable){
            teiXPathTable.viewModel.onWindowResize();
            rt.responsiveTable(elementTable[0]);
        }
        $('table.responsive-table td:first-child a,' +
             'table.responsive-table td:first-child button').on('click', function(e) {
             e.stopImmediatePropagation();
        });
    });

    $(window).resize(function() {
        if (!!teiXPathTable) {
          	teiXPathTable.viewModel.onWindowResize();
        }
    });

});

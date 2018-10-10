'use strict';

// var $ = require('jquery');
// var Raven = require('raven-js');
// require('bootstrap-editable');
// require('osf-panel');

var VisContainer = require('visContainer');

// require('ace-noconflict');
// require('ace-mode-markdown');
// require('ace-ext-language_tools');
// require('addons/wiki/static/ace-markdown-snippets.js');
// require('../../vendor/ace-plugins/spellcheck_ace.js');

// var WikiMenu = require('../wikiMenu');
// var Comment = require('js/comment'); //jshint ignore:line
// var $osf = require('js/osfHelpers');

// var ctx = window.contextVars.wiki;  // mako context variables

// var editable = (ctx.panelsUsed.indexOf('edit') !== -1);
// var viewable = (ctx.panelsUsed.indexOf('view') !== -1);
// var comparable = (ctx.panelsUsed.indexOf('compare') !== -1);
// var menuVisible = (ctx.panelsUsed.indexOf('menu') !== -1);

// var viewVersion = ctx.versionSettings.view || (editable ? 'preview' : 'current');
// var compareVersion = ctx.versionSettings.compare || 'previous';

// var visContainerOptions = {
//     editVisible: editable,
//     viewVisible: viewable,
//     compareVisible: comparable,
//     menuVisible: menuVisible,
//     canEdit: ctx.canEdit,
//     viewVersion: viewVersion,
//     compareVersion: compareVersion,
//     urls: ctx.urls,
//     metadata: ctx.metadata
// };

var visContainer = new VisContainer('#visContainer', {});

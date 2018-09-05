'use strict';

var $ = require('jquery');
var ko = require('knockout');
var bootbox = require('bootbox');
var $osf = require('js/osfHelpers');
require('js/osfToggleHeight');
require('bootstrap-editable');

var ctx = window.contextVars;

function TeiXPathViewModel(data, $root) {
    var self = this;
    self.$root = $root;
    $.extend(self, data);

    self.xpath = ko.observable(data.xpath);
    self.name = ko.observable(data.name);

    self.expanded = ko.observable(false);

    self.toggleExpand = function() {
        self.expanded(!self.expanded());
    };
}

function TeiXPathTableViewModel(url, table) {
    var self = this;
    self.url = url;
    self.teiXPaths = ko.observableArray();
    self.nodeUrl = ko.observable(null);

    self.visible = ko.computed(function() {
        return self.teiXPaths().length > 0;
    });

    function onFetchSuccess(response) {
        var node = response.node;
        self.teiXPaths(ko.utils.arrayMap(node.xpath_exprs, function(xpath_expr) {
            return new TeiXPathViewModel(xpath_expr, self);
        }));
        self.nodeUrl(node.absolute_url);
    }

    function onFetchError() {
        $osf.growl('Could not retrieve XPath expressions.', 'Please refresh the page or contact ' +
                $osf.osfSupportLink() + ' if the problem persists.');
    }

    function fetch() {
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json'
        }).done(
            onFetchSuccess
        ).fail(
            onFetchError
        );
    }

    fetch();

    self.removeXPath = function(data) {
        var dataToSend = {
            'xpath': data.xpath(),
            'name': data.name()
        };
        bootbox.confirm({
            title: 'Remove XPath expression?',
            message: 'Are you sure you want to remove this XPath expression?',
            callback: function(result) {
                if(result) {
                    $.ajax({
                    type: 'delete',
                    url: ctx.node.urls.api + 'teistats/config/remove-xpath/',
                    contentType: 'application/json',
                    dataType: 'json',
                    data: JSON.stringify(dataToSend)
                }).done(function() {
                    self.teiXPaths.remove(data);
                }).fail(function() {
                    $osf.growl('Error:','Failed to delete the XPath expression.');
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

    self.setupEditable = function(elm, data) {

        function setupEditableSpan(span, field) {
            span.editable({
                type: 'text',
                url: ctx.node.urls.api + 'teistats/config/edit-xpath/',
                placement: 'bottom',
                ajaxOptions: {
                    type: 'PUT',
                    dataType: 'json',
                    contentType: 'application/json'
                },
                send: 'always',
                title: function() {
                    switch (field) {
                        case 'xpath':
                            return 'Edit XPath expression';
                        case 'name':
                            return 'Edit Name';
                    }
                },
                params: function(params){
                    params.xpath = data.xpath();
                    params.name = data.name();
                    params.pk = field;
                    return JSON.stringify(params);
                },
                success: function(response) {
                    switch (field) {
                        case 'xpath':
                            data.xpath(response);
                            break;
                        case 'name':
                            data.name(response);
                            break;
                    }
                    fetch();
                },
                error: $osf.handleEditableError
            });
        }

        var $elm = $(elm);
        var $editableXPath = $elm.find('.xpath-expr');
        setupEditableSpan($editableXPath, 'xpath');
        var $editableName = $elm.find('.xpath-name');
        setupEditableSpan($editableName, 'name');
    };

    self.collapsed = ko.observable();

    self.afterRenderXPath = function(elm, data) {
        var $tr = $(elm);
        if (self.teiXPaths().indexOf(ko.dataFor($tr[1])) === 0) {
            self.onWindowResize();
        }
        self.setupEditable(elm, data);
    };

    self.table = $(table);

    self.onWindowResize = function () {
        self.collapsed(self.table.children().filter('thead').is(':hidden'));
    };

}

function TeiXPathTable(selector, url, table) {
    var self = this;
    self.viewModel = new TeiXPathTableViewModel(url, table);
    $osf.applyBindings(self.viewModel, selector);

}
module.exports = TeiXPathTable;

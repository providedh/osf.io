'use strict';

var $ = require('jquery');
var ko = require('knockout');
var $osf = require('js/osfHelpers');
var ChangeMessageMixin = require('js/changeMessage');


var TeiXPathViewModel = function(url) {
    var self = this;
    ChangeMessageMixin.call(self);
    self.url = url;
    self.xpath = ko.observable(null).extend({
        required: true
    });

    self.checkRequired = function(data, event) {
        if (event.target.value.trim().length > 0) {
            self.disableSubmit(false);
        } else {
            self.disableSubmit(true);
        }
        return true;
    };

    self.name = ko.observable(null);

    self.messageClass = ko.observable('text-danger');

    self.disableSubmit = ko.observable(true);
    self.submitText = ko.observable('Create');

    self.submit = function() {

        self.disableSubmit(true);
        self.submitText('Please wait');

        $osf.postJSON(
            self.url,
            {
                xpath: self.xpath(),
                name: self.name()
            }
        ).done(function() {
            window.location.reload();
        }).fail(function(response) {
            self.changeMessage(response.responseJSON.message_long, 'text-danger');
            self.disableSubmit(false);
            self.submitText('Create');
        });
    };

};
$.extend(TeiXPathViewModel.prototype, ChangeMessageMixin.prototype);


function TeiXPathManager(selector, url) {
    var self = this;
    self.viewModel = new TeiXPathViewModel(url);
    $osf.applyBindings(self.viewModel, selector);
}
module.exports = TeiXPathManager;

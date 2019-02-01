'use strict';

var m = require('mithril');
var Raven = require('raven-js');
var $osf = require('js/osfHelpers');
var waterbutler = require('js/waterbutler');

var d3 = require('d3');
// var d3tip = require('d3-tip');
var bootbox = require('bootbox');


var FileFetcher = {
    clear: function(){
        self = this;
        delete self.promise;
    },
    fetch: function(url, reload){
        self = this;
        if(typeof self.promise === 'undefined' || reload){
            self.promise = $.ajax({
                type: 'GET',
                url: url,
                dataType: 'text',
                beforeSend: $osf.setXHRAuthorization,
            });
        }
        return self.promise;
    }
};


var CloseReadingWidget = {
    controller: function(options) {
        var self = this;
        self.node = options.node;
        self.file = options.file;

        self.url = waterbutler.buildDownloadUrl(self.file.path, self.file.provider, self.node.id, {direct: true, mode: 'render'})
        self.loaded = false;
        self.content = '';

        self.loadFile = function(reload) {
            self.loaded = false;
            var response = FileFetcher.fetch(self.url, reload);

            response.done(function (parsed, status, response) {
                m.startComputation();
                self.loaded = true;
                self.content = response.responseText;
                m.endComputation();
            });

            response.fail(function (xhr, textStatus, error) {
                $osf.growl('Error','The file content could not be loaded.');
                Raven.captureMessage('Could not GET file contents.', {
                    extra: {
                        url: self.url,
                        textStatus: textStatus,
                        error: error
                    }
                });
            });
        };

        self.loadFile(false);

        return self;
    },
    view: function(ctrl) {
        return m('.panel-body', [
            m('', [
                m('h3', ctrl.file.filename),
                !ctrl.loaded ?
                m('.spinner-loading-wrapper', [
                    m('.ball-scale.ball-scale-blue', [m('div')]),
                    m('p.m-t-sm.fg-load-message', ' Loading... ')
                ]) :
                m('', {style: {'padding-top': '10px'}}, [
                    m('div.file-content', ctrl.content)
                ])
            ])
        ]);
    }
};

module.exports = {
    CloseReadingWidget: CloseReadingWidget
};

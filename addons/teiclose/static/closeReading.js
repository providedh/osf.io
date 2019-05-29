'use strict';

var m = require('mithril');
var Raven = require('raven-js');
var $osf = require('js/osfHelpers');
var waterbutler = require('js/waterbutler');

var annotator = require('./teicloseAnnotator.js');

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

        self.url = waterbutler.buildDownloadUrl(self.file.path, self.file.provider, self.node.id, {direct: true, mode: 'render', version: self.file.version});
        self.loaded = false;
        self.content = '';

        self.socket = null;
        self.first_entry = true;

        createWebSocket();

        function createWebSocket()
        {
            self.socket = new WebSocket('ws://' + window.location.host.split(':')[0] + ':8000' + '/websocket/' + self.node.id + '_' + self.file.id + '/');

            if (self.socket.readyState === WebSocket.OPEN) {
                self.socket.onopen();
            }

            self.socket.onopen = function open() {
                console.log("WebSockets connection created.");
            };

            self.socket.onmessage = function message(event) {
                console.log("data from socket:" + event.data);

                if (self.first_entry)
                {
                    m.startComputation();
                    self.loaded = true;
                    self.content = JSON.parse(event.data);
                    m.endComputation();

                    if (self.content.status === 200)
                    {
                        annotator.setup(self.content.xml_content);
                        self.first_entry = false;
                    }
                }
                else
                {
                    self.content = JSON.parse(event.data);

                    if (self.content.status === 200)
                    {
                        console.log('annotate - success < ', self.content);
                        window.updateFile(self.content.xml_content);
                    }
                    else
                    {
                        console.log('annotate - failed < ', self.content);
                    }
                }

                // self.content = event.data;
            };
        }

        window.send = function (json)
        {
            // var zawartosc = document.getElementById("input_field").value;
            // socket.send(zawartosc);

            // socket.send(json);
            self.socket.send(json);
        };

        // self.loadFile = function(reload) {
        //     self.loaded = false;
        //     var response = FileFetcher.fetch(self.url, reload);
        //
        //     response.done(function (parsed, status, response) {
        //         m.startComputation();
        //         self.loaded = true;
        //         self.content = response.responseText;
        //         m.endComputation();
        //
        //         annotator.setup(self.content);
        //     });
        //
        //     response.fail(function (xhr, textStatus, error) {
        //         $osf.growl('Error','The file content could not be loaded.');
        //         Raven.captureMessage('Could not GET file contents.', {
        //             extra: {
        //                 url: self.url,
        //                 textStatus: textStatus,
        //                 error: error
        //             }
        //         });
        //     });
        // };


        let linkVersions = '/' + self.file.id + '/?show=revision&version=' + self.file.version;

        if(self.file.provider === 'osfstorage'){
            changeVersionHeader();
        }

        function changeVersionHeader(){
            document.getElementById('versionLink').style.display = 'inline';
            m.render(document.getElementById('versionLink'), m('a', {onclick: redirectToVersions}, document.getElementById('versionLink').innerHTML));
        }

        function redirectToVersions (){
            window.location = linkVersions;
            return false;
        }

        // self.loadFile(false);

        return self;
    },
    view: function(ctrl) {
        return null;
    }
};

module.exports = {
    CloseReadingWidget: CloseReadingWidget
};

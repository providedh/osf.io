'use strict';

require('./teistatsWidget.css');

var m = require('mithril');
var $ = require('jquery');
var $osf = require('js/osfHelpers');
var Raven = require('raven-js');


var TeiStatsWidget = {

    controller: function(options) {
        var self = this;
        self.node = options.node;
        self.totalFiles = m.prop('-');
        self.teiFiles = m.prop('-');
        self.statistics = m.prop([]);
        self.requestPending = m.prop(false);
        self.failed = false;

        self.updateStatistics = function (result) {
            self.totalFiles(result.meta.totalFiles);
            self.teiFiles(result.meta.teiFiles);
            self.statistics(result.statistics);
        }

        self.getStatistics = function() {
            if(!self.requestPending()) {
                self.requestPending(true);
                var url = self.node.urls.api + 'teistats/get-statistics/';
                var promise = m.request({
                    method : 'GET',
                    url : url
                });
                promise.then(
                    function(result) {
                        self.updateStatistics(result);
                        self.requestPending(false);
                        return promise;
                    }, function(xhr, textStatus, error) {
                        self.failed = true;
                        self.requestPending(false);
                        Raven.captureMessage('Error retrieving TEI statistics', {extra: {url: url, textStatus: textStatus, error: error}});
                    }
                );
            }
        };

        console.log(self.node.urls.web)

        self.getStatistics()
    },

    view : function(ctrl) {

        var OSF_SUPPORT_EMAIL = $osf.osfSupportEmail();

        return m('.tei-statistics-list.m-t-md', [
            // Error message if the TEI statistics request fails
            ctrl.failed ? m('p', [
                'Unable to retrieve TEI statistics at this time. Please refresh the page or contact ',
                m('a', {'href': 'mailto:' + OSF_SUPPORT_EMAIL}, OSF_SUPPORT_EMAIL), ' if the problem persists.'
            ]) :
            // Show OSF spinner while there is a pending TEI statistics request
            ctrl.requestPending() ?  m('.spinner-loading-wrapper', [
                m('.ball-scale.ball-scale-blue', [m('div')]),
                m('p.m-t-sm.fg-load-message', 'Loading TEI statistics...')
            ]) :
            // Display each statistics item (element name or xpath and number of occurrences)
            [
                m('p', ['Number of examined files: ', m('span', ctrl.totalFiles())]),
                m('p', ['Correct TEI files: ', m('span', ctrl.teiFiles())]),
                [ctrl.statistics() ? ctrl.statistics().map(function(item) {
                    return m('.tei-statistics-item', [
                        m('span.p-l-sm.p-r-sm', item.element),
                        m('span.text-right', item.n)
                    ]);
                }) : ''],
                m('br'),
                m('p.f-w-xl.pull-right', ['Check the TEI Statistics page to run calculations and visualizations ',
                    m('a', {'href': ctrl.node.urls.web + 'teistats/'}, m('i.fa.fa-external-link'))
                ])
            ]
        ]);

    }
};


module.exports = {
    TeiStatsWidget: TeiStatsWidget
};

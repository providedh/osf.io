var m = require('mithril');

var TeiStatsWidget = require('./teistatsWidget.js');

// Skip if widget is not enabled, i.e. the addon is not enabled
if ($('#teistatsWidget')[0]) {
    m.mount(document.getElementById('teistatsWidget'), m.component(TeiStatsWidget.TeiStatsWidget,
        {node: window.contextVars.node}));
}

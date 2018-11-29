# -*- coding: utf-8 -*-
"""TeiStats addon routes."""
from addons.teistats import views
from framework.routing import Rule, json_renderer

from website.routes import OsfWebRenderer

TEMPLATE_DIR = './addons/teistats/templates/'

page_routes = {

    'rules': [

        # Home (Base) | GET
        Rule(
            [
                '/project/<pid>/teistats/',
                '/project/<pid>/node/<nid>/teistats/',
            ],
            'get',
            views.teistats_get_main_vis,
            OsfWebRenderer('teistats_vis_main.mako', trust=False, template_dir=TEMPLATE_DIR)
        ),
    ]
}

api_routes = {

    'rules': [

        # Config
        Rule(
             [
                '/project/<pid>/teistats/config/add-xpath/',
                '/project/<pid>/node/<nid>/teistats/config/add-xpath/'
             ],
             'post',
             views.teistats_config_add_xpath,
             json_renderer
        ),

        Rule(
             [
                '/project/<pid>/teistats/config/edit-xpath/',
                '/project/<pid>/node/<nid>/teistats/config/edit-xpath/'
             ],
             'put',
             views.teistats_config_edit_xpath,
             json_renderer
        ),

        Rule(
             [
                '/project/<pid>/teistats/config/remove-xpath/',
                '/project/<pid>/node/<nid>/teistats/config/remove-xpath/'
             ],
             'delete',
             views.teistats_config_remove_xpath,
             json_renderer
        ),

        Rule(
            [
                '/project/<pid>/teistats/config/',
                '/project/<pid>/node/<nid>/teistats/config/'
            ],
            'get',
            views.teistats_config_get,
            json_renderer
        ),

        # Calculations
        Rule(
            [
                '/project/<pid>/teistats/start-statistics/',
                '/project/<pid>/node/<nid>/teistats/start-statistics/'
            ],
            'get',
            views.teistats_statistics_start,
            json_renderer
        ),

        Rule(
            [
                '/project/<pid>/teistats/stop-statistics/',
                '/project/<pid>/node/<nid>/teistats/stop-statistics/'
            ],
            'get',
            views.teistats_statistics_stop,
            json_renderer
        ),

        Rule(
             [
                '/project/<pid>/teistats/reset-statistics/',
                '/project/<pid>/node/<nid>/teistats/reset-statistics/'
             ],
             'delete',
             views.teistats_statistics_reset,
             json_renderer
        ),

        Rule(
            [
                '/project/<pid>/teistats/get-statistics/',
                '/project/<pid>/node/<nid>/teistats/get-statistics/',
            ],
            'get',
            views.teistats_statistics_get,
            json_renderer,
        ),
    ],

    'prefix': '/api/v1',

}

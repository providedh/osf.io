# -*- coding: utf-8 -*-
"""TeiStats addon routes."""
from addons.teistats import views
from framework.routing import Rule, json_renderer

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
              
        # Widget
        Rule(
            [
                '/project/<pid>/teistats/statistics/',
                '/project/<pid>/node/<nid>/teistats/statistics/',
            ],
            'get',
            views.teistats_statistics_get,
            json_renderer,
        ),
    ],

    'prefix': '/api/v1',

}
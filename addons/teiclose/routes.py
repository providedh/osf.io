# -*- coding: utf-8 -*-
"""TeiClose addon routes."""
from addons.teiclose import views
from framework.routing import Rule, json_renderer

from website.routes import OsfWebRenderer

TEMPLATE_DIR = './addons/teiclose/templates/'

page_routes = {

    'rules': [

        # Home (Base) | GET
        Rule(
            [
                '/project/<pid>/teiclose/<file_id>/<file_ver>/',
                '/project/<pid>/node/<nid>/teiclose/<file_id>/',
            ],
            'get',
            views.teiclose_get_main_vis,
            OsfWebRenderer('teiclose_vis_main.mako', trust=False, template_dir=TEMPLATE_DIR)
        ),
    ]
}

api_routes = {

    'rules': [

        # changes
        Rule(
            [
                '/project/<pid>/teiclose/add-annotation/',
                '/project/<pid>/node/<nid>/teiclose/add-annotation/'
            ],
            'post',
            views.teiclose_annotation_add,
            json_renderer
        ),
    ],

    'prefix': '/api/v1',

}

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
                '/project/<pid>/node/<nid>/teiclose/<file_id>/<file_ver>/',
            ],
            'get',
            views.teiclose_get_main_vis,
            OsfWebRenderer('teiclose_vis_main.mako', trust=False, template_dir=TEMPLATE_DIR)
        ),
    ]
}

api_routes = {

    'rules': [
        Rule(
            [
                '/project/<project_guid>/teiclose/<file_guid>/<file_ver>/certhistory/',
                '/project/<project_guid>/node/<node_guid>/teiclose/<file_guid>/<file_ver>/certhistory/',
            ],
            'get',
            views.teiclose_get_annotation_history,
            json_renderer
        ),
        Rule(
            [
                '/project/<project_guid>/teiclose/<file_guid>/annotate/',
                '/project/<project_guid>/node/<node_guid>/teiclose/<file_guid>/annotate/',
            ],
            'put',
            views.teiclose_add_annotation,
            lambda x: x,
        ),
        Rule(
            [
                '/project/<project_guid>/teiclose/<file_guid>/save/',
                '/project/<project_guid>/node/<node_guid>/teiclose/<file_guid>/save/',
            ],
            'put',
            views.teiclose_save_annotations,
            lambda x: x,
        )
    ],
    'prefix': '/api/v1',
}

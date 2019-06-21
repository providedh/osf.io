# -*- coding: utf-8 -*-
"""PeopleVis addon routes."""
from addons.peoplevis import views
from framework.routing import Rule, json_renderer

from website.routes import OsfWebRenderer

TEMPLATE_DIR = './addons/teiclose/templates/'

page_routes = {

    'rules': [

        # Home (Base) | GET
        Rule(
            [
                '/project/<pid>/peoplevis',
            ],
            'get',
            views.peoplevis_get_main_vis,
            OsfWebRenderer('peoplevis_vis_main.mako', trust=False, template_dir=TEMPLATE_DIR)
        ),
    ]
}

api_routes = {

    'rules': [],

    'prefix': '/api/v1',

}

import os

from addons.base.apps import BaseAddonAppConfig

HERE = os.path.dirname(os.path.abspath(__file__))
NODE_SETTINGS_TEMPLATE = os.path.join(
    HERE,
    'templates',
    'teistats_node_settings.mako',
)

class TeiStatsAddonConfig(BaseAddonAppConfig):

    name = 'addons.teistats'
    label = 'addons_teistats'
    full_name = 'TEI Statistics'
    short_name = 'teistats'
    owners = ['node']
    configs = ['node']
    views = ['widget']
    categories = ['visualizations']
    has_hgrid_files = False
    node_settings_template = NODE_SETTINGS_TEMPLATE

    XPATH_EXPRESSION_ADDED = 'teistats_xpath_expression_added'
    XPATH_EXPRESSION_CHANGED = 'teistats_xpath_expression_changed'
    XPATH_EXPRESSION_REMOVED = 'teistats_xpath_expression_removed'

    actions = (XPATH_EXPRESSION_ADDED, XPATH_EXPRESSION_CHANGED, XPATH_EXPRESSION_REMOVED)

    @property
    def routes(self):
        from .routes import api_routes
        return [api_routes]

    @property
    def node_settings(self):
        return self.get_model('NodeSettings')
    

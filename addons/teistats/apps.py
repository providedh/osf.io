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
    views = ['widget', 'page']
    categories = ['visualizations']
    has_hgrid_files = False
    node_settings_template = NODE_SETTINGS_TEMPLATE

    XPATH_EXPRESSION_ADDED = 'teistats_xpath_expression_added'
    XPATH_EXPRESSION_CHANGED = 'teistats_xpath_expression_changed'
    XPATH_EXPRESSION_REMOVED = 'teistats_xpath_expression_removed'
    TEI_STATISTICS_START = 'teistats_statistics_start'
    TEI_STATISTICS_STOP = 'teistats_statistics_stop'
    TEI_STATISTICS_RESET = 'teistats_statistics_reset'

    actions = (XPATH_EXPRESSION_ADDED, XPATH_EXPRESSION_CHANGED, XPATH_EXPRESSION_REMOVED, TEI_STATISTICS_START,
               TEI_STATISTICS_STOP, TEI_STATISTICS_RESET)

    @property
    def routes(self):
        from .routes import page_routes, api_routes
        return [page_routes, api_routes]

    @property
    def node_settings(self):
        return self.get_model('NodeSettings')

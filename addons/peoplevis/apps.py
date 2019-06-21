from addons.base.apps import BaseAddonAppConfig


class PeopleVisAddonConfig(BaseAddonAppConfig):
    name = 'addons.peoplevis'
    label = 'addons_peoplevis'
    full_name = 'People Uncertainty Visualization'
    short_name = 'peoplevis'
    owners = ['node']
    views = ['page']
    categories = ['visualizations']
    has_hgrid_files = False

    @property
    def routes(self):
        from .routes import page_routes, api_routes
        return [page_routes, api_routes]
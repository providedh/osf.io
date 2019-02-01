from addons.base.apps import BaseAddonAppConfig


class TeiCloseAddonConfig(BaseAddonAppConfig):
    name = 'addons.teiclose'
    label = 'addons_teiclose'
    full_name = 'TEI Close Reading'
    short_name = 'teiclose'
    owners = ['node']
    views = ['page']
    categories = ['visualizations']
    has_hgrid_files = False

    TEI_CLOSE_READING_UPDATED = 'teiclose_file_updated'

    actions = (TEI_CLOSE_READING_UPDATED, )

    @property
    def routes(self):
        from .routes import page_routes, api_routes
        return [page_routes, api_routes]

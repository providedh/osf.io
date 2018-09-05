# -*- coding: utf-8 -*-

def settings_complete(node_addon):
    return not not node_addon.xpath_exprs

def serialize_teistats_widget(node):
    node_addon = node.get_addon('teistats')
    teistats_widget_data = {
        'complete': settings_complete(node_addon),
        'xpath_exprs': node_addon.xpath_exprs
    }
    teistats_widget_data.update(node_addon.config.to_json())
    return teistats_widget_data

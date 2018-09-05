# -*- coding: utf-8 -*-
import httplib as http

from flask import request

from framework.exceptions import HTTPError
from osf.exceptions import ValidationError
from website.project.decorators import (
    must_have_addon,
    must_have_permission,
    must_not_be_registration,
    must_be_valid_project)


@must_have_permission('write')
@must_not_be_registration
@must_have_addon('teistats', 'node')
def teistats_config_add_xpath(auth, node_addon, **kwargs):
    """Add XPath expression to the teistats node settings, adding a log if settings have changed.

    :param-json str with XPath expression and user-friendly name of it
    :raises: HTTPError(400) if values are missing or invalid

    """
    try:
        node_addon.add_xpath_expr(request.json)
    except ValidationError as e:
        raise HTTPError(
            http.BAD_REQUEST,
            data=dict(message_long=str(e.message))
        )

    # Add a log
    node_addon.owner.add_log(
         action='teistats_xpath_expression_added',
         params=dict(
             node=node_addon.owner._id,
             project=node_addon.owner.parent_id,
             xpath_expr=request.json.get('xpath')
         ),
         auth=auth,
         save=True,
    )

    return {}


@must_have_permission('write')
@must_not_be_registration
@must_have_addon('teistats', 'node')
def teistats_config_edit_xpath(auth, node_addon, **kwargs):
    """Edit XPath expression of the teistats node settings, adding a log if settings have changed.

    :param-json str with XPath expression, user-friendly name of it and field (pk) to change and new value
    :raises: HTTPError(400) if values are missing or invalid

    """
    field = request.json.pop('pk')
    value = request.json.pop('value', '')

    changed = False
    try:
        changed = node_addon.change_xpath_expr(request.json, field, value)
    except ValidationError as e:
        raise HTTPError(
            http.BAD_REQUEST,
            data=dict(message_long=str(e.message))
        )

    # Add a log
    if changed:
        node_addon.owner.add_log(
            action='teistats_xpath_expression_changed',
            params=dict(
                node=node_addon.owner._id,
                project=node_addon.owner.parent_id,
                xpath_expr=request.json.get('xpath')
            ),
            auth=auth,
            save=True,
        )

    return value


@must_have_permission('write')
@must_not_be_registration
@must_have_addon('teistats', 'node')
def teistats_config_remove_xpath(auth, node_addon, **kwargs):
    """Remove XPath expression from the teistats node settings, adding a log if settings have changed.

    :param-json str with XPath expression and user-friendly name of it
    :raises: HTTPError(400) if values missing or invalid

    """
    removed = node_addon.remove_xpath_expr(request.json)
    if not removed:
        raise HTTPError(
            http.BAD_REQUEST,
        )

    # Add a log
    node_addon.owner.add_log(
         action='teistats_xpath_expression_removed',
         params=dict(
             node=node_addon.owner._id,
             project=node_addon.owner.parent_id,
             xpath_expr=request.json.get('xpath')
         ),
         auth=auth,
         save=True,
    )

    return {}


@must_be_valid_project
@must_have_addon('teistats', 'node')
def teistats_config_get(node, node_addon, **kwargs):
    data = {
        'node': {
            'absolute_url': node.absolute_url,
            'xpath_exprs': node_addon.xpath_exprs,
        }
    }
    data.update({'is_registration': node.is_registration})
    return data

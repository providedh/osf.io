# -*- coding: utf-8 -*-
import httplib as http
import logging

from flask import request

from addons.teistats.models import TeiStatistics
from addons.teistats.tasks import calculate_tei_statistics
from framework.celery_tasks import app as celery_app
from framework.exceptions import HTTPError
from osf.exceptions import ValidationError
from website.profile.utils import get_profile_image_url
from website.project.decorators import check_contributor_auth
from website.project.decorators import (
    must_have_addon,
    must_have_permission,
    must_not_be_registration,
    must_be_valid_project)
from website.project.views.node import _view_project

logger = logging.getLogger(__name__)


@must_be_valid_project
@must_have_addon('teistats', 'node')
def teistats_get_main_vis(auth, node_addon, **kwargs):
    node = kwargs['node'] or kwargs['project']

    ret = {
        'category': node.category,
        'urls': {
            'api': '',
            'web': '',
            'profile_image': get_profile_image_url(auth.user, 25),
        },
    }
    ret.update(_view_project(node, auth, primary=True))
    return ret


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

    clear_node_statistics(node_addon.owner)

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

    clear_node_statistics(node_addon.owner)

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

    clear_node_statistics(node_addon.owner)

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


def clear_node_statistics(node):
    """Clear current statistics of all users for a given node and stops all tasks that are currently counting those statistocs.

    """

    for tei_statistics in TeiStatistics.objects.filter(node=node):
        task_id = tei_statistics.task_id
        if task_id:
            celery_app.control.revoke(task_id, terminate=True)
        tei_statistics.reset()
        tei_statistics.task_id = None
        tei_statistics.save()


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


@must_have_permission('read')
@must_be_valid_project
@must_have_addon('teistats', 'node')
def teistats_statistics_start(auth, node, node_addon, **kwargs):
    logger.debug(
        'Starting calculation TEI statistics for node {} (node_id = {}) by user {} (user_id = {}) called'.format(
            node.title, node.id, auth.user.username, auth.user.id))

    auth_redirect = check_contributor_auth(node, auth, include_public=True, include_view_only_anon=True)
    if auth_redirect:  # redirection to CAS, but we can't do that in backend
        raise HTTPError(
            http.UNAUTHORIZED,
        )

    try:
        tei_statistics = TeiStatistics.objects.get(node=node, owner=auth.user)
    except TeiStatistics.DoesNotExist:
        tei_statistics = TeiStatistics.objects.create(node=node, owner=auth.user)

    if tei_statistics.calculations['statistics'] and node.last_logged > tei_statistics.modified:
        # node has changed since last calculation
        logger.debug('Clearing TEI statistics of all users for node {}'.format(node))
        clear_node_statistics(node)

    if not tei_statistics.task_id:
        logger.debug('Running a celery task calculating TEI statistics for node_id {} by user_id {}'.format(node.id,
                                                                                                            auth.user.id))
        node_addon.owner.add_log(
            action='teistats_statistics_start',
            params=dict(
                node=node_addon.owner._id,
                project=node_addon.owner.parent_id
            ),
            auth=auth,
            save=True,
        )

        async_result = calculate_tei_statistics.delay(auth.user.id, node.id, node_addon.xpath_exprs, tei_statistics.id,
                                                      False, request.cookies, request.headers.get('HTTP_AUTHORIZATION'))
        tei_statistics.task_id = async_result.task_id
        tei_statistics.save(update_modified=False)

    return {}


@must_have_permission('read')
@must_be_valid_project
@must_have_addon('teistats', 'node')
def teistats_statistics_stop(auth, node, node_addon, **kwargs):
    logger.debug(
        'Stopping calculation TEI statistics for node {} (node_id = {}) by user {} (user_id = {}) called'.format(
            node.title, node.id, auth.user.username, auth.user.id))

    try:
        tei_statistics = TeiStatistics.objects.get(node=node, owner=auth.user)
        task_id = tei_statistics.task_id
        if task_id:
            celery_app.control.revoke(task_id, terminate=True)
        tei_statistics.task_id = None
        tei_statistics.save(update_modified=False)
        logger.debug('Celery task for node_id {} and user_id {} stopped'.format(node.id, auth.user.id))
    except Exception as e:
        logger.debug('Error while stopping celery task for node_id {} and user_id {}: {}'.format(node, auth.user, e))
        return {}

    # Add a log
    node_addon.owner.add_log(
        action='teistats_statistics_stop',
        params=dict(
            node=node_addon.owner._id,
            project=node_addon.owner.parent_id
        ),
        auth=auth,
        save=True,
    )

    return {}


@must_have_permission('read')
@must_be_valid_project
@must_have_addon('teistats', 'node')
def teistats_statistics_reset(auth, node, node_addon, **kwargs):
    try:
        tei_statistics = TeiStatistics.objects.get(node=node, owner=auth.user)
        tei_statistics.reset()
        tei_statistics.save(update_modified=True)
    except TeiStatistics.DoesNotExist:
        return {}

    # Add a log
    node_addon.owner.add_log(
        action='teistats_statistics_reset',
        params=dict(
            node=node_addon.owner._id,
            project=node_addon.owner.parent_id
        ),
        auth=auth,
        save=True,
    )

    return {}


@must_have_permission('read')
@must_be_valid_project
@must_have_addon('teistats', 'node')
def teistats_statistics_get(auth, node, node_addon, **kwargs):
    # return current statistics
    try:
        return TeiStatistics.objects.get(node=node, owner=auth.user).calculations
    except TeiStatistics.DoesNotExist:
        return TeiStatistics.EMPTY_CALCULATIONS

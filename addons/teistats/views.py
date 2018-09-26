# -*- coding: utf-8 -*-
import httplib as http
import logging
from StringIO import StringIO

import furl
import requests
from django.db import transaction
from django.utils.http import urlquote
from flask import request
from lxml import etree

from addons.teistats.models import TeiStatistics
from api.base.utils import waterbutler_api_url_for
from framework.exceptions import HTTPError
from osf.exceptions import ValidationError
from osf.models import BaseFileNode
from website import settings as website_settings
from website.project.decorators import check_contributor_auth
from website.project.decorators import (
    must_have_addon,
    must_have_permission,
    must_not_be_registration,
    must_be_valid_project)

logger = logging.getLogger(__name__)


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

    clear_statistics(node_addon.owner)

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

    clear_statistics(node_addon.owner)

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

    clear_statistics(node_addon.owner)

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


def clear_statistics(node):
    """Clear current statistics for a given node

    """
    try:
        tei_statistics = TeiStatistics.objects.get(node=node)
        tei_statistics.reset()
        tei_statistics.save()
    except TeiStatistics.DoesNotExist:
        TeiStatistics.objects.create(node=node)


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


@must_be_valid_project
@must_have_addon('teistats', 'node')
def teistats_statistics_get(auth, node, node_addon, **kwargs):
    """Calculate partial statistics and update those calculated last time, writing simultaneously to database the state for further computation.

    :param node: node for which statistic will be calculated
    :return: Updated statistics
    :raises: HTTPError if API does not respond as desired

    """
    logger.debug('Calculation TEI statistics for node {} by user {} called'.format(node, auth.user))
    auth_redirect = check_contributor_auth(node, auth, include_public=True, include_view_only_anon=True)
    if auth_redirect:  # redirection to CAS, but we can't do that in backend
        raise HTTPError(
            http.UNAUTHORIZED,
        )

    tei_statistics = lock_node(node)
    if not tei_statistics:
        # another thread is calculating statistics - return the current one
        return TeiStatistics.objects.get(node=node).calculations

    logger.debug('Calculation TEI statistics for node {} by user {} has started'.format(node, auth.user))
    try:
        if tei_statistics.calculations['statistics'] and node.last_logged > tei_statistics.modified:
            # if node has changed since last calculation
            tei_statistics.reset()
            tei_statistics.save(update_modified=True)

        if not tei_statistics.current_todos:
            # there is no next step
            providers = node_storage_providers(node)
            if not tei_statistics.current_provider:
                if not tei_statistics.calculations['statistics']:
                    # there is no current provider, get the first one
                    provider = providers[0]
                    logger.debug('Setting new provider {} for calculating TEI statistics for node {}'.format(provider, node))
                else:
                    # statistics are already calculated - return them
                    return tei_statistics.calculations
            else:
                if providers.index(tei_statistics.current_provider) + 1 < len(providers):
                    # get the next one
                    provider = providers[providers.index(tei_statistics.current_provider) + 1]
                    logger.debug('Setting next provider {} for calculating TEI statistics for node {}'.format(provider, node))
                else:
                    # no next provider, return calculated statistics - that's end
                    tei_statistics.current_provider = None
                    tei_statistics.set_finished()
                    tei_statistics.save(update_modified=True)
                    return tei_statistics.calculations
            # call API for the root of the provider
            api_url = api_url_for(node._id, provider)
            # change current provider
            tei_statistics.current_provider = provider
        elif tei_statistics.current_todos:
            # call the next step of API
            api_url = tei_statistics.current_todos[0].replace(website_settings.API_DOMAIN, website_settings.API_INTERNAL_DOMAIN, 1)
            # remove current call
            tei_statistics.current_todos.pop(0)

        api_json = call_api(api_url, request.cookies, request.headers.get('HTTP_AUTHORIZATION'))

        try:
            links = api_json['links']
            if 'next' in links and links['next']:
                tei_statistics.current_todos.append(links['next'])

            namespaces = {'tei': 'http://www.tei-c.org/ns/1.0'}
            for d in api_json['data']:
                if d['type'] == 'files':
                    if d['attributes']['kind'] == 'file':
                        file = get_file(d['id'])
                        if file:
                            waterbutler_url = waterbutler_api_url_for(node._id, tei_statistics.current_provider, file.path, True)
                            tei = call_waterbutler_quietly(waterbutler_url, request.cookies, request.headers.get('HTTP_AUTHORIZATION'))
                            if tei:
                                tei_statistics.inc_total_files()
                                try:
                                    tree = etree.parse(tei)
                                    tei_statistics.inc_tei_files()
                                    for xpath_expr in node_addon.xpath_exprs:
                                        xpath = xpath_expr['xpath']
                                        name = xpath_expr['name'] if 'name' in xpath_expr and xpath_expr['name'] else xpath
                                        statistic = get_or_create_statistic(name, tei_statistics)
                                        n = statistic.get('n')
                                        try:
                                            prefixed_xpath = prefix_xpath(xpath)
                                            nodeset = tree.xpath(prefixed_xpath, namespaces=namespaces)
                                            statistic.update({'n': n + len(nodeset)})
                                        except etree.XPathEvalError:
                                            # XML -> incorrect XPath
                                            pass
                                except etree.XMLSyntaxError:
                                    # not XML -> not TEI
                                    pass
                    elif d['attributes']['kind'] == 'folder':
                        tei_statistics.current_todos.append(d['relationships']['files']['links']['related']['href'])

        except KeyError:
            # unexpected json from API -> omit data from this call
            pass

        tei_statistics.save(update_modified=True)
    finally:
        unlock_node(node)

    return TeiStatistics.objects.get(node=node).calculations


def lock_node(node):
    try:
        with transaction.atomic():
            tei_statistics = TeiStatistics.objects.filter(node=node, in_progress=False).select_for_update(True).get()
            tei_statistics.in_progress = True
            tei_statistics.save(update_modified=False)
            return tei_statistics
    except Exception as e:
        logger.debug('Another thread has already a lock: {}'.format(e))


def unlock_node(node):
    try:
        with transaction.atomic():
            tei_statistics = TeiStatistics.objects.filter(node=node, in_progress=True).select_for_update(True).get()
            tei_statistics.in_progress = False
            tei_statistics.save(update_modified=False)
    except Exception as e:
        logger.error('Error while releasing a lock: {}'.format(e))


def node_storage_providers(node):
    return [addon.config.short_name for addon in node.get_addons() if
                 addon.config.has_hgrid_files and addon.configured]


def api_url_for(node_id, provider, path='/', _internal=True, **kwargs):
    assert path.startswith('/'), 'Path must always start with /'
    url = furl.furl((website_settings.API_INTERNAL_DOMAIN if _internal else website_settings.API_DOMAIN) + 'v2')
    segments = ['nodes', node_id, 'files', provider] + path.split('/')[1:]
    url.path.segments.extend([urlquote(x) for x in segments])
    url.args.update(kwargs)
    return url.url


def call_api(url, cookies, auth_header):
    logger.debug('Calling API function: {}'.format(url))
    api_response = requests.get(
        url,
        cookies=cookies,
        headers={'Authorization': auth_header}
    )

    if api_response.status_code != 200:
        raise HTTPError(
            api_response.status_code,
        )
    try:
        return api_response.json()
    except ValueError:
        raise HTTPError(
            http.SERVICE_UNAVAILABLE,
        )


def call_waterbutler_quietly(url, cookies, auth_header):
    logger.debug('Calling WaterButler: {}'.format(url))
    download_response = requests.get(
        url,
        cookies=cookies,
        headers={'Authorization': auth_header}
    )

    if download_response.status_code == 200:
        try:
            return StringIO(download_response.content)
        except (IOError, UnicodeError) as e:
            logger.warn('Error while reading content from WaterButler: {}'.format(e))
            pass


def get_file(file_id):
    file = BaseFileNode.active.filter(_id=file_id).first()
    if file and file.is_file:
        return file


def get_or_create_statistic(name, tei_statistics):
    for statistic in tei_statistics.calculations['statistics']:
        if statistic.get('element') == name:
            return statistic
    statistic = {
         'element': name,
        'n': 0,
    }
    tei_statistics.calculations['statistics'].append(statistic)
    return statistic


def prefix_xpath(xpath):
    """For a given XPath expression that hasn't got any namespaces returns the 'tei' prefixed one.

    :param xpath: node for which statistic will be calculated
    :return: prefixed XPath expression

    """
    prefixed_xpath = ''
    empty = False
    for part in xpath.split('/'):
        if not part:
            prefixed_xpath += '/'
            empty = True
            continue
        if not empty:
            prefixed_xpath += '/'
        empty = False
        if not part.startswith('*') and not part.startswith('@'):
            prefixed_xpath += 'tei:'
        prefixed_xpath += part
    return prefixed_xpath
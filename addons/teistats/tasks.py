# -*- coding: utf-8 -*-
import httplib as http
import logging
import re
import time
from StringIO import StringIO

import furl
import requests
from django.db import transaction
from django.utils.http import urlquote
from lxml import etree

from addons.teistats.models import TeiStatistics
from api.base.utils import waterbutler_api_url_for
from framework.celery_tasks import app as celery_app
from framework.exceptions import HTTPError
from osf.models import BaseFileNode
from osf.models.node import AbstractNode
from website import settings as website_settings

logger = logging.getLogger(__name__)


@celery_app.task(name='calculate_tei_statistics', bind=True)
def calculate_tei_statistics(self, user_id, node_id, xpath_exprs, tei_statistics_id, all_providers, cookies, auth_header):
    logger.debug('Calculation TEI statistics for node_id {} by user_id {} has started'.format(node_id, user_id))
    node = AbstractNode.objects.get(id=node_id)

    time.sleep(5)
    tei_statistics = TeiStatistics.objects.get(id=tei_statistics_id)
    providers = node_storage_providers(node, all_providers)
    while providers:
        if not tei_statistics.current_todos:
            # there is no next step
            if not tei_statistics.current_provider:
                if not tei_statistics.calculations['statistics']:
                    # there is no current provider, get the first one
                    provider = providers[0]
                    logger.debug(
                        'Setting new provider {} for calculating TEI statistics for node_id {} and user_id {}'.format(
                            provider, node_id, user_id))
                else:
                    # statistics are already calculated
                    logger.debug(
                        'TEI statistics are already calculated for node_id {} and user_id {}'.format(node_id, user_id))
                    break
            else:
                if providers.index(tei_statistics.current_provider) + 1 < len(providers):
                    # get the next one
                    provider = providers[providers.index(tei_statistics.current_provider) + 1]
                    logger.debug(
                        'Setting next provider {} for calculating TEI statistics for node_id {} and user_id {}'.format(
                            provider, node_id, user_id))
                else:
                    # no next provider, that's end
                    logger.debug(
                        'There is no next provider for calculating TEI statistics for node_id {} and user_id {}'.format(
                            node_id, user_id))
                    tei_statistics.current_provider = None
                    tei_statistics.set_finished()
                    save_tei_statistics(tei_statistics, True, node_id, user_id)
                    break
            # call API for the root of the provider
            api_url = api_url_for(node, provider)
            # change current provider
            tei_statistics.current_provider = provider
            save_tei_statistics(tei_statistics, False, node_id, user_id)
        else:
            # call the next step of API
            api_url = tei_statistics.current_todos[0].replace(website_settings.API_DOMAIN,
                                                              website_settings.API_INTERNAL_DOMAIN, 1)
            # remove current call
            tei_statistics.current_todos.pop(0)
            save_tei_statistics(tei_statistics, False, node_id, user_id)

        try:
            api_json = call_api(api_url, cookies, auth_header)
        except Exception as e:
            logger.error(
                'Error while calling API in calculating TEI statistics for node_id {} and user_id {}: {}'.format(
                    node_id, user_id, e))
            continue

        try:
            links = api_json['links']
            if 'next' in links and links['next']:
                tei_statistics.current_todos.append(links['next'])

            namespaces = {'tei': 'http://www.tei-c.org/ns/1.0'}
            for d in api_json['data']:
                if d['type'] == 'files':
                    if d['attributes']['kind'] == 'file':
                        file = get_file(d['id'])
                        if file and file.get_version().metadata['is_tei_p5_unprefixed']:
                            waterbutler_url = waterbutler_api_url_for(node._id, tei_statistics.current_provider,
                                                                      file.path, True)
                            file_response = call_waterbutler_quietly(waterbutler_url, cookies, auth_header)
                            if file_response:
                                tei_statistics.inc_total_files()
                                try:
                                    tree = etree.fromstring(file_response.content)
                                    tei_statistics.inc_tei_files()
                                    lines = len(file_response.text.split('\n'))
                                    tei_statistics.update_max_lines(lines)
                                    for xpath_expr in xpath_exprs:
                                        xpath = xpath_expr['xpath']
                                        name = xpath_expr['name'] if 'name' in xpath_expr and xpath_expr[
                                            'name'] else xpath
                                        statistic = get_or_create_statistic(name, tei_statistics)
                                        n = statistic.get('n')
                                        percentages = statistic.get('percentages')
                                        try:
                                            prefixed_xpath = prefix_xpath(xpath)
                                            nodeset = tree.xpath(prefixed_xpath, namespaces=namespaces)
                                            if len(nodeset):
                                                parent_string = stringify_children(nodeset[0].getparent()).encode(
                                                    'utf-8')
                                                k = nodeset[0].tag.rfind('}')
                                                bare_stripped = nodeset[0].tag[k + 1:] + ' '
                                                p = re.compile(bare_stripped)
                                                result_percentages = []
                                                for m in p.finditer(parent_string):
                                                    result_percentages.append(str(
                                                        int(100 * float(m.start()) / len(parent_string))))
                                                logger.debug('{} found at percentages {}'.format(bare_stripped,
                                                                                                 ', '.join(
                                                                                                     result_percentages)))
                                                for item in result_percentages:
                                                    if item in percentages:
                                                        percentages[item] += 1
                                                    else:
                                                        percentages[item] = 1
                                            logger.debug(percentages)
                                            statistic.update({'n': n + len(nodeset), 'percentages': percentages})

                                        except etree.XPathEvalError:
                                            # XML -> incorrect XPath
                                            pass
                                except etree.XMLSyntaxError:
                                    # not XML -> not TEI
                                    pass
                    elif d['attributes']['kind'] == 'folder':
                        tei_statistics.current_todos.append(d['relationships']['files']['links']['related']['href'])

                save_tei_statistics(tei_statistics, True, node_id, user_id)
        except KeyError:
            # unexpected json from API -> omit data from this call
            pass

    logger.debug('Calculation TEI statistics for node_id {} by user_id {} has finished'.format(node_id, user_id))
    tei_statistics.task_id = None
    save_tei_statistics(tei_statistics, False, node_id, user_id)


def stringify_children(node):
    from lxml.etree import tostring
    from itertools import chain
    parts = ([node.text] +
             list(chain(*([c.text, tostring(c), c.tail] for c in node.getchildren()))) + [node.tail])
    # filter removes possible Nones in texts and tails
    return ''.join(filter(None, parts))


def node_storage_providers(node, all_providers):
    node_providers = [addon.config.short_name for addon in node.get_addons() if
                      addon.config.has_hgrid_files and addon.configured]
    logger.debug('Node provoders node_id={}: {}'.format(node.id, node_providers))
    if all_providers:
        return node_providers
    else:
        if 'osfstorage' in node_providers:
            return ['osfstorage']
        else:
            return []


def save_tei_statistics(tei_statistics, update_modified, node_id, user_id):
    try:
        with transaction.atomic():
            tei_statistics.save(update_modified=update_modified)
    except Exception as e:
        logger.error('Error while saving TEI statistics for node_id {} and user_id {}'.format(
            node_id, user_id), e)


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
        'percentages': {}
    }
    tei_statistics.calculations['statistics'].append(statistic)
    return statistic


def api_url_for(node, provider, path='/', _internal=True, **kwargs):
    assert path.startswith('/'), 'Path must always start with /'
    url = furl.furl((website_settings.API_INTERNAL_DOMAIN if _internal else website_settings.API_DOMAIN) + 'v2')
    segments = ['nodes', node._id, 'files', provider] + path.split('/')[1:]
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
            return download_response
        except (IOError, UnicodeError) as e:
            logger.warn('Error while reading content from WaterButler: {}'.format(e))
            pass


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

import httplib as http
from flask import request
from osf.models import Guid, BaseFileNode
from framework.exceptions import HTTPError
from api.base.utils import waterbutler_api_url_for
from addons.teistats.tasks import call_waterbutler_quietly

import requests

import logging
logger = logging.getLogger(__name__)


def load_file(project_guid, file_guid, version=None):
    try:
        guid = Guid.objects.get(_id=file_guid)
        base_file_node = BaseFileNode.objects.get(id=guid.object_id)

    except (Guid.DoesNotExist, BaseFileNode.DoesNotExist):
        raise HTTPError(http.NOT_FOUND)

    provider = base_file_node.provider
    file_path = '/' + base_file_node._id

    if version:
        waterbutler_url = waterbutler_api_url_for(project_guid, provider, file_path, True, version=version)
    else:
        waterbutler_url = waterbutler_api_url_for(project_guid, provider, file_path, True)

    cookies = request.cookies
    auth_header = request.headers.get('HTTP_AUTHORIZATION')
    file_response = call_waterbutler_quietly(waterbutler_url, cookies, auth_header)

    text = file_response.content

    return text


def load_file_with_cookies(project_guid, file_guid, cookies, version=None):
    try:
        guid = Guid.objects.get(_id=file_guid)
        base_file_node = BaseFileNode.objects.get(id=guid.object_id)

    except (Guid.DoesNotExist, BaseFileNode.DoesNotExist):
        raise HTTPError(http.NOT_FOUND)

    provider = base_file_node.provider
    file_path = '/' + base_file_node._id

    if version:
        waterbutler_url = waterbutler_api_url_for(project_guid, provider, file_path, True, version=version)
    else:
        waterbutler_url = waterbutler_api_url_for(project_guid, provider, file_path, True)

    auth_header = None
    file_response = call_waterbutler_quietly(waterbutler_url, cookies, auth_header)

    text = file_response.content

    return text


def save_file(project_id, file_id, text):
    try:
        guid = Guid.objects.get(_id=file_id)
        base_file_node = BaseFileNode.objects.get(id=guid.object_id)

    except (Guid.DoesNotExist, BaseFileNode.DoesNotExist):
        raise HTTPError(http.NOT_FOUND)

    provider = base_file_node.provider
    file_path = '/' + base_file_node._id

    waterbutler_url = waterbutler_api_url_for(project_id, provider, file_path, True)

    cookies = request.cookies
    auth_header = request.headers.get('HTTP_AUTHORIZATION')

    file_response = call_waterbutler_quietly_put(waterbutler_url, text, cookies, auth_header)


def call_waterbutler_quietly_put(url, data, cookies, auth_header):
    logger.debug('Calling WaterButler: {}'.format(url))

    upload_response = requests.put(
        url,
        data,
        cookies=cookies,
        headers={'Authorization': auth_header}
    )

    if upload_response.status_code == 200:
        try:
            return upload_response
        except (IOError, UnicodeError) as e:
            logger.warn('Error while sending content to WaterButler: {}'.format(e))
            pass

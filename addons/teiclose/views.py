# -*- coding: utf-8 -*-
import httplib as http
import logging
import json

from framework.auth.decorators import collect_auth
from framework.exceptions import HTTPError
from osf.models import (
    Guid,
    BaseFileNode,
)
from website.profile.utils import get_profile_image_url
from website.project.decorators import (
    must_have_permission,
    must_not_be_registration,
    must_be_valid_project,
    must_have_read_permission_or_be_public)
from website.project.views.node import _view_project


from addons.teiclose.annotation_history_handler import AnnotationHistoryHandler
from addons.teiclose.annotator import Annotator

from flask import request
from framework.sessions import get_session

from .file_loader import load_text, save_text


logger = logging.getLogger(__name__)


@must_be_valid_project
@collect_auth
@must_have_read_permission_or_be_public
def teiclose_get_main_vis(**kwargs):
    node = kwargs['node'] or kwargs['project']
    auth = kwargs['auth']
    file_id = kwargs['file_id']
    file_version = kwargs['file_ver']
    project_guid = kwargs['pid']

    try:
        guid = Guid.objects.get(_id=file_id)
        base_file_node = BaseFileNode.objects.get(id=guid.object_id)
    except (Guid.DoesNotExist, BaseFileNode.DoesNotExist) as e:
        raise HTTPError(
            http.NOT_FOUND,
        )

    annotation_history_handler = AnnotationHistoryHandler(project_guid, file_id)
    annotation_history_handler.update_history()

    ret = {
        'file': {
            'id': file_id,
            'filename': base_file_node.name,
            'provider': base_file_node.provider,
            'path': base_file_node._id,
            'addon_url': node.url + 'teiclose/' + file_id + '/' + file_version + '/',
            'version': file_version,
        },
        'category': node.category,
        'urls': {
            'api': '',
            'web': '',
            'profile_image': get_profile_image_url(auth.user, 25),
        },
    }
    ret.update(_view_project(node, auth, primary=True))
    return ret



# @must_have_permission('write')
# @must_not_be_registration
def teiclose_annotation_add(**kwargs):
    file_id = kwargs['file_guid']
    project_guid = kwargs['project_guid']

    current_session = get_session()
    user_guid = current_session.data['auth_user_id']

    request_json = json.loads(request.data)

    file_key = '_'.join(('xml_text', project_guid, file_id))

    if file_key not in current_session.data:
        xml_text = load_text(project_guid, file_id)
        current_session.data[file_key] = xml_text

    xml_text = load_text(project_guid, file_id)     #   TYLKO DO TESTÓW
    current_session.data[file_key] = xml_text     #

    xml_text = current_session.data[file_key]

    annotator = Annotator()
    xml_text = annotator.add_annotation(xml_text, request_json, user_guid)
    current_session.data[file_key] = xml_text
    current_session.save()

    return current_session.data[file_key]


def teiclose_annotation_save(**kwargs):
    file_id = kwargs['file_guid']
    project_guid = kwargs['project_guid']

    current_session = get_session()

    file_key = '_'.join(('xml_text', project_guid, file_id))

    if file_key not in current_session.data:
        return {'message': 'Nothing to save.'}

    else:
        xml_text = current_session.data[file_key]


        xml_text = xml_text.encode('utf-8')
        # tu będzie upload pliku
        save_text(project_guid, file_id, xml_text)


        # usunięcie pliku z sesji
        # current_session.data.pop(file_key, None)
        return {'message': 'File saved.'}




def teiclose_get_annotation_history(**kwargs):
    file_id = kwargs['file_id']
    project_guid = kwargs['pid']
    file_version = int(kwargs['file_ver'])

    annotation_history_handler = AnnotationHistoryHandler(project_guid, file_id)
    history = annotation_history_handler.get_history(file_version)

    return history





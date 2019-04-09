# -*- coding: utf-8 -*-
import json
import httplib as http
from flask import request

from framework.auth.decorators import collect_auth
from framework.exceptions import HTTPError
from osf.models import (
    Guid,
    BaseFileNode,
)
from framework.sessions import get_session

from website.profile.utils import get_profile_image_url
from website.project.decorators import (
    must_have_permission,
    must_not_be_registration,
    must_be_valid_project,
    must_have_read_permission_or_be_public)
from website.project.views.node import _view_project

from addons.teiclose.annotation_history_handler import AnnotationHistoryHandler
from addons.teiclose.annotator import Annotator
from addons.teiclose.file_loader import load_text, save_text


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
def teiclose_add_annotation(**kwargs):
    file_guid = kwargs['file_guid']
    project_guid = kwargs['project_guid']

    current_session = get_session()
    user_guid = current_session.data['auth_user_id']

    request_json = json.loads(request.data)

    file_key = '_'.join(('xml_text', project_guid, file_guid))

    if file_key not in current_session.data:
        xml_text = load_text(project_guid, file_guid)
        current_session.data[file_key] = xml_text

    xml_text = load_text(project_guid, file_guid)   # ONLY FOR TESTS - RELOAD DEFAULT FILE TO current_session.data
    current_session.data[file_key] = xml_text       # ONLY FOR TESTS - RELOAD DEFAULT FILE TO current_session.data

    xml_text = current_session.data[file_key]

    annotator = Annotator()
    xml_text = annotator.add_annotation(xml_text, request_json, user_guid)
    current_session.data[file_key] = xml_text
    current_session.save()

    return current_session.data[file_key]


def teiclose_save_annotations(**kwargs):
    file_guid = kwargs['file_guid']
    project_guid = kwargs['project_guid']

    current_session = get_session()

    file_key = '_'.join(('xml_text', project_guid, file_guid))

    if file_key not in current_session.data:
        return '', 404

    else:
        xml_text = current_session.data[file_key]
        xml_text = xml_text.encode('utf-8')

        save_text(project_guid, file_guid, xml_text)

        current_session.data.pop(file_key, None)

        return '', 200


def teiclose_get_annotation_history(**kwargs):
    file_guid = kwargs['file_guid']
    project_guid = kwargs['project_guid']
    file_version = int(kwargs['file_ver'])

    annotation_history_handler = AnnotationHistoryHandler(project_guid, file_guid)
    history = annotation_history_handler.get_history(file_version)

    return history

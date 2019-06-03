
import json

from addons.teiclose.annotator import Annotator
from addons.teiclose.waterbutler_file_handler import load_file_with_cookies
from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
from channels_presence.models import Room
from channels_presence.decorators import touch_presence
from models import AnnotatingXmlContent
from osf.models import Session


@channel_session_user_from_http
def ws_connect(message):
    room_symbol = get_room_symbol(message)
    cookies = get_cookies_for_waterbutler(message)

    try:
        user_guid = get_user_guid(cookies)
        message.channel_session['user_guid'] = user_guid

    except Exception as exception:
        response = {
            'status': 401,
            'message': exception.message,
            'xml_content': None,
        }

        response = json.dumps(response)
        message.reply_channel.send(response)
        return

    try:
        annotating_xml_content = AnnotatingXmlContent.objects.get(file_symbol=room_symbol)

    except AnnotatingXmlContent.DoesNotExist:
        project_guid, file_guid = room_symbol.split('_')

        xml_content = load_file_with_cookies(project_guid, file_guid, cookies)
        xml_content = xml_content.decode('utf-8')

        annotating_xml_content = AnnotatingXmlContent(file_symbol=room_symbol, xml_content=xml_content)
        annotating_xml_content.save()

    Group(room_symbol).add(message.reply_channel)
    Room.objects.add(room_symbol, message.reply_channel.name, message.user)

    response = {
        'status': 200,
        'message': 'OK',
        'xml_content': annotating_xml_content.xml_content,
    }

    response = json.dumps(response)

    message.reply_channel.send({'text': response})


@touch_presence
@channel_session_user
def ws_message(message):
    room_symbol = get_room_symbol(message)
    request_json = message.content['text']

    annotating_xml_content = AnnotatingXmlContent.objects.get(file_symbol=room_symbol)
    xml_content = annotating_xml_content.xml_content

    user_guid = message.channel_session['user_guid']

    request_json = json.loads(request_json)

    try:
        annotator = Annotator()
        xml_content = annotator.add_annotation(xml_content, request_json, user_guid)

        annotating_xml_content.xml_content = xml_content
        annotating_xml_content.save()

        response = {
            'status': 200,
            'message': 'OK',
            'xml_content': annotating_xml_content.xml_content,
        }

        response = json.dumps(response)

        Group(room_symbol).send({'text': response})

    except (ValueError, TypeError) as error:
        response = {
            'status': 400,
            'message': error.message,
            'xml_content': None,
        }

        response = json.dumps(response)

        message.reply_channel.send(response)


@channel_session_user
def ws_disconnect(message):
    room_symbol = get_room_symbol(message)

    room = Room.objects.get(channel_name=room_symbol)
    users_connected = room.get_anonymous_count()

    if users_connected < 2:
        annotating_xml_content = AnnotatingXmlContent.objects.get(file_symbol=room_symbol)
        annotating_xml_content.delete()

    Group(room_symbol).discard(message.reply_channel)
    Room.objects.remove(room_symbol, message.reply_channel.name)


def get_room_symbol(message):
    room_symbol = message['path'].strip('/').split('/')[-1]

    return room_symbol


def get_cookies_for_waterbutler(message):
    cookies = dict(message.content['headers'])['cookie']
    cookies = cookies.split('; ')

    cookies_for_waterbutler = {}

    for cookie in cookies:
        parts = cookie.split('=')
        cookies_for_waterbutler.update({parts[0]: parts[1]})

    return cookies_for_waterbutler


def get_user_guid(cookies):
    osf_id = cookies['osf']
    osf_id = osf_id.split('.')[0]

    try:
        osf_session = Session.objects.get(_id=osf_id)
    except Session.DoesNotExist:
        raise Exception("No session in database for this user.")

    if "auth_user_id" not in osf_session.data:
        raise Exception("User unauthenticated.")
    else:
        return osf_session.data["auth_user_id"]

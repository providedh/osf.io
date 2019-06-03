from channels import Group
import json

from channels.sessions import channel_session
from channels.auth import channel_session_user, channel_session_user_from_http

from pprint import pprint
from models import AnnotatingXmlContent
from addons.teiclose.waterbutler_file_handler import load_file_with_cookies

from addons.teiclose.annotator import Annotator
from framework.sessions import get_session

from channels_presence.models import Room
from channels_presence.decorators import touch_presence


# @channel_session
@channel_session_user_from_http
def ws_connect(message):
    room_symbol = get_room_symbol(message)

    try:
        annotating_xml_content = AnnotatingXmlContent.objects.get(file_symbol=room_symbol)
    except AnnotatingXmlContent.DoesNotExist:
        project_guid, file_guid = room_symbol.split('_')
        cookies = get_cookies_for_waterbutler(message)

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

    # Temporary hardcoded user giud (user with this guid must be in database)
    # TODO: Get user guid from session
    user_guid = 'wenuq'

    request_json = json.loads(request_json)

    room = Room.objects.get(channel_name=room_symbol)
    userzy = room.get_anonymous_count()

    print 'USERZY ANONIMOWI: %s' % userzy

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






    # print '\n'              #
    # pprint(message)         #
    # print '\n'              #
    # pprint(vars(message))   # to print object variables to console
    # print '\n'              #

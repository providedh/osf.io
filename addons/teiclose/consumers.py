from channels import Group

from channels.auth import channel_session_user, channel_session_user_from_http

from pprint import pprint
from models import AnnotatingXmlContent
from addons.teiclose.waterbutler_file_handler import load_file_with_cookies


@channel_session_user_from_http
def ws_connect(message):
    room_symbol = get_room_symbol(message)

    try:
        annotating_xml_content = AnnotatingXmlContent.objects.get(file_symbol=room_symbol)
    except AnnotatingXmlContent.DoesNotExist:
        project_guid, file_guid = room_symbol.split('_')
        cookies = get_cookies_for_waterbutler(message)

        xml_content = load_file_with_cookies(project_guid, file_guid, cookies)

        annotating_xml_content = AnnotatingXmlContent(file_symbol=room_symbol, xml_content=xml_content)
        annotating_xml_content.save()

    Group(room_symbol).add(message.reply_channel)
    message.reply_channel.send({'text': annotating_xml_content.xml_content})



def ws_message(message):
    room_symbol = get_room_symbol(message)

    recived_text = message.content['text']

    print recived_text

    # Group(room_symbol).send({'text': recived_text})



def ws_disconnect(message):
    room_symbol = get_room_symbol(message)

    Group(room_symbol).send({'text': 'disconnected'})
    Group(room_symbol).discard(message.reply_channel)


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

from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http

from pprint import pprint


def ws_connect(message):
    room_symbol = get_room_symbol(message)

    Group(room_symbol).add(message.reply_channel)
    Group(room_symbol).send({'text': 'connected'})

def ws_message(message):
    room_symbol = get_room_symbol(message)

    recived_text = message.content['text']

    Group(room_symbol).send({'text': recived_text})



def ws_disconnect(message):
    room_symbol = get_room_symbol(message)

    Group(room_symbol).send({'text': 'disconnected'})
    Group(room_symbol).discard(message.reply_channel)


def get_room_symbol(message):
    room_symbol = message['path'].strip('/').split('/')[-1]

    return room_symbol





    # print '\n'              #
    # pprint(message)         #
    # print '\n'              #
    # pprint(vars(message))   # to print object variables to console
    # print '\n'              #

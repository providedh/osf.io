from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http


def ws_connect(message):
    Group('channel_test').add(message.reply_channel)
    Group('channel_test').send({'text': 'connected'})

def ws_message(message):
    recived_text = message.content['text']

    Group('channel_test').send({'text': recived_text})

def ws_disconnect(message):
    Group('channel_test').send({'text': 'disconnected'})
    Group('channel_test').discard(message.reply_channel)



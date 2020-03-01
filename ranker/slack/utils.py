import random
import string as _string

from ranker.slack import bot_token


def strip_id(string):
    """ Extract SlackID from Slack user string """
    user_start = string.find('<')
    user_index = string.find('@')
    user_trans = string.find('|')
    user_end = string.find('>')
    if user_start == -1 or user_index == -1 or user_trans == -1 or user_end == -1:
        return string
    return string[user_index+1:user_trans]


def rotate_token():
    bot_token["bearer"] = ''.join(random.choice(_string.ascii_lowercase) for _ in range(64))
    return bot_token["bearer"]

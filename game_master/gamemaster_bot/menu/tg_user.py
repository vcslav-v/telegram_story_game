import json
from os import environ

import requests
from gamemaster_bot import tools
from gamemaster_bot.menu import story

DB_URL = environ.get('DB_URL') or 'http://127.0.0.1:8000/{item}/{cmd}'

SHOW_STORIES_PREFIX = 'show_all_stories_tg_user?'


class TelegramUser:
    """Telegram user."""

    def __init__(self, tg_id: int):
        user_resp = json.loads(
            requests.post(
                DB_URL.format(item='telegram_user', cmd='get'),
                json={'tg_id': tg_id},
            ).text
        )
        self.id = int(user_resp['id'])
        self.telegram_id = int(user_resp['telegram_id'])
        self.stories = [story.Story(story_resp['id']) for story_resp in user_resp['stories']]

    def show_stories(self):
        msg = 'Ваши истории.'
        buttons = {}
        for _story in self.stories:
            buttons.update(
                {_story.name: tools.make_call_back(story.SHOW_PREFIX, {
                    'story_id': _story.id
                })}
            )
        buttons.update(
                {'Создать историю': tools.make_call_back(story.MAKE_PREFIX)}
            )

        tools.send_menu_msg(self.telegram_id, msg, buttons)

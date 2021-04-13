import json
from os import environ
from gamemaster_bot import mem, tools
from gamemaster_bot.menu import tg_user

import requests

DB_URL = environ.get('DB_URL') or 'http://127.0.0.1:8000/{item}/{cmd}'
SHOW_PREFIX = 'show_story?'
MAKE_PREFIX = 'make_story?'
RENAME_PREFIX = 'rename_story?'
RM_PREFIX = 'rm_story?'


def get_name_for_new_story(tg_id: int):
    msg = 'Напишите название своей истории'
    tools.send_menu_msg(tg_id, msg, exit_menu=True)
    user_context = mem.UserContext(tg_id)
    user_context.set_status('wait_line')
    user_context.set_params(
        {
            'call_to': MAKE_PREFIX,
        }
    )


def make_new_story(tg_id: int, story_name: str):
    new_story_resp = json.loads(
            requests.post(
                DB_URL.format(item='story', cmd='make'),
                json={
                    'tg_id': tg_id,
                    'story_name': story_name,
                },
            ).text
        )
    _story = Story(new_story_resp['id'])
    _story.show(tg_id)


class Story:
    """Story."""
    def __init__(self, story_id: int):
        story_resp = json.loads(
            requests.post(
                DB_URL.format(item='story', cmd='get'),
                json={'story_id': story_id},
            ).text
        )
        self.id = int(story_resp['id'])
        self.name = story_resp['name']
        self.author_id = int(story_resp['author_id'])

    def show(self, tg_id: int):
        msg = self.name
        user_context = mem.UserContext(tg_id)
        user_context.update_context('story_id', str(self.id))

        buttons = {
            'Переименовать': tools.make_call_back(RENAME_PREFIX),
            'Удалить': tools.make_call_back(RM_PREFIX, {'is_sure': False}),
            'Все истории': tools.make_call_back(tg_user.SHOW_STORIES_PREFIX),
        }
        tools.send_menu_msg(tg_id, msg, buttons)

    def make_sure_rm(self, tg_id: int):
        msg = 'Вы уверены, что хотите удалить историю: "{}"'.format(self.name)
        buttons = {
            'Да': tools.make_call_back(RM_PREFIX, {'is_sure': True}),
            'Нет': tools.make_call_back(SHOW_PREFIX),
        }
        tools.send_menu_msg(tg_id, msg, buttons)

    def rm(self, tg_id: int):
        result = json.loads(
            requests.post(
                DB_URL.format(item='story', cmd='rm'),
                json={
                    'story_id': self.id,
                    'tg_id': tg_id,
                },
            ).text
        )
        if result.get('result') == 'ok':
            msg = 'Успешно.'
        else:
            msg = result.get('error')

        buttons = {
            'Мои истории': tools.make_call_back(tg_user.SHOW_STORIES_PREFIX),
        }
        tools.send_menu_msg(tg_id, msg, buttons)

    def get_new_name(self, tg_id: int):
        msg = 'Напишите новое название для истории "{}"'.format(self.name)
        tools.send_menu_msg(tg_id, msg, exit_menu=True)
        user_context = mem.UserContext(tg_id)
        user_context.set_status('wait_line')
        user_context.set_params({'call_to': RENAME_PREFIX})

    def rename(self, tg_id: int, new_name: str):
        renamed_story_resp = json.loads(
            requests.post(
                DB_URL.format(item='story', cmd='rename'),
                json={
                    'story_id': self.id,
                    'tg_id': tg_id,
                    'new_name': new_name,
                },
            ).text
        )
        if renamed_story_resp.get('error'):
            msg = renamed_story_resp.get('error')
            tools.send_menu_msg(tg_id, msg)
        else:
            self.name = new_name
            self.show(tg_id)

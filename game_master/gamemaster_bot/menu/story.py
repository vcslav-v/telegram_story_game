import json
from gamemaster_bot import mem, tools, DB_URL
from gamemaster_bot.menu import tg_user, chapter

import requests

SHOW_PREFIX = 'show_story?'
MAKE_PREFIX = 'make_story?'
RENAME_PREFIX = 'rename_story?'
RM_PREFIX = 'rm_story?'
SHOW_CHAPTERS_PREFIX = 'show_story_chapters?'


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
        self.id = int(story_resp.get('id'))
        self.name = story_resp.get('name')
        self.author_id = int(story_resp.get('author_id'))
        self.chapters = sorted(
            story_resp.get('chapters'),
            key=lambda chapter: int(chapter.get('number'))
        )

    def show(self, tg_id: int):
        msg = self.name
        user_context = mem.UserContext(tg_id)
        user_context.update_context('story_id', str(self.id))

        buttons = [
            [('Посмотреть главы', tools.make_call_back(SHOW_CHAPTERS_PREFIX))],
            [('Переименовать', tools.make_call_back(RENAME_PREFIX))],
            [('Удалить', tools.make_call_back(RM_PREFIX, {'is_sure': False}))],
            [('Все истории', tools.make_call_back(tg_user.SHOW_STORIES_PREFIX))],
        ]
        tools.send_menu_msg(tg_id, msg, buttons)

    def make_sure_rm(self, tg_id: int):
        msg = 'Вы уверены, что хотите удалить историю: "{}"'.format(self.name)
        buttons = [
            [('Да', tools.make_call_back(RM_PREFIX, {'is_sure': True}))],
            [('Нет', tools.make_call_back(SHOW_PREFIX))],
        ]
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

        buttons = [
            [('Мои истории', tools.make_call_back(tg_user.SHOW_STORIES_PREFIX))],
        ]
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

    def show_chapters(self, tg_id: int):
        msg = 'Главы истории {}.'.format(self.name)
        buttons = []
        for _chapter in self.chapters:
            buttons.append(
                [
                    (
                        _chapter.get('name'),
                        tools.make_call_back(chapter.SHOW_PREFIX, {
                            'chapter_id': _chapter.get('id')
                        })
                    ),
                ]
            )
            settings_row = []
            if int(_chapter.get('number')) != 0:
                settings_row.append(
                        (
                            'Up', tools.make_call_back(chapter.UP_PREFIX, {
                                'chapter_id': _chapter.get('id'),
                            })
                        )
                )
            if int(_chapter.get('number')) != len(self.chapters) - 1:
                settings_row.append(
                        (
                            'Down', tools.make_call_back(chapter.DOWN_PREFIX, {
                                'chapter_id': _chapter.get('id'),
                            })
                        )
                )
            buttons.append(settings_row)
        buttons.extend([
                [('Новая глава', tools.make_call_back(chapter.MAKE_PREFIX))],
                [('Назад', tools.make_call_back(SHOW_PREFIX))],
        ])

        tools.send_menu_msg(tg_id, msg, buttons, 3)

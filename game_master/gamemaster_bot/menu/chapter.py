from gamemaster_bot import tools, mem, DB_URL, APP_URL
from gamemaster_bot.menu import story, message

import hashlib
import requests
import json

SHOW_PREFIX = 'show_chapter?'
MAKE_PREFIX = 'make_chapter?'
RENAME_PREFIX = 'rename_chapter?'
RM_PREFIX = 'rm_chapter?'
UP_PREFIX = 'up_chapter?'
DOWN_PREFIX = 'down_chapter?'
REF_BLOCK_PREFIX = 'ref_block_chapter?'


def get_name_for_new_chapter(tg_id: int):
    msg = 'Напишите название новой главы'
    tools.send_menu_msg(tg_id, msg, exit_menu=True)
    user_context = mem.UserContext(tg_id)
    user_context.set_status('wait_line')
    user_context.set_params(
        {
            'call_to': MAKE_PREFIX,
        }
    )


def make_new_chapter(tg_id: int, chapter_name: str):
    user_context = mem.UserContext(tg_id)
    new_chapter_resp = json.loads(
            requests.post(
                DB_URL.format(item='chapter', cmd='make'),
                json={
                    'tg_id': tg_id,
                    'story_id': user_context.get_context('story_id'),
                    'chapter_name': chapter_name,
                },
            ).text
        )
    _chapter = Chapter(user_context.get_context('story_id'), new_chapter_resp.get('id'))
    _chapter.show(tg_id)


class Chapter:
    def __init__(self, story_id: int, chapter_id: int):
        chapter_resp = json.loads(
            requests.post(
                DB_URL.format(item='chapter', cmd='get'),
                json={'story_id': story_id, 'chapter_id': chapter_id},
            ).text
        )
        first_msg = json.loads(
            requests.post(
                DB_URL.format(item='message', cmd='get_start_for_chapter'),
                json={'chapter_id': chapter_id},
            ).text
        )
        self.id = int(chapter_resp.get('id'))
        self.name = chapter_resp.get('name')
        self.number = int(chapter_resp.get('number'))
        self.story_id = int(chapter_resp.get('story_id'))
        self.start_message = first_msg

    def show(self, tg_id: int):
        msg = f'id: {self.id}\n{self.name}'
        user_context = mem.UserContext(tg_id)
        user_context.update_context('chapter_id', str(self.id))

        if self.start_message:
            buttons = [[
                (
                    'Все сообщения',
                    None,
                    '{app_url}chapter/{chapter_uid}'.format(
                        app_url=APP_URL,
                        chapter_uid=hashlib.sha224(bytes(f'{self.id}{tg_id}', 'utf-8')).hexdigest(),
                    )
                )
            ]]
        else:
            buttons = [
                [('Написать первое сообщение', tools.make_call_back(message.MAKE_PREFIX, {
                    'is_start_chapter_msg': True,
                }))]
            ]

        buttons.extend([
            [
                ('Установить ref-block', tools.make_call_back(REF_BLOCK_PREFIX)),
                ('Переименовать', tools.make_call_back(RENAME_PREFIX)),
                ('Удалить', tools.make_call_back(RM_PREFIX, {'is_sure': False})),
            ],
            [
                ('Все главы', tools.make_call_back(story.SHOW_CHAPTERS_PREFIX)),
            ],
        ])
        tools.send_menu_msg(tg_id, msg, buttons)

    def replace(self, new_num: int, tg_id: int):
        up_chapter_resp = json.loads(
            requests.post(
                DB_URL.format(item='chapter', cmd='replace'),
                json={
                    'story_id': self.story_id,
                    'tg_id': tg_id,
                    'chapter_id': self.id,
                    'new_num': new_num,
                },
            ).text
        )
        if up_chapter_resp.get('error'):
            msg = up_chapter_resp.get('error')
            tools.send_menu_msg(tg_id, msg)
        else:
            story.Story(self.story_id).show_chapters(tg_id)

    def make_sure_rm(self, tg_id: int):
        msg = 'Вы уверены, что хотите удалить главу: "{}"'.format(self.name)
        buttons = [
            [('Да', tools.make_call_back(RM_PREFIX, {'is_sure': True}))],
            [('Нет', tools.make_call_back(story.SHOW_CHAPTERS_PREFIX))],
        ]
        tools.send_menu_msg(tg_id, msg, buttons)

    def rm(self, tg_id: int):
        result = json.loads(
            requests.post(
                DB_URL.format(item='chapter', cmd='rm'),
                json={
                    'story_id': self.story_id,
                    'tg_id': tg_id,
                    'chapter_id': self.id
                },
            ).text
        )
        if result.get('result') == 'ok':
            msg = 'Успешно.'
        else:
            msg = result.get('error')

        buttons = [
            [('Все главы', tools.make_call_back(story.SHOW_CHAPTERS_PREFIX))],
        ]
        tools.send_menu_msg(tg_id, msg, buttons)

    def get_new_name(self, tg_id: int):
        msg = 'Напишите новое название для главы "{}"'.format(self.name)
        tools.send_menu_msg(tg_id, msg, exit_menu=True)
        user_context = mem.UserContext(tg_id)
        user_context.set_status('wait_line')
        user_context.set_params({'call_to': RENAME_PREFIX})

    def set_ref_block(self, tg_id: int, ref_block: int):
        chapter_resp = json.loads(
            requests.post(
                DB_URL.format(item='chapter', cmd='set_ref_block'),
                json={
                    'story_id': self.story_id,
                    'tg_id': tg_id,
                    'chapter_id': self.id,
                    'ref_block': ref_block,
                },
            ).text
        )
        if chapter_resp.get('error'):
            msg = chapter_resp.get('error')
            tools.send_menu_msg(tg_id, msg)
        else:
            self.show(tg_id)

    def get_ref_block(self, tg_id: int):
        msg = 'Кол-во рефералов для доступа к главе'
        tools.send_menu_msg(tg_id, msg, exit_menu=True)
        user_context = mem.UserContext(tg_id)
        user_context.set_status('wait_line')
        user_context.set_params({'call_to': REF_BLOCK_PREFIX})

    def rename(self, tg_id: int, new_name: str):
        renamed_chapter_resp = json.loads(
            requests.post(
                DB_URL.format(item='chapter', cmd='rename'),
                json={
                    'story_id': self.story_id,
                    'chapter_id': self.id,
                    'tg_id': tg_id,
                    'new_name': new_name,
                },
            ).text
        )
        if renamed_chapter_resp.get('error'):
            msg = renamed_chapter_resp.get('error')
            tools.send_menu_msg(tg_id, msg)
        else:
            self.name = new_name
            self.show(tg_id)

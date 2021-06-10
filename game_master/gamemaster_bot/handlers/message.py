from gamemaster_bot import bot
from gamemaster_bot import tools, mem
from gamemaster_bot.menu import message
import os
from loguru import logger

@bot.callback_query_handler(
    func=tools.is_correct_prefix(message.MAKE_PREFIX)
)
def make_msg(call):
    params = tools.get_call_back_params(call.data)
    message.get_new_msg(
        call.from_user.id,
        params.get('is_start_chapter_msg'),
        params.get('from_msg_id'),
        params.get('from_btn_id'),
    )


@bot.callback_query_handler(
    func=tools.is_correct_prefix(message.SHOW_PREFIX)
)
@logger.catch
def show_msg(call):
    user_context = mem.UserContext(call.from_user.id)
    params = tools.get_call_back_params(call.data)
    _message = message.Message(
        params.get('msg_id') or user_context.get_context('message_id'),
        )
    _message.show(call.from_user.id)


@bot.callback_query_handler(
    func=tools.is_correct_prefix(message.RM_PREFIX)
)
def rm_message(call):
    user_context = mem.UserContext(call.from_user.id)
    params = tools.get_call_back_params(call.data)
    _message = message.Message(
        int(user_context.get_context('message_id')),
    )
    if params.get('is_sure'):
        _message.rm(call.from_user.id)
    else:
        _message.make_sure_rm(call.from_user.id)


@bot.callback_query_handler(
    func=tools.is_correct_prefix(message.EDIT_PREFIX)
)
def edit_msg(call):
    user_context = mem.UserContext(call.from_user.id)
    _message = message.Message(
        user_context.get_context('message_id'),
        )
    _message.get_new_msg(call.from_user.id)


@bot.callback_query_handler(
    func=tools.is_correct_prefix(message.EDIT_REFERAL_BLOCK_PREFIX)
)
def edit_referal_block_msg(call):
    user_context = mem.UserContext(call.from_user.id)
    _message = message.Message(
        user_context.get_context('message_id'),
        )
    _message.get_line(call.from_user.id, 'Необходимое кол-во рефералов:', message.EDIT_REFERAL_BLOCK_PREFIX)


@bot.callback_query_handler(
    func=tools.is_correct_prefix(message.ADD_BUTTON_PREFIX)
)
def add_btn_msg(call):
    user_context = mem.UserContext(call.from_user.id)
    _message = message.Message(
        user_context.get_context('message_id'),
        )
    _message.get_new_btn(call.from_user.id)


@bot.callback_query_handler(
    func=tools.is_correct_prefix(message.RM_BUTTON_PREFIX)
)
def rm_btn_msg(call):
    params = tools.get_call_back_params(call.data)
    user_context = mem.UserContext(call.from_user.id)
    _message = message.Message(
        user_context.get_context('message_id'),
        )
    _message.rm_btn(call.from_user.id, params.get('btn_id'), params.get('is_sure'))


@bot.callback_query_handler(
    func=tools.is_correct_prefix(message.EDIT_BUTTON_PREFIX)
)
def edit_btn_msg(call):
    params = tools.get_call_back_params(call.data)
    user_context = mem.UserContext(call.from_user.id)
    _message = message.Message(
        user_context.get_context('message_id'),
        )
    _message.get_text_btn(call.from_user.id, params.get('btn_id'))


@bot.callback_query_handler(
    func=tools.is_correct_prefix(message.MOVE_BUTTON_PREFIX)
)
def move_btn(call):
    params = tools.get_call_back_params(call.data)
    user_context = mem.UserContext(call.from_user.id)
    _message = message.Message(
        user_context.get_context('message_id'),
        )
    _message.move_btn(call.from_user.id, params.get('move'), params.get('btn_id'))


@bot.callback_query_handler(
    func=tools.is_correct_prefix(message.CHANGE_REACTION_PREFIX)
)
def change_reaction(call):
    params = tools.get_call_back_params(call.data)
    user_context = mem.UserContext(call.from_user.id)
    _message = message.Message(
        user_context.get_context('message_id'),
        )
    _message.change_reaction(call.from_user.id, params.get('reaction_id'))


@bot.callback_query_handler(
    func=tools.is_correct_prefix(message.ADD_BUTTON_LINK_PREFIX)
)
def add_btn_link_msg(call):
    params = tools.get_call_back_params(call.data)
    user_context = mem.UserContext(call.from_user.id)
    _message = message.Message(
        user_context.get_context('message_id'),
        )
    _message.get_link_btn(call.from_user.id, params.get('btn_id'))


@bot.callback_query_handler(
    func=tools.is_correct_prefix(message.ADD_DIRECT_LINK_PREFIX)
)
def add_direct_link_msg(call):
    user_context = mem.UserContext(call.from_user.id)
    _message = message.Message(
        user_context.get_context('message_id'),
        )
    _message.get_direct_link(call.from_user.id)


@bot.callback_query_handler(
    func=tools.is_correct_prefix(message.EDIT_TIMEOUT_PREFIX)
)
def edit_timeout_msg(call):
    user_context = mem.UserContext(call.from_user.id)
    _message = message.Message(
        user_context.get_context('message_id'),
        )
    _message.get_timeout(call.from_user.id)


@bot.message_handler(
    content_types=['photo', 'text', 'voice', 'video_note'],
    func=tools.is_wait_line_for(message.MAKE_PREFIX),
)
def wait_line_make(msg):
    user_context = mem.UserContext(msg.from_user.id)
    user_context.rm_status()
    data = {}
    if msg.content_type == 'text':
        data['message'] = msg.text
    elif msg.content_type in ['photo', 'voice', 'video_note']:
        if msg.content_type == 'photo':
            media_file_id = sorted(msg.photo, key=lambda item: item.width)[-1].file_id
            content_type = 'image'
        elif msg.content_type == 'voice':
            media_file_id = msg.voice.file_id
            content_type = 'video'
        elif msg.content_type == 'video_note':
            media_file_id = msg.video_note.file_id
            content_type = 'video'
        media_data = bot.get_file(media_file_id)
        data['name'] = os.path.basename(media_data.file_path)
        data['content_type'] = f'{content_type}/{data["name"].split(".")[-1]}'
        data['media'] = bot.download_file(media_data.file_path)
        data['message'] = msg.caption
    message.make_new_msg(msg.from_user.id, data, msg.content_type)


@bot.message_handler(
    content_types=['photo', 'text', 'voice', 'video_note'],
    func=tools.is_wait_line_for(message.EDIT_PREFIX),
)
def wait_line_edit(msg):
    user_context = mem.UserContext(msg.from_user.id)
    user_context.rm_status()
    _message = message.Message(
        user_context.get_context('message_id'),
        )
    data = {}
    if msg.content_type == 'text':
        data['message'] = msg.text
    elif msg.content_type in ['photo', 'voice', 'video_note']:
        if msg.content_type == 'photo':
            media_file_id = sorted(msg.photo, key=lambda item: item.width)[-1].file_id
            content_type = 'image'
        elif msg.content_type == 'voice':
            media_file_id = msg.voice.file_id
            content_type = 'video'
        elif msg.content_type == 'video_note':
            media_file_id = msg.video_note.file_id
            content_type = 'video'
        media_data = bot.get_file(media_file_id)
        data['name'] = os.path.basename(media_data.file_path)
        data['content_type'] = f'{content_type}/{data["name"].split(".")[-1]}'
        data['media'] = bot.download_file(media_data.file_path)
        data['message'] = msg.caption
    _message.edit(msg.from_user.id, data, msg.content_type)


@bot.message_handler(
    content_types='text',
    func=tools.is_wait_line_for(message.EDIT_BUTTON_PREFIX),
)
def wait_line_edit_btn_text(msg):
    user_context = mem.UserContext(msg.from_user.id)
    user_context.rm_status()
    params = user_context.get_params()
    _message = message.Message(
        user_context.get_context('message_id'),
        )
    _message.edit_text_btn(msg.from_user.id, msg.text, int(params['btn_id']))


@bot.message_handler(
    content_types='text',
    func=tools.is_wait_line_for(message.ADD_BUTTON_LINK_PREFIX),
)
def wait_line_add_link_btn(msg):
    user_context = mem.UserContext(msg.from_user.id)
    user_context.rm_status()
    params = user_context.get_params()
    _message = message.Message(
        user_context.get_context('message_id'),
        )
    try:
        int(msg.text)
    except Exception:
        _message.show(msg.from_user.id)
    else:
        _message.add_link_btn(msg.from_user.id, msg.text, int(params['btn_id']))


@bot.message_handler(
    content_types='text',
    func=tools.is_wait_line_for(message.ADD_DIRECT_LINK_PREFIX),
)
def wait_line_add_direct_link(msg):
    user_context = mem.UserContext(msg.from_user.id)
    user_context.rm_status()
    _message = message.Message(
        user_context.get_context('message_id'),
        )
    try:
        int(msg.text)
    except Exception:
        _message.show(msg.from_user.id)
    else:
        _message.add_direct_link(msg.from_user.id, msg.text)


@bot.message_handler(
    content_types='text',
    func=tools.is_wait_line_for(message.EDIT_TIMEOUT_PREFIX),
)
def wait_line_edit_timeout(msg):
    user_context = mem.UserContext(msg.from_user.id)
    user_context.rm_status()
    _message = message.Message(
        user_context.get_context('message_id'),
        )
    try:
        assert(int(msg.text) >= 0)
    except Exception:
        _message.show(msg.from_user.id)
    else:
        _message.edit_timeout(msg.from_user.id, int(msg.text))


@bot.message_handler(
    content_types='text',
    func=tools.is_wait_line_for(message.ADD_BUTTON_PREFIX),
)
def wait_line_add_btn(msg):
    user_context = mem.UserContext(msg.from_user.id)
    user_context.rm_status()
    _message = message.Message(
        user_context.get_context('message_id'),
        )
    _message.add_button(msg.from_user.id, msg.text)


@bot.message_handler(
    content_types='text',
    func=tools.is_wait_line_for(message.EDIT_REFERAL_BLOCK_PREFIX),
)
def wait_line_edit_referal_block(msg):
    user_context = mem.UserContext(msg.from_user.id)
    user_context.rm_status()
    _message = message.Message(
        user_context.get_context('message_id'),
        )
    try:
        assert(int(msg.text) >= 0)
    except Exception:
        _message.show(msg.from_user.id)
    else:
        _message.edit_referal_block(msg.from_user.id, int(msg.text))

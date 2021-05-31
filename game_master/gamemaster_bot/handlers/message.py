from gamemaster_bot import bot
from gamemaster_bot import tools, mem
from gamemaster_bot.menu import message
import os


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


@bot.message_handler(
    content_types=['photo', 'text'],
    func=tools.is_wait_line_for(message.MAKE_PREFIX),
)
def wait_line_make(msg):
    user_context = mem.UserContext(msg.from_user.id)
    user_context.rm_status()
    data = {}
    if msg.content_type == 'text':
        data['message'] = msg.text
    elif msg.content_type == 'photo':
        photo = bot.get_file(sorted(msg.photo, key=lambda item: item.width)[-1].file_id)
        data['name'] = os.path.basename(photo.file_path)
        data['content_type'] = f'image/{data["name"].split(".")[-1]}'
        data['photo'] = bot.download_file(photo.file_path)
        data['message'] = msg.caption
    message.make_new_msg(msg.from_user.id, data, msg.content_type)


@bot.message_handler(
    content_types=['photo', 'text'],
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
    elif msg.content_type == 'photo':
        photo = bot.get_file(sorted(msg.photo, key=lambda item: item.width)[-1].file_id)
        data['name'] = os.path.basename(photo.file_path)
        data['content_type'] = f'image/{data["name"].split(".")[-1]}'
        data['photo'] = bot.download_file(photo.file_path)
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
    func=tools.is_wait_line_for(message.ADD_BUTTON_PREFIX),
)
def wait_line_add_btn(msg):
    user_context = mem.UserContext(msg.from_user.id)
    user_context.rm_status()
    _message = message.Message(
        user_context.get_context('message_id'),
        )
    _message.add_button(msg.from_user.id, msg.text)

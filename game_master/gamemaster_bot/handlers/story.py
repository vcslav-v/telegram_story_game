from gamemaster_bot import bot
from gamemaster_bot import tools, mem
from gamemaster_bot.menu import story


@bot.callback_query_handler(
    func=tools.is_correct_prefix(story.SHOW_PREFIX)
)
def show_story(call):
    params = tools.get_call_back_params(call.data)
    _story = story.Story(params.get('story_id'))
    _story.show(call.from_user.id)


@bot.callback_query_handler(
    func=tools.is_correct_prefix(story.RM_PREFIX)
)
def rm_story(call):
    params = tools.get_call_back_params(call.data)
    user_context = mem.UserContext(call.from_user.id)
    _story = story.Story(int(user_context.get_context('story_id')))
    if params.get('is_sure'):
        _story.rm(call.from_user.id)
    else:
        _story.make_sure_rm(call.from_user.id)


@bot.callback_query_handler(
    func=tools.is_correct_prefix(story.RENAME_PREFIX)
)
def rename_story(call):
    user_context = mem.UserContext(call.from_user.id)
    _story = story.Story(int(user_context.get_context('story_id')))
    _story.get_new_name(call.from_user.id)


@bot.callback_query_handler(
    func=tools.is_correct_prefix(story.MAKE_PREFIX)
)
def make_story(call):
    story.get_name_for_new_story(call.from_user.id)


@bot.message_handler(
    content_types='text',
    func=tools.is_wait_line_for(story.RENAME_PREFIX),
)
def wait_line_rename(message):
    user_context = mem.UserContext(message.from_user.id)
    user_context.rm_status()
    _story = story.Story(user_context.get_context('story_id'))
    _story.rename(message.from_user.id, message.text)


@bot.message_handler(
    content_types='text',
    func=tools.is_wait_line_for(story.MAKE_PREFIX),
)
def wait_line_make(message):
    user_context = mem.UserContext(message.from_user.id)
    user_context.rm_status()
    story.make_new_story(message.from_user.id, message.text)

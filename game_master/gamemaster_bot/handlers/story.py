from gamemaster_bot import bot
from gamemaster_bot import tools, mem
from gamemaster_bot.menu import story


@bot.callback_query_handler(
    func=tools.is_correct_prefix(story.SHOW_PREFIX)
)
def show_story(call):
    params = tools.get_call_back_params(call.data)
    user_context = mem.UserContext(call.from_user.id)
    _story = story.Story(params.get('story_id') or int(user_context.get_context('story_id')))
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
    func=tools.is_correct_prefix(story.UPLOAD_REACTIONS_PREFIX)
)
def upload_reactions(call):
    user_context = mem.UserContext(call.from_user.id)
    _story = story.Story(int(user_context.get_context('story_id')))
    _story.get_reactions_file(call.from_user.id)


@bot.callback_query_handler(
    func=tools.is_correct_prefix(story.DOWNLOAD_REACTIONS_PREFIX)
)
def download_reactions(call):
    user_context = mem.UserContext(call.from_user.id)
    _story = story.Story(int(user_context.get_context('story_id')))
    _story.get_reactions(call.from_user.id)

@bot.callback_query_handler(
    func=tools.is_correct_prefix(story.RENAME_PREFIX)
)
def rename_story(call):
    user_context = mem.UserContext(call.from_user.id)
    _story = story.Story(int(user_context.get_context('story_id')))
    _story.get_new_name(call.from_user.id)


@bot.callback_query_handler(
    func=tools.is_correct_prefix(story.SET_BASE_TIMEOUT)
)
def edit_base_timeout_story(call):
    user_context = mem.UserContext(call.from_user.id)
    _story = story.Story(int(user_context.get_context('story_id')))
    _story.get_timeout(call.from_user.id, story.SET_BASE_TIMEOUT)


@bot.callback_query_handler(
    func=tools.is_correct_prefix(story.SET_K_TIMEOUT)
)
def edit_k_timeout_story(call):
    user_context = mem.UserContext(call.from_user.id)
    _story = story.Story(int(user_context.get_context('story_id')))
    _story.get_timeout(call.from_user.id, story.SET_K_TIMEOUT)


@bot.callback_query_handler(
    func=tools.is_correct_prefix(story.MAKE_PREFIX)
)
def make_story(call):
    story.get_name_for_new_story(call.from_user.id)


@bot.callback_query_handler(
    func=tools.is_correct_prefix(story.SHOW_CHAPTERS_PREFIX)
)
def show_chapters(call):
    user_context = mem.UserContext(call.from_user.id)
    _story = story.Story(int(user_context.get_context('story_id')))
    _story.show_chapters(call.from_user.id)


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
    func=tools.is_wait_line_for(story.SET_BASE_TIMEOUT),
)
def wait_line_base_timeout(message):
    user_context = mem.UserContext(message.from_user.id)
    user_context.rm_status()
    _story = story.Story(user_context.get_context('story_id'))
    try:
        int(message.text)
    except:
        _story.show(message.from_user.id)
    else:
        _story.set_base_timeout(message.from_user.id, int(message.text))


@bot.message_handler(
    content_types='text',
    func=tools.is_wait_line_for(story.SET_K_TIMEOUT),
)
def wait_line_k_timeout(message):
    user_context = mem.UserContext(message.from_user.id)
    user_context.rm_status()
    _story = story.Story(user_context.get_context('story_id'))
    try:
        int(message.text)
    except:
        _story.show(message.from_user.id)
    else:
        _story.set_k_timeout(message.from_user.id, int(message.text))


@bot.message_handler(
    content_types='text',
    func=tools.is_wait_line_for(story.MAKE_PREFIX),
)
def wait_line_make(message):
    user_context = mem.UserContext(message.from_user.id)
    user_context.rm_status()
    story.make_new_story(message.from_user.id, message.text)


@bot.message_handler(
    content_types='document',
    func=tools.is_wait_line_for(story.UPLOAD_REACTIONS_PREFIX),
)
def wait_line_upload_reactions(message):
    user_context = mem.UserContext(message.from_user.id)
    user_context.rm_status()
    _story = story.Story(user_context.get_context('story_id'))
    document = bot.get_file(message.document.file_id)
    _story.set_reaction(message.from_user.id, bot.download_file(document.file_path))

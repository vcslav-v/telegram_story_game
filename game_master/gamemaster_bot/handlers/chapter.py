from gamemaster_bot import bot
from gamemaster_bot import tools, mem
from gamemaster_bot.menu import chapter


@bot.callback_query_handler(
    func=tools.is_correct_prefix(chapter.SHOW_PREFIX)
)
def show_chapter(call):
    params = tools.get_call_back_params(call.data)
    user_context = mem.UserContext(call.from_user.id)
    _chapter = chapter.Chapter(
        int(user_context.get_context('story_id')),
        params.get('chapter_id') or user_context.get_context('chapter_id'),
    )
    _chapter.show(call.from_user.id)


@bot.callback_query_handler(
    func=tools.is_correct_prefix(chapter.MAKE_PREFIX)
)
def make_chapter(call):
    chapter.get_name_for_new_chapter(call.from_user.id)


@bot.callback_query_handler(
    func=tools.is_correct_prefix(chapter.UP_PREFIX)
)
def up_chapter(call):
    user_context = mem.UserContext(call.from_user.id)
    params = tools.get_call_back_params(call.data)
    _chapter = chapter.Chapter(
        int(user_context.get_context('story_id')),
        params.get('chapter_id'),
    )
    _chapter.replace(_chapter.number - 1, call.from_user.id)


@bot.callback_query_handler(
    func=tools.is_correct_prefix(chapter.DOWN_PREFIX)
)
def down_chapter(call):
    user_context = mem.UserContext(call.from_user.id)
    params = tools.get_call_back_params(call.data)
    _chapter = chapter.Chapter(
        int(user_context.get_context('story_id')),
        params.get('chapter_id'),
    )
    _chapter.replace(_chapter.number + 1, call.from_user.id)


@bot.callback_query_handler(
    func=tools.is_correct_prefix(chapter.RM_PREFIX)
)
def rm_chapter(call):
    params = tools.get_call_back_params(call.data)
    user_context = mem.UserContext(call.from_user.id)
    _chapter = chapter.Chapter(
        int(user_context.get_context('story_id')),
        int(user_context.get_context('chapter_id')),
    )
    if params.get('is_sure'):
        _chapter.rm(call.from_user.id)
    else:
        _chapter.make_sure_rm(call.from_user.id)


@bot.callback_query_handler(
    func=tools.is_correct_prefix(chapter.RENAME_PREFIX)
)
def rename_chapter(call):
    user_context = mem.UserContext(call.from_user.id)
    _chapter = chapter.Chapter(
        int(user_context.get_context('story_id')),
        int(user_context.get_context('chapter_id')),
        )
    _chapter.get_new_name(call.from_user.id)


@bot.message_handler(
    content_types='text',
    func=tools.is_wait_line_for(chapter.MAKE_PREFIX),
)
def wait_line_make(message):
    user_context = mem.UserContext(message.from_user.id)
    user_context.rm_status()
    chapter.make_new_chapter(message.from_user.id, message.text)


@bot.message_handler(
    content_types='text',
    func=tools.is_wait_line_for(chapter.RENAME_PREFIX),
)
def wait_line_rename(message):
    user_context = mem.UserContext(message.from_user.id)
    user_context.rm_status()
    _chapter = chapter.Chapter(
        user_context.get_context('story_id'),
        user_context.get_context('chapter_id'),
        )
    _chapter.rename(message.from_user.id, message.text)
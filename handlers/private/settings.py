from aiogram import types as t
from aiogram.dispatcher import FSMContext

from bot import dp
from handlers.private import alias_form
from libs.classes import UserText, User, DictSettings
from libs.classes.Errors import EmptyOwns
from libs.classes.Utils import is_private
from libs.objects import MessageData, Database
from libs.src import buttons

s = buttons.private.settings


@dp.message_handler(is_private, commands=["settings"])
async def settings_cmd(msg: t.Message):
    src = UserText(msg.from_user.language_code)
    await src.buttons.private.settings.settings.send(msg)


@s.chat_list()
async def chat_list_menu(clb: t.CallbackQuery):
    src = UserText(clb.from_user.language_code)

    if not Database.get_owns(clb.from_user.id):
        raise EmptyOwns(src.lang)
    await clb.message.edit_text(src.text.private.settings.chat_loading)

    user: User = await User(clb.from_user, clb.message.chat)
    chats = user.iter_owns()

    menu = src.buttons.private.settings.chats.copy
    async for chat in chats:
        chat_settings = src.buttons.private.settings.chat_settings.copy
        settings = chat_settings.get_menu(chat.settings, chat.id, src.lang, text=chat.title)
        settings.storage["settings"] = chat_settings
        settings.storage["chat"] = chat

        menu.add(settings)

    await menu.edit(clb.message)


@s.add_alias()
async def add_alias_button(clb: t.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["settings_message"] = clb.message
    with await MessageData.data(clb.message) as data:
        element: DictSettings = data.current_element

    if element.key == "sticker_alias":
        await alias_form.start_sticker(clb)
    elif element.key == "text_alias":
        await alias_form.start_text(clb)
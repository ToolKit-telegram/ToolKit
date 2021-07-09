import typing as p

from aiogram import types as t

from bot import bot, dp
from libs import system
from libs.classes.Buttons import Menu
from libs.classes.Chat import Chat
from libs.classes.Errors import BackError, MyError, ERRORS, IGNORE, ForceError
from libs.classes.Localisation import UserText
from libs.classes.Utils import (add_member, check, is_chat, is_private,
                                promote_admin, removed_member, restrict_admin)
from libs.objects import Database, MessageData
from libs import filters as f


async def test_clb(clb: t.CallbackQuery):
    await clb.answer(dp.callback_query_handlers.handlers.__len__())


@dp.message_handler(f.message.is_chat, f.message.is_alias, f.message.is_reply,
                    content_types=[t.ContentType.TEXT, t.ContentType.STICKER])
async def alias_executor(msg: t.Message):
    upd = t.Update.get_current()
    chat = await Chat.create(msg.chat)
    if msg.sticker:
        msg.text = chat.settings.sticker_alias[msg.sticker.file_unique_id]
        msg.sticker = None
    elif msg.text:
        msg.text = chat.settings.text_alias[msg.text]
    else:
        return

    upd.message = msg
    await dp.process_update(upd)


# @dp.callback_query_handler(test_clb)
# @any.command.AdminCommandParser()
@dp.message_handler(commands=["test"])
async def test_xd(msg: t.Message):
    await msg.answer(msg.reply_to_message.message_id)


@dp.message_handler(is_private, commands=["start"])
async def start(msg: t.Message):
    src = UserText(msg.from_user.language_code)
    await msg.answer(src.text.private.start_text)


@system.delete_this(is_chat, state="*")
async def delete_this(clb: t.CallbackQuery):
    await clb.message.delete()


@system.back()
async def back(clb: t.CallbackQuery):
    msg = clb.message
    with await MessageData.data(msg) as data:
        try:
            history: p.List[Menu] = data.history
            history.pop(-1)
            await history[-1].edit(msg, False)
            data.history = history
        except Exception:
            raise BackError(clb.from_user.language_code)


@dp.my_chat_member_handler(add_member)
async def bot_chat_added(upd: t.ChatMemberUpdated):
    chat: Chat = await Chat.create(upd.chat)
    src = chat.owner.src
    await bot.send_message(chat.id, src.text.chat.start_text)


@dp.my_chat_member_handler(removed_member)
async def bot_chat_removed(upd: t.ChatMemberUpdated):
    Database.delete_chat(upd.chat.id)


@dp.my_chat_member_handler(promote_admin)
async def bot_promote(upd: t.ChatMemberUpdated):
    chat: Chat = await Chat.create(upd.chat)
    src = chat.owner.src
    await bot.send_message(chat.id, src.text.chat.promote_admin)


@dp.my_chat_member_handler(restrict_admin)
async def bot_chat_restrict(upd: t.ChatMemberUpdated):
    chat: Chat = await Chat.create(upd.chat)
    src = chat.owner.src
    await bot.send_message(chat.id, src.text.chat.restrict_admin)


@dp.message_handler(check, content_types=[t.ContentType.TEXT, t.ContentType.PHOTO])
async def check():
    pass


@dp.errors_handler()
async def errors(upd: t.Update, error: p.Union[MyError, Exception]):
    if error.__class__ in ERRORS:
        await error.answer(upd)
    elif error.__class__ in IGNORE:
        pass
    else:
        my_err = ForceError(f"⚠ {error.__class__.__name__}:{error.args[0]}", 0, True, False)
        await my_err.log(upd)
        await my_err.answer(upd)

    return True

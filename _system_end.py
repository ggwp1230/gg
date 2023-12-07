from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext

from _loader import dp, bot
from handlers._filters import IsWork, IsUser
from keyboards.inline._system import *


# Сообщения без обработки
@dp.message_handler(content_types = ["any"], state="*")
async def get_message_text(message: types.Message, state: FSMContext):
	user_id, message_id = message.from_user.id, message.message_id
	try: await bot.delete_message(user_id, message_id)
	except: pass

# Обработка перезапуска скрипта
@dp.callback_query_handler(state="*")
async def processing_missed_callback(call: CallbackQuery, state: FSMContext):
	try: await bot.delete_message(call.message.chat.id, call.message.message_id)
	except: pass
	await bot.send_message(call.from_user.id, "<b>Упс... Наша система была перезагружена.\n♻ Выполните действие заново.</b>", reply_markup=kb_btn_restart)
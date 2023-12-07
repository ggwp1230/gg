from datetime import datetime
from string import Template

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from _loader import dp, bot
from keyboards.inline.admin import *

import utils.sql._handlers as db
import utils._func as func


print(f'[DEBUG][ADMIN] Load.')


# Главное меню
@dp.message_handler(commands = ['admx'], state="*")
async def admin_menu(message: types.Message, state: FSMContext):
	user_id, message_id = message.from_user.id, message.message_id
	udata, uclean, urole = db.GetUsers(user_id), db.GetClean(user_id), func.GetRole(user_id)
	
	await state.finish()

	if urole["id"] > 0:
		await func.DeleteMSG(bot, user_id, [message_id, uclean["sticker_id"], uclean["home_id"]])

		if urole["id"] == 1: caption = "👑 Гл. Администратор"
		if urole["id"] == 2: caption = "📗 Администратор"
		if urole["id"] == 3: caption = "📙 Модератор"
		if urole["id"] == 4: caption = "👨‍💻 Оператор"
		if urole["id"] == 5: caption = "👨‍💻💢 Оператор"
		if urole["id"] == 6: caption = "👨‍💻🛒 Оператор"
		r_message = await message.answer(f"<b>🔒 Панель управления.</b>\n<b>{caption}:</b> <i>{udata['firstname']}</i>", reply_markup=kb_admin_menu(udata))

		db.SetClean(user_id, "sticker_id", 0)
		db.SetClean(user_id, "home_id", r_message.message_id)


# Главное меню (Кнопка)
@dp.callback_query_handler(text="admin_menu", state="*")
async def admin_menu_callback(call: CallbackQuery, state: FSMContext):
	user_id, message_id = call.message.chat.id, call.message.message_id
	udata, uclean, urole = db.GetUsers(user_id), db.GetClean(user_id), func.GetRole(user_id)

	await state.finish()

	if urole["id"] > 0:
		await func.DeleteMSG(bot, user_id, [message_id, uclean["sticker_id"], uclean["home_id"]])

		if urole["id"] == 1: caption = "👑 Гл. Администратор"
		if urole["id"] == 2: caption = "📗 Администратор"
		if urole["id"] == 3: caption = "📙 Модератор"
		if urole["id"] == 4: caption = "👨‍💻 Оператор"
		if urole["id"] == 5: caption = "👨‍💻💢 Оператор"
		if urole["id"] == 6: caption = "👨‍💻🛒 Оператор"
		r_message = await call.message.answer(f"<b>🔒 Панель управления.</b>\n<b>{caption}:</b> <i>{udata['firstname']}</i>", reply_markup=kb_admin_menu(udata))

		db.SetClean(user_id, "sticker_id", 0)
		db.SetClean(user_id, "home_id", r_message.message_id)
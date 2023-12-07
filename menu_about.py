from datetime import datetime
from string import Template

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from _loader import dp, bot
from keyboards.inline.users import *

import handlers._system_start as _system
import utils.sql._handlers as db
import utils._func as func


# Информация
@dp.callback_query_handler(text_startswith="menu_about", state="*")
async def menu_about(call: CallbackQuery, state: FSMContext):
	user_id, message_id = call.message.chat.id, call.message.message_id
	udata, uclean, settings = db.GetUsers(user_id), db.GetClean(user_id), db.GetSettings()

	if settings['engineering_mode'] and not func.GetRole(user_id)["id"]: return await _system.engineering_work(user_id, message_id)

	split = call.data.split(":")
	try: menu_item = split[1]
	except: menu_item = False

	# Генерация
	if not menu_item:
		caption = "<b>Run by 🌑 BLVCK</b>"
	else:
		caption = settings[f"screen_{menu_item}"]

	markup = kb_menu_about(menu_item, settings)


	# Сообщение
	if uclean['location'] != "menu_about":
		await func.DeleteMSG(bot, user_id, [message_id, uclean["sticker_id"], uclean["home_id"]])
		try: r_sticker = await call.message.answer_sticker(settings["sticker_about"])
		except: r_sticker = False
		if r_sticker: db.SetClean(user_id, "sticker_id", r_sticker.message_id)
		r_message = await bot.send_message(user_id, caption, reply_markup=markup)
		db.SetClean(user_id, "home_id", r_message.message_id)
		db.SetClean(user_id, "location", "menu_about")
	else:
		try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
		except: pass
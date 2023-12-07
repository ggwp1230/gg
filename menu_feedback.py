from datetime import datetime
from string import Template

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

from _loader import dp, bot
from handlers._states import StateAppeal, StateSupport
from keyboards.inline.users import *
from keyboards.inline.admin import *

import handlers._system_start as _system
import utils.sql._handlers as db
import utils._func as func
import utils._cfg as cfg


# Обратная связь
@dp.callback_query_handler(text_startswith="menu_feedback", state="*")
async def menu_feedback(call: CallbackQuery, state: FSMContext):
	user_id, message_id = call.message.chat.id, call.message.message_id
	udata, uclean, settings = db.GetUsers(user_id), db.GetClean(user_id), db.GetSettings()
	
	await state.finish()

	if settings['engineering_mode'] and not func.GetRole(user_id)["id"]: return await _system.engineering_work(user_id, message_id)

	split = call.data.split(":")
	try: menu_switch = split[1]
	except: menu_switch = False
	try: action_type = split[2]
	except: action_type = False

	# Тип обращения
	if not menu_switch:
		caption = f"<b>📮 Обратная связь.</b>\n\nВыберите тип обращения:"
		markup = kb_menu_support(udata, menu_switch)

	# Жалоба
	if menu_switch == "appeal":
		caption = f"<b>💢 Жалоба на товар.</b>\n\nДля получения обратной связи, напиши сообщение и ожидайте ответа оператора."
		
		if not action_type:
			caption = caption + f"\n\n<b>Статус:</b> ✏️ Напишите сообщение"
			markup = kb_menu_support(udata, menu_switch)
			await StateAppeal.user.set()

		if action_type == "off":
			if udata["support"]: await bot.send_message(udata["support"], "<b>👨‍💼 Пользователь завершил диалог.</b>", reply_markup=kb_admin_menu_support(menu_switch = "exit"))
			db.UpdateUsers(user_id, "support", "0")
			db.UpdateSupport("appeal", user_id, "message_id", "")
			udata["support"] = 0

			caption = caption + f"\n\n<b>Статус:</b> ⭕️ Диалог завершен"
			markup = kb_menu_support(udata, "exit")
			res = await bot.send_message(user_id, "🔄⌨️", reply_markup=ReplyKeyboardRemove())
			await bot.delete_message(user_id, res.message_id)

	# Прямая покупка
	if menu_switch == "support":
		caption = f"<b>🛒 Прямая покупка.</b>\n\nДля получения обратной связи, напиши сообщение и ожидайте ответа оператора."
		
		if not action_type:
			caption = caption + f"\n\n<b>Статус:</b> ✏️ Напишите сообщение"
			markup = kb_menu_support(udata, menu_switch)
			await StateSupport.user.set()

		if action_type == "off":
			await bot.send_message(udata["support"], "<b>👨‍💼 Пользователь завершил диалог.</b>", reply_markup=kb_admin_menu_support(menu_switch = "exit"))
			db.UpdateUsers(user_id, "support", "0")
			db.UpdateSupport("support", user_id, "message_id", "")
			udata["support"] = 0

			caption = caption + f"\n\n<b>Статус:</b> ⭕️ Диалог завершен"
			markup = kb_menu_support(udata, "exit")
			res = await bot.send_message(user_id, "🔄⌨️", reply_markup=ReplyKeyboardRemove())
			await bot.delete_message(user_id, res.message_id)

	# Сообщение
	if uclean['location'] != "menu_feedback":
		await func.DeleteMSG(bot, user_id, [message_id, uclean["sticker_id"], uclean["home_id"]])
		try: r_sticker = await call.message.answer_sticker(settings["sticker_feedback"])
		except: r_sticker = False
		if r_sticker: db.SetClean(user_id, "sticker_id", r_sticker.message_id)
		r_message = await bot.send_message(user_id, caption, reply_markup=markup)
		db.SetClean(user_id, "home_id", r_message.message_id)
		db.SetClean(user_id, "location", "menu_feedback")
	else:
		try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
		except: pass


# Обработчик жалобы
@dp.message_handler(content_types = ["any"], state=StateAppeal.user)
async def menu_feedback_handler(message: types.Message, state: FSMContext):
	# __init__ #
	user_id, message_id = message.from_user.id, message.message_id
	udata, uclean, settings = db.GetUsers(user_id), db.GetClean(user_id), db.GetSettings()

	off_text = "⭕️ Деактивировать"
	try: off = message.text
	except: off = False
	if off:
		if off == off_text:
			if udata["support"]: await bot.send_message(udata["support"], "<b>👨‍💼 Пользователь завершил диалог.</b>", reply_markup=kb_admin_menu_support(menu_switch = "exit"))
			db.UpdateUsers(user_id, "support", "0")
			db.UpdateSupport("appeal", user_id, "message_id", "")
			udata["support"] = 0
			
			caption = f"<b>💢 Жалоба на товар.</b>\n\nДля получения обратной связи, напиши сообщение и ожидайте ответа оператора."
			caption = caption + f"\n\n<b>Статус:</b> ⭕️ Диалог завершен"
			markup = kb_menu_support(udata, "exit")
			await bot.send_message(user_id, caption, reply_markup=markup)
			await bot.send_message(user_id, False, reply_markup=ReplyKeyboardRemove())
			await state.finish()

	if settings['engineering_mode'] and not func.GetRole(user_id)["id"]: return await _system.engineering_work(user_id, message_id)

	if not udata["support"]:
		if off:
			if off == off_text: return
		db.AddSupport("appeal", user_id, message_id)
		
		# Оповещение
		kb_markup = ReplyKeyboardMarkup(resize_keyboard=True)
		kb_markup.add("⭕️ Деактивировать")
		await bot.send_message(user_id, "<b>✅ Сообщение успешно отправлено, ожидайте оператора.</b>", reply_markup=kb_markup)
		await _system.SendNotify(f'<b>👨‍💼 Пользователь:</b> <a href="tg://user?id={user_id}">{udata["firstname"]}</a>\n<b>💢 Жалоба на товар.</b> Ожидает ответа оператора.', "appeal")
		
		# Сообщение
		caption = f"<b>💢 Жалоба на товар.</b>\n\nДля получения обратной связи, напиши сообщение и ожидайте ответа оператора."
		caption = caption + f"\n\n<b>Статус:</b> 👨‍💻 Ожидается ответ оператора"
		markup = kb_menu_support(udata, "appeal_off")
		try: await bot.edit_message_text(caption, user_id, uclean["home_id"], reply_markup=markup)
		except: pass
	else:
		await bot.forward_message(udata["support"], user_id, message_id)


# Обработчик прямой продажи
@dp.message_handler(content_types = ["any"], state=StateSupport.user)
async def menu_feedback_handler(message: types.Message, state: FSMContext):
	# __init__ #
	user_id, message_id = message.from_user.id, message.message_id
	udata, uclean, settings = db.GetUsers(user_id), db.GetClean(user_id), db.GetSettings()

	off_text = "⭕️ Деактивировать"
	try: off = message.text
	except: off = False
	if off:
		if off == off_text:
			if udata["support"]: await bot.send_message(udata["support"], "<b>👨‍💼 Пользователь завершил диалог.</b>", reply_markup=kb_admin_menu_support(menu_switch = "exit"))
			db.UpdateUsers(user_id, "support", "0")
			db.UpdateSupport("support", user_id, "message_id", "")
			udata["support"] = 0
			
			caption = f"<b>🛒 Прямая покупка.</b>\n\nДля получения обратной связи, напиши сообщение и ожидайте ответа оператора."
			caption = caption + f"\n\n<b>Статус:</b> ⭕️ Диалог завершен"
			markup = kb_menu_support(udata, "exit")
			await bot.send_message(user_id, caption, reply_markup=markup)
			res = await bot.send_message(user_id, "🔄⌨️", reply_markup=ReplyKeyboardRemove())
			await bot.delete_message(user_id, res.message_id)
			await state.finish()

	if settings['engineering_mode'] and not func.GetRole(user_id)["id"]: return await _system.engineering_work(user_id, message_id)

	if not udata["support"]:
		if off:
			if off == off_text: return
		db.AddSupport("support", user_id, message_id)
		
		# Оповещение
		kb_markup = ReplyKeyboardMarkup(resize_keyboard=True)
		kb_markup.add("⭕️ Деактивировать")
		await bot.send_message(user_id, "<b>✅ Сообщение успешно отправлено, ожидайте оператора.</b>", reply_markup=kb_markup)
		await _system.SendNotify(f'<b>👨‍💼 Пользователь:</b> <a href="tg://user?id={user_id}">{udata["firstname"]}</a>\n<b>🛒 Прямая покупка.</b> Ожидает ответа оператора.', "support")
		
		# Сообщение
		caption = f"<b>🛒 Прямая покупка.</b>\n\nДля получения обратной связи, напиши сообщение и ожидайте ответа оператора."
		caption = caption + f"\n\n<b>Статус:</b> 👨‍💻 Ожидается ответ оператора"
		markup = kb_menu_support(udata, "support_off")
		try: await bot.edit_message_text(caption, user_id, uclean["home_id"], reply_markup=markup)
		except: pass
	else:
		await bot.forward_message(udata["support"], user_id, message_id)
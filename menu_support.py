from datetime import datetime
from string import Template

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

from _loader import dp, bot
from handlers._states import StateAppeal, StateSupport
from keyboards.inline.admin import *
from keyboards.inline.users import *

import utils.sql._handlers as db
import utils._func as func
import utils._cfg as cfg


# Техническая поддежрка
@dp.callback_query_handler(text_startswith="admin_menu_support", state="*")
async def admin_menu_support(call: CallbackQuery, state: FSMContext):
	user_id, message_id = call.message.chat.id, call.message.message_id
	udata, urole = db.GetUsers(user_id), func.GetRole(user_id)

	# Параметры
	split = call.data.split(":")
	try: menu_switch = split[1]
	except: menu_switch = False
	try: offset = int(split[2])
	except: offset = 0
	try: action_type = split[2]
	except: action_type = False

	# Генерация
	if urole["id"] == 1 or urole["id"] == 2 or urole["id"] == 4 or urole["id"] == 5 or urole["id"] == 6:
		if not menu_switch:
			caption = "<b>📮 Обратная связь.</b>\n\nВыберите тип обращения:"
			markup = kb_admin_menu_support(udata, urole, menu_switch)

		# Жалоба
		if menu_switch == "appeal":
			if not action_type:
				caption = "<b>📮 Обратная связь.</b>\n\nСписок обращений:"
				markup = kb_admin_menu_support(udata, urole, menu_switch, offset)

			# Деактивация
			if action_type == "off":
				state_data = await state.get_data()
				select_id = state_data.get("select_id", False)
				db.UpdateUsers(select_id, "support", "0")
				db.UpdateSupport("appeal", select_id, "message_id", "")
				
				# Оповещение
				select = db.GetUsers(select_id)
				caption = f'<b>📮 Обратная связь.</b>\n\n<b>👨‍💼 Пользователь:</b> <a href="tg://user?id={select_id}">{select["firstname"]}</a>'
				caption = caption + f'\n<b>💢 Тип обращения:</b> Жалоба на товар'
				caption = caption + f"\n\n<b>Статус:</b> ⭕️ Диалог завершен"
				markup = kb_admin_menu_support(udata, menu_switch = "exit")
				
				await bot.send_message(select_id, "<b>👨‍💻 Оператор завершил диалог.</b>", reply_markup=kb_menu_support(menu_switch = "exit"))
				await bot.send_message(user_id, caption, reply_markup=markup)
				res = await bot.send_message(user_id, "🔄⌨️", reply_markup=ReplyKeyboardRemove())
				await bot.delete_message(user_id, res.message_id)
				await state.finish()
				return

		# Прямая покупка
		if menu_switch == "support":
			if not action_type:
				caption = "<b>📮 Обратная связь.</b>\n\nСписок обращений:"
				markup = kb_admin_menu_support(udata, urole, menu_switch, offset)

			# Деактивация
			if action_type == "off":
				state_data = await state.get_data()
				select_id = state_data.get("select_id", False)
				db.UpdateUsers(select_id, "support", "0")
				db.UpdateSupport("support", select_id, "message_id", "")
				
				# Оповещение
				select = db.GetUsers(select_id)
				caption = f'<b>📮 Обратная связь.</b>\n\n<b>👨‍💼 Пользователь:</b> <a href="tg://user?id={select_id}">{select["firstname"]}</a>'
				caption = caption + f'\n<b>🛒 Тип обращения:</b> Прямая покупка'
				caption = caption + f"\n\n<b>Статус:</b> ⭕️ Диалог завершен"
				markup = kb_admin_menu_support(udata, menu_switch = "exit")
				
				await bot.send_message(select_id, "<b>👨‍💻 Оператор завершил диалог.</b>", reply_markup=kb_menu_support(menu_switch = "exit"))
				await bot.send_message(user_id, caption, reply_markup=markup)
				res = await bot.send_message(user_id, "🔄⌨️", reply_markup=ReplyKeyboardRemove())
				await bot.delete_message(user_id, res.message_id)
				await state.finish()
				return

		if menu_switch == "open":
			select_id = int(split[3])
			data = db.GetSupport(action_type, select_id)
			for i in data["message_id"].split(','):
				if i: await bot.forward_message(user_id, select_id, i)
			
			# Оповещение
			select = db.GetUsers(select_id)
			caption = f'<b>📮 Обратная связь.</b>\n\n<b>👨‍💼 Пользователь:</b> <a href="tg://user?id={select_id}">{select["firstname"]}</a>\n'
			if action_type == "appeal":
				caption = caption + f'\n<b>💢 Тип обращения:</b> Жалоба на товар'
			if action_type == "support":
				caption = caption + f'\n<b>🛒 Тип обращения:</b> Прямая покупка'
			caption = caption + f'\n\n<b>Статус:</b> ✉️ Ожидает ответа'
			markup = kb_admin_menu_support(udata, urole, menu_switch, action_type = action_type, select_id = select_id)
			
		if menu_switch == "activate":
			select_id = int(split[3])

			# Оповещение
			select = db.GetUsers(select_id)
			caption = f'<b>📮 Обратная связь.</b>\n\n<b>👨‍💼 Пользователь:</b> <a href="tg://user?id={select_id}">{select["firstname"]}</a>'
			if action_type == "appeal":
				caption = caption + f'\n<b>💢 Тип обращения:</b> Жалоба на товар'
			if action_type == "support":
				caption = caption + f'\n<b>🛒 Тип обращения:</b> Прямая покупка'
			caption = caption + f'\n\n<b>Статус:</b> ✉️ Ожидает ответа'
			caption = caption + f'\n\nВы подключились к диалогу с пользователем, ожидается сообщение:'
			markup = kb_admin_menu_support(udata, urole, menu_switch, action_type = action_type, select_id = select_id)

			# Активация режима
			db.UpdateUsers(select_id, "support", user_id)
			db.UpdateSupport(action_type, user_id, "message_id", "")
			await bot.send_message(select_id, "<b>👨‍💻 Оператор присоединился к диалогу, ожидайте ответа.</b>")
			
			# Жалоба на товар
			if action_type == "appeal":
				await StateAppeal.operator.set()
				await state.update_data(select_id=select_id)

			# Прямая покупка
			if action_type == "support":
				await StateSupport.operator.set()
				await state.update_data(select_id=select_id)

			# Кнопка деактивации
			kb_markup = ReplyKeyboardMarkup(resize_keyboard=True)
			kb_markup.add("⭕️ Деактивировать")
			await bot.send_message(user_id, f'<b>✅ Вы присоединились к диалогу.</b>\nВсе сообщения будут отправлены пользователю: <a href="tg://user?id={select_id}">{select["firstname"]}</a>\n\n⚠️ После деактивации, повторная активация будет недоступна!', reply_markup=kb_markup)


	# Сообщение
	try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
	except: pass


# Обработчик жалобы
@dp.message_handler(content_types = ["any"], state=StateAppeal.operator)
async def menu_feedback_handler(message: types.Message, state: FSMContext):
	# __init__ #
	user_id, message_id = message.from_user.id, message.message_id
	udata, uclean = db.GetUsers(user_id), db.GetClean(user_id)

	state_data = await state.get_data()
	select_id = state_data.get("select_id", False)

	off_text = "⭕️ Деактивировать"
	try: off = message.text
	except: off = False
	if off:
		if off == off_text:
			db.UpdateUsers(select_id, "support", "0")
			db.UpdateSupport("appeal", select_id, "message_id", "")
			
			# Оповещение
			select = db.GetUsers(select_id)
			caption = f'<b>📮 Обратная связь.</b>\n\n<b>👨‍💼 Пользователь:</b> <a href="tg://user?id={select_id}">{select["firstname"]}</a>'
			caption = caption + f'\n<b>💢 Тип обращения:</b> Жалоба на товар'
			caption = caption + f"\n\n<b>Статус:</b> ⭕️ Диалог завершен"
			markup = kb_admin_menu_support(udata, menu_switch = "exit")
			
			await bot.send_message(select_id, "<b>👨‍💻 Оператор завершил диалог.</b>", reply_markup=kb_menu_support(menu_switch = "exit"))
			await bot.send_message(user_id, caption, reply_markup=markup)
			res = await bot.send_message(user_id, "🔄⌨️", reply_markup=ReplyKeyboardRemove())
			await bot.delete_message(user_id, res.message_id)
			await state.finish()
			return

	await bot.copy_message(select_id, user_id, message_id)


# Обработчик прямой покупки
@dp.message_handler(content_types = ["any"], state=StateSupport.operator)
async def menu_feedback_handler(message: types.Message, state: FSMContext):
	# __init__ #
	user_id, message_id = message.from_user.id, message.message_id
	udata, uclean = db.GetUsers(user_id), db.GetClean(user_id)

	state_data = await state.get_data()
	select_id = state_data.get("select_id", False)

	off_text = "⭕️ Деактивировать"
	try: off = message.text
	except: off = False
	if off:
		if off == off_text:
			db.UpdateUsers(select_id, "support", "0")
			db.UpdateSupport("support", select_id, "message_id", "")
			
			# Оповещение
			select = db.GetUsers(select_id)
			caption = f'<b>📮 Обратная связь.</b>\n\n<b>👨‍💼 Пользователь:</b> <a href="tg://user?id={select_id}">{select["firstname"]}</a>'
			caption = caption + f'\n<b>🛒 Тип обращения:</b> Прямая покупка'
			caption = caption + f"\n\n<b>Статус:</b> ⭕️ Диалог завершен"
			markup = kb_admin_menu_support(udata, menu_switch = "exit")
			
			await bot.send_message(select_id, "<b>👨‍💻 Оператор завершил диалог.</b>", reply_markup=kb_menu_support(menu_switch = "exit"))
			await bot.send_message(user_id, caption, reply_markup=markup)
			res = await bot.send_message(user_id, "🔄⌨️", reply_markup=ReplyKeyboardRemove())
			await bot.delete_message(user_id, res.message_id)
			await state.finish()
			return

	await bot.copy_message(select_id, user_id, message_id)
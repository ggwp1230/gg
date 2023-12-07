from datetime import datetime
from string import Template

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from _loader import dp, bot
from handlers._states import StateNewsletter
from keyboards.inline.admin import *

import utils.sql._handlers as db
import utils._func as func


# Меню рассылки
@dp.callback_query_handler(text_startswith="admin_menu_newsletter", state="*")
async def admin_menu_newsletter(call: CallbackQuery, state: FSMContext):
	user_id, message_id = call.message.chat.id, call.message.message_id
	udata, uclean, urole = db.GetUsers(user_id), db.GetClean(user_id), func.GetRole(user_id)
	
	await state.finish()

	split = call.data.split(":")
	try: offset = split[1]
	except: offset = 0
	
	# Генерация
	if urole["id"] == 1 or urole["id"] == 2:
		await func.DeleteMSG(bot, user_id, uclean["home_id"])
		caption = f"<b>✉️ Меню рассылки.</b>\n\nВыберите уже существующую или сделайте новую:"
		markup = kb_admin_menu_newsletter(offset)
		r_message = await bot.send_message(user_id, caption, reply_markup=markup)
		db.SetClean(user_id, 'home_id', r_message.message_id)


# Управление рассылкой
@dp.callback_query_handler(text_startswith="call_a_menu_newsletter", state="*")
async def callback_a_menu_newsletter(call: CallbackQuery, state: FSMContext):
	user_id, message_id = call.message.chat.id, call.message.message_id
	udata, uclean = db.GetUsers(user_id), db.GetClean(user_id)

	state_data = await state.get_data()

	# Тип действия
	split = call.data.split(":")
	menu_item = split[1]
	try: action_type = split[2]
	except: action_type = False

	# Удалить сообщение если
	if (menu_item == "sender" and action_type == "send") or menu_item == "open" or menu_item == "delete":
		await func.DeleteMSG(bot, user_id, uclean["home_id"])

	# Сделать рассылку
	if menu_item == "sender":
		if not action_type:
			caption = "✉️ Создание новой рассылки.\n\n" \
						"⚠️ Внимание! Разрешено использование HTML разметки.\n" \
						"⏱ Если сообщение пропало и не появляется, может показаться что бот завис - это не так.\n" \
						"Время отправки рассылки зависит от количества пользователей в боте.\n\n" \
						"Тип сообщения: фото, гифка, текст.\nОжидается сообщение:"
			markup = kb_admin_menu_newsletter_handler("back")
			await StateNewsletter.data.set()
			await state.update_data(menu_item=menu_item)

		# Отправить
		if action_type == "send":
			content = [state_data.get("content_type", False), state_data.get("content_text", False), state_data.get("content_file", False)]
			send_id = []
			for i in db.GetUsers(multiple = True):
				try:
					if content[0] == "photo": s_message = await bot.send_photo(i["user_id"], content[2], content[1])
					if content[0] == "animation": s_message = await bot.send_animation(i["user_id"], content[2], caption=content[1])
					if content[0] == "text": s_message = await bot.send_message(i["user_id"], content[1])
					send_id.append(s_message.message_id)
				except: pass
			db.AddNewsletter(content[0], content[1], content[2], send_id, user_id)

			caption = f"<b>✅ Рассылка отправлена.</b>\n<b>✉️ Отправлено сообщение:</b> <i>{len(send_id)} шт.</i>"
			markup = kb_admin_menu_newsletter_handler("back")
			r_message = await bot.send_message(user_id, caption, reply_markup=markup)
			db.SetClean(user_id, 'home_id', r_message.message_id)

	# Информация о рассылке
	if menu_item == "open":
		data = db.GetNewsletter(int(action_type))
		content = [data["content_type"], data["content_text"], data["content_file"]]
		markup = kb_admin_menu_newsletter_handler("open", action_type)
		
		creator = db.GetUsers(data['creator_id'])
		count = len(data['send_id'].replace('[','').replace(' ','').replace(']','').split(','))

		if content[1] == 'None': content[1] = ''
		content[1] = content[1] + f"\n\n<b>✉️ Информация о рассылке:</b> <code>ID{data['newsletter_id']}</code>\n" \
							f"<b>♻️ Отправил:</b> <i>{creator['firstname']}</i>\n" \
							f"<b>⏱ Время:</b> <i>{data['creator_time']}</i>\n" \
							f"<b>🚀 Отправлено:</b> <i>{count} шт.</i>"
		if content[0] == "photo": r_message = await bot.send_photo(user_id, content[2], content[1], reply_markup=markup)
		if content[0] == "animation": r_message = await bot.send_animation(user_id, content[2], caption=content[1], reply_markup=markup)
		if content[0] == "text": r_message = await bot.send_message(user_id, content[1], reply_markup=markup)
		db.SetClean(user_id, 'home_id', r_message.message_id)

	# Удаление
	if menu_item == "delete":
		newsletter_id = int(action_type)
		data = db.GetNewsletter(newsletter_id)
		users = db.GetUsers(multiple = True)
		send_id = data['send_id'].replace('[','').replace(' ','').replace(']','').split(',')

		# Удаление сообщений
		x = 0
		for i in range(len(send_id)):
			await func.DeleteMSG(bot, users[i]["user_id"], int(send_id[i]))
			x = x + 1
		db.DeleteNewsletter(newsletter_id)

		caption = f"<b>✉️ Удаление рассылки.</b>\n<b>🗑 Удалено:</b> <i>{x} шт.</i>"
		markup = kb_admin_menu_newsletter_handler("back")
		r_message = await bot.send_message(user_id, caption, reply_markup=markup)
		db.SetClean(user_id, 'home_id', r_message.message_id)


	# Сообщение
	try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
	except: pass


# Обработчик управления рассылкой
@dp.message_handler(content_types=["text", "photo", "animation"], state=StateNewsletter.data)
async def callback_a_menu_newsletter_handler(message: types.Message, state: FSMContext):
	# __init__ #
	user_id, message_id = message.from_user.id, message.message_id
	udata, uclean = db.GetUsers(user_id), db.GetClean(user_id)
	await func.DeleteMSG(bot, user_id, message_id)
	message_id = uclean["home_id"]

	state_data = await state.get_data()
	
	# Тип действия
	menu_item = state_data.get("menu_item", False)

	if menu_item == "sender":
		# Обработка данных для рассылки
		content_type = False
		# Фото
		try:
			if message.photo: content_type = "photo"
		except: pass
		# GIF
		try:
			if message.animation: content_type = "animation"
		except: pass
		# Text
		try:
			if message.text: content_type = "text"
		except: pass

		# Получить текстовое содержимое
		if content_type == "photo" or content_type == "animation":
			try: content_text = message.caption
			except: content_text = False
		if content_type == "text": content_text = message.text

		# Отправить для проверки
		if content_type:
			markup = kb_admin_menu_newsletter_handler("sender")
			await func.DeleteMSG(bot, user_id, message_id)
			
			content_file = False
			if content_type == "photo":
				content_file = message.photo[-1].file_id
				r_message = await bot.send_photo(user_id, content_file, content_text, reply_markup=markup)
			if content_type == "animation":
				content_file = message.animation.file_id
				r_message = await bot.send_animation(user_id, content_file, caption=content_text, reply_markup=markup)
			if content_type == "text":
				r_message = await bot.send_message(user_id, content_text, reply_markup=markup)
			db.SetClean(user_id, 'home_id', r_message.message_id)
			
			await state.update_data(content_type=content_type)
			await state.update_data(content_text=content_text)
			await state.update_data(content_file=content_file)
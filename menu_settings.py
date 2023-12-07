from datetime import datetime
from string import Template

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from _loader import dp, bot
from handlers._states import StateSettings
from keyboards.inline.admin import *

import utils.sql._handlers as db
import utils._func as func


# Меню настроек магазина
@dp.callback_query_handler(text_startswith="admin_menu_settings", state="*")
async def admin_menu_settings(call: CallbackQuery, state: FSMContext):
	user_id, message_id = call.message.chat.id, call.message.message_id
	udata, urole = db.GetUsers(user_id), func.GetRole(user_id)

	# Параметры
	split = call.data.split(":")
	try: menu_switch = split[1]
	except: menu_switch = False
	try: menu_item = split[2]
	except: menu_item = False
	try: offset = split[3]
	except: offset = 0

	# Crutch
	if menu_item != "stickers":
		await state.finish()
	
	# Генерация
	if urole["id"] == 1 or urole["id"] == 2:
		markup = kb_admin_menu_settings(udata, menu_switch, menu_item, offset)
		settings = db.GetSettings()
		
		# Настройки
		if not menu_switch:
			if settings["engineering_mode"]: caption = "Технические работы"
			else: caption = "Работает"
			caption = f"<b>⚙️ Настройки магазина.</b>\n<b>🚧 Статус:</b> <code>{caption}</code>"
		
		# Главная
		if menu_switch == "main":
			caption = f"<b>🏠 Настройки главного экрана, стикеры, кнопки.</b>"
			# Главный экран
			if menu_item == "screen":
				caption = f"<b>🖥 Настройки главного экрана.</b>\n\nТекущий текст:\n{settings['screen_main']}"

			# Стикеры
			if menu_item == "stickers":
				caption = f"<b>🔥 Управление стикерами.</b>"
				state_data = await state.get_data()
				current_sticker = state_data.get("current", False)
				if current_sticker:
					try: await bot.delete_message(user_id, current_sticker)
					except: pass

			# Кнопка «Партнеры»
			if menu_item == "specbtn":
				if settings['specbtn_toggle']: caption = "Включена"
				else: caption = "Выключена"
				caption = f"<b>🌑 Управление кнопкой «Партнеры»</b>\n\nСтатус: {caption}\nТекст: {settings['specbtn_text']}\nСсылка: {settings['specbtn_link']}\n\n⚠️ Внимание! Ссылка должна быть в правильном формате, кликабельна."
		
		# Информация
		if menu_switch == "info":
			caption = f"<b>ℹ️ Настройка информации.</b>"
			# Контакты
			if menu_item == "contacts":
				caption = f"<b>☎️ Контакты</b>\n\nСодержимое:\n{settings['screen_contacts']}"

			# Инструкции
			if menu_item == "instructions":
				caption = f"<b>📖 Инструкции</b>\n\nСодержимое:\n{settings['screen_instructions']}"

			# Правила
			if menu_item == "rules":
				caption = f"<b>🎓 Правила</b>\n\nСодержимое:\n{settings['screen_rules']}"
			
			# Чат
			if menu_item == "chat":
				caption = f"<b>💬 Чат</b>\n\nСсылка: {settings['chat_link']}\n\n⚠️ Внимание! Ссылка должна быть в правильном формате, кликабельна."

		# Права доступа
		if menu_switch == "access":
			caption = f"<b>🔒 Управление правами доступа.</b>"

		# Технические работы
		if menu_switch == "engineering":
			if settings["engineering_mode"]:
				db.SetSettings('engineering_mode', '0')
				caption = "Работает"
			else:
				db.SetSettings('engineering_mode', '1')
				caption = "Технические работы"
			caption = f"<b>⚙️ Настройки магазина.</b>\n<b>🚧 Статус:</b> <code>{caption}</code>"

		# Сообщение
		try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
		except: pass


# Управление настройками
@dp.callback_query_handler(text_startswith="call_a_menu_settings", state="*")
async def callback_a_menu_settings(call: CallbackQuery, state: FSMContext):
	user_id, message_id = call.message.chat.id, call.message.message_id
	udata = db.GetUsers(user_id)
	
	state_data = await state.get_data()
	
	split = call.data.split(":")

	# Тип действия
	menu_switch = split[1]
	menu_item = split[2]
	try: action_type = split[3]
	except: action_type = False

	if menu_switch and menu_item:
		settings = db.GetSettings()
		# Главная
		if menu_switch == "main":
			# Главный экран
			if menu_item == "screen":
				# Изменить
				if action_type == "edit":
					caption = f"<b>🖥 Настройки главного экрана.</b>\n\n" \
						f"Текущий текст:\n{settings['screen_main']}\n\n" \
						f"⚠️ Внимание! Для этого экрана доступен вывод информации: Имя и баланс пользователя.\n" \
						f"Для их вывода напишите переменные <code>$username</code> и <code>$balance</code> в нужном месте.\n" \
						f"Пример: Ваше имя: <code>$username</code> (<code>$balance</code>).\n\n" \
						f"Введите новый текст:"
					markup = kb_admin_menu_settings_handler("back", menu_switch, menu_item)
					await StateSettings.data.set()
					await state.update_data(menu_switch=menu_switch)
					await state.update_data(menu_item=menu_item)
					await state.update_data(action_type=action_type)

				# Сохранить
				if action_type == "save":
					screen_main_text = state_data.get("screen_main_text", False)
					db.SetSettings("screen_main", screen_main_text)
					caption = f"<b>✅ Настройки успешно изменены.</b>"
					markup = kb_admin_menu_settings_handler("back", menu_switch, menu_item)

			# Стикеры
			if menu_item == "stickers":
				# Изменить
				if action_type != "save":
					if action_type == "home":
						caption = "🏠 Главное меню"
						sticker = settings["sticker_main"]
					if action_type == "shop":
						caption = "🛒 Купить (Каталог)"
						sticker = settings["sticker_shop"]
					if action_type == "pricelist":
						caption = "🗒 Прайс"
						sticker = settings["sticker_pricelist"]
					if action_type == "profile":
						caption = "🧑‍💼 Кабинет"
						sticker = settings["sticker_profile"]
					if action_type == "about":
						caption = "ℹ️ Информация"
						sticker = settings["sticker_about"]
					if action_type == "feedback":
						caption = "📮 Связь"
						sticker = settings["sticker_feedback"]
					
					if sticker == "Off":
						toggle = "Off"
						current = False
					else:
						toggle = "ниже"
						current = await call.message.answer_sticker(sticker)
					
					caption = f"<b>🔥 Изменение стикеров: {caption}</b>\n\nТекущий стикер: <code>{toggle}</code>\n\n⚠️ Отправьте новый стикер чтобы произвести замену, или слово «<code>Off</code>» для отключения:"
					markup = kb_admin_menu_settings_handler("back", menu_switch, menu_item)
					await StateSettings.data.set()
					await state.update_data(menu_switch=menu_switch)
					await state.update_data(menu_item=menu_item)
					await state.update_data(action_type=action_type)
					if current: await state.update_data(current=current.message_id)

				# Сохранить
				if action_type == "save":
					sticker_new = state_data.get("sticker_new", False)
					sticker_type = state_data.get("sticker_type", False)
					db.SetSettings(sticker_type, sticker_new)
					caption = f"<b>✅ Настройки успешно изменены.</b>"
					markup = kb_admin_menu_settings_handler("back", menu_switch, menu_item)

			# Кнопка «Партнеры»
			if menu_item == "specbtn":
				# Видимость
				if action_type == "visible":
					current = settings['specbtn_toggle']
					if current:
						db.SetSettings("specbtn_toggle", "0")
						caption = "Выключена"
					else:
						db.SetSettings("specbtn_toggle", "1")
						caption = "Включена"
					caption = f"<b>🌑 Управление кнопкой «Партнеры»</b>\n\nСтатус: {caption}\nТекст: {settings['specbtn_text']}\nСсылка: {settings['specbtn_link']}"
					markup = kb_admin_menu_settings(udata, menu_switch, menu_item)

				# Изменить
				if action_type == "edit":
					caption = f"<b>🌑 Настройка кнопки «Партнеры»</b>\n\nТекущее название: <i>{settings['specbtn_text']}</i>\nТекущая ссылка: {settings['specbtn_link']}\n\nВведите новое название:"
					markup = kb_admin_menu_settings_handler("back", menu_switch, menu_item)
					await StateSettings.data.set()
					await state.update_data(menu_switch=menu_switch)
					await state.update_data(menu_item=menu_item)
					await state.update_data(action_type=action_type)
					await state.update_data(stage_id="name")

				# Продолжить
				if action_type == "step":
					specbtn_text = state_data.get("specbtn_text", False)
					caption = f"<b>🌑 Настройка кнопки «Партнеры»</b>\n\nТекущее название: <i>{settings['specbtn_text']}</i>\nТекущая ссылка: {settings['specbtn_link']}\n\nНовое название: <i>{specbtn_text}</i>\nВведите новую ссылку:"
					markup = kb_admin_menu_settings_handler("back", menu_switch, menu_item)
					await state.update_data(stage_id="link")

				# Сохранить
				if action_type == "save":
					specbtn_text = state_data.get("specbtn_text", False)
					specbtn_link = state_data.get("specbtn_link", False)
					db.SetSettings("specbtn_text", specbtn_text)
					db.SetSettings("specbtn_link", specbtn_link)
					caption = f"<b>✅ Настройки успешно изменены.</b>"
					markup = kb_admin_menu_settings_handler("back", menu_switch, menu_item)

		# Информация
		if menu_switch == "info":
			# Подготовка
			if menu_item == "contacts":
				caption = "☎️ Контакты"
				current = "screen_contacts"
			if menu_item == "instructions":
				caption = "📖 Инструкции"
				current = "screen_instructions"
			if menu_item == "rules":
				caption = "🎓 Правила"
				current = "screen_rules"
			if menu_item == "chat":
				caption = "💬 Чат"
				current = "chat_link"

			# Изменить
			if action_type == "edit":
				caption = f"<b>ℹ️ Настройка информации: {caption}</b>\n\n⚠️ Внимание! Для кнопки «💬 Чат» значение это ссылка.\n\nТекущее значение:\n{settings[current]}\n\nВведите новое значение:"
				markup = kb_admin_menu_settings_handler("back", menu_switch, menu_item)
				await StateSettings.data.set()
				await state.update_data(menu_switch=menu_switch)
				await state.update_data(menu_item=menu_item)
				await state.update_data(action_type=action_type)

			# Сохранить
			if action_type == "save":
				new_value = state_data.get("new_value", False)
				db.SetSettings(current, new_value)
				caption = f"<b>✅ Настройки успешно изменены.</b>"
				markup = kb_admin_menu_settings_handler("back", menu_switch, menu_item)

		# Права доступа
		if menu_switch == "access":
			# Добавить
			if menu_item == "add":
				if not action_type:
					caption = "<b>🔒 Выдать права доступа.</b>\n\nВведите ID пользователя:"
					markup = kb_admin_menu_settings_handler("back", menu_switch)
					await StateSettings.data.set()
					await state.update_data(menu_switch=menu_switch)
					await state.update_data(menu_item=menu_item)
					await state.update_data(stage_id="admin_id")

				# Продолжить
				if action_type == "step":
					admin_id = state_data.get("admin_id", False)
					data = db.GetUsers(admin_id)
					caption = f"<b>🔒 Выдать права доступа.</b>\n\nID: <i>{admin_id}</i>\nUsername: @{data['username']}\nFirstname: <i>{data['firstname']}</i>\n\nВыберите права доступа:"
					markup = kb_admin_menu_settings_handler("access", menu_switch, menu_item)

				# Права доступа
				if action_type == "access":
					role_switch = split[4]
					admin_id = state_data.get("admin_id", False)
					data = db.GetUsers(admin_id)
					if role_switch == "root": role_data = [1, "👑 Гл. Администратор"]
					if role_switch == "admin": role_data = [2, "📗 Администратор"]
					if role_switch == "moder": role_data = [3, "📙 Модератор"]
					if role_switch == "operator": role_data = [4, "👨‍💻 Оператор"]
					if role_switch == "appeal": role_data = [5, "👨‍💻💢 Оператор"]
					if role_switch == "support": role_data = [6, "👨‍💻🛒 Оператор"]
					caption = f"<b>🔒 Выдать права доступа.</b>\n\nID: <i>{admin_id}</i>\nUsername: @{data['username']}\nFirstname: <i>{data['firstname']}</i>\n\nПрава доступа: <i>{role_data[1]}</i>"
					markup = kb_admin_menu_settings_handler("save", menu_switch, menu_item)
					await state.update_data(role_switch=role_data[0])

				# Сохранить
				if action_type == "save":
					admin_id = state_data.get("admin_id", False)
					role_switch = state_data.get("role_switch", False)
					db.UpdateUsers(admin_id, "role_id", role_switch)
					caption = f"<b>✅ Права успешно сохранены.</b>"
					markup = kb_admin_menu_settings_handler("back", menu_switch)

			# [Открыть/Уведомления]
			if menu_item == "open" or menu_item == "notify" or menu_item == "notify_appeal" or menu_item == "notify_support":
				select_id = int(action_type)
				data = db.GetUsers(select_id)
				role_notify = {
					"all": "Выключены",
					"appeal": "Выключены",
					"support": "Выключены"
				}
				if data["role_id"] == 1: role_data = "👑 Гл. Администратор"
				if data["role_id"] == 2: role_data = "📗 Администратор"
				if data["role_id"] == 3: role_data = "📙 Модератор"
				if data["role_id"] == 4: role_data = "👨‍💻 Оператор"
				if data["role_id"] == 5: role_data = "👨‍💻💢 Оператор"
				if data["role_id"] == 6: role_data = "👨‍💻🛒 Оператор"
				if data["role_notify"]: role_notify["all"] = "Включены"
				if data["role_notify_appeal"]: role_notify["appeal"] = "Включены"
				if data["role_notify_support"]: role_notify["support"] = "Включены"
				
				# Все уведомления
				if menu_item == "notify":
					if data["role_notify"]:
						role_notify["all"] = "Выключены"
						db.UpdateUsers(select_id, 'role_notify', '0')
					else:
						role_notify["all"] = "Включены"
						db.UpdateUsers(select_id, 'role_notify', '1')
			
				# Жалобы
				if menu_item == "notify_appeal":
					if data["role_notify_appeal"]:
						role_notify["appeal"] = "Выключены"
						db.UpdateUsers(select_id, 'role_notify_appeal', '0')
					else:
						role_notify["appeal"] = "Включены"
						db.UpdateUsers(select_id, 'role_notify_appeal', '1')
				
				# Прямая покупка
				if menu_item == "notify_support":
					if data["role_notify_support"]:
						role_notify["support"] = "Выключены"
						db.UpdateUsers(select_id, 'role_notify_support', '0')
					else:
						role_notify["support"] = "Включены"
						db.UpdateUsers(select_id, 'role_notify_support', '1')

				caption = f"<b>🔒 Управление правами доступа.</b>\n\nID: <i>{select_id}</i>\nUsername: @{data['username']}\nFirstname: <i>{data['firstname']}</i>\n\nПрава доступа: <i>{role_data}</i>\nУведомления: <i>{role_notify['all']}</i>\nО жалобах: <i>{role_notify['appeal']}</i>\nО прямой покупке: <i>{role_notify['support']}</i>"
				markup = kb_admin_menu_settings(udata, menu_switch, "open", select_id = select_id)

			# Удалить
			if menu_item == "delete":
				select_id = int(action_type)
				db.UpdateUsers(select_id, 'role_id', '0')
				db.UpdateUsers(select_id, 'role_notify', '0')
				db.UpdateUsers(select_id, 'role_notify_appeal', '0')
				db.UpdateUsers(select_id, 'role_notify_support', '0')
				caption = f"<b>❌ Права успешно удалены.</b>"
				markup = kb_admin_menu_settings_handler("back", menu_switch)


		# Сообщение
		try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
		except: pass


# Обработчик управления настройками
@dp.message_handler(content_types=["text", "sticker"], state=StateSettings.data)
async def callback_a_menu_settings_handler(message: types.Message, state: FSMContext):
	# __init__ #
	user_id, message_id = message.from_user.id, message.message_id
	udata, uclean = db.GetUsers(user_id), db.GetClean(user_id)
	await func.DeleteMSG(bot, user_id, message_id)
	message_id = uclean["home_id"]

	state_data = await state.get_data()
	
	# Тип действия
	menu_switch = state_data.get("menu_switch", False)
	menu_item = state_data.get("menu_item", False)
	action_type = state_data.get("action_type", False)
	try: get_data = message.text
	except: get_data = ""

	if menu_switch and menu_item:
		settings = db.GetSettings()
		# Главная
		if menu_switch == "main":
			# Главный экран
			if menu_item == "screen":
				if len(get_data):
					# Изменить
					if action_type == "edit":
						caption = f"<b>🖥 Настройки главного экрана.</b>\n\n" \
							f"Текущий текст:\n{settings['screen_main']}\n\n" \
							f"⚠️ Внимание! Для этого экрана доступен вывод информации: Имя и баланс пользователя.\n" \
							f"Для их вывода напишите переменные <code>$username</code> и <code>$balance</code> в нужном месте.\n" \
							f"Пример: Ваше имя: <code>$username</code> (<code>$balance</code>).\n\n" \
							f"Новый текст:\n{get_data}"
						markup = kb_admin_menu_settings_handler("save", menu_switch, menu_item)
						await state.update_data(screen_main_text=get_data)

			# Стикеры
			if menu_item == "stickers":
				try: new_sticker = message.sticker.file_id
				except: new_sticker = False
				if new_sticker or get_data == "Off":
					if action_type == "home":
						caption = "🏠 Главное меню"
						sticker = "sticker_main"
					if action_type == "shop":
						caption = "🛒 Купить (Каталог)"
						sticker = "sticker_shop"
					if action_type == "pricelist":
						caption = "🗒 Прайс"
						sticker = "sticker_pricelist"
					if action_type == "profile":
						caption = "🧑‍💼 Кабинет"
						sticker = "sticker_profile"
					if action_type == "about":
						caption = "ℹ️ Информация"
						sticker = "sticker_about"
					if action_type == "feedback":
						caption = "📮 Связь"
						sticker = "sticker_feedback"
					
					current = state_data.get("current", False)
					try: await bot.delete_message(user_id, current)
					except: pass
					if get_data == "Off":
						toggle = "Off"
						new_sticker = "Off"
					else: toggle = "ниже"
					
					caption = f"<b>🔥 Изменение стикеров: {caption}</b>\n\nНовый стикер: <code>{toggle}</code>\n\n⚠️ Отправьте новый стикер чтобы произвести замену, или слово «<code>Off</code>» для отключения:"
					markup = kb_admin_menu_settings_handler("save", menu_switch, menu_item)
					
					try: current = await message.answer_sticker(new_sticker)
					except: current = False
					await state.update_data(sticker_type=sticker)
					await state.update_data(sticker_new=new_sticker)
					if current: await state.update_data(current=current.message_id)

			# Кнопка «Партнеры»
			if menu_item == "specbtn":
				if len(get_data):
					# Изменить
					if action_type == "edit":
						stage_id = state_data.get("stage_id", False)
						# Новое название
						if stage_id == "name":
							caption = f"<b>🌑 Настройка кнопки «Партнеры»</b>\n\nТекущее название: <i>{settings['specbtn_text']}</i>\nТекущая ссылка: {settings['specbtn_link']}\n\nНовое название: <i>{get_data}</i>"
							markup = kb_admin_menu_settings_handler("step", menu_switch, menu_item)
							await state.update_data(specbtn_text=get_data)

						# Новая ссылка
						if stage_id == "link":
							specbtn_text = state_data.get("specbtn_text", False)
							caption = f"<b>🌑 Настройка кнопки «Партнеры»</b>\n\nТекущее название: <i>{settings['specbtn_text']}</i>\nТекущая ссылка: {settings['specbtn_link']}\n\nНовое название: <i>{specbtn_text}</i>\nНовая ссылка: {get_data}"
							markup = kb_admin_menu_settings_handler("save", menu_switch, menu_item)
							await state.update_data(specbtn_link=get_data)

		# Информация
		if menu_switch == "info":
			# Подготовка
			if menu_item == "contacts":
				caption = "☎️ Контакты"
				current = "screen_contacts"
			if menu_item == "instructions":
				caption = "📖 Инструкции"
				current = "screen_instructions"
			if menu_item == "rules":
				caption = "🎓 Правила"
				current = "screen_rules"
			if menu_item == "chat":
				caption = "💬 Чат"
				current = "chat_link"

			# Изменить
			if action_type == "edit" and len(get_data):
				caption = f"<b>ℹ️ Настройка информации: {caption}</b>\n\n⚠️ Внимание! Для кнопки «💬 Чат» значение это ссылка.\n\nТекущее значение:\n{settings[current]}\n\nНовое значение:\n{get_data}"
				markup = kb_admin_menu_settings_handler("save", menu_switch, menu_item)
				await state.update_data(new_value=get_data)

		# Права доступа
		if menu_switch == "access":
			# Добавить
			get_data = func.StrToNum(get_data)
			if menu_item and type(get_data) == int:
				stage_id = state_data.get("stage_id", False)
				if stage_id == "admin_id":
					data = db.GetUsers(get_data)
					if data:
						caption = f"<b>🔒 Выдать права доступа.</b>\n\nID: <i>{data['user_id']}</i>\nUsername: @{data['username']}\nFirstname: <i>{data['firstname']}</i>"
						markup = kb_admin_menu_settings_handler("step", menu_switch, menu_item)
						await state.update_data(admin_id=get_data)
					else:
						caption = "<b>🔒 Выдать права доступа.</b>\n\n🚫 Пользователь не найден.\n\nВведите ID пользователя:"
						markup = kb_admin_menu_settings_handler("back", menu_switch, menu_item)

		# Сообщение
		try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
		except: pass
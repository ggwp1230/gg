from datetime import datetime
from string import Template

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import CallbackQuery

from _loader import dp, bot
from handlers._states import StateUsers
import handlers._system_start as _system
from keyboards.inline.admin import *

import utils.sql._handlers as db
import utils._func as func


# Пользователи
@dp.callback_query_handler(text_startswith="admin_menu_users", state="*")
async def admin_menu_users(call: CallbackQuery, state: FSMContext):
	user_id, message_id = call.message.chat.id, call.message.message_id
	udata = db.GetUsers(user_id)
	
	await state.finish()
	
	split = call.data.split(":")
	try: search = split[1]
	except: search = False
	try: offset = int(split[2])
	except: offset = 0

	# Поиск пользователей
	if not search:
		caption = "<b>💵 Управление пользователями.</b>\n\n⚠️ Внимание! Поиск пользователя происходит по 3 основным параметрам: ID, Username, Firstname\n\nВведите данные для поиска:"
		markup = kb_admin_menu_users_handler("back")
		await StateUsers.data.set()
		await state.update_data(action_type="search")
	
	# Навигация по поиску	
	if search:
		caption = "<b>💵 Управление пользователями.</b>\n\n⚠️ Внимание! Поиск пользователя происходит по 3 основным параметрам: ID, Username, Firstname"
		markup = kb_admin_menu_users(offset, search.replace('@',''))


	# Сообщение
	try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
	except: pass


# Управление пользователями
@dp.callback_query_handler(text_startswith="call_a_menu_users", state="*")
async def callback_a_menu_users(call: CallbackQuery, state: FSMContext):
	user_id, message_id = call.message.chat.id, call.message.message_id
	udata = db.GetUsers(user_id)
	
	state_data = await state.get_data()

	# Тип действия
	split = call.data.split(":")
	menu_item = split[1]
	try: search_id = split[2]
	except: search_id = False
	try: search = split[3]
	except: search = False

	# Управление пользователем
	if menu_item == "open" and search_id and search:
		data = db.GetUsers(search_id)
		caption = "<b>💵 Управление пользователями.</b>\n\n" \
					f"<b>🧑‍💼 ID:</b> <code>{data['user_id']}</code>\n" \
					f"<b>🏷 Имя:</b> <code>{data['firstname']}</code>\n" \
					f"<b>📌 Username:</b> @{data['username']}\n\n" \
					f"<b>💰 Баланс:</b> <i>{data['balance']} KZT</i>\n\n" \
					f'<b>💎 Пополнено:</b> <code>{udata["s_pay"]} KZT</code>\n\n' \
					f'<b>🛒 Покупок:</b> <code>{udata["s_buy"]}</code>\n' \
					f'<b>💳 На сумму:</b> <code>{udata["s_buy_pay"]} KZT</code>\n\n' \
					f"<b>⏱ Регистрация:</b> <i>{data['reg_time']}</i>"
		markup = kb_admin_menu_users_handler("open", search_id, search)

	# Изменить баланс
	if menu_item == "balance" and search_id:
		data = db.GetUsers(search_id)
		caption = f"<b>💳 Управление балансом пользователя.</b>\n\nТекущий баланс: <i>{data['balance']} KZT</i>\nВведите новый баланс:" # Валюта
		markup = kb_admin_menu_users_handler("back", search_id, search)
		await StateUsers.data.set()
		await state.update_data(action_type="balance")
		await state.update_data(search_id=search_id)
		await state.update_data(search=search)

	# Сохранить
	if menu_item == "save":
		action_type = state_data.get("action_type", False)
		search_id = state_data.get("search_id", False)
		search = state_data.get("search", False)
		# Баланс
		if action_type == "balance":
			data = db.GetUsers(search_id)
			new_balance = state_data.get("new_balance", 0)
			db.UpdateUsers(search_id, 'balance', new_balance)
			caption = f"<b>✅ Баланс пользователя, успешно изменен.</b>"
			markup = kb_admin_menu_users_handler("back", search_id, search)
			await _system.SendNotify(f"<b>🔉 Администратор:</b> <code>{udata['firstname']}</code>\n<b>Действие:</b> ✏️ Изменил баланс пользователя.\n<b>Пользователь:</b> @{data['username']}\n<b>Баланс:</b> <i>{data['balance']} KZT</i> » <i>{new_balance} KZT</i>")

	# История пополнений
	if menu_item == "pay_history" or menu_item == "buy_history":
		data = db.GetUsers(search_id)

		try: offset = int(split[4])
		except: offset = 0

		if menu_item == "pay_history":
			caption = "<b>📗 История пополнений.</b>"
		if menu_item == "buy_history":
			caption = "<b>📙 История покупок.</b>"

		caption = f"{caption}\n\n" \
					f"<b>🧑‍💼 ID:</b> <code>{data['user_id']}</code>\n" \
					f"<b>🏷 Имя:</b> <code>{data['firstname']}</code>\n" \
					f"<b>📌 Username:</b> @{data['username']}\n\n" \
					f"<b>💰 Баланс:</b> <i>{data['balance']} KZT</i>" # Валюта

		if menu_item == "pay_history":
			caption = f"{caption}\n\n" \
					f'<b>💎 Пополнено:</b> <code>{udata["s_pay"]} KZT</code>'
		if menu_item == "buy_history":
			caption = "<b>📙 История покупок.</b>" \
					f'<b>🛒 Покупок:</b> <code>{udata["s_buy"]}</code>\n' \
					f'<b>💳 На сумму:</b> <code>{udata["s_buy_pay"]} KZT</code>'

		markup = kb_admin_menu_users_history(menu_item, search_id, search, offset)

	# Открыть историю
	if menu_item == "pay_history_open" or menu_item == "buy_history_open":
		try: offset = int(split[4])
		except: offset = 0

		trns_id = int(split[5])
		users = db.GetUsers(search_id)

		if menu_item == "pay_history_open":
			data = db.GetTransaction("pay", trns_id)
			if data["pay_system"] == "qiwi:p2p": method_name = "QiwiP2P (По форме)"
			if data["pay_system"] == "qiwi:terminal": method_name = "Qiwi Терминал"
			if data["pay_system"] == "qiwi:nickname": method_name = "Qiwi (По никнейму)"
			caption = f"<b>📖 Транзакция:</b> <code>#{data['pay_id']}</code>\n" \
				f"<b>Пользователь:</b> <a href='tg://user?id={data['user_id']}'>{users['firstname']}</a> (@{users['username']}) | {data['user_id']}\n" \
				f"<b>⏱ Время платежа:</b> <i>{data['pay_time']}</i>\n" \
				f"<b>🏦 Способ:</b> <i>{method_name}</i>\n" \
				f"<b>🧾 Код:</b> <i>{data['receipt']}</i>\n" \
				f"<b>💰 Сумма:</b> <i>{data['amount']} {data['currency'].upper()}</i>\n" \
				f"<b>До:</b> <i>{data['before']} KZT</i>\n" \
				f"<b>После:</b> <i>{data['after']} KZT</i> ⚠️ <code>0 = NaN</code>\n\n" \
				f"<b>📍 Статус:</b> <i>{data['pay_status']}</i>"

		if menu_item == "buy_history_open":
			data = db.GetTransaction("buy", trns_id)
			creator = db.GetUsers(data["creator_id"])
			caption = f"<b>📖 Транзакция:</b> <code>#{data['buy_id']}</code>\n" \
				f"<b>Пользователь:</b> <a href='tg://user?id={data['user_id']}'>{users['firstname']}</a> (@{users['username']}) | {data['user_id']}\n" \
				f"<b>До:</b> <i>{data['before']} KZT</i>\n" \
				f"<b>После:</b> <i>{data['after']} KZT</i>\n" \
				f"<b>⏱ Время покупки:</b> <i>{data['buy_time']}</i>\n" \
				f"<b>📋 Позиция:</b> <i>{data['position_name']}</i>\n" \
				f"<b>💰 Цена:</b> <i>{data['price']} KZT</i>\n\n" \
				f"<b>📍 Товар:</b> {data['content']}\n" \
				f"<b>Добавил:</b> <a href='tg://user?id={data['creator_id']}'>{creator['firstname']}</a> (@{creator['username']}) | {data['creator_id']}\n" \
				f"<b>Дата:</b> <i>{data['creator_id']}</i>"

		markup = kb_admin_menu_users_history(menu_item.replace("_open", ""), search_id, search, offset, True)

	# Сообщение
	try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
	except: pass


# Обработчик управления пользователями
@dp.message_handler(content_types=["text"], state=StateUsers.data)
async def callback_a_menu_users_handler(message: types.Message, state: FSMContext):
	# __init__ #
	user_id, message_id = message.from_user.id, message.message_id
	udata, uclean = db.GetUsers(user_id), db.GetClean(user_id)
	await func.DeleteMSG(bot, user_id, message_id)
	message_id = uclean["home_id"]

	state_data = await state.get_data()
	action_type = state_data.get("action_type", False)
	search_id = state_data.get("search_id", False)
	search = state_data.get("search", False)

	get_data = message.text
	if len(get_data):
		# Поиск пользователя
		if action_type == "search":
			caption = "<b>💵 Управление пользователями.</b>\n\n⚠️ Внимание! Поиск пользователя происходит по 3 основным параметрам: ID, Username, Firstname"
			search = db.GetUsers(search = get_data)
			if not search:
				caption = caption + f"\n\n🚫 Запрос: «<code>{get_data}</code>». Нет результатов."
				markup = kb_admin_menu_users_handler("back")
			else:
				markup = kb_admin_menu_users(search = get_data)

		# Изменить баланс
		if action_type == "balance":
			get_data = func.StrToNum(get_data)
			if type(get_data) == int or type(get_data) == float:
				data = db.GetUsers(search_id)
				caption = f"<b>💳 Управление балансом пользователя.</b>\n\nТекущий баланс: <i>{data['balance']} KZT</i>\nНовый баланс: <i>{get_data} KZT</i>" # Валюта
				markup = kb_admin_menu_users_handler("save", search_id, search)
				await state.update_data(new_balance=get_data)


		# Сообщение
		try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
		except: pass
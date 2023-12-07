from datetime import datetime
from string import Template

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from _loader import dp, bot
from handlers._states import StateTransactions
from keyboards.inline.admin import *

import utils.sql._handlers as db
import utils._func as func


# Пользователи
@dp.callback_query_handler(text_startswith="admin_menu_transactions", state="*")
async def admin_menu_transactions(call: CallbackQuery, state: FSMContext):
	user_id, message_id = call.message.chat.id, call.message.message_id
	udata = db.GetUsers(user_id)
	
	await state.finish()
	
	split = call.data.split(":")
	try: menu_switch = split[1]
	except: menu_switch = False
	try: offset = int(split[2])
	except: offset = 0

	# Выбор типа
	if not menu_switch:
		caption = "<b>🔍 История транзакций.</b>\n\nВыберите тип:"
		markup = kb_admin_menu_transactions(menu_switch)
	
	# Пополнения
	if menu_switch == "pay":
		caption = "<b>🔍 История транзакций.</b>\n\nВыберите транзакцию или действие:"
		markup = kb_admin_menu_transactions(menu_switch, offset)

	# Продажи
	if menu_switch == "buy":
		caption = "<b>🔍 История транзакций.</b>\n\nВыберите транзакцию или действие:"
		markup = kb_admin_menu_transactions(menu_switch, offset)
	
	# Открыть
	if menu_switch == "open":
		menu_item = split[2]
		# Пополнение
		if menu_item == "pay":
			pay_id = int(split[3])
			data = db.GetTransaction("pay", pay_id)
			users = db.GetUsers(data["user_id"])
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
			markup = kb_admin_menu_transactions(menu_switch, menu_item = menu_item, pay_id = pay_id)

		# Продажа
		if menu_item == "buy":
			buy_id = int(split[3])
			data = db.GetTransaction("buy", buy_id)
			users = db.GetUsers(data["user_id"])
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
			markup = kb_admin_menu_transactions(menu_switch, menu_item = menu_item, pay_id = buy_id)

	# Взаимодействие
	if menu_switch == "action":
		menu_item = split[2]
		# Пополнение
		if menu_item == "pay":
			pay_id = int(split[3])
			# Метка Support
			db.UpdateTransaction("pay", pay_id, "pay_status", "SUPPORT")
			caption = "<b>✅ Метка установлена.</b>"
			markup = kb_admin_menu_transactions(menu_switch, menu_item = menu_item, pay_id = pay_id)

	# Поиск
	if menu_switch == "search":
		menu_item = split[2]
		if menu_item == "pay": name = "Пополнения"
		if menu_item == "buy": name = "Продажи"
		caption = f"<b>🔍 Поиск транзакции. [{name}]</b>\n\nВведите ID транзакции:"
		markup = kb_admin_menu_transactions(menu_switch, menu_item = menu_item)
		await StateTransactions.data.set()
		await state.update_data(menu_item=menu_item)


	# Сообщение
	try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
	except: pass


# Поиск транзакций
@dp.message_handler(content_types=["text"], state=StateTransactions.data)
async def admin_menu_users_handler(message: types.Message, state: FSMContext):
	# __init__ #
	user_id, message_id = message.from_user.id, message.message_id
	udata, uclean = db.GetUsers(user_id), db.GetClean(user_id)
	await func.DeleteMSG(bot, user_id, message_id)
	message_id = uclean["home_id"]

	state_data = await state.get_data()
	menu_item = state_data.get("menu_item", False)

	get_data = func.StrToNum(message.text)
	if type(get_data) == int or type(get_data) == float:
		if menu_item == "pay": name = "Пополнения"
		if menu_item == "buy": name = "Продажи"
		caption = f"<b>🔍 Поиск транзакции. [{name}]</b>\n\n<b>ID:</b> <code>#{get_data}</code>"
		markup = kb_admin_menu_transactions("search", menu_item = menu_item, pay_id = get_data)

	# Сообщение
	try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
	except: pass
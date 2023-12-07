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
import random


# Прайс-лист
@dp.callback_query_handler(text_startswith="menu_profile", state="*")
async def menu_profile(call: CallbackQuery, state: FSMContext):
	user_id, message_id = call.message.chat.id, call.message.message_id
	udata, uclean, settings = db.GetUsers(user_id), db.GetClean(user_id), db.GetSettings()

	if settings['engineering_mode'] and not func.GetRole(user_id)["id"]: return await _system.engineering_work(user_id, message_id)

	split = call.data.split(":")
	try: action_type = split[1]
	except: action_type = False
	try: item_type = split[2]
	except: item_type = False
	try: offset = int(split[3])
	except: offset = 0

	# Профиль
	if not action_type:
		caption = f'<b>👨‍⚕️ Личный кабинет</b>\n\n' \
				f'<b>🍁 ID:</b> <code>{udata["user_id"]}</code>\n' \
				f'<b>🔅 Имя:</b> <a href="tg://?user={udata["user_id"]}">{udata["firstname"]}</a>\n' \
				f'<b>💰Баланс:</b> <code>{udata["balance"]} KZT</code>\n' \
				f'<b>💎 Пополнено:</b> <code>{udata["s_pay"]} KZT</code>\n\n' \
				f'<b>🛒 Покупок:</b> <code>{udata["s_buy"]}</code>\n' \
				f'<b>💳 На сумму:</b> <code>{udata["s_buy_pay"]} KZT</code>\n\n' \
				f'<b>⏱Регистрация:</b> <i>{udata["reg_time"]}</i>'
		markup = kb_menu_profile() # Валюта

	# История
	if action_type == "history":
		# Пополнений
		if item_type == "pay":
			caption = f"<b>📗 История пополнений.</b>"

		# Покупок
		if item_type == "buy":
			caption = f"<b>📙 История покупок.</b>"
		
		markup = kb_menu_profile(action_type, item_type, offset, user_id)

	# Открыть
	if action_type == "open":
		select_id = int(split[3])
		
		# Пополнение
		if item_type == "pay":
			caption = f"<b>📖 Транзакция:</b> <code>#{select_id}</code>"
			data = db.GetTransaction("pay", select_id)
			if data["pay_system"] == "qiwi:p2p": method_name = "QiwiP2P (По форме)"
			if data["pay_system"] == "qiwi:terminal": method_name = "Qiwi Терминал"
			if data["pay_system"] == "qiwi:nickname": method_name = "Qiwi (По никнейму)"
			caption = f"<b>📖 Транзакция:</b> <code>#{data['pay_id']}</code>\n" \
				f"<b>⏱ Время платежа:</b> <i>{data['pay_time']}</i>\n" \
				f"<b>🏦 Способ:</b> <i>{method_name}</i>\n" \
				f"<b>🧾 Код:</b> <i>{data['receipt']}</i>\n" \
				f"<b>💰 Сумма:</b> <i>{data['amount']} {data['currency'].upper()}</i>\n\n" \
				f"<b>📍 Статус:</b> <i>{data['pay_status']}</i>"
			markup = kb_menu_profile("back", split[4].replace('*',':'))

		# Покупка
		if item_type == "buy":
			data = db.GetTransaction("buy", select_id)
			caption = f"<b>📖 Транзакция:</b> <code>#{data['buy_id']}</code>\n" \
				f"<b>⏱ Время покупки:</b> <i>{data['buy_time']}</i>\n" \
				f"<b>📋 Позиция:</b> <i>{data['position_name']}</i>\n" \
				f"<b>💰 Цена:</b> <i>{data['price']} KZT</i>\n\n" \
				f"<b>📍 Товар:</b> {data['content']}"
			markup = kb_menu_profile("back", split[4].replace('*',':'))


	# Сообщение
	if uclean['location'] != "menu_profile":
		await func.DeleteMSG(bot, user_id, [message_id, uclean["sticker_id"], uclean["home_id"]])
		try: r_sticker = await call.message.answer_sticker(settings["sticker_profile"])
		except: r_sticker = False
		if r_sticker: db.SetClean(user_id, "sticker_id", r_sticker.message_id)
		r_message = await bot.send_message(user_id, caption, reply_markup=markup)
		db.SetClean(user_id, "home_id", r_message.message_id)
		db.SetClean(user_id, "location", "menu_profile")
	else:
		try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
		except: pass
from datetime import datetime
from string import Template
from pyqiwip2p import QiwiP2P

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from _loader import dp, bot
from handlers._states import StatePaySystem
import handlers._system_start as _system
from keyboards.inline.admin import *

import asyncio, json, requests
import utils.sql._handlers as db
import utils._func as func


# Платежные системы
@dp.callback_query_handler(text_startswith="admin_menu_payments", state="*")
async def admin_menu_payments(call: CallbackQuery, state: FSMContext):
	user_id, message_id = call.message.chat.id, call.message.message_id
	udata, urole = db.GetUsers(user_id), func.GetRole(user_id)
	await state.finish()

	# Параметры
	split = call.data.split(":")
	try: menu_switch = split[1]
	except: menu_switch = False
	try: currency = split[2]
	except: currency = False
	if currency == "rub" or currency == "kzt":
		try: menu_item = split[3]
		except: menu_item = False
	else:
		try: menu_item = split[2]
		except: menu_item = False

	# Генерация
	if urole["id"] == 1 or urole["id"] == 2:	
		paysys = db.GetPaySystem()
		
		# Список
		if not menu_switch:
			caption = "<b>💳 Платежные системы.</b>"

		# QIWI
		if menu_switch == "qiwi":
			if not currency:
				caption = "<b>💳 Платежные системы.</b>\n<b>⚙️ Способ:</b> <code>Qiwi</code>"

			if currency:
				if currency == "rub": country = "🇷🇺"
				if currency == "kzt": country = "🇰🇿"
				caption = f"<b>💳 Платежные системы.</b>\n<b>⚙️ Способ:</b> {country} <code>Qiwi</code>"
				paysys = paysys[f"{menu_switch}_{currency}"].split('|*|')

			if menu_item and menu_item != "action" and currency:
				if menu_item == "p2p": method_name, paysys = "По форме", paysys[0]
				if menu_item == "terminal": method_name, paysys = "По комментарию (Терминал)", paysys[1]
				if menu_item == "nickname": method_name, paysys = "По никнейму", paysys[2]
				paysys = paysys.split(':')
				if func.StrBool(paysys[1]): status = "<b>🟢 Статус:</b> <code>On</code>"
				else: status = "<b>🔴 Статус:</b> <code>Off</code>"
				if paysys[2] != "NaN": token = "<b>🔑 Токен:</b> <code>Указан</code>"
				else: token = "<b>🔑 Токен:</b> <code>NaN</code>"
				phone = f"<b>📱 Телефон:</b> <code>{paysys[3]}</code>"
				try: nickname = f"\n<b>🏷 Никнейм:</b> <code>{paysys[4]}</code>"
				except: nickname = ""
				caption = f"<b>💳 Платежные системы.</b>\n<b>⚙️ Способ:</b> {country} <code>Qiwi</code>\n<b>🔩 Метод:</b> <code>{method_name}</code>\n{status}\n{token}\n{phone}{nickname}"

			# Действия
			if menu_item == "action":
				menu_item = split[4]
				action = split[5]
				if menu_item == "p2p": method_name = "По форме"
				if menu_item == "terminal": method_name = "По комментарию (Терминал)"
				if menu_item == "nickname": method_name = "По никнейму"

				# Включить / Выключить
				if action == "on" or action == "off":
					caption = f"<b>💳 Платежные системы.</b>\n<b>⚙️ Способ:</b> {country} <code>Qiwi</code>\n<b>🔩 Метод:</b> <code>{method_name}</code>\n"

				# Включить
				if action == "on":
					db.SetPaySystem(f"qiwi", menu_item, currency, visible = "1")
					caption = caption + "<b>🟢 Статус:</b> <code>On</code>"
					await _system.SendNotify(f"<b>🔉 Администратор:</b> <code>{udata['firstname']}</code>\n<b>Действие:</b> 🟢 Включил <i>Qiwi ({method_name})</i> пополнения")

				# Выключить
				if action == "off":
					db.SetPaySystem(f"qiwi", menu_item, currency, visible = "0")
					caption = caption + "<b>🔴 Статус:</b> <code>Off</code>"
					await _system.SendNotify(f"<b>🔉 Администратор:</b> <code>{udata['firstname']}</code>\n<b>Действие:</b> 🔴 Выключил <i>Qiwi ({method_name})</i> пополнения")

				# Телефон / Токен
				if action == "token" or action == "phone":
					sub_action = split[6]
					caption = f"<b>💳 Платежные системы.</b>\n<b>⚙️ Способ:</b> {country} <code>Qiwi</code>\n<b>🔩 Метод:</b> <code>{method_name}</code>\n"
					if menu_item == "p2p": ps_id = 0
					if menu_item == "terminal": ps_id = 1
					if menu_item == "nickname": ps_id = 2
					paysys = paysys[ps_id].split(':')

				# Добавить телефон
				if action == "phone":
					if sub_action == "edit":
						caption = caption + "\nВведите логин (номер) Qiwi кошелька:"
						
						await StatePaySystem.data.set()
						await state.update_data(menu_switch=menu_switch)
						await state.update_data(menu_item=menu_item)
						await state.update_data(currency=currency)
						await state.update_data(action=action)
						await state.update_data(sub_action=sub_action)
						menu_switch = "cancel"

				# Добавить токен
				if action == "token":
					if sub_action == "edit":
						if paysys[3] == "NaN":
							caption = caption + "\n❌ Для начала укажите логин (номер)."
						else:
							# По форме
							if menu_item == "p2p":
								caption = caption + "\n⚠️ Получить можно тут 👉 <a href='https://qiwi.com/p2p-admin/transfers/api'>Перейти по ссылке</a>\nВведите приватный p2p токен:"
							
							# По комментарию и никнейму
							if menu_item == "terminal" or menu_item == "nickname":
								caption = caption + "\n⚠️ Получить можно тут 👉 <a href='https://qiwi.com/api'>Перейти по ссылке</a>\nПри получении токена, ставьте только первые 3 галочки.\nВведите QIWI токен:"
							
							await StatePaySystem.data.set()
							await state.update_data(menu_switch=menu_switch)
							await state.update_data(menu_item=menu_item)
							await state.update_data(currency=currency)
							await state.update_data(action=action)
							await state.update_data(sub_action=sub_action)
							await state.update_data(phone=paysys[3])
							menu_switch = "cancel"

		markup = kb_admin_menu_payments(udata, menu_switch, menu_item, currency)


		# Сообщение
		try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
		except: pass


# Обработчик платежных систем
@dp.message_handler(content_types=["text"], state=StatePaySystem.data)
async def admin_menu_payments_handler(message: types.Message, state: FSMContext):
	# __init__ #
	user_id, message_id = message.from_user.id, message.message_id
	udata, uclean = db.GetUsers(user_id), db.GetClean(user_id)
	await func.DeleteMSG(bot, user_id, message_id)

	message_id = uclean["home_id"]

	state_data = await state.get_data()
	get_data = message.text

	if len(get_data):
		menu_switch = state_data.get("menu_switch", False)
		menu_item = state_data.get("menu_item", False)
		currency = state_data.get("currency", False)
		action = state_data.get("action", False)
		sub_action = state_data.get("sub_action", False)
		phone = state_data.get("phone", False)

		# Qiwi
		if menu_switch == "qiwi":
			if currency:
				# Телефон
				if action == "phone":
					if sub_action == "edit":
						db.SetPaySystem("qiwi", menu_item, currency, phone = get_data)
						await _system.SendNotify(f"<b>🔉 Администратор:</b> <code>{udata['firstname']}</code>\n<b>Действие:</b> 📱 Изменил данные для: <i>Qiwi ({menu_item})</i>")
						caption = "<b>✅ Логин (номер) успешно изменён.</b>"
						markup = kb_admin_menu_payments(udata, "exit")
						await state.finish()

				# Токен
				if action == "token":
					# Добавить / Редактировать TOKEN
					if sub_action == "edit":
						# Для P2P формы
						if menu_item == "p2p":
							try: 
								qiwi = QiwiP2P(get_data)
								bill = qiwi.bill(amount=1, lifetime=1)
								error = False
							except: error = True
							if error:
								caption = "<b>❌ Неверный приватный p2p токен.</b>\n\nВведите новый токен:"
								markup = kb_admin_menu_payments(udata, "cancel")
							else:
								db.SetPaySystem("qiwi", menu_item, currency, token = get_data)
								await _system.SendNotify(f"<b>🔉 Администратор:</b> <code>{udata['firstname']}</code>\n<b>Действие:</b> 🔑 Изменил данные для: <i>Qiwi ({menu_item})</i>")
								caption = "<b>✅ Приватный p2p токен успешно изменён.</b>"
								markup = kb_admin_menu_payments(udata, "exit")
								await state.finish()

						# Для QIWI/API
						if menu_item == "terminal" or menu_item == "nickname":
							await asyncio.sleep(0.5)
							try:
								request = requests.Session()
								request.headers["authorization"] = "Bearer " + get_data
								check_history = request.get(f"https://edge.qiwi.com/payment-history/v2/persons/{phone}/payments", params={"rows": 1, "operation": "IN"})
								check_profile = request.get(f"https://edge.qiwi.com/person-profile/v1/profile/current?authInfoEnabled=true&contractInfoEnabled=true&userInfoEnabled=true")
								check_balance = request.get(f"https://edge.qiwi.com/funding-sources/v2/persons/{phone}/accounts")
								try:
									if check_history.status_code == 200 and check_profile.status_code == 200 and check_balance.status_code == 200:
										# По комментарию
										if menu_item == "terminal":
											db.SetPaySystem("qiwi", menu_item, currency, token = get_data)
											await _system.SendNotify(f"<b>🔉 Администратор:</b> <code>{udata['firstname']}</code>\n<b>Действие:</b> 🔑 Изменил данные для: <i>Qiwi ({menu_item})</i>")
											caption = "<b>✅ Qiwi токен успешно изменён.</b>"
											markup = kb_admin_menu_payments(udata, "exit")
											await state.finish()

										# По никнейму
										if menu_item == "nickname":
											nickname = request.get(f"https://edge.qiwi.com/qw-nicknames/v1/persons/{phone}/nickname")
											check_nickname = json.loads(nickname.text).get("nickname")
											if check_nickname is None:
												caption = "<b>❌ На аккаунте отсутствует Qiwi никнейм.</b>"
												markup = kb_admin_menu_payments(udata, "cancel")
											else:
												db.SetPaySystem("qiwi", menu_item, currency, token = get_data)
												db.SetPaySystem("qiwi", menu_item, currency, nickname = check_nickname)
												await _system.SendNotify(f"<b>🔉 Администратор:</b> <code>{udata['firstname']}</code>\n<b>Действие:</b> 🔑 Изменил данные для: <i>Qiwi ({menu_item})</i>")
												caption = "<b>✅ Qiwi токен успешно изменён.</b>"
												markup = kb_admin_menu_payments(udata, "exit")
												await state.finish()
									elif check_history.status_code == 403 or check_profile.status_code == 403 or check_balance.status_code == 403:
										caption = "<b>❌ Веденные данные не прошли проверку.</b>\n<code>Ошибка: Нет прав на данный запрос (недостаточно разрешений у API токена)</code>"
										markup = kb_admin_menu_payments(udata, "cancel")
									elif check_history.status_code == 401 or check_profile.status_code == 401 or check_balance.status_code == 401:
										caption = "<b>❌ Веденные данные не прошли проверку.</b>\n<code>Ошибка: Неверный токен или истек срок действия.</code>"
										markup = kb_admin_menu_payments(udata, "cancel")
									elif check_history.status_code == 400 or check_profile.status_code == 400 or check_balance.status_code == 400:
										caption = "<b>❌ Веденные данные не прошли проверку.</b>\n<code>Ошибка: Номер телефона указан в неверном формате.</code>"
										markup = kb_admin_menu_payments(udata, "cancel")
									else:
										if check_history.status_code != 200: error = check_history.status_code
										if check_profile.status_code != 200: error = check_profile.status_code
										if check_balance.status_code != 200: error = check_balance.status_code
										caption = f"<b>❌ Веденные данные не прошли проверку.</b>\n<code>Ошибка: Код ошибки ({error}).</code>"
										markup = kb_admin_menu_payments(udata, "cancel")
								except json.decoder.JSONDecodeError:
									caption = f"<b>❌ Веденные данные не прошли проверку.</b>\n<code>Ошибка: Токен не найден.</code>"
									markup = kb_admin_menu_payments(udata, "cancel")
							except IndexError:
								caption = f"<b>❌ Веденные данные не прошли проверку.</b>\n<code>Ошибка: IndexError.</code>"
								markup = kb_admin_menu_payments(udata, "cancel")
							except UnicodeEncodeError:
								caption = f"<b>❌ Веденные данные не прошли проверку.</b>\n<code>Ошибка: Токен не найден.</code>"
								markup = kb_admin_menu_payments(udata, "cancel")


		# Сообщение
		try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
		except: pass
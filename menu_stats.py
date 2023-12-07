from datetime import datetime
from string import Template

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from _loader import dp, bot
from handlers._states import StateStats
from keyboards.inline.admin import *

import utils.sql._handlers as db
import utils._func as func


# Статистика
@dp.callback_query_handler(text_startswith="admin_menu_stats", state="*")
async def admin_menu_stats(call: CallbackQuery, state: FSMContext):
	user_id, message_id = call.message.chat.id, call.message.message_id
	udata = db.GetUsers(user_id)
	
	split = call.data.split(":")
	try: menu_switch = split[1]
	except: menu_switch = False
	try: menu_item = split[2]
	except: menu_item = False

	# Генерация
	if not menu_switch:
		await state.finish()
		stats = db.GetStats()
		caption = f"<b>📖 Статистика.</b>\n\n" \
			f"<b>Общая: {stats['s_work_time']}</b>\n" \
			f"<b>👨‍⚕️ Пользователи:</b> <code>{stats['s_all_users']}</code>\n" \
			f"<b>💳 Пополнено:</b> <code>{stats['s_all_payments']}</code>\n" \
			f"<b>🛒 Продано:</b> <code>{stats['s_all_sale']}</code>\n" \
			f"<b>💰 На сумму:</b> <code>{stats['s_all_sale_pay']}</code>\n\n" \
			f"<b>Сегодня: {stats['s_today']}</b>\n" \
			f"<b>👨‍⚕️ Пользователи:</b> <code>{stats['s_today_users']}</code>\n" \
			f"<b>💳 Пополнено:</b> <code>{stats['s_today_payments']}</code>\n" \
			f"<b>🛒 Продано:</b> <code>{stats['s_today_sale']}</code>\n" \
			f"<b>💰 На сумму:</b> <code>{stats['s_today_sale_pay']}</code>"

	# Генерация списка кошельков
	if menu_switch == "wallets":
		await state.finish()
		caption = f"<b>⚙️ Генерация отчета.</b>\n<b>🔧 Тип:</b> <code>Пользователи</code>\n\n✅ Отчет успешно создан."
		wallets, stats = db.GetUsers(wallets = True), {"balance": 0, "s_pay": 0, "s_sale": 0, "s_sale_pay": 0}
		
		# Таблица
		txt = ['<table class="table"><thead><tr>' \
			"<th>ID</th><th>Username</th><th>Firstname</th><th>Баланс</th><th>Пополнено</th><th>Покупок</th><th>На сумму</th><th>Регистрация</th>" \
			"</tr></thead><tbody>", "", "</tbody><table>",]
		
		# Сбор данных 
		if type(wallets) == dict: wallets = [wallets]
		for i in wallets:
			txt[1] = txt[1] + f"<tr><td>{i['user_id']}</td><td>{i['username']}</td><td>{i['firstname']}</td><td>{i['balance']}</td><td>{i['s_pay']}</td><td>{i['s_buy']}</td><td>{i['s_buy_pay']}</td><td>{i['reg_time']}</td></tr>"
			stats["balance"] = stats["balance"] + i["balance"]
			stats["s_pay"] = stats["s_pay"] + i["s_pay"]
			stats["s_sale"] = stats["s_sale"] + i["s_buy"]
			stats["s_sale_pay"] = stats["s_sale_pay"] + i["s_buy_pay"]
		
		# Итоговые результаты
		total = ['<div class="total">', '', '</div>']
		total[1] = total[1] + f"<p><b>Пользователей:</b> {len(wallets)}</p>"
		total[1] = total[1] + f"<p><b>На балансе:</b> {stats['balance']} KZT</p>"
		total[1] = total[1] + f"<p><b>Пополнено:</b> {stats['s_pay']} KZT</p>"
		total[1] = total[1] + f"<p><b>Куплено:</b> {stats['s_sale']}</p>"
		total[1] = total[1] + f"<p><b>На сумму:</b> {stats['s_sale_pay']} KZT</p>"

		# Сохранение в файл
		txt, total = txt[0] + txt[1] + txt[2], total[0] + total[1] + total[2]
		func.StatsHTML(total + txt)

		# Отправка
		await bot.send_document(user_id, document = open("data/SX9.stats.html", "rb"), caption = f"<b>⚙️ Тип:</b> <i>Выгрузка пользователей</i>\n<b>⏱ Метка:</b> <code>{func.timestamp()}</code>")

	# Генерация списка пополнений/продаж
	if menu_switch == "n-num":
		await state.finish()
		caption = f"<b>⚙️ Генерация отчета.</b>\n"
		if menu_item == "pay":
			caption = caption + f"<b>🔧 Тип:</b> <code>Пополнения</code>\n\n"
		if menu_item == "buy":
			caption = caption + f"<b>🔧 Тип:</b> <code>Продажи</code>\n\n"
		caption = caption + f"⚠️ Введите «all», чтобы получить всю информацию.\n"
		caption = caption + f"Предполагаемое количество:"
		await StateStats.data.set()
		await state.update_data(stats_type=menu_item)

	# Генерация
	if menu_switch == "generate":
		state_data = await state.get_data()
		stats_type = state_data.get("stats_type", False)
		count = state_data.get("count", False)
		if stats_type and count:
			if stats_type == "pay": stats_name = "Пополнения"
			if stats_type == "buy": stats_name = "Продажи"
			caption = f"<b>⚙️ Генерация отчета.</b>\n<b>🔧 Тип:</b> <code>{stats_name}</code>\n\n"
			trans, stop_count = db.GetTransaction(stats_type, multiple = True), count
			
			if not trans:
				caption = caption + f"❌ Нет данных для генерации"
			else:
				# Таблица
				if stats_type == "pay":
					stats = {"p_count": 0, "p_success": 0, "p_rub_success": 0, "p_kzt_success": 0, "p_sum_success": 0, "p_error": 0, "p_rub_error": 0, "p_kzt_error": 0, "p_sum_error": 0}
					txt = ['<table class="table"><thead><tr>' \
						"<th>ID</th><th>Пользователь</th><th>Сумма</th><th>Система</th><th>Код</th><th>Время</th><th>Статус</th><th>До</th><th>После</th>" \
						"</tr></thead><tbody>", "", "</tbody><table>",]
				if stats_type == "buy":
					stats = {"b_sale": 0, "b_sale_pay": 0}
					txt = ['<table class="table"><thead><tr>' \
						"<th>ID</th><th>Пользователь</th><th>Сумма</th><th>Товар</th><th>Позиция</th><th>Оплачено</th><th>[Баланс] До</th><th>[Баланс] После</th><th>Добавил</th><th>Добавлено</th>" \
						"</tr></thead><tbody>", "", "</tbody><table>",]

				# Сбор данных
				if type(trans) == dict: trans = [trans]
				trans.reverse()
				for i in trans:
					if stop_count == 0: break
					if stop_count != "all": stop_count = stop_count - 1
					if stats_type == "pay":
						txt[1] = txt[1] + f"<tr><td>{i['pay_id']}</td><td>{i['user_id']}</td><td>{i['amount']} {i['currency'].upper()}</td><td>{i['pay_system']}</td><td>{i['receipt']}</td><td>{i['pay_time']}</td><td>{i['pay_status']}</td><td>{i['before']}</td><td>{i['after']}</td></tr>"
						stats["p_count"] = stats["p_count"] + 1
						if i["pay_status"] == "PAID" or i["pay_status"] == "SUPPORT" or i["pay_status"] == "SUCCESS":
							stats["p_success"] = stats["p_success"] + 1
							if i["currency"] == "rub":
								stats["p_rub_success"] = stats["p_rub_success"] + i["amount"]
							if i["currency"] == "kzt":
								stats["p_kzt_success"] = stats["p_kzt_success"] + i["amount"]
						else:
							stats["p_error"] = stats["p_error"] + 1
							if i["currency"] == "rub":
								stats["p_rub_error"] = stats["p_rub_error"] + i["amount"]
							if i["currency"] == "kzt":
								stats["p_kzt_error"] = stats["p_kzt_error"] + i["amount"]
					if stats_type == "buy":
						txt[1] = txt[1] + f"<tr><td>{i['buy_id']}</td><td>{i['user_id']}</td><td>{i['price']} KZT</td><td>{i['content']}</td><td>{i['position_name']}</td><td>{i['buy_time']}</td><td>{i['before']}</td><td>{i['after']}</td><td>{i['creator_id']}</td><td>{i['creator_time']}</td></tr>"
						stats["b_sale"] = stats["b_sale"] + 1
						stats["b_sale_pay"] = stats["b_sale_pay"] + i["price"]

				# Итоговые результаты
				total = ['<div class="total">', '', '</div>']
				if stats_type == "pay":
					stats["p_sum_success"] = stats["p_kzt_success"] + func.CurrConvert("RUB:KZT", stats["p_rub_success"])
					stats["p_sum_error"] = stats["p_kzt_error"] + func.CurrConvert("RUB:KZT", stats["p_rub_error"])
					total[1] = total[1] + f"<p><b>Пополнений:</b> {stats['p_count']}</p><br>"
					total[1] = total[1] + f"<p><b>Удачных:</b> {stats['p_success']}</p>"
					total[1] = total[1] + f"<p><b>На сумму:</b> {stats['p_kzt_success']} KZT + {stats['p_rub_success']} RUB ~ {stats['p_sum_success']} KZT</p>"
					total[1] = total[1] + f"<p><b>Неудачных:</b> {stats['p_error']}</p>"
					total[1] = total[1] + f"<p><b>На сумму:</b> {stats['p_kzt_error']} KZT + {stats['p_rub_error']} RUB ~ {stats['p_sum_error']} KZT</p>"
				if stats_type == "buy":
					total[1] = total[1] + f"<p><b>Продано:</b> {stats['b_sale']}</p>"
					total[1] = total[1] + f"<p><b>На сумму:</b> {stats['b_sale_pay']} KZT</p>"

				# Сохранение в файл
				txt, total = txt[0] + txt[1] + txt[2], total[0] + total[1] + total[2]
				func.StatsHTML(total + txt)

				# Отправка
				await bot.send_document(user_id, document = open("data/SX9.stats.html", "rb"), caption = f"<b>⚙️ Тип:</b> <i>{stats_name}</i>\n<b>⏱ Метка:</b> <code>{func.timestamp()}</code>")
				caption = caption + f"✅ Отчет успешно создан."

	markup = kb_admin_menu_stats(menu_switch)


	# Сообщение
	try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
	except: pass


# Обработка N статистики
@dp.message_handler(content_types=["text"], state=StateStats.data)
async def admin_menu_stats_handler(message: types.Message, state: FSMContext):
	# __init__ #
	user_id, message_id = message.from_user.id, message.message_id
	udata, uclean = db.GetUsers(user_id), db.GetClean(user_id)
	await func.DeleteMSG(bot, user_id, message_id)
	message_id = uclean["home_id"]

	state_data = await state.get_data()
	stats_type = state_data.get("stats_type", False)

	get_data = func.StrToNum(message.text)
	if stats_type and get_data:
		if get_data == "all" or type(get_data) == int:
			if stats_type == "pay": stats_name = "Пополнения"
			if stats_type == "buy": stats_name = "Продажи"
			caption = f"<b>⚙️ Генерация отчета.</b>\n<b>🔧 Тип:</b> <code>{stats_name}</code>\n\nКоличество для генерации: <code>{get_data}</code>"
			markup = kb_admin_menu_stats("step")
			await state.update_data(count=get_data)


		# Сообщение
		try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
		except: pass
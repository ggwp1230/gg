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

# Магазин
@dp.callback_query_handler(text_startswith="menu_shop", state="*")
async def menu_shop(call: CallbackQuery, state: FSMContext):
	user_id, message_id = call.message.chat.id, call.message.message_id
	udata, uclean, settings = db.GetUsers(user_id), db.GetClean(user_id), db.GetSettings()
	
	await state.finish()

	if settings['engineering_mode'] and not func.GetRole(user_id)["id"]: return await _system.engineering_work(user_id, message_id)

	split = call.data.split(":")

	# Отступ
	try: offset = int(split[1])
	except: offset = 0

	### Тип генерации ###
	try: catalog_type = split[2]
	except: catalog_type = "category"

	if catalog_type == "s_and_p":
		category_id = int(split[3])

	if catalog_type == "subcategory":
		category_id = int(split[3])
		try: subcategory_id = int(split[4])
		except: subcategory_id = False
		try: sscategory_id = int(split[5])
		except: sscategory_id = False

	if catalog_type == "position":
		category_id = int(split[3])
		try: position_id = int(split[4])
		except: position_id = False
		try: subcategory_id = int(split[5])
		except: subcategory_id = False


	### Генерация ###
	caption = f'<b>🏪 Актуальный каталог магазина.</b>\n\n' \
			f'<b>🧑‍💼 Покупатель:</b> <a href="@{udata["username"]}">{udata["firstname"]}</a>\n' \
			f'<b>💰 Баланс:</b> <i>{udata["balance"]} KZT</i>\n\n' # Валюта
	
	# Список категорий
	if catalog_type == "category":
		markup = kb_menu_shop(offset, catalog_type)

	# Список подкатегорий и позиций в категории
	if catalog_type == "s_and_p":
		data = db.GetCategory(category_id)
		caption = caption + f'<b>📦 Категория:</b> <code>{data["category_name"]}</code>'
		markup = kb_menu_shop(offset, catalog_type, category_id)

	# Подкатегория
	if catalog_type == "subcategory":
		data = db.GetCategory(category_id)
		caption = caption + f'<b>📦 Категория:</b> <code>{data["category_name"]}</code>\n'
		
		if sscategory_id:
			data = db.GetSubCategory(category_id, sscategory_id)
			caption = caption + f'<b>📁 Подкатегория:</b> <code>{data["subcategory_name"]}</code>\n'

		if subcategory_id:
			data = db.GetSubCategory(category_id, subcategory_id)
			caption = caption + f'<b>📂 Подкатегория:</b> <code>{data["subcategory_name"]}</code>\n'
		
		markup = kb_menu_shop(offset, catalog_type, category_id, subcategory_id = subcategory_id)
	
	# Позиция
	if catalog_type == "position":
		data = db.GetCategory(category_id)
		caption = caption + f'<b>📦 Категория:</b> <code>{data["category_name"]}</code>\n'
		not_balance = False

		if subcategory_id:
			data = db.GetSubCategory(category_id, subcategory_id)
			caption = caption + f'<b>📁 Подкатегория:</b> <code>{data["subcategory_name"]}</code>\n'

		data = db.GetPosition(position_id)
		caption = caption + f'<b>📋 Позиция:</b> <code>{data["position_name"]}</code>\n'
		caption = caption + f'<b>💰 Цена:</b> <i>{data["position_price"]} KZT</i>\n'	# Валюта
		if db.GetProduct(position_id = position_id):
			if udata['balance'] < data["position_price"]: 
				caption = caption + f"<b>⚠️ На вашем балансе недостаточно средств.</b>"
				not_balance = True
		else:
			caption = caption + f"<b>⚠️ Нет в наличии.</b>"

		markup = kb_menu_shop(offset, catalog_type, category_id, position_id, subcategory_id, not_balance)


	# Сообщение
	if uclean['location'] != "menu_shop":
		await func.DeleteMSG(bot, user_id, [message_id, uclean["sticker_id"], uclean["home_id"]])
		try: r_sticker = await call.message.answer_sticker(settings["sticker_shop"])
		except: r_sticker = False
		if r_sticker: db.SetClean(user_id, "sticker_id", r_sticker.message_id)
		r_message = await bot.send_message(user_id, caption, reply_markup=markup)
		db.SetClean(user_id, "home_id", r_message.message_id)
		db.SetClean(user_id, "location", "menu_shop")
	else:
		try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
		except: pass


# Обработка покупки
@dp.callback_query_handler(text_startswith="call_menu_shop", state="*")
async def callback_a_menu_category(call: CallbackQuery, state: FSMContext):
	user_id, message_id = call.message.chat.id, call.message.message_id
	udata, settings = db.GetUsers(user_id), db.GetSettings()

	if settings['engineering_mode'] and not func.GetRole(user_id)["id"]: return await _system.engineering_work(user_id, message_id)

	state_data = await state.get_data()

	# Тип действия
	split = call.data.split(":")
	action_type = split[1]

	# Обработка
	if action_type == "buy":
		position_id = int(split[2])
		position, products = db.GetPosition(position_id), db.GetProduct(position_id = position_id)
		back_data = split[3]
# Валюта
		caption = f"<b>🛒 Оформление покупки товара:</b> <code>{position['position_name']}</code>\n" \
				f"<b>💰 Цена:</b> <i>{position['position_price']} KZT</i>\n" \
				f"<b>📦 Наличие:</b> "
		if type(products) == dict: products = [products]
		if products: caption = caption + "<code>есть</code>"
		else: caption = caption + "<code>нету</code>"
		if products and udata["balance"] >= position["position_price"]:
			buy_cost = udata["balance"] - position["position_price"]
			buy_cost = func.toFixed(buy_cost, 2)
		caption = caption + f'\n\n<b>🧑‍💼 Покупатель:</b> <a href="tg://user?id={udata["user_id"]}">{udata["firstname"]}</a>\n' \
							f'<b>💰 Баланс:</b> <i>{buy_cost} KZT</i>\n\n' # Валюта
		caption = caption + "<b>📍 Статус:</b> "
		if not products:
			caption = caption + "<code>Нет в наличии</code>"
			markup = kb_menu_shop_handler("back", back_data)
		else:
			if udata["balance"] < position["position_price"]:
				caption = caption + "<code>Недостаточно средств</code>"
				markup = kb_menu_shop_handler("not_balance", back_data)
			else:
				# Покупка
				buy_item = products[random.randint(0, len(products)-1)]
				db.UpdateUsers(user_id, "balance", float(buy_cost))
				db.UpdateUsers(user_id, "s_buy", udata["s_buy"] + 1)
				db.UpdateUsers(user_id, "s_buy_pay", udata["s_buy_pay"] + position["position_price"])
				db.SetStats("sale")
				db.SetStats("sale_pay", position["position_price"])
				buy = db.AddTransaction("buy", (buy_item["product_id"], user_id, udata["balance"], float(buy_cost)))

				caption = caption + "<code>Успешно</code>\n"
				caption = caption + f"<b>⭕️ Списано:</b> <i>{position['position_price']} KZT</i>\n\n" \
									f"<b>ℹ️ Все купленные товары всегда доступны в личном кабинете.</b>"
				markup = kb_menu_shop_handler("buy", back_data, buy["buy_id"])

	# Открыть купленный товар
	if action_type == "open":
		buy_id = int(split[2])
		data = db.GetTransaction("buy", buy_id)

		caption = f"<b>📖 Транзакция:</b> <code>#{data['buy_id']}</code>\n" \
				f"<b>⏱ Время покупки:</b> <i>{data['buy_time']}</i>\n" \
				f"<b>📋 Позиция:</b> <i>{data['position_name']}</i>\n" \
				f"<b>💰 Цена:</b> <i>{data['price']} KZT</i>\n\n" \
				f"<b>📍 Товар:</b> {data['content']}"
		markup = kb_menu_shop_handler("back")


	# Сообщение
	try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
	except: pass
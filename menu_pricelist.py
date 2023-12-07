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
@dp.callback_query_handler(text_startswith="menu_pricelist", state="*")
async def menu_pricelist(call: CallbackQuery, state: FSMContext):
	user_id, message_id = call.message.chat.id, call.message.message_id
	udata, uclean, settings = db.GetUsers(user_id), db.GetClean(user_id), db.GetSettings()
	
	if settings['engineering_mode'] and not func.GetRole(user_id)["id"]: return await _system.engineering_work(user_id, message_id)

	# Сбор данных
	category, subcategory, position, products = {}, {}, {}, {}
	for i in db.GetCategory(multiple = True): category[i["category_id"]] = i
	for i in db.GetSubCategory(multiple = True): subcategory[i["subcategory_id"]] = i
	for i in db.GetPosition(multiple = True):
		position[i["position_id"]] = i
		position[i["position_id"]]["products"] = []
	for i in db.GetProduct(multiple = True):
		try: position[i["position_id"]]["products"].append(i)
		except: pass

	# Генерация
	caption = "<b>🗒 Актуальный прайс-лист.</b>\n\n"
	data = {}
	for i in position:
		i = position[i]
		if i["products"]:
			id_c, id_s = i["category_id"], i["subcategory_id"]
			name_c = category[id_c]["category_name"]
			if not name_c in data.keys(): data[name_c] = {}
			if id_s:
				name_s, id_stop, c_stop = subcategory[id_s]["subcategory_name"], subcategory[id_s]["sscategory_id"], 3
				while id_stop:
					if not c_stop: break
					name_s, id_stop, c_stop = subcategory[id_stop]["subcategory_name"] + " » " + name_s, subcategory[id_stop]["sscategory_id"], c_stop - 1
				if not name_s in data[name_c].keys(): data[name_c][name_s] = []
			if not "items" in data[name_c]: data[name_c]["items"] = []
			item = f"<b>📗</b> <code>{i['position_name']}</code> | <code>{i['position_price']} KZT</code>\n" # Валюта
			if id_s: data[name_c][name_s].append(item)
			else: data[name_c]["items"].append(item)

	if data:
		for i in data:
			caption = caption + f"<b>📌 {i}</b>\n"
			for item in data[i]["items"]: caption = f"{caption}{item}"
			for sub in data[i]:
				if sub != "items":
					caption = f"{caption}\n🗄 {sub}\n"
					for item in data[i][sub]: caption = caption + item
			caption = f"{caption}\n🔸🔹🔸🔹🔸🔹🔸🔹🔸\n\n"
		caption = caption[:-11]
	else: caption = caption + "🤷‍♂️ К сожалению, товара нет в наличии."
	markup = kb_menu_pricelist()


	# Сообщение
	if uclean['location'] != "menu_pricelist":
		await func.DeleteMSG(bot, user_id, [message_id, uclean["sticker_id"], uclean["home_id"]])
		try: r_sticker = await call.message.answer_sticker(settings["sticker_pricelist"])
		except: r_sticker = False
		if r_sticker: db.SetClean(user_id, "sticker_id", r_sticker.message_id)
		r_message = await bot.send_message(user_id, caption, reply_markup=markup)
		db.SetClean(user_id, "home_id", r_message.message_id)
		db.SetClean(user_id, "location", "menu_pricelist")
	else:
		try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
		except: pass
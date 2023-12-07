from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext

from _loader import dp, bot
from handlers._filters import IsWork, IsUser
from handlers.users._index import *
from keyboards.inline._system import *

import utils.sql._handlers as db
import utils._func as func


ework_caption = "<b>🚧 Мы ушли на технические работы.\n⏱ Пожалуйста, подождите...</b>"
sign_caption = "<b>🚫 Серверная ошибка.</b>\n⚠️ Похоже ваш профиль отсутствует в нашей системе.\n\nℹ️ Воспользуйтесь кнопкой перезагрузки или командой: /start"

# Технические работы
@dp.message_handler(IsWork())
async def engineering_work_message(message: types.Message):
	user_id, message_id = message.from_user.id, message.message_id
	await bot.delete_message(user_id, message_id)
	await bot.send_message(user_id, ework_caption, reply_markup=kb_btn_restart)

async def engineering_work(user_id, message_id):
	settings = db.GetSettings()
	trigger = False
	if settings['engineering_mode']:
		if func.GetRole(user_id)["id"] > 0: trigger = False
		else: trigger = True
	if trigger:
		try: await bot.delete_message(user_id, message_id)
		except: pass
		await bot.send_message(user_id, ework_caption, reply_markup=kb_btn_restart)


# Проверка регистрации
@dp.message_handler(IsUser())
async def users_check_message(message:types.Message):
	user_id, message_id = message.from_user.id, message.message_id
	await bot.delete_message(user_id, message_id)
	await bot.send_message(user_id, sign_caption, reply_markup=kb_btn_restart)

@dp.callback_query_handler(IsUser())
async def users_check_callback(call: CallbackQuery):
	user_id, message_id = call.message.chat.id, call.message.message_id
	await bot.delete_message(user_id, message_id)
	await bot.send_message(user_id, sign_caption, reply_markup=kb_btn_restart)


# Система уведомлений
async def SendNotify(text = False, n_type = False):
	if text:
		sender_users, sender_id = db.GetUsers(role = True), []
		if type(sender_users) == dict: sender_users = [sender_users]
		if sender_users:
			for i in sender_users:
				if i["role_notify"]: sender_id.append(i["user_id"])
				if n_type == "appeal":
					if i["role_notify_appeal"] and not i["user_id"] in sender_id: sender_id.append(i["user_id"])
				if n_type == "support":
					if i["role_notify_support"]  and not i["user_id"] in sender_id: sender_id.append(i["user_id"])
			for i in sender_id: await bot.send_message(i, text, reply_markup=kb_btn_notify)

# Скрыть уведомление
@dp.callback_query_handler(text="notify_hide", state="*")
async def HideNotify(call: CallbackQuery, state: FSMContext):
	user_id, message_id = call.message.chat.id, call.message.message_id
	await func.DeleteMSG(bot, user_id, message_id)
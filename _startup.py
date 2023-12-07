# -*- coding: utf-8 -*-
from aiogram import types


# Команды
async def set_default_commands(dp):
	await dp.bot.set_my_commands([
		types.BotCommand("start", "Запустить бота 🔥")
	])
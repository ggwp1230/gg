# -*- coding: utf-8 -*-
import asyncio


async def on_startup(dp):
	from utils._startup import set_default_commands
	await set_default_commands(dp)

if __name__ == "__main__":
	from aiogram import executor
	from handlers import dp
	from utils.sql._sql import SQL
	import utils.sql._handlers as HandlersSQL

	db = SQL()
	db.check_table()
	db.debug()
	HandlersSQL.CheckSettings()
	HandlersSQL.CheckPaySystem()
	HandlersSQL.CheckStats()

	executor.start_polling(dp, on_startup=on_startup)
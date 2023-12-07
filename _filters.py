from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from _loader import bot
import utils.sql._handlers as db
import utils._func as func


class IsAdmin(BoundFilter):
	async def check(self, message: types.Message):
		if func.GetRole(message.from_user.id)["id"] > 0: return True
		return False


class IsWork(BoundFilter):
	async def check(self, message: types.Message):
		settings = db.GetSettings()
		if settings["engineering_mode"]:
			if func.GetRole(message.from_user.id)["id"] > 0:
				return False
			return True
		return False


class IsUser(BoundFilter):
	async def check(self, message: types.Message):
		if db.GetUsers(message.from_user.id): return False
		return True
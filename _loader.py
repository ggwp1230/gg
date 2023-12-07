# -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import utils._cfg as cfg

bot = Bot(token=cfg.get("bot_token"), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import utils._func as func


# Кнопка перезагрузки (Функция обновления)
kb_btn_restart = InlineKeyboardMarkup()
kb_btn_restart.row(InlineKeyboardButton("🔄 Перезагрузить", callback_data="menu_home"))


# Кнопка (Возврат в главное меню)
kb_btn_home = InlineKeyboardMarkup()
kb_btn_home.row(InlineKeyboardButton("🏠 Главное меню", callback_data="menu_home"))


# Скрыть уведомление
kb_btn_notify = InlineKeyboardMarkup()
kb_btn_notify.row(InlineKeyboardButton("💢 Прочитано", callback_data="notify_hide"))
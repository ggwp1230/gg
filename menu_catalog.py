from datetime import datetime
from string import Template

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from _loader import dp, bot
from handlers._states import StateCatalog
from keyboards.inline.admin import *

import utils.sql._handlers as db
import utils._func as func


# Create/Edit данные (Создал/Редактировал)
def CE_Data(creator_id, creator_time, editor_id = False, editor_time = False):
	creator_data = db.GetUsers(creator_id)
	caption = f'<b>♻️ Создал:</b> <i>{creator_data["firstname"]}</i>\n'
	caption = caption + f'<b>⏱ Время:</b> <i>{creator_time}</i>\n'
	if editor_id:
		if editor_id == creator_id: editor_data = creator_data
		else: editor_data = db.GetUsers(editor_id)
		caption = caption + f'<b>✏️ Редактировал:</b> <i>{editor_data["firstname"]}</i>\n'
		caption = caption + f'<b>⏱ Время:</b> <i>{editor_time}</i>\n'
	return caption


# Category/SubCategory данные
def CS_Data(category_id, subcategory_id = False):
	category_data = db.GetCategory(category_id)
	sscategory_id = 0
	caption = f'<b>📦 Категория:</b> <i>{category_data["category_name"]}</i>\n'
	if subcategory_id:
		subcategory_data = db.GetSubCategory(category_id, subcategory_id)
		sscategory_id = subcategory_data["sscategory_id"]
		caption = caption + f'<b>📁 Подкатегория:</b> <i>{subcategory_data["subcategory_name"]}</i>\n'
	return [caption, sscategory_id] # Сообщение + Главная подкатегория


# Каталог категорий / подкатегорий & позиций && Кнопки действий с ними
@dp.callback_query_handler(text_startswith="admin_menu_catalog", state="*")
async def admin_menu_catalog(call: CallbackQuery, state: FSMContext):
	user_id, message_id = call.message.chat.id, call.message.message_id
	urole = func.GetRole(user_id)
	
	await state.finish()

	split = call.data.split(":")

	# Отступ
	try: offset = int(split[1])
	except: offset = 0

	# Тип генерации
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

	if catalog_type == "product":
		product_id = int(split[3])

	# Генерация
	if urole["id"] > 0:
		# Список категорий
		if catalog_type == "category":
			caption = f"<b>🗄 Управление категориями.</b>\n\nВыберите категорию или действие:"
			markup = kb_admin_menu_catalog(offset, catalog_type)

		# Список подкатегорий и позиций в категории
		if catalog_type == "s_and_p":
			data = db.GetCategory(category_id)
			caption = f"<b>🗄 Управление подкатегориями и позициями.</b>\n\n"

			# Описание категории
			caption = caption + f'<b>📦 Категория:</b> <code>{data["category_name"]}</code>\n'
			caption = caption + CE_Data(data["creator_id"], data["creator_time"], data["editor_id"], data["editor_time"])

			caption = caption + '\nВыберите подкатегорию/позицию или действие:'
			markup = kb_admin_menu_catalog(offset, catalog_type, category_id)

		# Подкатегория
		if catalog_type == "subcategory":
			data = db.GetCategory(category_id)
			caption = f"<b>🗄 Управление подкатегориями и позициями.</b>\n\n"
			
			# Описание категории
			caption = caption + f'<b>📦 Категория:</b> <code>{data["category_name"]}</code>\n'
			caption = caption + CE_Data(data["creator_id"], data["creator_time"], data["editor_id"], data["editor_time"])

			# Описание главной подкатегории
			if sscategory_id:
				data = db.GetSubCategory(category_id, sscategory_id)
				caption = caption + f'\n<b>📂 Главная подкатегория:</b> <code>{data["subcategory_name"]}</code>\n'
				caption = caption + CE_Data(data["creator_id"], data["creator_time"], data["editor_id"], data["editor_time"])

			# Описание подкатегории
			if subcategory_id:
				data = db.GetSubCategory(category_id, subcategory_id)
				caption = caption + f'\n<b>📁 Подкатегория:</b> <code>{data["subcategory_name"]}</code>\n'
				caption = caption + CE_Data(data["creator_id"], data["creator_time"], data["editor_id"], data["editor_time"])
			
			caption = caption + '\nВыберите подкатегорию/позицию или действие:'
			markup = kb_admin_menu_catalog(offset, catalog_type, category_id, subcategory_id)
		
		# Позиция
		if catalog_type == "position":
			data = db.GetCategory(category_id)
			caption = f"<b>🗄 Управление позицией.</b>\n\n"

			# Описание категории
			caption = caption + f'<b>📦 Категория:</b> <code>{data["category_name"]}</code>\n'
			caption = caption + CE_Data(data["creator_id"], data["creator_time"], data["editor_id"], data["editor_time"])

			# Описание подкатегории
			if subcategory_id:
				data = db.GetSubCategory(category_id, subcategory_id)
				caption = caption + f'\n<b>📁 Подкатегория:</b> <code>{data["subcategory_name"]}</code>\n'
				caption = caption + CE_Data(data["creator_id"], data["creator_time"], data["editor_id"], data["editor_time"])

			# Описание позиции
			if position_id:
				data = db.GetPosition(position_id)
				caption = caption + f'\n<b>📋 Позиция:</b> <code>{data["position_name"]}</code>\n'
				caption = caption + f'<b>💰 Цена:</b> <i>{data["position_price"]} KZT</i>\n'	# Валюта
				caption = caption + CE_Data(data["creator_id"], data["creator_time"], data["editor_id"], data["editor_time"])

			caption = caption + '\nВыберите действие:'
			markup = kb_admin_menu_catalog(offset, catalog_type, category_id, position_id, subcategory_id)
		
		# Товар
		if catalog_type == "product":
			data = db.GetProduct(product_id)
			caption = f'<b>📝 Товар:</b> <code>#{data["product_id"]}</code>\n<b>✏️ Содержимое:</b> <i>{data["product_content"]}</i>\n\n'

			category_id = data["category_id"]
			subcategory_id = data["subcategory_id"]

			# Описание категории
			data = db.GetCategory(category_id)
			caption = caption + f'<b>📦 Категория:</b> <code>{data["category_name"]}</code>\n'
			caption = caption + CE_Data(data["creator_id"], data["creator_time"], data["editor_id"], data["editor_time"])

			# Описание подкатегории
			if subcategory_id:
				data = db.GetSubCategory(category_id, subcategory_id)
				caption = caption + f'\n<b>📁 Подкатегория:</b> <code>{data["subcategory_name"]}</code>\n'
				caption = caption + CE_Data(data["creator_id"], data["creator_time"], data["editor_id"], data["editor_time"])

			caption = caption + '\nВыберите действие:'
			markup = kb_admin_menu_product(product_id)

		# Сообщение
		try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
		except: pass


# Управление каталогом
@dp.callback_query_handler(text_startswith="call_a_menu_catalog", state="*")
async def callback_a_menu_category(call: CallbackQuery, state: FSMContext):
	user_id, message_id = call.message.chat.id, call.message.message_id
	split = call.data.split(":")
	state_data = await state.get_data()

	# Тип действия
	catalog_type = split[1]
	action_type = split[2]

	if catalog_type and action_type:
		# Создать (Начало)
		if action_type == "create":
			# Категория
			if catalog_type == "category":
				caption = f"<b>📦 Создание категории.</b>\n\nВведите название:"
				markup = kb_admin_menu_catalog_handler("back", "category")
				
				await StateCatalog.data.set()
				await state.update_data(catalog_type="category")
			
			# Подкатегория
			if catalog_type == "subcategory":
				category_id = int(split[3])
				try: subcategory_id = int(split[4])
				except: subcategory_id = 0
				cs_data = CS_Data(category_id, subcategory_id)
				sscategory_id = cs_data[1]
				
				caption = f"<b>📁 Создание подкатегории.</b>\n\n{cs_data[0]}\nВведите название:"
				markup = kb_admin_menu_catalog_handler("back", "subcategory", category_id, subcategory_id, sscategory_id)

				await StateCatalog.data.set()
				await state.update_data(catalog_type="subcategory")
				await state.update_data(category_id=category_id)
				await state.update_data(subcategory_id=subcategory_id)
				await state.update_data(sscategory_id=sscategory_id)

			# Позиция
			if catalog_type == "position":
				category_id = int(split[3])
				try: subcategory_id = int(split[4])
				except: subcategory_id = 0
				cs_data = CS_Data(category_id, subcategory_id)
				sscategory_id = cs_data[1]
				
				caption = f"<b>📋 Создание позиции.</b>\n\n{cs_data[0]}\nВведите название:"
				markup = kb_admin_menu_catalog_handler("back", "position", category_id, subcategory_id, sscategory_id)

				await StateCatalog.data.set()
				await state.update_data(catalog_type="position")
				await state.update_data(category_id=category_id)
				await state.update_data(subcategory_id=subcategory_id)
				await state.update_data(sscategory_id=sscategory_id)
				await state.update_data(step_id="name")

			# Товар
			if catalog_type == "product":
				position_id = int(split[3])
				data = db.GetPosition(position_id)
				
				caption = f"<b>📝 Добавление товара: </b> <code>{data['position_name']}</code>\n\n<b>⚙️ Сценарий:</b> <i>1 ✉️ - 1 товар.</i>\n\nНапишите содержимое товара:"
				markup = kb_admin_menu_catalog_handler("back", "product", data["category_id"], data["subcategory_id"], position_id = position_id)
				
				await StateCatalog.data.set()
				await state.update_data(catalog_type="product")
				await state.update_data(position_id=position_id)
		
			await state.update_data(action_type="create")

		# Шаг (Далее)
		if action_type == "step":
			call_type = state_data.get("action_type", False)
			# Позиция
			if catalog_type == "position":
				# Создать
				if call_type == "create":
					category_id = state_data.get("category_id", False)
					subcategory_id = state_data.get("subcategory_id", False)
					position_name = state_data.get("position_name", False)
					cs_data = CS_Data(category_id, subcategory_id)
					try: s_data = db.GetSubCategory(subcategory_id = subcategory_id)["sscategory_id"]
					except: s_data = 0

					caption = f"<b>📋 Создание позиции.</b>\n\n{cs_data[0]}\nНазвание: {position_name}\nВведите цену:"
					markup = kb_admin_menu_catalog_handler("back", "position", category_id, subcategory_id, s_data)
					await state.update_data(step_id="price")

				if call_type == "edit":
					position_id = state_data.get("position_id", False)
					category_id = state_data.get("category_id", False)
					subcategory_id = state_data.get("subcategory_id", False)
					sscategory_id = state_data.get("sscategory_id", False)
					position_name = state_data.get("position_name", False)
					data = db.GetPosition(position_id)

					caption = f"<b>✏️ Редактирование позиции.</b>\n\nНазвание: {data['position_name']}\nЦена: {data['position_price']} KZT\n\nНовое название: {position_name}\nНовая цена:"
					markup = kb_admin_menu_catalog_handler("back", "position", category_id, subcategory_id, sscategory_id, position_id) # Валюта
					await state.update_data(step_id="price")

		# Очистить
		if action_type == "clean":
			# Товар
			if catalog_type == "product":
				position_id = state_data.get("position_id", False)
				product_list = state_data.get("product_list", [])
				
				clean_type = split[3]
				data = db.GetPosition(position_id)
					
				caption = f"<b>📝 Добавление товара:</b> <code>{data['position_name']}</code>\n\n<b>⚙️ Сценарий:</b> <i>1 ✉️ - 1 товар.</i>\n\nДобавить:\n\n"
				markup = kb_admin_menu_catalog_handler("clean", "product", data["category_id"], data["subcategory_id"], position_id)

				if len(product_list) > 0:
					if clean_type == "last": product_list.pop(-1) # Последний
					if clean_type == "all": product_list = [] # Все
					await state.update_data(product_list=product_list)
				else:
					markup = kb_admin_menu_catalog_handler("back", "product", data["category_id"], data["subcategory_id"], position_id = position_id)

				if product_list:
					for i in range(len(product_list)):
						caption = caption + f"<b>[#{i}]:</b> {product_list[i]}\n"

		# Сохранить
		if action_type == "save":
			call_type = state_data.get("action_type", False)
			# Категория
			if catalog_type == "category":
				category_name = state_data.get("category_name", False)
			
				# Создать
				if call_type == "create":
					db.AddCategory(category_name, user_id)
					caption = "✅ Новая категория успешно создана."
					markup = kb_admin_menu_catalog_handler("back", "category")

				# Редактировать
				if call_type == "edit":
					category_id = state_data.get("category_id", False)
					db.EditCategory(category_id, category_name, user_id)
					caption = "✅ Категория успешно отредактирована."
					markup = kb_admin_menu_catalog_handler("back", "category", category_id)

			# Подкатегория
			if catalog_type == "subcategory":
				category_id = state_data.get("category_id", False)
				subcategory_id = state_data.get("subcategory_id", False)
				sscategory_id = state_data.get("sscategory_id", False)
				subcategory_name = state_data.get("subcategory_name", False)

				# Создать
				if call_type == "create":
					db.AddSubCategory(subcategory_name, category_id, subcategory_id, user_id)
					caption = "✅ Новая подкатегория успешно создана."
					markup = kb_admin_menu_catalog_handler("back", "subcategory", category_id, subcategory_id, sscategory_id)

				# Редактировать
				if call_type == "edit":
					db.EditSubCategory(subcategory_id, subcategory_name, user_id)
					caption = "✅ Податегория успешно отредактирована."
					markup = kb_admin_menu_catalog_handler("back", "subcategory", category_id, subcategory_id, sscategory_id)

			# Позиция
			if catalog_type == "position":
				category_id = state_data.get("category_id", False)
				subcategory_id = state_data.get("subcategory_id", False)
				sscategory_id = state_data.get("sscategory_id", False)
				position_name = state_data.get("position_name", False)
				position_price = state_data.get("position_price", False)

				# Создать
				if call_type == "create":
					db.AddPosition(position_name, position_price, category_id, subcategory_id, user_id)
					caption = "✅ Новая позиция успешно создана."
					markup = kb_admin_menu_catalog_handler("back", "position", category_id, subcategory_id, sscategory_id)

				# Редактировать
				if call_type == "edit":
					position_id = state_data.get("position_id", False)
					db.EditPosition(position_id, position_name, position_price, user_id)
					caption = "✅ Позиция успешно отредактирована."
					markup = kb_admin_menu_catalog_handler("back", "position", category_id, subcategory_id, sscategory_id, position_id)

			# Товар
			if catalog_type == "product":
				position_id = state_data.get("position_id", False)
				product_list = state_data.get("product_list", [])

				if len(product_list) > 0:
					data = db.GetPosition(position_id)
					caption = f"<b>📝 Позиция:</b> <code>{data['position_name']}</code>\n\nСписок товаров:\n"

					for i in range(len(product_list)):
						db.AddProduct(product_list[i], position_id, data["category_id"], data["subcategory_id"], user_id)
						caption = caption + f"<b>[#{i}]:</b> {product_list[i]}\n"

					caption = caption + f"✅ Успешно загружено в кол-ве: {len(product_list)} шт."
					markup = kb_admin_menu_catalog_handler("back", "product", data["category_id"], data["subcategory_id"], position_id = position_id)
	
		# Редактировать
		if action_type == "edit":
			# Категория
			if catalog_type == "category":
				category_id = int(split[3])
				data = db.GetCategory(category_id)

				caption = f"<b>✏️ Редактирование категории.</b>\n\nНазвание: {data['category_name']}\nНовое название:"
				markup = kb_admin_menu_catalog_handler("back", "category", category_id)
				
				await StateCatalog.data.set()
				await state.update_data(catalog_type="category")
				await state.update_data(category_id=category_id)

			# Подкатегория
			if catalog_type == "subcategory":
				subcategory_id = int(split[3])
				data = db.GetSubCategory(subcategory_id = subcategory_id)

				caption = f"<b>✏️ Редактирование подкатегории.</b>\n\nНазвание: {data['subcategory_name']}\nНовое название:"
				markup = kb_admin_menu_catalog_handler("back", "subcategory", data["category_id"], data["subcategory_id"], data["sscategory_id"])

				await StateCatalog.data.set()
				await state.update_data(catalog_type="subcategory")
				await state.update_data(category_id=data["category_id"])
				await state.update_data(subcategory_id=data["subcategory_id"])
				await state.update_data(sscategory_id=data["sscategory_id"])

			# Позиция
			if catalog_type == "position":
				position_id = int(split[3])
				data = db.GetPosition(position_id)
				s_data = db.GetSubCategory(subcategory_id = data["subcategory_id"])

				caption = f"<b>✏️ Редактирование позиции.</b>\n\nНазвание: {data['position_name']}\nЦена: {data['position_price']} KZT\n\nНовое название:" # Валюта
				markup = kb_admin_menu_catalog_handler("back", "position", data["category_id"], data["subcategory_id"], s_data["sscategory_id"], position_id)

				await StateCatalog.data.set()
				await state.update_data(catalog_type="position")
				await state.update_data(position_id=data["position_id"])
				await state.update_data(category_id=data["category_id"])
				await state.update_data(subcategory_id=data["subcategory_id"])
				await state.update_data(sscategory_id=s_data["sscategory_id"])
				await state.update_data(step_id="name")

			await state.update_data(action_type="edit")

		# Удалить
		if action_type == "delete":
			try: delete_confirm = split[4]
			except: delete_confirm = False
			# Категория
			if catalog_type == "category":
				category_id = int(split[3])
				data = db.GetCategory(category_id)
				
				# Предупреждение
				if not delete_confirm:
					caption = f"<b>🗑 Удалить категорию: {data['category_name']}?</b>\n\n⚠️ Внимание! Все содержимое будет удалено."
					markup = kb_admin_menu_catalog_handler("delete", "category", category_id)
				# Подтвердить
				else:
					db.DeleteCategory(category_id)
					caption = f"<b>❌ Категория удалена.</b>"
					markup = kb_admin_menu_catalog_handler("back", "category")

			# Подкатегория
			if catalog_type == "subcategory":
				subcategory_id = int(split[3])
				data = db.GetSubCategory(subcategory_id = subcategory_id)

				# Предупреждение
				if not delete_confirm:
					caption = f"<b>🗑 Удалить подкатегорию: {data['subcategory_name']}?</b>\n\n⚠️ Внимание! Все содержимое будет удалено."
					markup = kb_admin_menu_catalog_handler("delete", "subcategory", data["category_id"], subcategory_id, data["sscategory_id"])
				# Подтвердить
				else:
					db.DeleteSubCategory(subcategory_id)
					caption = f"<b>❌ Подкатегория удалена.</b>"
					markup = kb_admin_menu_catalog_handler("back", "subcategory", data["category_id"], sscategory_id = data["sscategory_id"])

			# Позиция
			if catalog_type == "position":
				position_id = int(split[3])
				data = db.GetPosition(position_id)
				s_data = db.GetSubCategory(subcategory_id = data["subcategory_id"])

				# Предупреждение и кнопки выбора
				if not delete_confirm:
					caption = f"<b>🗑 Удалить/Очистить позицию: {data['position_name']}?</b>\n\n⚠️ Внимание! При удалении позиции, все товары будут удалены."
					markup = kb_admin_menu_catalog_handler("delete", "position", data["category_id"], data["subcategory_id"], s_data["sscategory_id"], position_id)
				# Очистить
				elif delete_confirm == "clear":
					db.DeletePosition(position_id, clear = True)
					caption = f"<b>🗑 Позиция очищена.</b>"
					markup = kb_admin_menu_catalog_handler("back", "position", data["category_id"], data["subcategory_id"], position_id = position_id)
				# Удалить
				else:
					db.DeletePosition(position_id, delete = True)
					caption = f"<b>❌ Позиция удалена.</b>"
					markup = kb_admin_menu_catalog_handler("back", "position", data["category_id"], data["subcategory_id"], s_data["sscategory_id"])

			# Товар
			if catalog_type == "product":
				product_id = int(split[3])
				data = db.GetProduct(product_id)

				db.DeleteProduct(product_id)
				caption = f"<b>❌ Товар удален.</b>"
				markup = kb_admin_menu_catalog_handler("back", "product", data["category_id"], data["subcategory_id"], position_id = data["position_id"])

		# Сообщение
		try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
		except: pass


# Обработчик управления каталогом
@dp.message_handler(state=StateCatalog.data)
async def callback_a_menu_category_handler(message: types.Message, state: FSMContext):
	# __init__ #
	user_id, message_id = message.from_user.id, message.message_id
	udata, uclean = db.GetUsers(user_id), db.GetClean(user_id)
	await func.DeleteMSG(bot, user_id, message_id)
	
	message_id = uclean["home_id"]

	state_data = await state.get_data()
	
	# Тип действия
	catalog_type = state_data.get("catalog_type", False)
	action_type = state_data.get("action_type", False)
	get_data = message.text

	if catalog_type and action_type:
		# Создать
		if action_type == "create":
			if len(get_data):
				# Категория
				if catalog_type == "category":
					caption = f"<b>📦 Создание категории.</b>\n\nНазвание: {get_data}"
					markup = kb_admin_menu_catalog_handler("save", "category")
					await state.update_data(category_name=get_data)

				# Подкатегория
				if catalog_type == "subcategory":
					category_id = state_data.get("category_id", False)
					subcategory_id = state_data.get("subcategory_id", False)
					cs_data = CS_Data(category_id, subcategory_id)

					caption = f"<b>📁 Создание подкатегории.</b>\n\n{cs_data[0]}\nНазвание: {get_data}"
					markup = kb_admin_menu_catalog_handler("save", "subcategory", category_id, subcategory_id)
					await state.update_data(subcategory_name=get_data)

				# Позиция
				if catalog_type == "position":
					category_id = state_data.get("category_id", False)
					subcategory_id = state_data.get("subcategory_id", False)
					step_id = state_data.get("step_id", False)
					cs_data = CS_Data(category_id, subcategory_id)
					
					if step_id == "name":
						caption = f"<b>📋 Создание позиции.</b>\n\n{cs_data[0]}\nНазвание: {get_data}"
						markup = kb_admin_menu_catalog_handler("step", "position", category_id, subcategory_id)
						await state.update_data(position_name=get_data)

					if step_id == "price":
						get_data = func.StrToNum(get_data)
						if type(get_data) == int or type(get_data) == float:
							if get_data > 0:
								position_name = state_data.get("position_name", False)
								caption = f"<b>📋 Создание позиции.</b>\n\n{cs_data[0]}\nНазвание: {position_name}\nЦена: {get_data} KZT" # Валюта
								markup = kb_admin_menu_catalog_handler("save", "position", category_id, subcategory_id)
								await state.update_data(position_price=get_data)

				# Товар
				if catalog_type == "product":
					position_id = state_data.get("position_id", False)
					data = db.GetPosition(position_id)

					product_list = state_data.get("product_list", [])
					
					caption = f"<b>📝 Добавление товара:</b> <code>{data['position_name']}</code>\n\n<b>⚙️ Сценарий:</b> <i>1 ✉️ - 1 товар.</i>\n\nДобавить:\n\n"
					markup = kb_admin_menu_catalog_handler("clean", "product", data["category_id"], data["subcategory_id"], position_id = position_id)

					if len(get_data) > 0:
						product_list.append(get_data)

					if product_list:
						for i in range(len(product_list)):
							caption = caption + f"<b>[#{i}]:</b> {product_list[i]}\n"

					if len(caption) > 3800:
						caption = caption + f"⚠️ Превышен лимит размера сообщения.\n💿 Сохраните результаты и повторите попытку."
					else:
						await state.update_data(product_list=product_list)

						
		# Редактировать
		if action_type == "edit":
			if len(get_data) > 0:
				# Категория
				if catalog_type == "category":
					category_id = state_data.get("category_id", False)
					data = db.GetCategory(category_id)

					caption = f"<b>✏️ Редактирование категории.</b>\n\nНазвание: {data['category_name']}\nНовое название: {get_data}"
					markup = kb_admin_menu_catalog_handler("save", "category", category_id)
					await state.update_data(category_name=get_data)

				# Подкатегория
				if catalog_type == "subcategory":
					subcategory_id = state_data.get("subcategory_id", False)
					data = db.GetSubCategory(subcategory_id = subcategory_id)

					caption = f"<b>✏️ Редактирование подкатегории.</b>\n\nНазвание: {data['subcategory_name']}\nНовое название: {get_data}"
					markup = kb_admin_menu_catalog_handler("save", "subcategory", data["category_id"], data["subcategory_id"], data["sscategory_id"])
					await state.update_data(subcategory_name=get_data)

				# Позиция
				if catalog_type == "position":
					position_id = state_data.get("position_id", False)
					category_id = state_data.get("category_id", False)
					subcategory_id = state_data.get("subcategory_id", False)
					sscategory_id = state_data.get("sscategory_id", False)
					step_id = state_data.get("step_id", False)
					data = db.GetPosition(position_id)

					if step_id == "name":
						caption = f"<b>✏️ Редактирование позиции.</b>\n\nНазвание: {data['position_name']}\nЦена: {data['position_price']} KZT\n\nНовое название: {get_data}" # Валюта
						markup = kb_admin_menu_catalog_handler("step", "position", category_id, subcategory_id, sscategory_id, position_id)
						await state.update_data(position_name=get_data)

					if step_id == "price":
						get_data = func.StrToNum(get_data)
						if type(get_data) == int or type(get_data) == float:
							if get_data > 0:
								position_name = state_data.get("position_name", False)
								caption = f"<b>✏️ Редактирование позиции.</b>\n\nНазвание: {data['position_name']}\nЦена: {data['position_price']} KZT\n\nНовое название: {position_name}\nНовая цена: {get_data} KZT" # Валюта
								markup = kb_admin_menu_catalog_handler("save", "position", category_id, subcategory_id, sscategory_id, position_id)
								await state.update_data(position_price=get_data)
		
		# Сообщение
		try: await bot.edit_message_text(caption, user_id, message_id, reply_markup=markup)
		except: pass
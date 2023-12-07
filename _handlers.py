from datetime import datetime, timedelta
from utils.sql._sql import SQL
import utils._func as func

db = SQL()

### Пользователи ###
def GetUsers(user_id = False, role = False, search = False, multiple = False, wallets = False):
	# Извлечь данные
	if user_id: query = f"`user_id` = {user_id}"
	if role: query = f"`role_id` > 0"
	if search: query = f"`user_id` LIKE '%{search}%' OR `username` LIKE '%{search}%' OR `firstname` LIKE '%{search}%'"
	if wallets: query = f"ORDER BY `balance` DESC"
	if multiple: query = "all"
	return db.select("users", "users", query)

def AddUsers(user_id = False, username = False, firstname = False):
	# Зарегистрировать
	if user_id and username and firstname:
		db.insert("users", "users", "user_id, username, firstname, reg_time", (user_id, username, firstname, func.timestamp()))
		db.insert("clean", "clean", "user_id", (user_id,))
		return db.select("users", "users", f"`user_id` = {user_id}")

def UpdateUsers(user_id = False, option = False, value = False):
	# Обновить
	if user_id and option:
		return db.update("users", "users", (option, value, f"`user_id` = {user_id}"))


### Данные о ID сообщений (Для чистоты и взаимодействия) ###
def GetClean(user_id = False):
	# Извлечь данные
	if user_id:
		return db.select("clean", "clean", f"`user_id` = {user_id}")

def SetClean(user_id = False, option = False, value = False):
	# Обновить
	if user_id and option:
		return db.update("clean", "clean", (option, value, f"`user_id` = {user_id}"))


### Настройки ###
def CheckSettings():
	if not GetSettings():
		db.insert("settings", "settings", "settings_id", ("0",))

def GetSettings():
	return db.select("settings", "settings", "`settings_id` = 0")

def SetSettings(option = False, value = False):
	if option:
		return db.update("settings", "settings", (option, value, "`settings_id` = 0"))

### Статистика
def CheckStats():
	if not GetStats():
		db.insert("stats", "stats", "stats_id", ("0",))
		db.update("stats", "stats", ("s_work_time", func.timestamp(), f"`stats_id` = 0"))
		db.update("stats", "stats", ("s_today", func.timestamp(True), f"`stats_id` = 0"))

def TodayStats(data = False):
	if data:
		if data["s_today"] != func.timestamp(True):
			stats_id = "`stats_id` = 0"
			db.update("stats", "stats", ("s_today", func.timestamp(True), stats_id))
			db.update("stats", "stats", ("s_today_users", "0", stats_id))
			db.update("stats", "stats", ("s_today_payments", "0", stats_id))
			db.update("stats", "stats", ("s_today_sale", "0", stats_id))
			db.update("stats", "stats", ("s_today_sale_pay", "0", stats_id))
			data = db.select("stats", "stats", stats_id)
		return data

def GetStats():
	data = db.select("stats", "stats", "`stats_id` = 0")
	if data:
		data = TodayStats(data)
		data["s_work_time"] = datetime.today() - datetime.strptime(data["s_work_time"],"%d.%m.%Y %X")
		data["s_work_time"] = str(data["s_work_time"].days) + " дн."
	return data

def SetStats(s_type = False, value = False):
	data = GetStats()
	data = TodayStats(data)
	stats_id = "`stats_id` = 0"
	if s_type == "users":		new = [["s_all_users", data["s_all_users"] + 1],["s_today_users", data["s_today_users"] + 1]]
	if s_type == "pay":			new = [["s_all_payments", data["s_all_payments"] + value],["s_today_payments", data["s_today_payments"] + value]]
	if s_type == "sale":		new = [["s_all_sale", data["s_all_sale"] + 1],["s_today_sale", data["s_today_sale"] + 1]]
	if s_type == "sale_pay":	new = [["s_all_sale_pay", data["s_all_sale_pay"] + value],["s_today_sale_pay", data["s_today_sale_pay"] + value]]
	db.update("stats", "stats", (new[0][0], new[0][1], stats_id))
	db.update("stats", "stats", (new[1][0], new[1][1], stats_id))

### Платежные системы ###
def CheckPaySystem():
	if not GetPaySystem():
		db.insert("settings", "payments", "uniq_id", ("0",))

def GetPaySystem():
	return db.select("settings", "payments", "`uniq_id` = 0")

def SetPaySystem(payment = False, method = False, currency = False, visible = False, token = False, phone = False, nickname = False):
	if payment == "qiwi":
		data = GetPaySystem()[f"{payment}_{currency}"]
		if visible == "0": data = data.replace(f"{method}:True", f"{method}:False")
		if visible == "1": data = data.replace(f"{method}:False", f"{method}:True")
		if token or phone:
			new = ""
			for i in data.split('|*|'):
				x = i.split(':')
				if x[0] == method:
					if token:
						x[2] = token
					if phone:
						x[3] = phone
					if nickname:
						x[4] = nickname
				if nickname: new = f"{new}|*|{x[0]}:{x[1]}:{x[2]}:{x[3]}:{x[4]}"
				else: new = f"{new}|*|{x[0]}:{x[1]}:{x[2]}:{x[3]}"
			data = new[3:]
		db.update("settings", "payments", (f"{payment}_{currency}", data, "`uniq_id` = 0"))
	return True


### Категории ###
def GetCategory(category_id = False, multiple = False):
	# Извлечь данные
	if category_id: query = f"`category_id` = {category_id}"
	if multiple: query = "all"
	return db.select("catalog", "category", query)

def AddCategory(category_name = False, creator_id = False):
	# Добавить
	if category_name and creator_id:
		return db.insert("catalog", "category", "category_name, creator_id, creator_time", (category_name, creator_id, func.timestamp()))

def EditCategory(category_id = False, category_name = False, editor_id = False):
	# Изменить (Название)
	if category_id and category_name and editor_id:
		category_id = f"`category_id` = {category_id}"
		db.update("catalog", "category", ("category_name", category_name, category_id))
		db.update("catalog", "category", ("editor_id", editor_id, category_id))
		db.update("catalog", "category", ("editor_time", func.timestamp(), category_id))
		return True

def DeleteCategory(category_id = False):
	# Удалить
	if category_id:
		category_id = f"`category_id` = {category_id}"
		db.delete("catalog", "category", category_id)
		db.delete("catalog", "subcategory", category_id)
		db.delete("catalog", "position", category_id)
		db.delete("catalog", "product", category_id)
		return True


### Подкатегории ###
def GetSubCategory(category_id = False, subcategory_id = False, sscategory_id = False, multiple = False):
	# Извлечь данные
	if subcategory_id: query = f"`subcategory_id` = {subcategory_id}"
	if category_id: query = f"`category_id` = {category_id} AND `sscategory_id` = 0"
	if category_id and multiple: query = f"`category_id` = {category_id}"
	if category_id and subcategory_id: query = f"`category_id` = {category_id} AND `subcategory_id` = {subcategory_id}"
	if category_id and sscategory_id: query = f"`category_id` = {category_id} AND `sscategory_id` = {sscategory_id}"
	if multiple: query = "all"
	return db.select("catalog", "subcategory", query)

def AddSubCategory(subcategory_name = False, category_id = False, subcategory_id = 0, creator_id = False):
	# Добавить
	if subcategory_name and category_id and creator_id:
		return db.insert("catalog", "subcategory", "subcategory_name, category_id, sscategory_id, creator_id, creator_time", (subcategory_name, category_id, subcategory_id, creator_id, func.timestamp()))

def EditSubCategory(subcategory_id = False, subcategory_name = False, editor_id = False):
	# Изменить
	if subcategory_id and subcategory_name and editor_id:
		subcategory_id = f"`subcategory_id` = {subcategory_id}"
		db.update("catalog", "subcategory", ("subcategory_name", subcategory_name, subcategory_id))
		db.update("catalog", "subcategory", ("editor_id", editor_id, subcategory_id))
		db.update("catalog", "subcategory", ("editor_time", func.timestamp(), subcategory_id))
		return True

def DeleteSubCategory(subcategory_id = False):
	# Удалить
	if subcategory_id:
		db.delete("catalog", "subcategory", f"`sscategory_id` = {subcategory_id}")
		subcategory_id = f"`subcategory_id` = {subcategory_id}"
		db.delete("catalog", "subcategory", subcategory_id)
		db.delete("catalog", "position", subcategory_id)
		db.delete("catalog", "product", subcategory_id)
		return True


### Позиции ###
def GetPosition(position_id = False, category_id = False, subcategory_id = False, multiple = False):
	# Извлечь данные
	if position_id: query = f"`position_id` = {position_id}"
	if category_id: query = f"`category_id` = {category_id} AND `subcategory_id` = 0"
	if category_id and multiple: query = f"`category_id` = {category_id}"
	if category_id and subcategory_id: query = f"`category_id` = {category_id} AND `subcategory_id` = {subcategory_id}"
	if multiple: query = "all"
	return db.select("catalog", "position", query)

def AddPosition(position_name = False, position_price = False, category_id = False, subcategory_id = 0, creator_id = False):
	# Добавить
	if position_name and category_id and creator_id:
		return db.insert("catalog", "position", "position_name, position_price, category_id, subcategory_id, creator_id, creator_time", (position_name, position_price, category_id, subcategory_id, creator_id, func.timestamp()))

def EditPosition(position_id = False, position_name = False, position_price = False, editor_id = False):
	# Изменить
	if position_id and editor_id:
		position_id = f"`position_id` = {position_id}"
		if position_name: db.update("position", ("position_name", position_name, position_id))
		if position_price: db.update("position", ("position_price", position_price, position_id))
		db.update("catalog", "position", ("editor_id", editor_id, position_id))
		db.update("catalog", "position", ("editor_time", func.timestamp(), position_id))
		return True

def DeletePosition(position_id = False, clear = False, delete = False):
	# Удалить
	if position_id:
		position_id = f"`position_id` = {position_id}"
		if clear:
			db.delete("catalog", "product", position_id)
		if delete:
			db.delete("catalog", "product", position_id)
			db.delete("catalog", "position", position_id)
		return True


### Товары ###
def GetProduct(product_id = False, position_id = False, category_id = False, multiple = False):
	# Извлечь данные
	if product_id: query = f"`product_id` = {product_id}"
	if position_id: query = f"`position_id` = {position_id}"
	if category_id and multiple: query = f"`category_id` = {category_id}"
	if multiple: query = "all"
	return db.select("catalog", "product", query)

def AddProduct(product_content = False, position_id = False, category_id = False, subcategory_id = 0, creator_id = False):
	# Добавить
	if product_content and position_id and category_id and creator_id:
		return db.insert("catalog", "product", "product_content, position_id, category_id, subcategory_id, creator_id, creator_time", (product_content, position_id, category_id, subcategory_id, creator_id, func.timestamp()))

def DeleteProduct(product_id = False):
	# Удалить
	if product_id:
		return db.delete("catalog", "product", f"`product_id` = {product_id}")	


### Рассылка ###
def GetNewsletter(newsletter_id = False, multiple = False):
	# Извлечь данные
	if newsletter_id: query = f"`newsletter_id` = {newsletter_id}"
	if multiple: query = "all"
	return db.select("newsletter", "newsletter", query)

def AddNewsletter(content_type = False, content_text = False, content_file = False, send_id = False, creator_id = False):
	# Добавить
	if content_type and send_id and creator_id:
		return db.insert("newsletter", "newsletter", "content_type, content_text, content_file, send_id, creator_id, creator_time", (content_type, content_text, content_file, str(send_id), creator_id, func.timestamp()))

def DeleteNewsletter(newsletter_id = False):
	# Удалить
	if newsletter_id:
		return db.delete("newsletter", "newsletter", f"`newsletter_id` = {newsletter_id}")


### Транзакции ###
def GetTransaction(t_type = False, t_id = False, user_id = False, multiple = False):
	# Извлечь данные
	if t_type == "buy":
		if t_id: query = f"`buy_id` = {t_id}"
		if user_id: query = f"`user_id` = {user_id}"
		if multiple: query = f"all"
		return db.select("transaction", "transactions_buy", query)
	if t_type == "pay":
		if t_id: query = f"`pay_id` = {t_id}"
		if user_id: query = f"`user_id` = {user_id}"
		if multiple: query = f"all"
		return db.select("transaction", "transactions_pay", query)

def AddTransaction(t_type = False, data = False):
	# Добавить
	if t_type == "buy":
		product = GetProduct(data[0])
		position = GetPosition(product["position_id"])
		DeleteProduct(product["product_id"])
		values = (func.timestamp(), data[1], data[2], data[3], position["position_price"], position["position_name"], product["product_content"], product["creator_id"], product["creator_time"])
		db.insert("transaction", "transactions_buy", "buy_time, user_id, before, after, price, position_name, content, creator_id, creator_time", values)
		return db.select("transaction", "transactions_buy", f"`user_id` = {data[1]} ORDER BY `buy_id` DESC LIMIT 1")
	if t_type == "pay":
		if data[1] == "qiwi":
			pay_system = data[1]+':'+data[2]
			values = (func.timestamp(), pay_system, data[0]["user_id"], data[0]["balance"], "0", data[4], data[3], data[5], data[6])
		db.insert("transaction", "transactions_pay", "pay_time, pay_system, user_id, before, after, amount, currency, receipt, pay_url", values)
		return db.select("transaction", "transactions_pay", f"`user_id` = {data[0]['user_id']} ORDER BY `pay_id` DESC LIMIT 1")

def UpdateTransaction(t_type = False, t_id = False, option = False, value = False):
	# Изменить
	if t_type == "pay" and t_id and option:
		return db.update("transaction", "transactions_pay", (option, value, f"`pay_id` = {t_id}"))


### Обратная связь ###
def GetSupport(s_type = False, user_id = False, multiple = False):
	if s_type:
		if multiple: return db.select("support", s_type, "all")
		if user_id: return db.select("support", s_type, f"`user_id` = {user_id}")

def AddSupport(s_type = False, user_id = False, message_id = False):
	if s_type and user_id and message_id:
		if not GetSupport(s_type, user_id):
			db.insert("support", s_type, "user_id", (user_id,))
		data = GetSupport(s_type, user_id)
		db.update("support", s_type, ("message_id", f"{message_id}," + data["message_id"], f"`user_id` = {user_id}"))

def UpdateSupport(s_type = False, user_id = False, option = False, value = False):
	if s_type and user_id and option:
		return db.update("support", s_type, (option, value, f"`user_id` = {user_id}"))
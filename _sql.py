import sqlite3
import utils._func as func


class SQL():
	path = {
		"settings":	'data/sql/settings.sql',
		"catalog":	'data/sql/catalog.sql',
		"users":	'data/sql/users.sql',
		"clean":	'data/sql/clean.sql',
		"stats":	'data/sql/stats.sql',
		"support":	'data/sql/support.sql',
		"newsletter":	'data/sql/newsletter.sql',
		"transaction":	'data/sql/transaction.sql'
	}
	clean_save = [100, 100]

	def __init__(self, path=path):
		self.db = {}
		for name, file in path.items():
			self.db[name] = self.connect(name, file)
		#self.connect(database_path)

	# Connect
	def connect(self, name, file):
		self.db[name] = {}
		self.db[name]["db"] = sqlite3.connect(file)
		self.db[name]["query"] = self.db[name]["db"].cursor()
		return self.db[name]
		#self.db = sqlite3.connect(self.database_path)
		#self.query = self.db.cursor()

	# Save > one
	def commit(self, name, cs=clean_save):
		#return True
		if name == "cle4an": # off
			if not cs[0]:
				self.db[name]["db"].commit()
				self.clean_save[0] = cs[1]
			else: self.clean_save[0] = cs[0] - 1
			return True
		self.db[name]["db"].commit()
		#self.db.commit()

	# Save > all
	def save(self, path=path):
		for i, x in path.items():
			self.commit(i)

	# Debug
	def debug(self, path=path):
		for i, x in path.items():
			for table in self.db[i]["query"].execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
				for item in self.db[i]["query"].execute(f"SELECT * from {table[0]}").fetchall():
					func.debug(f"[DEBUG][SQL][{i}][{table[0]}]: {item}")
		#for table in self.query.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
			#for item in self.query.execute(f"SELECT * from {table[0]}").fetchall():
				#func.debug(f'[DEBUG][SQL][{table[0]}]: {item}')

	# Check tables
	def check_table(self, path=path):
		self.db["users"]["query"].execute("""CREATE TABLE IF NOT EXISTS `users` (
			user_id INT,
			username TEXT,
			firstname TEXT,
			balance REAL DEFAULT 0.00,
			s_pay REAL DEFAULT 0.00,
			s_buy INT DEFAULT 0,
			s_buy_pay REAL DEFAULT 0.00,
			support INT DEFAULT 0,
			role_id INT DEFAULT 0,
			role_notify BOOL DEFAULT 0,
			role_notify_appeal BOOL DEFAULT 0,
			role_notify_support BOOL DEFAULT 0,
			reg_time TEXT
		)""")
		self.db["clean"]["query"].execute("""CREATE TABLE IF NOT EXISTS `clean` (
			user_id INT,
			sticker_id INT DEFAULT 0,
			home_id INT DEFAULT 0,
			location TEXT DEFAULT 'menu_home'
		)""")
		self.db["settings"]["query"].execute("""CREATE TABLE IF NOT EXISTS `settings` (
			settings_id INT DEFAULT 0,
			engineering_mode BOOL DEFAULT 0,
			screen_main TEXT DEFAULT '<code>Данный текст можно изменить в ПУ.</code>\n\nИмя: $username\nБаланс: $balance',
			screen_contacts TEXT DEFAULT '<code>Данный текст можно изменить в ПУ.</code>',
			screen_instructions TEXT DEFAULT '<code>Данный текст можно изменить в ПУ.</code>',
			screen_rules TEXT DEFAULT '<code>Данный текст можно изменить в ПУ.</code>',
			sticker_main TEXT DEFAULT 'CAACAgIAAxkBAAECsWVhC-lSTIoHEIfqyeXcIfKlBW49MwACogIAAu7EoQqE9A4b2L7vtyAE',
			sticker_shop TEXT DEFAULT 'CAACAgIAAxkBAAECsXJhC-qqwLVasWgnQBzkaAUS9YlAfwAChwIAAu7EoQqwJTMW_TojAAEgBA',
			sticker_pricelist TEXT DEFAULT 'CAACAgIAAxkBAAECsXBhC-qchx45Rw0CZ0MnByivM07d0AAClQIAAu7EoQqYDfhJOpD7CSAE',
			sticker_profile TEXT DEFAULT 'CAACAgIAAxkBAAECsXRhC-q5W-hFz_AbC-fosXCZvTJpeAACkwIAAu7EoQqn-7IGJkPgfCAE',
			sticker_about TEXT DEFAULT 'CAACAgIAAxkBAAECsXZhC-rcSL-MRdvq-J0Iblf-VkQWPwACiQIAAu7EoQpa_Xevn-WeRCAE',
			sticker_feedback TEXT DEFAULT 'CAACAgIAAxkBAAECsWxhC-pUmGQQu4h9HJovDxJ93_3D7wACigIAAu7EoQqKLjvV2dZJ_iAE',
			specbtn_toggle BOOL DEFAULT 1,
			specbtn_text TEXT DEFAULT 'Партнеры',
			specbtn_link TEXT DEFAULT 'https://t.me/telegram',
			chat_link TEXT DEFAULT 'https://t.me/telegram'
		)""")
		self.db["settings"]["query"].execute("""CREATE TABLE IF NOT EXISTS `payments` (
			uniq_id INT DEFAULT 0,
			qiwi_rub TEXT DEFAULT 'p2p:False:NaN:NaN|*|terminal:False:NaN:NaN|*|nickname:False:NaN:NaN:NaN',
			qiwi_kzt TEXT DEFAULT 'p2p:False:NaN:NaN|*|terminal:False:NaN:NaN|*|nickname:False:NaN:NaN:NaN'
		)""")
		self.db["catalog"]["query"].execute("""CREATE TABLE IF NOT EXISTS `category` (
			category_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
			category_name TEXT,
			creator_id INT DEFAULT 0,
			creator_time TEXT,
			editor_id INT DEFAULT 0,
			editor_time TEXT DEFAULT 'NaN'
		)""")
		self.db["catalog"]["query"].execute("""CREATE TABLE IF NOT EXISTS `subcategory` (
			subcategory_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
			category_id INT,
			sscategory_id INT DEFAULT 0,
			subcategory_name TEXT,
			creator_id INT DEFAULT 0,
			creator_time TEXT,
			editor_id INT DEFAULT 0,
			editor_time TEXT DEFAULT 'NaN'
		)""")
		self.db["catalog"]["query"].execute("""CREATE TABLE IF NOT EXISTS `position` (
			position_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
			category_id INT,
			subcategory_id INT DEFAULT 0,
			position_name TEXT,
			position_price REAL DEFAULT 0.00,
			creator_id INT DEFAULT 0,
			creator_time TEXT,
			editor_id INT DEFAULT 0,
			editor_time TEXT DEFAULT 'NaN'
		)""")
		self.db["catalog"]["query"].execute("""CREATE TABLE IF NOT EXISTS `product` (
			product_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
			position_id INT,
			category_id INT,
			subcategory_id INT DEFAULT 0,
			product_content TEXT,
			creator_id INT DEFAULT 0,
			creator_time TEXT
		)""")
		self.db["transaction"]["query"].execute("""CREATE TABLE IF NOT EXISTS `transactions_buy` (
			buy_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
			buy_time TEXT,
			user_id INT,
			before REAL,
			after REAL,
			price REAL,
			position_name TEXT,
			content TEXT,
			creator_id INT,
			creator_time TEXT
		)""")
		self.db["transaction"]["query"].execute("""CREATE TABLE IF NOT EXISTS `transactions_pay` (
			pay_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
			pay_time TEXT,
			pay_system TEXT,
			pay_status TEXT DEFAULT 'WAIT',
			pay_url TEXT,
			user_id INT,
			before REAL,
			after REAL,
			amount REAL,
			currency TEXT,
			receipt TEXT
		)""")
		self.db["newsletter"]["query"].execute("""CREATE TABLE IF NOT EXISTS `newsletter` (
			newsletter_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
			content_type TEXT,
			content_text TEXT,
			content_file TEXT,
			send_id TEXT,
			creator_id INT DEFAULT 0,
			creator_time TEXT
		)""")
		self.db["support"]["query"].execute("""CREATE TABLE IF NOT EXISTS `appeal` (
			user_id INT,
			message_id TEXT DEFAULT ''
		)""")
		self.db["support"]["query"].execute("""CREATE TABLE IF NOT EXISTS `support` (
			user_id INT,
			message_id TEXT DEFAULT ''
		)""")
		self.db["stats"]["query"].execute("""CREATE TABLE IF NOT EXISTS `stats` (
			stats_id INT,
			s_work_time TEXT,
			s_today TEXT,
			s_all_users INT DEFAULT 0,
			s_all_payments REAL DEFAULT 0.00,
			s_all_sale INT DEFAULT 0,
			s_all_sale_pay REAL DEFAULT 0.00,
			s_today_users INT DEFAULT 0,
			s_today_payments REAL DEFAULT 0.00,
			s_today_sale INT DEFAULT 0,
			s_today_sale_pay REAL DEFAULT 0.00
		)""")
		for i, x in path.items():
			self.commit(i)

	def tuple_convert(self, a, b):
		if a == 'INT' or a == 'INTEGER': c = int(b)
		if a == 'REAL': c = float(b)
		if a == 'BOOL': c = func.StrBool(b)
		if a == 'TEXT': c = str(b)
		return c

	def insert(self, name, table = False, columns = False, values = False):
		if table and columns and values:
			inj = ""
			for i in range(len(values)): inj = inj + f'?,'
			self.db[name]["query"].execute(f"INSERT INTO `{table}` ({columns}) VALUES ({inj[:-1]})", values)
			self.commit(name)
			return True
		return False

	def select(self, name, table = False, search = False, multiple = False):
		if table and search:
			# COLUMNS
			row = self.db[name]["query"].execute(f"PRAGMA table_info(`{table}`)").fetchall()
			columns = {}
			for i in row:
				columns[i[1]] = i[2]

			# INFO
			if search == 'all': request = f"SELECT * FROM `{table}`"
			elif search.startswith('ORDER'): request = f"SELECT * FROM `{table}` {search}"
			else: request = f"SELECT * FROM `{table}` WHERE {search}"

			data = self.db[name]["query"].execute(request).fetchall()

			# CONSTRUCT
			if multiple or search == "all" or len(data) > 1:
				result = []
				for item in data:
					x = 0
					temp = {}
					for key, value in columns.items():
						temp[key] = self.tuple_convert(value, item[x])
						x = x + 1
					result.append(temp)
			elif data:
				x = 0
				result = {}
				for key, value in columns.items():
					result[key] = self.tuple_convert(value, data[0][x])
					x = x + 1
			else:
				result = None	
			return result
		return False

	def update(self, name, table = False, values = False):
		if table and type(values) == tuple:
			self.db[name]["query"].execute(f"UPDATE `{table}` SET `{values[0]}` = ? WHERE {values[2]}", (values[1],))
			self.commit(name)
			return True
		return False

	def delete(self, name, table = False, values = False):
		if table and values:
			self.db[name]["query"].execute(f"DELETE FROM `{table}` WHERE {values}")
			self.commit(name)
			return True
		return False
from ast import literal_eval
import time, random, requests
import utils._cfg as cfg
import utils.sql._handlers as db
from bs4 import BeautifulSoup


# Штамп времени
def timestamp(a = False):
	if a: ft = "%d.%m.%Y"
	else: ft = "%d.%m.%Y %X"
	return time.strftime(ft)


# Кол-во символов после точки
def toFixed(numObj, digits=0):
	return f"{numObj:.{digits}f}"


# Проверка на содержание ссылки
def UrlCheck(a):
	url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', a)
	return url


# Конвертация типа str в int/float
def StrToNum(s):
	if isinstance(s, str):
		try: val = literal_eval(s)
		except: val = s
	else: val = s
	
	if isinstance(val, float):
		if val.is_integer(): 
			return int(val)
	return val


# Костыль проверка str/int с выходом в bool
def StrBool(a):
	if a == 'True' or a == 1: return True
	return False


# Дебаг по триггеру
def debug(a):
	if StrBool(cfg.get("DEBUG")): return print(a)


# Заменить теги на звездочки (При необходимости можно дополнить)
def TagClear(a):
	return a.replace("<", "*").replace(">", "*").replace("'", "*").replace('"', "*")


# Фильтр HTML сообщений для SQL
def EncodeSQL(a):
	return a.replace("'","\'").replace('"','\"') #.replace('<','*').replace('>','*')

def DecodeSQL(a):
	return a.replace("\'","'").replace('\"','"') #.replace('*','<').replace('*','>')


# Получить права пользователя
def GetRole(a):
	b = db.GetUsers(a)
	c = {"id": b["role_id"], "notify": b["role_notify"], "notify_appeal": b["role_notify_appeal"], "notify_support": b["role_notify_support"]}
	if a == int(cfg.get("ADMIN_ID")): c = {"id": 1, "notify": b["role_notify"], "notify_appeal": b["role_notify_appeal"], "notify_support": b["role_notify_support"]}
	return c


# Генерация чека для платежей
def ReceiptPay():
	#a = list("ABCDEFGHIGKLMNOPQRSTUVYXWZ")
	#random.shuffle(a)
	#a = "".join([random.choice(a) for x in range(1)])
	a = "obmen"
	a += str(random.randint(10000000, 99999999))
	return a


# Генерация платежной Qiwi ссылки:
def QiwiPayUrl(a, b, c, d, e): # a = type | b = number/nickname | c = currency | d = sum | e = comment
	s = []
	if type(d) == float: s = str(d).split('.')
	else: s = [d, 0]
	if c == "rub": c = 643
	if c == "kzt": c = 398
	ready = {'amountInteger': s[0], 'amountFraction': s[1], 'currency': c, 'extra["comment"]': e, 'extra["account"]': b, 'blocked[1]': 'account', 'blocked[2]': 'comment'}
	if a == "terminal": a, ready['extra["accountType"]'] = 99, 'phone'
	if a == "nickname": a, ready['extra["accountType"]'] = 99999, 'nickname'
	x = requests.Session()
	z = x.get('https://qiwi.com/payment/form/'+str(a), params = ready)
	return z.url


# Конвертер валют
def CurrConvert(a, b):
	a = a.split(':')
	b = StrToNum(b)
	if type(b) == str: x = b
	if type(b) == float: b = int(b)
	if type(b) == int:
		if not b: x = 0
		else:
			x = requests.get(f"https://pokur.su/{a[0]}/{a[1]}/{b}/")
			x = BeautifulSoup(x.text, "html.parser").select("div[class$='blockquote-classic'] > p")[0].text
			x = x.replace(' ','').split('=')[1].split(a[1])[0]
			if "," in x: x = float(x.replace(",", "."))
			else: x = 0
	return x


# Удаление сообщений
async def DeleteMSG(a, b, c):
	if type(c) == list:
		for i in c:
			if i:
				try: await a.delete_message(b, i)
				except: pass
	else:
		try: await a.delete_message(b, c)
		except: pass
	return True


# Генерация html (Для статистики)
def StatsHTML(a):
	html = '<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0"><title>SHOPX9 - Статистика</title>' \
		'<style type="text/css"> * { margin: 0; padding: 0; } body { background-color: #141726; padding: 10px 15px; font-size: 13px; font-family: sans-serif; color: #ffffff; } .total { background-color: #1b2033; border-radius: 8px; padding: 10px 15px; line-height: 16px; color: #198cff; margin: 0px 2px; margin-bottom: 0px; display: inline-block; } .total > p > b { color: #ffffff; } .logotype { font-size: 25px; color: #198cff; font-weight: bold; margin-top: 10px; margin-left: 5px; margin-bottom: 5px; } .logotype span { color: #ffffff; } .table { width: 100%; border: none; margin-bottom: 20px; } .table thead th { font-weight: bold; text-align: left; border: none; padding: 10px 15px; background: #1b2033; font-size: 14px; } .table thead tr th:first-child { border-radius: 8px 0 0 8px; } .table thead tr th:last-child { border-radius: 0 8px 8px 0; } .table tbody td { text-align: left; border: none; padding: 10px 15px; font-size: 14px; vertical-align: top; } .table tbody tr:nth-child(even){ background: #0f121d; } .table tbody tr td:first-child { border-radius: 8px 0 0 8px; } .table tbody tr td:last-child { border-radius: 0 8px 8px 0; }</style>' \
		'</head><body><div class="logotype">SHOP<span>X9</span></div>' \
		f'{a}' \
		'</body></html>'
	open("data/SX9.stats.html", "w", encoding="utf8").write(html)
	return True
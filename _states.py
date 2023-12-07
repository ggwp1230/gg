from aiogram.dispatcher.filters.state import State, StatesGroup


class StateCatalog(StatesGroup):
	data = State()

class StateSettings(StatesGroup):
	data = State()

class StateNewsletter(StatesGroup):
	data = State()

class StateUsers(StatesGroup):
	data = State()

class StatePaySystem(StatesGroup):
	data = State()

class StatePayments(StatesGroup):
	data = State()

class StateTransactions(StatesGroup):
	data = State()

class StateStats(StatesGroup):
	data = State()

class StateAppeal(StatesGroup):
	user = State()
	operator = State()

class StateSupport(StatesGroup):
	user = State()
	operator = State()
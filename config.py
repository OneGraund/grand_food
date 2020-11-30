import db_manipulator
import sqlite3

DEBUG = 1

GREETINGS_STICKER = 'static/welcome.webp'
#-------REPLY-KEYBOARD--------
ITEM1 = "🛒 Магазин 🛒"
ITEM2 = "👤Личный Кабинет👤"
#---------INLINE-KEYBOARD-----
ITEM1_INLINE='➡️Перевод➡️'
ITEM2_INLINE='💰Средства💰'

ALERT_TEXT = 'Callback inline action'

def bank_message(your_id):
	return str(f'<b>Твой ID: {your_id}    (Номер твоего кошелька)</b>\nЭто твой личный кабинет. В нём ты можешь перевести 💵деньги💵 а также просмотреть количество 💰средств💰 на своём акаунте.')

SHOP_MESSAGE='''Это - магазин. В нём ты можешь заказать 
себе еду. Чтобы сделать заказ, надо ...'''

MONEY_TRANSACTION='''Для того чтобы перевести деньги, тебе нужен <b>ID кошелька</b> на который ты хочешь отправить деньги
(чтобы посмотреть ID, нажми на личный кабинет)\n\n<b>ID кошелька</b>:'''

IN_MONEY_TRANSACTION='Для того чтобы перевести деньги, тебе нужен ID кошелька на который ты хочешь отправить деньги\n(чтобы посмотреть ID, нажми на личный кабинет)\n\nID кошелька:'

WRONG_TYPE_OF_ID="Похоже на то, что ты неправильно ввёл ID кошелька ☹️ Учти, что он состоит только из девяти или десяти цифр. Попробуй ещё раз."
ID_GOOD_DB_BAD="ID кошелька введён в правильном формате, но мне не удаётся найти такого человека ☹️ Скорее всего у тебя где-то опечатка. Попробуй ещё раз."
def ALL_GOOD_DB_ID(user):
	if user[1] != None and user[2]!=None and user[3]!=None:
		return f"Всё супер!\nЧеловек, которому ты пытаетешься перевести деньги:\nID - {user[0]}\nИмя - {user[1]}\nФамилия - {user[2]}\nНикнейм - {user[3]}\nТеперь введи суму которую ты хочешь перевести:"
	elif user[1]!=None and user[2]!=None and user[3]==None:
		return f"Всё супер!\nЧеловек, которому ты пытаетешься перевести деньги:\nID - {user[0]}\nИмя - {user[1]}\nФамилия - {user[2]}\nТеперь введи суму которую ты хочешь перевести:"
	elif user[1]!=None and user[2]==None and user[3]==None:
		return f"Всё супер!\nЧеловек, которому ты пытаетешься перевести деньги:\nID - {user[0]}\nИмя - {user[1]}\nТеперь введи суму которую ты хочешь перевести:"
	elif user[1]==None and user[2]==None and user[3]==None:
		return f"Всё супер!\nЧеловек, которому ты пытаетешься перевести деньги:\nID - {user[0]}\n\nТеперь введи суму которую ты хочешь перевести:"
	elif user[1] != None and user[2]==None and user[3]!=None:
		return f"Всё супер!\nЧеловек, которому ты пытаетешься перевести деньги:\nID - {user[0]}\nИмя - {user[1]}\nНикнейм - {user[3]}\nТеперь введи суму которую ты хочешь перевести:"
	elif user[1] == None and user[2]==None and user[3]!=None:
		return f"Всё супер!\nЧеловек, которому ты пытаетешься перевести деньги:\nID - {user[0]}\nНикнейм - {user[3]}\nТеперь введи суму которую ты хочешь перевести:"
	elif user[1] == None and user[2]!=None and user[3]==None:
		return f"Всё супер!\nЧеловек, которому ты пытаетешься перевести деньги:\nID - {user[0]}\nФамилия - {user[2]}\nТеперь введи суму которую ты хочешь перевести:"
	elif user[1] == None and user[2]!=None and user[3]!=None:
		return f"Всё супер!\nЧеловек, которому ты пытаетешься перевести деньги:\nID - {user[0]}\nФамилия - {user[2]}\nНикнейм - {user[3]}\nТеперь введи суму которую ты хочешь перевести:"

TRY_TO_SEND_MONEY_TO_YOURSELF='Ты ввёл ID своего кошелька 😅 Не думаю что это целесообразно) Если ты хочешь перевести деньги другому человеку, то попроси его зайти в личный кабинет и продиктовать ID своего кошелька. Попробуй ещё раз:'
APPROOVAL_MONEY_TRANSFER='Всё супер!\nЧеловек, которому ты пытаетешься перевести деньги:'
def NOT_ENOUGH_MONEY(try_to_transfer, user_has):
	return (f'К сожалению, ты <b>пытаешься перевести {try_to_transfer} 💵грандиков💵</b>, хотя всего у тебя <b>на счету {user_has} 💵грандиков💵</b>\nПопробуй ещё раз')


PRODUCTS=None
LAST_SENT_MESSAGE=None

NOT_CORRECT_CASH = "К сожалению это неправильный формат денег ☹️ Пожалуйста, введи только суму которую хочешь перевести без каких-либо букв. Надеюсь ты не пытаешься сделать sql injection)"
def SUCCESSFULL_TRANSACTION(user_id,cash_amount,user_cash):
	db = sqlite3.connect('server.db')
	sql= db.cursor()
	user = db_manipulator.get_user_by_id(sql_cursor=sql, id_of_user=int(user_id))
	if user[1]!=None:
		name=user[1]
	elif user[2]!=None:
		name=user[2]
	elif user[3]!=None:
		name=user[3]
	else:
		name=user[0]

	return (f"<b>Транзакция успешна!</b>\n<b>{name}</b> получил/а свои <b>💵{cash_amount} грандиков💵</b>\n<b>Остаток на вашем счету - 💵{user_cash} грандиков💵</b>")

def SHOW_USER_DATA(user):
	print(f"SHOW_USER_DATA request...\nOperating user: \n{user}\n{'_'*30}")
	if user[5] == 0:
		grade = 'не добавлен'
	if user[6]=='student':
		position='нет'
	if user[7]=='unemployed':
		job='безработный'
	return(f"<b>👤Информация о пользователе👤:</b>\n\n<b>ID</b> - {user[0]}\n<b>Имя</b> - {user[1]}\n<b>Фамилия</b> - {user[2]}\n<b>Никнейм</b> - {user[3]}\n<b>Грандиков</b> - {user[4]}\n"
		   f"\nКласс - {grade}\nДолжность - {position}\nЗарплата - {user[8]}\nРабота - {job}")

USER_ORDER=None

def ORDER_MESSAGE(cart_price,products_in_cart):
	string=f'Стоимость товаров в твоей корзине - 💵{cart_price} грандиков💵\n'
	for elem in products_in_cart:
		if elem[1]!=0:
			string = string + str(f'<b>{elem[0][1]}</b> - {elem[1]} шт.\n')
	return string

BOT_ORDER_MESSAGE=None

ORDER_MESSAGE_MARKUP=None

def ORDER_CONFIRMED_MESSAGE(cart, user_money):
	string = f'Твой заказ принят и уже пакуется в <b>зале хореографии</b>. Ожидай его там). Приятного аппетита !\n\n<b>Твой заказ:</b>\n'
	for elem in cart:
		if elem[1]!=0:
			string = string + f'{elem[0][1]} - {elem[1]} шт.\n'
	string = f'{string}\nОстаток - <b>💵{user_money} грандиков💵</b>'
	return string


ORDER_CANCELLED_MESSAGE='Заказ отменён, корзина очищена'

def ORDER_NOT_ENOUGH_MONEY(user_cash_amount, cart_cash_amount):
	return f'<b>Заказ не может быть оплачен.</b>\nК сожалению, у тебя на счету <b>💵{user_cash_amount} грандиков💵</b>.\n<b>Стоимость заказа - 💵{cart_cash_amount} грандиков💵</b>'


USER_IN_CLASS=None

#---------IMPORTS-----------
import telebot
import config
import random
import sqlite3
import products
import secret_token

from telebot import types
#from db_manipulator import User, get_users_from_db, get_user_by_id
import db_manipulator
#---------------------------

#-------------------------------------------------------------
print("Grand_food has started work ...")
#-------------------------------------------------------------

#----------------START-UP-----------
bot = telebot.TeleBot(secret_token.TOKEN)
#-----------------------------------

#---------------------USER-registration-------------------
def register_user(message):
	#print("Start func init. Registration? ...")
	db = sqlite3.connect('server.db')
	sql= db.cursor()
	if db_manipulator.get_user_by_id(int(message.from_user.id), sql_cursor=sql) == None:
		#print(f"User - {message.from_user.id} is not in DB. Adding...")
		config.USER_IN_CLASS=db_manipulator.User(message.from_user.id,message.from_user.first_name, 
			message.from_user.last_name, message.from_user.username, 0).write_user_to_db(sql_cursor=sql, db=db)
	else:
		#print(f"User - {message.from_user.id} is in DB. Continuing...")
		config.USER_IN_CLASS=db_manipulator.User(message.from_user.id,message.from_user.first_name, 
			message.from_user.last_name, message.from_user.username, 0)
		return
#---------------------------------------------------------

#----------------------START-FUNC--------------------------
@bot.message_handler(commands=['start'])
def welcome(message):
	delete_shop_UI(message.chat.id)
	config.LAST_SENT_MESSAGE=None
	#-----------------keyboard------------------------------
	markup= types.ReplyKeyboardMarkup(resize_keyboard=True)
	item1 = types.KeyboardButton(config.ITEM1)
	item2 = types.KeyboardButton(config.ITEM2)
	markup.add(item1, item2)
	#-------------------------------------------------------
	#--------------Greetings-sticker-----------------------
	sti=open(config.GREETINGS_STICKER, 'rb')
	bot.send_sticker(message.chat.id, sti,reply_markup=markup)
	#------------------------------------------------------
	#----------------Register-user-------------------------
	register_user(message)
	#------------------------------------------------------
	markup2 = types.InlineKeyboardMarkup(row_width=1)
	item1=types.InlineKeyboardButton("Поддержка", url='https://t.me/OneGraund')
	markup2.add(item1)
	#-----------------Hello-Message-------------------------
	bot.send_message(message.chat.id, 
		f'''Привет, {message.from_user.first_name}!\n 
			Это - <b>{bot.get_me().first_name}</b>!''',
		parse_mode='html',
		reply_markup=markup2)
	#-------------------------------------------------------
#-----------------------------------------------------------

def searchProductByMessageId(products, messageId):
	for elem in products:
		if elem.sentMessageId == messageId:
			return elem

#-----------------------Product-class-----------------------
class Product(object):
	amountInOrder = 0
	sentMessageId = None
	def __init__(self, product_id, product_name, img, price, isInStock):
		self.product_id = product_id
		self.product_name = product_name
		self.img= img
		self.price = price
		self.isInStock = isInStock

	def sendMessage(self, message):

		markup = types.InlineKeyboardMarkup(row_width=3)
		item1=types.InlineKeyboardButton("🔻", callback_data='less')
		item2=types.InlineKeyboardButton(f'{self.amountInOrder} шт.',callback_data='nothing') 
		item3=types.InlineKeyboardButton("🔺", callback_data='more')
		markup.add(item1, item2, item3)

		img = open(self.img, 'rb')
		message=bot.send_photo(message.chat.id, img, f"{self.product_name}. Цена - {self.price}",reply_markup=markup)
		self.sentMessageId = message.message_id

	def __str__(self):
		print(f"Product name - {self.product_name}\n"
			  f"Image - {self.img}\n"
			  f"Price - {self.price}\n"
			  f"isInStock - {self.isInStock}\n"
			  f"amountInOrder - {self.amountInOrder}\n"
			  f"sentMessageId - {self.sentMessageId}\n")
#-----------------------------------------------------------
def check_if_int(string_to_check):
	try:
		string_to_check=int(string_to_check)
	except Exception as e:
		return False
	return True
#-----------------------------------------------------------
def delete_shop_UI(chat_id):
	try:
		for elem in config.PRODUCTS:
			bot.delete_message(chat_id, elem.sentMessageId)
		bot.delete_message(chat_id, config.BOT_ORDER_MESSAGE.message_id)
	except Exception as e:
		pass
		#print(f"An error occurred - {e}. You shop UI is was probably not triggered yet.")
#--------------------Text-reaction--------------------------
@bot.message_handler(content_types=['text'])
def text_message_func(message):
	if message.chat.type == 'private':

		if message.text  == config.ITEM1:		#This is a shop button
			delete_shop_UI(message.chat.id)
			config.USER_ORDER=db_manipulator.Order(message.from_user.id)
			config.LAST_SENT_MESSAGE=None
			config.USER_ORDER.clear_cart()
			tovar=[]
			for elem in products.products:
				tovar.append(Product(elem[0],elem[1],elem[2],elem[3],elem[4]))

			config.PRODUCTS = tovar

			for elem in config.PRODUCTS:
				elem.sendMessage(message)
				#elem.__str__()

			markup = types.InlineKeyboardMarkup(row_width=2)
			item1=types.InlineKeyboardButton("❌Отменить заказ❌", callback_data='cancel_order')
			item3=types.InlineKeyboardButton("✅Подтвердить заказ✅", callback_data='confirm_order')
			markup.add(item1, item3)
			config.ORDER_MESSAGE_MARKUP=markup

			config.BOT_ORDER_MESSAGE=bot.send_message(
				message.chat.id, 
				config.ORDER_MESSAGE(
					cart_price=config.USER_ORDER.get_cart_price(),
					products_in_cart=config.USER_ORDER.cart),
				reply_markup=markup,
				parse_mode='html'
			)


		elif message.text== config.ITEM2:		#This is a bank button
			delete_shop_UI(message.chat.id)
			config.LAST_SENT_MESSAGE=None
			#----------inline-keyboard-initialisation---------
			markup= types.InlineKeyboardMarkup(row_width=2)
			item1 = types.InlineKeyboardButton(config.ITEM1_INLINE,callback_data='good')
			item2 = types.InlineKeyboardButton(config.ITEM2_INLINE,callback_data='bad' )
			markup.add(item1, item2)
			#------------------------------------------------
			bot.send_message(message.chat.id, config.bank_message(message.from_user.id), 
				parse_mode='html',reply_markup=markup)
#---------------------------------INPUT-COMMANDS--------------------------------------------------------------------------------
		elif config.LAST_SENT_MESSAGE!=None:
			delete_shop_UI(message.chat.id)
			#-----------------------------MONEY-TRANSFER------------------------------------------------------------
			if (config.APPROOVAL_MONEY_TRANSFER in config.LAST_SENT_MESSAGE.text)==True:
				a=config.LAST_SENT_MESSAGE.text
				#CHECK IF USER SEND NORMAL AMOUNT OF CASH
				if check_if_int(message.text)==True:
					db = sqlite3.connect('server.db')
					sql= db.cursor()
					if int(message.text)<=db_manipulator.get_user_cash_by_id(int(message.from_user.id),sql):
						res=db_manipulator.do_money_transfer(db=db,sql=sql,id1=message.chat.id, id2=int(a[ (a.find('ID')+5) : (a.find('ID')+14) ]),
							cash=int(message.text))
						if res == 'Success':
							bot.send_message(message.chat.id, config.SUCCESSFULL_TRANSACTION(
								user_id=int(a[ (a.find('ID')+5) : (a.find('ID')+14) ]),
								cash_amount=int(message.text),
								user_cash=db_manipulator.get_user_cash_by_id(int(message.from_user.id),sql)),
								parse_mode='html'
							)
					else:
						bot.send_message(message.chat.id, config.NOT_ENOUGH_MONEY(
							try_to_transfer=message.text, 
							user_has=db_manipulator.get_user_cash_by_id(int(message.chat.id), sql)
							),
						parse_mode='html'
						)
				else:
					bot.send_message(message.chat.id, config.NOT_CORRECT_CASH)
			#--------------------------------------------------------------------------------------------------------
			#----------------------------GET-ID-FOR-TRANSFER-----------------------------------------------
			elif config.LAST_SENT_MESSAGE.text==config.IN_MONEY_TRANSACTION:
				if len(str(message.text))==9 and check_if_int(message.text)==True: 
					db = sqlite3.connect('server.db')
					sql= db.cursor()
					user_in_db = db_manipulator.get_user_by_id(int(message.text), sql)
					if user_in_db != None:
						if user_in_db[0]!=message.from_user.id:
							config.LAST_SENT_MESSAGE=bot.send_message(message.chat.id, config.ALL_GOOD_DB_ID(user_in_db))
						else:
							bot.send_message(message.chat.id, config.TRY_TO_SEND_MONEY_TO_YOURSELF)
					else:
						bot.send_message(message.chat.id, config.ID_GOOD_DB_BAD)
				else:
					bot.send_message(message.chat.id, config.WRONG_TYPE_OF_ID)

		else:									#This is when a random text is given
			bot.send_message(message.chat.id, 'Неизвесная команда☹️ \nПопробуй - /start')
#--------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------


#----------------Inline-BANK-keyboard-processing------------------
@bot.callback_query_handler(func=lambda call: True)
def callback_bank_inline_query(call):
	#try:
	if call.message:
		#----PRODUCT-BUUTONS-ON-INLINE-KEYBOARD-HANDLER-------
		def inline_keyboard_products_action(status):
			if config.USER_ORDER!=None:
				productAction = searchProductByMessageId(config.PRODUCTS,call.message.message_id)
				
				if status=='less':
					config.USER_ORDER.remove_from_cart(productAction.product_id)
				elif status=='more':
					config.USER_ORDER.add_to_cart(productAction.product_id)

				for elem in config.USER_ORDER.cart:
					if elem[0][1]==productAction.product_name:
						amountInOrder=elem[1]
				
				bot.edit_message_reply_markup(
					chat_id=call.message.chat.id,
					message_id=productAction.sentMessageId,
					reply_markup=types.InlineKeyboardMarkup(row_width=3).add(
							types.InlineKeyboardButton("🔻", callback_data='less'),
							types.InlineKeyboardButton(f'{amountInOrder} шт.',callback_data='nothing'),
							types.InlineKeyboardButton("🔺", callback_data='more')
						)
					)
				
				bot.edit_message_text(chat_id=call.message.chat.id, 
					message_id=config.BOT_ORDER_MESSAGE.message_id, 
					text=config.ORDER_MESSAGE(
						cart_price=config.USER_ORDER.get_cart_price(),
						products_in_cart=config.USER_ORDER.cart
						),
					reply_markup=config.ORDER_MESSAGE_MARKUP,
					parse_mode='html'
				)
		#print("Callback request")
		#------------------------Money-perevod------------
		if call.data == 'good':
			config.LAST_SENT_MESSAGE=None
			#print("CALLBACK ACTION: Money transaction")
			config.LAST_SENT_MESSAGE=bot.send_message(call.message.chat.id, config.MONEY_TRANSACTION, parse_mode='html')
			bot.edit_message_text(chat_id=call.message.chat.id, 
				message_id=call.message.message_id, text=config.bank_message(call.from_user.id),
				parse_mode='html', reply_markup=None)
			bot.answer_callback_query(callback_query_id=call.id, 
				show_alert=False,
				text="Вы выбрали перевод средств")
		#--------------------------------------------
		#-------------------Show-amount-of-money----------
		elif call.data == 'bad' :
			config.LAST_SENT_MESSAGE=None
			#print("CALLBACK ACTION: Show amount of money")
			db = sqlite3.connect('server.db')
			sql= db.cursor()
			bot.send_message(
				call.message.chat.id, 
				config.SHOW_USER_DATA(
						user=db_manipulator.get_user_by_id(call.from_user.id, sql)
					),
				reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
							types.InlineKeyboardButton("🔄Обновить данные🔄", callback_data='reload_profile'),
							types.InlineKeyboardButton("✅Закончить регистрацию✅", callback_data='finish_registration')
						),
			parse_mode='html')
			bot.edit_message_text(chat_id=call.message.chat.id, 
				message_id=call.message.message_id, text=config.bank_message(call.from_user.id),
				parse_mode='html', reply_markup=None)
			bot.answer_callback_query(callback_query_id=call.id, 
				show_alert=False,
				text="Вы выбрали отображение средств")
		#--------------------------------------------------
		#----------------RELOAD-USER-INFORMATION-----------
		elif call.data == 'reload_profile':
			config.LAST_SENT_MESSAGE=None
			#user_id, first_name, second_name, username, cash
			db = sqlite3.connect('server.db')
			sql= db.cursor()
			config.USER_IN_CLASS=db_manipulator.User(
					call.from_user.id,
					call.from_user.first_name, 
					call.from_user.last_name, 
					call.from_user.username, 
					db_manipulator.get_user_cash_by_id(
							idForScan=call.from_user.id, 
							sql=sql
						)
				)
			res=config.USER_IN_CLASS.reload_data_in_class(
					sql_cursor=sql, 
					db=db
				)
			
			bot.edit_message_text(
					chat_id=call.message.chat.id,
					message_id=call.message.message_id,
					text=config.SHOW_USER_DATA(
						user=db_manipulator.get_user_by_id(call.from_user.id, sql)
					),
					parse_mode='html'
				)
		#--------------------------------------------------
		#---------------Finish-user-registration-----------
		elif call.data == 'finish_registration':
			db = sqlite3.connect('server.db')
			sql= db.cursor()
			bot.edit_message_text(chat_id=call.message.chat.id, 
				message_id=call.message.message_id, 
				text=config.SHOW_USER_DATA(
						user=db_manipulator.get_user_by_id(call.from_user.id, sql)
					),
				reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
							types.InlineKeyboardButton("🔄Обновить данные🔄", callback_data='reload_profile'),
						),
			parse_mode='html')
			bot.send_message(call.message.chat.id, text='User registration request')
		#-------------------Product-staff------------------		
		elif call.data == 'less':
			inline_keyboard_products_action('less')

		elif call.data == 'more':
			inline_keyboard_products_action('more')

		elif call.data == 'cancel_order':
			bot.send_message(chat_id=call.message.chat.id, 				#bot.edit_message
				#message_id=config.BOT_ORDER_MESSAGE.message_id, 
				text=config.ORDER_CANCELLED_MESSAGE,
				reply_markup=None
				)
			delete_shop_UI(call.message.chat.id)
			config.USER_ORDER.clear_cart()

		elif call.data == 'confirm_order':
			db = sqlite3.connect('server.db')
			sql= db.cursor()
			if config.USER_ORDER.confirm_order(sql,database=db)!='ERROR - NOT ENOUGH MONEY':
				if config.USER_ORDER.get_cart_price()!=0:
					bot.send_message(call.message.chat.id, 
						config.ORDER_CONFIRMED_MESSAGE(
							cart=config.USER_ORDER.cart, 
							user_money=db_manipulator.get_user_cash_by_id(call.from_user.id, sql)
							),
						parse_mode='html'
					)
					bot.edit_message_text(chat_id=call.message.chat.id, 
						message_id=config.BOT_ORDER_MESSAGE.message_id, 
						text=config.ORDER_MESSAGE(
							cart_price=config.USER_ORDER.get_cart_price(),
							products_in_cart=config.USER_ORDER.cart
							),
						reply_markup=None,
						parse_mode='html'
						)
					delete_shop_UI(call.message.chat.id)
					config.USER_ORDER.clear_cart()
				else:
					bot.answer_callback_query(
						callback_query_id=call.id, 
						show_alert=True,
						text="Твоя корзина пустая!"
					)
			else:
				bot.send_message(
					call.message.chat.id, 
					config.ORDER_NOT_ENOUGH_MONEY(
						db_manipulator.get_user_by_id(call.from_user.id, sql)[4],
						config.USER_ORDER.get_cart_price()
						),
					parse_mode='html'
					)
				delete_shop_UI(call.message.chat.id)
				config.USER_ORDER.clear_cart()
		#------------------------------------------------
	#except Exception as e:
	#	print(repr(e))
#--------------------------------------------------------------


#----------RUN-------------
bot.polling(none_stop=True)
#--------------------------
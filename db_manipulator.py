import sqlite3
import products
import config

db = sqlite3.connect('server.db')
sql= db.cursor()

sql.execute('''CREATE TABLE IF NOT EXISTS users (
	user_id INT,
	first_name TEXT,
	second_name TEXT,
	username TEXT,
	cash BIGINT,
	grade INT,
	position TEXT,
	job TEXT,
	salary INT)''')

db.commit()

class User(object):
	grade=0
	position='student' #должность в лицейской асамблее
	job='unemployed' 	  #работа в лицее
	salary = 0 #зарпалата основаная на работе

	def __init__(self, user_id, first_name, second_name, username, cash):
		self.user_id = user_id
		self.first_name = first_name
		self.second_name =second_name
		self.username = username
		self.cash = cash

	def write_user_to_db(self, sql_cursor, db):
		sql_cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (self.user_id, 
			self.first_name, self.second_name, self.username, self.cash, self.grade, self.position, self.job, self.salary))
		db.commit()
		print(f"User - {self.first_name} has been written to db")

	def reload_data_in_class(self, sql_cursor, db):
		user=get_user_by_id(self.user_id, sql_cursor)
		if user[1]==self.first_name and user[2]==self.second_name and user[3]==self.username:
			print("User data is the same... Continuing...")
			return None
		else:
			print(f"Update db data request: \nOld name - {user[1]};\t New name - {self.first_name}\n"
				f"Old second name - {user[2]}\t New second name - {self.second_name}\n"
				f"Old username - {user[3]}\t New username - {self.username}\n"
				f"ID - {self.user_id};")
			sql_cursor.execute("UPDATE users SET first_name= ? ,second_name= ? , username = ? WHERE user_id= ?", (self.first_name, self.second_name, self.username, self.user_id))

			db.commit()

def get_user_cash_by_id(idForScan, sql):
	return int(get_user_by_id(idForScan, sql)[4])

def get_users_from_db():
	lines = []
	for value in sql.execute("SELECT * FROM users"):
		lines.append(value)
	for elem in lines:
		pass
		#print(f"{elem[1]}-{type(elem)}")

def get_user_by_id(idFromDB, sql_cursor):
	lines = []
	for value in sql_cursor.execute("SELECT * FROM users"):
		lines.append(value)
	for elem in lines:
		if elem[0]==idFromDB:
			#print(f"I have been lookinf for a user with ID - {elem[0]} and found out that he has {elem[4]} cash")
			return elem
	return None

def give_user_money_by_id(idOfUser,amount_of_money, db, sql):
	sql.execute(f'SELECT user_id FROM users WHERE user_id = {idOfUser}')
	if sql.fetchone() is None:
		return 'Error. There is no such id. Error should be in bot.py'
	else:
		sql.execute(f"UPDATE users SET cash = {int(get_user_by_id(idOfUser, sql)[4])+amount_of_money} WHERE user_id = {idOfUser}")
		db.commit()


def do_money_transfer(db, sql,id1, id2, cash):
	print(f'''Doing moeny transfer from {id1} to {id2}\nName of 1 - {get_user_by_id(id1, sql)[1]}
Name of 2 - {get_user_by_id(id2, sql)[1]}\nAmount of money first person - {get_user_cash_by_id(id1,sql)}
Amount of money second person - {get_user_cash_by_id(id2, sql)}''')
	print("Transfering...")
	sql.execute(f"UPDATE users SET cash = {get_user_cash_by_id(id2,sql)+cash} WHERE user_id={id2}")
	sql.execute(f"UPDATE users SET cash = {get_user_cash_by_id(id1,sql)-cash} WHERE user_id={id1}")
	print("Money has been transfered!\n" + "_"*50)
	db.commit()
	print(f'''From {id1} to {id2}\nName of 1 - {get_user_by_id(id1, sql)[1]}
Name of 2 - {get_user_by_id(id2, sql)[1]}\nAmount of money first person - {get_user_cash_by_id(id1,sql)}
Amount of money second person - {get_user_cash_by_id(id2, sql)}''')
	return 'Success'

class Order(object):
	status = None #created, accepted, completed
	cart = []
	for elem in products.products:
		cart.append([elem, 0]) # product, quantity

	def __init__(self, user_id):
		self.user_id = user_id
		self.status = 'created'

	def add_to_cart(self, product_id):
		self.cart[product_id-1][1]=self.cart[product_id-1][1]+1

	def remove_from_cart(self, product_id):
		if int(self.cart[product_id-1][1])>0:
			self.cart[product_id-1][1]=self.cart[product_id-1][1]-1

	def clear_cart(self):
		for i in range(len(self.cart)):
			self.cart[i][1]=0

	def get_cart_price(self):
		price=0
		for elem in self.cart:
			#print(elem)
			if elem[1]!=0:
				price = price + (elem[0][3]*elem[1])
		return price

	def confirm_order(self,sql_order,database):
		if get_user_cash_by_id(sql=sql_order,idForScan=self.user_id)>=self.get_cart_price():# and config.USER_ORDER.get_cart_price()!=0: #ERROR RIGHT HERE
			if self.get_cart_price()!=0:
				user_info=get_user_by_id(idFromDB=self.user_id, sql_cursor=sql_order)
				self.status='confirmed'
				print("-"*50)
				print(f"""Order was confirmed by:
	ID - {self.user_id}\nName - {user_info[1]}\nLast name - {user_info[2]}
	Username - {user_info[3]}\n{"-  "*17}\nPlease, start packing this order:""")
				for elem in self.cart:
					if elem[1]!=0:
						print(f"{elem[0][1]} - quantity:{elem[1]} ")
				sql_order.execute(f"UPDATE users SET cash = {user_info[4]-self.get_cart_price()} WHERE user_id = {self.user_id}")
				database.commit()
			else:
				return
		else:
			return 'ERROR - NOT ENOUGH MONEY'

	def __str__(self):
		cart_string=''
		for elem in self.cart:
			cart_string = cart_string + str(elem) + "\n"
		return(f"Client ID - {self.user_id}\nStatus - {self.status}\nCart items:{cart_string}")



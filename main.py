import os
import csv
import sqlite3


class DataHandler:

	def __init__(self):
		self.tablenames = {'companies': 'test/companies.csv',
				'financial': 'test/financial.csv'}
		self.table_details = {
				'companies': {"ticker": "text primary key",
					"name": "text",
					"sector": "text"},
				'financial': {"ticker": "text primary key",
					"ebitda": "real",
					"sales": "real",
					"net_profit": "real",
					"market_price": "real",
					"net_debt": "real",
					"assets": "real",
					"equity": "real",
					"cash_equivalents": "real",
					"liabilities": "real"}
					}
		self.connection = None
		self.cursor = None
		self.db_file = 'investor.db'
		self.create_tables()

	def connect(self):
		self.connection = sqlite3.connect(self.db_file)
		self.connection.row_factory = sqlite3.Row
		self.cursor = self.connection.cursor()

	def disconnect(self):
		self.cursor.close()
		self.connection.close()

	def create_table(self, table):
		with open(self.tablenames[table]) as file:
			freader = csv.reader(file, delimiter=',')
			head = next(freader)
			command = f"create table if not exists {table} ("
			command += ", ".join(f"{name} {self.table_details[table][name]}" for name in head) + ");"
			self.cursor.execute(command)
			values = [tuple(value if value else None for value in line) for line in freader]
			command = f"insert into {table} values (" + ", ".join("?" for _ in head) + ")"
			try:
				self.cursor.executemany(command, values)
				self.connection.commit()
			except sqlite3.IntegrityError:
				pass

	def create_tables(self):
		self.connect()
		for table in self.tablenames:
			self.create_table(table)

	def store_it(self):
		self.create_tables()
		self.disconnect()
		print("Database created successfully!")

	def remove_db(self):
		if os.path.exists(self.db_file):
			os.remove(self.db_file)

	def insert_row(self, table_name, value_dict):
		self.cursor.execute(f"select * from {table_name};")
		colnames = list(map(lambda x: x[0], self.cursor.description))
		val_tup = tuple(value_dict.get(name, None) for name in colnames)
		sql_query = f"insert into {table_name} values ({','.join('?' for _ in colnames)})"
		self.cursor.execute(sql_query, val_tup)
		self.connection.commit()

	def read_table_row(self, ticker):
		sql_query = f"select * from financial where ticker = '{ticker}';"
		self.cursor.execute(sql_query)
		return self.cursor.fetchone()

	def read_company_data(self, company, all_data=True):
		if all_data:
			sql_query = f"select * from (select * from companies c join financial f on c.ticker = f.ticker) where name like '%{company}%';"
		else:
			sql_query = f"select * from companies where name like '%{company}%';"
		self.cursor.execute(sql_query)
		return self.cursor.fetchall()

	def update_company_data(self, ticker, data):
		sql_query = f"update financial set ({', '.join(data.keys())}) = ({', '.join(str(val) for val in data.values())}) where ticker = '{ticker}';"
		self.cursor.execute(sql_query)
		self.connection.commit()

	def delete_company_data(self, ticker):
		self.cursor.execute(f"delete from companies where ticker = '{ticker}'")
		self.cursor.execute(f"delete from financial where ticker = '{ticker}'")
		self.connection.commit()

	def list_all_companies(self):
		self.cursor.execute("select * from companies order by ticker;")
		return self.cursor.fetchall()

	def top_ten(self, variable):
		sql_query = f"select ticker, round({variable['definition']}, 2) as new_var from financial order by new_var desc;"
		self.cursor.execute(sql_query)
		results = [[*row] for row in self.cursor.fetchmany(10)]
		print(f"TICKER {variable['name']}")
		print("\n".join(f"{x[0]} {x[1]}" for x in results))


class Menu:

	def __init__(self, dhandler):
		self.name = 'main'
		self.content = ['MAIN MENU',
				'0 Exit',
				'1 CRUD operations',
				'2 Show top ten companies by criteria']
		self.datahandler = dhandler

	def show(self):
		print()
		print('\n'.join(self.content), end='\n\n')
		return input("Enter an option: ")

	def play(self):
		try:
			val = int(self.show())
			if val == 0:
				print("Have a nice day!")
				return None
			elif val == 1:
				return 'crud'
			elif val == 2:
				return 'topten'
			else:
				raise ValueError
		except ValueError:
			print("Invalid option!")
			return self.name


class Crud(Menu):

	def __init__(self, dhandler):
		self.name = 'crud'
		self.content = ['CRUD MENU',
				'0 Back',
				'1 Create a company',
				'2 Read a company',
				'3 Update a company',
				'4 Delete a company',
				'5 List all companies']
		self.datahandler = dhandler
		self.company = None

	def play(self):
		try:
			val = int(self.show())
			if val == 0:
				return 'main'
			elif val == 1:
				self.create()
			elif val == 2:
				self.read()
			elif val == 3:
				self.update()
			elif val == 4:
				self.delete()
			elif val == 5:
				self.listall()
			else:
				raise ValueError
			return 'main'
		except ValueError:
			print("Invalid option!")
			return self.name

	def get_company_data(self):
		company_data = dict()
		company_data['ticker'] = input("Enter ticker (in the format 'MOON')\n")
		company_data['name'] = input("Enter company (in the format 'Moon Corp')\n")
		company_data['sector'] = input("Enter industries (in the format 'Technology')\n")
		return company_data

	def get_financial_data(self):
		financial_data = dict()
		financial_data['ebitda'] = input("Enter ebitda (in the format '987654321')\n")
		financial_data['sales'] = input("Enter sales (in the format '987654321')\n")
		financial_data['net_profit'] = input("Enter net profit (in the format '987654321')\n")
		financial_data['market_price'] = input("Enter market price (in the format '987654321')\n")
		financial_data['net_debt'] = input("Enter net dept (in the format '987654321')\n")
		financial_data['assets'] = input("Enter assets (in the format '987654321')\n")
		financial_data['equity'] = input("Enter equity (in the format '987654321')\n")
		financial_data['cash_equivalents'] = input("Enter cash equivalents (in the format '987654321')\n")
		financial_data['liabilities'] = input("Enter liabilities (in the format '987654321')\n")
		return financial_data

	def create(self):
		company = {**self.get_company_data(), **self.get_financial_data()}
		# company = {'ticker': 'CODD', 'name': 'Codd Corp', 'sector': 'Research', 'ebitda': 1000, 'sales': 1000, 'net_profit': 250, 'market_price': 2000, 'net_debt': 100, 'assets': 2000, 'equity': 2500, 'cash_equivalents': 2500, 'liabilities': 100}
		for table in self.datahandler.tablenames:
			self.datahandler.insert_row(table, company)

		print("Company created successfully!")

	def select_company(self):
		company = input("Enter company name: ")
		companies = self.datahandler.read_company_data(company, all_data=False)
		if not companies:
			self.company = None
			print("Company not found!")
			return False
		else:
			menu_items = {str(i): comp['name'] for i, comp in enumerate(companies)}
			while True:
				print('\n'.join(f"{key} {val}" for key, val in menu_items.items()))
				sel = input("Enter company number: ")
				if menu_items.get(sel, None):
					cinfo = companies[int(sel)]
					self.company = {'ticker': cinfo['ticker'], 'name': cinfo['name']}
					break
			return True

	def read(self):
		if self.select_company():
			data = self.datahandler.read_table_row(self.company['ticker'])
			cfinancials = {'P/E': data['market_price']/data['net_profit'],
						'P/S': data['market_price']/data['sales'],
						'P/B': data['market_price']/data['assets'],
						'ND/EBITDA': data['net_debt']/data['ebitda'] if data['ebitda'] else None,
						'ROE': data['net_profit']/data['equity'],
						'ROA': data['net_profit']/data['assets'],
						'L/A': data['liabilities']/data['assets']
			}
			print(f"{self.company['ticker']} {self.company['name']}")
			print('\n'.join(f"{key} = {val:.2f}" if val else f"{key} = None" for key, val in cfinancials.items()))

	def update(self):
		if self.select_company():
			fin_data = self.get_financial_data()
			# fin_data = {'ebitda': 1000, 'sales': 1000, 'net_profit': 250, 'market_price': 2000, 'net_debt': 100, 'assets': 2000, 'equity': 2500, 'cash_equivalents': 2500, 'liabilities': 10}
			self.datahandler.update_company_data(self.company['ticker'], fin_data)
			print("Company updated successfully!")

	def delete(self):
		if self.select_company():
			self.datahandler.delete_company_data(self.company['ticker'])
			print("Company deleted successfully!")

	def listall(self):
		print("COMPANY LIST")
		allcompanies = self.datahandler.list_all_companies()
		print("\n".join(" ".join([*company]) for company in allcompanies))


class TopTen(Menu):

	def __init__(self, dhandler):
		self.name = 'topten'
		self.content = ['TOP TEN MENU',
				'0 Back',
				'1 List by ND/EBITDA',
				'2 List by ROE',
				'3 List by ROA']
		self.datahandler = dhandler

	def play(self):
		try:
			val = int(self.show())
			if val == 0:
				return 'main'
			elif val == 1:
				self.ebitda()
			elif val == 2:
				self.roe()
			elif val == 3:
				self.roa()
			else:
				raise ValueError
			return 'main'
		except ValueError:
			print("Invalid option!")
			return 'main'

	def ebitda(self):
		self.datahandler.top_ten({'name': 'ND/EBITDA', 'definition': 'net_debt/ebitda'})

	def roe(self):
		self.datahandler.top_ten({'name': 'ROE', 'definition': 'net_profit/equity'})

	def roa(self):
		self.datahandler.top_ten({'name': 'ROA', 'definition': 'net_profit/assets'})


class Calculator:
	def __init__(self):
		self.welcome_msg = "Welcome to the Investor Program!"
		self.datahandler = DataHandler()
		self.datahandler.connect()
		self.menus = {'main': Menu(self.datahandler),
					'crud': Crud(self.datahandler),
					'topten': TopTen(self.datahandler)}
		self.current = self.menus['main']

	def play(self):
		print(self.welcome_msg)
		while True:
			self.current = self.menus.get(self.current.play(), None)
			if not self.current:
				break

Calculator().play()

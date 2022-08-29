import os
import csv
import sqlite3


class Menu:
	def __init__(self):
		self.main_content = ['MAIN MENU',
				'0 Exit',
				'1 CRUD operations',
				'2 Show top ten companies by criteria']
		self.crud_content = ['CRUD MENU',
				'0 Back',
				'1 Create a company',
				'2 Read a company',
				'3 Update a company',
				'4 Delete a company',
				'5 List all companies']
		self.top_ten_content = ['TOP TEN MENU',
				'0 Back',
				'1 List by ND/EBITDA',
				'2 List by ROE',
				'3 List by ROA']
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
		self.db_file = 'investor.db'

	def show(self, _option):
		d_options = {'main': self.main_content,
					'crud': self.crud_content,
					'top_ten': self.top_ten_content}
		print('\n'.join(d_options.get(_option, [""])), end='\n\n')
		return input("Enter an option: ")

	def play(self):
		print("Welcome to the Investor Program!", end='\n\n')
		while True:
			try:
				val = int(self.show('main'))
				if val == 0:
					print("Have a nice day!")
					break
				elif val == 1:
					print()
					val1 = int(self.show('crud'))
				elif val == 2:
					print()
					val2 = int(self.show('top_ten'))
				else:
					raise ValueError
				print("Not implemented!", end='\n\n')
			except ValueError:
				print("Invalid option!", end='\n\n')

	def create_table(self, table, cursor):
		with open(self.tablenames[table]) as file:
			freader = csv.reader(file, delimiter=',')
			head = next(freader)
			command = f"create table if not exists {table} ("
			command += ", ".join(f"{name} {self.table_details[table][name]}" for name in head) + ");"
			cursor.execute(command)
			values = [tuple(value if value else None for value in line) for line in freader]
			command = f"insert into {table} values (" + ", ".join("?" for _ in head) + ")"
			cursor.executemany(command, values)
			self.connection.commit()

	def store_it(self):
		if os.path.exists(self.db_file):
			os.remove(self.db_file)
		self.connection = sqlite3.connect(self.db_file)
		cursor = self.connection.cursor()
		for table in self.tablenames:
			self.create_table(table, cursor)
		cursor.close()
		self.connection.close()
		print("Database created successfully!")


Menu().play()

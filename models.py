class User(object):
	def __init__(self, username=None, password=None):
		self.username = username
		self.password = password
	
	def setUsername(self, username):
		self.username = username
	
	def setPassword(self, password):
		self.password = password
	
	def Autentikasi(self):
		import sqlite3, os
		dataName = os.getcwd() + '/login.db'
		con = sqlite3.connect(dataName)
		cur = con.cursor()
		cur.execute("SELECT COUNT(*) FROM login WHERE username='%s' and password='%s' " % (self.username, self.password))
		n = (cur.fetchone())[0]
		cur.close()
		con.close()
		return True if n==1 else False
		
		
from app import db, User
import datetime

username = "admin"
password = "admin123"
level = "Admin"
jam_masuk = datetime.datetime.now()
db.session.add(User(username,password,level,jam_masuk))
db.session.commit()

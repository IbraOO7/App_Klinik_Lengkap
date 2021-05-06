from flask import Flask, render_template, request, redirect, url_for, session, logging, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import InputRequired, Length, URL
from flask_bootstrap import Bootstrap
from flask_bcrypt import Bcrypt
from functools import wraps
import os, sys, datetime
from models import User
from sqlalchemy import func, or_
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'th1simp0rt4ntk3y$'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/klinik'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

class LoginForm(FlaskForm):
    username = StringField('', validators=[InputRequired()], render_kw={'autofocus':True, 'placeholder':'Username'})
    password = PasswordField('', validators=[InputRequired()], render_kw={'autofocus':True, 'placeholder':'Password'})
    level = SelectField('', validators=[InputRequired()], choices=[('Admin','Admin'),('Dokter','Dokter'),('Administrasi','Administrasi')])

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.Text, nullable=False)
    level = db.Column(db.String(100))
    jam_masuk = db.Column(db.String(100))
    usernya = db.relationship('Pasien', backref=db.backref('user', lazy=True))
    
    def __init__(self,username,password,level,jam_masuk):
        self.username = username
        if password != '':
            self.password = bcrypt.generate_password_hash(password).decode('UTF-8')
        self.level = level
        self.jam_masuk = jam_masuk
                
class Obat(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        namaobat = db.Column(db.String(200))
        jenisobat = db.Column(db.String(100))
        harga_beli = db.Column(db.Integer)
        harga_jual = db.Column(db.Integer)
        suplier_id = db.Column(db.Integer, db.ForeignKey('suplier.id'))
        kondisi = db.Column(db.String(100), default="Baik")

        def __init__(self,namaobat,jenisobat,harga_beli,harga_jual,suplier_id,kondisi):
                self.namaobat = namaobat
                self.jenisobat = jenisobat
                self.harga_beli = harga_beli
                self.harga_jual = harga_jual
                self.suplier_id = suplier_id
                self.kondisi = kondisi
	
class Suplier(db.Model):
	__tablename__ = 'suplier'
	id = db.Column(db.Integer, primary_key=True)
	perusahaan = db.Column(db.String(110), unique=False)
	kontak = db.Column(db.String(100))
	alamat = db.Column(db.Text)
	supliernya = db.relationship('Obat', backref=db.backref('suplier', lazy=True))
	
	def __init__(self, perusahaan, kontak, alamat):
		self.perusahaan = perusahaan
		self.kontak = kontak
		self.alamat = alamat
	

class Dokter(db.Model):
    __tablename__ = 'dokter'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(120), unique=True)
    jadwal = db.Column(db.Text)
    
    def __init__(self, nama, jadwal):
        self.nama = nama
        self.jadwal = jadwal
		
	
class Pasien(db.Model):
    __tablename__ = 'pasien'
    id = db.Column(db.BigInteger, primary_key=True)
    nama = db.Column(db.String(120))
    keluhan = db.Column(db.String(100))
    keterangan = db.Column(db.String(100))
    resep = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    daftar_id = db.Column(db.BigInteger, db.ForeignKey('daftar.id'))
    tanggal = db.Column(db.String(100))
    
    def __init__(self, nama, keluhan, keterangan, resep, user_id, daftar_id, tanggal):
        self.nama = nama
        self.keluhan = keluhan
        self.keterangan = keterangan
        self.resep = resep
        self.user_id = user_id
        self.daftar_id = daftar_id
        self.tanggal = tanggal

class Daftar(db.Model):
    tablename = 'daftar'
    id = db.Column(db.BigInteger, primary_key=True)
    nama = db.Column(db.String(200))
    tl = db.Column(db.String(100))
    tg_lahir = db.Column(db.String(200))
    jk = db.Column(db.String(100))
    status = db.Column(db.String(100))
    profesi = db.Column(db.String(100))
    alamat = db.Column(db.Text)
    keterangan = db.Column(db.String(100), default="Diproses")
    daftarnya = db.relationship('Pasien', backref=db.backref('daftar', lazy=True))
    
    def __init__(self,nama,tl,tg_lahir,jk,status,profesi,alamat,keterangan):
        self.nama = nama
        self.tl = tl
        self.tg_lahir = tg_lahir
        self.jk = jk
        self.status = status
        self.profesi = profesi
        self.alamat = alamat
        self.status = status
        self.keterangan = keterangan

db.create_all()

def is_logged_in(f):
	@wraps(f)
	def kunci(*args, **kwargs):
		if 'pengguna' in session:
			return f(*args, **kwargs)
		else:
			return redirect(url_for('login'))
	return kunci
	
@app.route('/')
def index():
    if session.get('pengguna') == True:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if session.get('pengguna') == True:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data) and user.level == form.level.data:
                session['pengguna'] = True
                session['username'] = user.username
                session['level'] = form.level.data
                session['id'] = user.id
                return redirect(url_for('dashboard'))
        pesan = 'Username atau Password anda salah'
        return render_template('login.html', pesan=pesan, form=form)
    return render_template('login.html', form=form)
	
@app.route('/dashboard')
@is_logged_in
def dashboard():
    row = db.session.query(Daftar).count()
    row1 = db.session.query(Dokter).count()
    row2 = db.session.query(func.sum(Obat.harga_jual)).filter_by(kondisi="Rusak").scalar()
    row3 = db.session.query(User).count()
    row4 = db.session.query(func.sum(Obat.harga_jual)).scalar()
    return render_template('dashboard.html',row=row,row1=row1,row2=row2,row3=row3,row4=row4)

@app.route('/apotek')
@is_logged_in
def obat():
    return render_template('apotek.html', data=Obat.query.all(), suplier=Suplier.query.all())

@app.route('/tambahobat', methods=['GET','POST'])
def tambahobat():
    if request.method == 'POST':
        namaobat = request.form.get('namaobat')
        jenisobat = request.form.get('jenisobat')
        harga_beli = request.form.get('harga_beli')
        harga_jual = request.form.get('harga_jual')
        suplier_id = request.form.get('suplier_id')
        kondisi = request.form.get('kondisi')
        data = Obat(namaobat,jenisobat,harga_beli,harga_jual,suplier_id,kondisi)
        db.session.add(data)
        db.session.commit()
        return jsonify({'success': True})

@app.route('/editobat/<id>', methods=['GET','POST'])
def editabsen(id):
    data = Obat.query.filter_by(id=id).first()
    if request.method == 'POST':
        data.namaobat = request.form.get('namaobat')
        data.jenisobat = request.form.get('jenisobat')
        data.harga_beli = request.form.get('harga_beli')
        data.harga_jual = request.form.get('harga_jual')
        data.suplier_id = request.form.get('suplier_id')
        data.kondisi = request.form.get('kondisi')
        db.session.add(data)
        db.session.commit()
        return redirect(request.referrer)

@app.route('/hapusobat/<id>', methods=['GET','POST'])
def hapusabsen(id):
	data = Obat.query.filter_by(id=id).first()
	db.session.delete(data)
	db.session.commit()
	return redirect(url_for('obat'))

@app.route('/suplier')
def suplier():
	return render_template('suplier.html', data=Suplier.query.all())

@app.route('/tambahsuplier', methods=['GET','POST'])
def tambahsuplier():
    if request.method == 'POST':
        perusahaan = request.form.get('perusahaan')
        kontak = request.form.get('kontak')
        alamat = request.form.get('alamat')
        data = Suplier(perusahaan,kontak,alamat)
        db.session.add(data)
        db.session.commit()
        return jsonify({"success":True})
    else:
        return redirect(request.referrer)
		

@app.route('/editsuplier/<id>', methods=['GET','POST'])
def editsuplier(id):
	data = Suplier.query.filter_by(id=id).first()
	if request.method == 'POST':
		data.perusahaan = request.form['perusahaan']
		data.kontak = request.form['kontak']
		data.alamat = request.form['alamat']
		db.session.add(data)
		db.session.commit()
		return redirect(request.referrer)

@app.route('/hapus_suplier/<id>', methods=['GET','POST'])
def hapus_suplier(id):
	data = Suplier.query.filter_by(id=id).first()
	db.session.delete(data)
	db.session.commit()
	return redirect(url_for('suplier'))

@app.route('/dokter')
def dokter():
	return render_template('dokter.html', data=Dokter.query.all())

@app.route('/tambahdokter', methods=['GET','POST'])
def tambahdokter():
    if request.method == 'POST':
        nama = request.form.get('nama')
        jadwal = request.form.get('jadwal')
        data = Dokter(nama,jadwal)
        db.session.add(data)
        db.session.commit()
        return jsonify({'success':True})

@app.route('/editdokter/<id>', methods=['GET','POST'])
def editdokter(id):
    data = Dokter.query.filter_by(id=id).first()
    if request.method == 'POST':
        data.nama = request.form['nama']
        data.jadwal = request.form['jadwal']
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('dokter'))

@app.route('/hapusdokter/<id>', methods=['GET','POST'])
def hapusdokter(id):
	data = Dokter.query.filter_by(id=id).first()
	db.session.delete(data)
	db.session.commit()
	return redirect(request.referrer)

@app.route('/pasien')
def pasien():
	return render_template('pasien.html', data=Daftar.query.all())

@app.route('/tambah_daftar', methods=['GET','POST'])
def tambah_daftar():
    if request.method == 'POST':
        nama = request.form.get('nama')
        tl = request.form.get('tempat')
        tg_lahir = request.form.get('tg_lahir')
        jk = request.form.get('jk')
        status = request.form.get('status')
        profesi = request.form.get('profesi')
        alamat = request.form.get('alamat')
        keterangan = request.form.get('keterangan')
        data = Daftar(nama,tl,tg_lahir,jk,status,profesi,alamat,keterangan)
        db.session.add(data)
        db.session.commit()
        return jsonify({"success":True})
    else:
        return redirect(url_for('pasien'))

@app.route('/edit_daftar/<id>', methods=['GET','POST'])
def edit_daftar(id):
	data = Daftar.query.filter_by(id=id).first()
	if request.method == 'POST':
		data.nama = request.form.get('nama')
		data.tl = request.form.get('tl')
		data.tg_lahir = request.form.get('tg_lahir')
		data.jk = request.form.get('jk')
		data.status = request.form.get('status')
		data.profesi = request.form.get('profesi')
		data.alamat = request.form.get('alamat')
		db.session.add(data)
		db.session.commit()
		return redirect(request.referrer)

@app.route('/tangani_pasien')
def tangani_pasien():
	return render_template('tangani.html', data=Daftar.query.filter_by(keterangan="Diproses").all())

@app.route('/tambahpasien/<id>', methods=['GET','POST'])
def tambahpasien(id):
    data = Daftar.query.filter_by(id=id).first()
    if request.method == 'POST':
        nama = request.form.get('nama')
        keluhan = request.form.get('keluhan')
        resep = request.form.get('resep')
        keterangan = request.form.get('keterangan')
        daftar_id = request.form.get('daftar_id')
        user_id = request.form.get('user_id')
        tanggal = datetime.datetime.now().strftime("%d %B %Y Jam %H:%M:%S")
        data.keterangan = "Selesai"
        db.session.add(data)
        db.session.commit()
        db.session.add(Pasien(nama,keluhan,keterangan,resep,user_id,daftar_id,tanggal))
        db.session.commit()
        return jsonify({'success':True})

@app.route('/editpasien/<id>', methods=['GET','POST'])
def editpasien(id):
    data = Pasien.query.filter_by(id=id).first()
    if request.method == 'POST':
        data.nama = request.form['nama']
        data.keluhan = request.form['keluhan']
        data.resep = request.form['resep']
        data.keterangan = request.form['keterangan']
        data.daftar_id = request.form['daftar_id']
        db.session.add(data)
        db.session.commit()
        return jsonify({'success':True})

@app.route('/kelola_user')
@is_logged_in
def kelola_user():
    user = User.query.all()
    return render_template('user.html', user=user)

@app.route('/tambahuser', methods=['GET','POST'])
@is_logged_in
def tambahuser():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        level = request.form.get('level')
        jam_masuk = datetime.datetime.now()
        db.session.add(User(username,password,level,jam_masuk))
        db.session.commit()
        return jsonify({'success':True})

@app.route('/edituser/<id>', methods=['GET','POST'])
@is_logged_in
def edituser(id):
    data = User.query.filter_by(id=id).first()
    if request.method == "POST":
        data.username = request.form.get('username')
        if data.password != '':
            data.password =  bcrypt.generate_password_hash(request.form.get('password')).decode('UTF-8')
        data.level = request.form.get('level')
        db.session.add(data)
        db.session.commit()
        return redirect(request.referrer)

@app.route('/hapususer/<id>', methods=['GET','POST'])
@is_logged_in
def hapususer(id):
    data = User.query.filter_by(id=id).first()
    db.session.delete(data)
    db.session.commit()
    return redirect(request.referrer)

@app.route('/laporan')
@is_logged_in
def laporan():
    return render_template('laporan.html')

@app.route('/backup', methods=['GET','POST'])
@is_logged_in
def backup():
    if request.method == 'POST':
        keyword = request.form['q']
        sv = "%{0}%".format(keyword)
        caridata = Pasien.query.join(User, Pasien.user_id == User.id).filter(or_(Pasien.tanggal.like(sv))).all()
        return render_template('laporan.html', caridata=caridata)
    else:
        flash('Data tidak di temukan')
        return redirect(request.referrer)
	
@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	return redirect(url_for('login'))
	
if __name__ == '__main__':
	app.run(debug=True, threaded=True)

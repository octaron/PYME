import os
from flask import Flask,flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime as dt
from datetime import datetime, timedelta, date
import pytz
import sqlite3
from flask_login import LoginManager
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from wtforms import ValidationError,StringField, IntegerField, SubmitField, IntegerField, FloatField, SelectField, RadioField,TextAreaField,SelectMultipleField,PasswordField

login_manager=LoginManager()

# Configuración de la base de datos:
basedir=os.path.abspath(os.path.dirname(__file__))


app=Flask(__name__)
app.config['SECRET_KEY'] = 'PYME'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
#Conectamos la base de datos (db) con la aplicación (app) para realizar las migraciones (Migrate(app,db))
Migrate(app,db)

login_manager.init_app(app)
login_manager.login_view='login'

################################################ MODELOS:
class Secciones(db.Model):
    __tablename__='secciones'

    id=db.Column(db.Integer,primary_key=True)
    sec=db.Column(db.String(90))
    puntos=db.Column(db.Float)

    def __init__(self,sec,puntos):
        self.sec=sec.strip()
        self.puntos=puntos

    def __repr__(self):
        return f"Se dio de alta una nueva sección: {self.sec}"

class Factores(db.Model):
    __tablename__='factores'

    id=db.Column(db.Integer,primary_key=True)
    sec_id= db.Column(db.Integer)
    fac=db.Column(db.String(120))
    desc=db.Column(db.Text)
    puntos=db.Column(db.Float)

    def __init__(self,sec_id,fac,desc,puntos):
        self.sec_id=sec_id
        self.fac=fac
        self.desc=desc
        self.puntos=puntos

    def __repr__(self):
        return f"Se dio de alta un factor o reactivo nuevo: {self.fac}"

    def checar_fac(self,sec_id,fac):
        conexion=sqlite3.connect("data.sqlite")
        cursor=conexion.cursor()
        cursor.execute("SELECT * FROM Factores WHERE sec_id={} AND fac='{}' ".format(sec_id,fac))
        r=cursor.fetchall()
        try:
            x=r[0][1]
        except IndexError:
            return True
        else:
            x='El siguiente factor ya se encuentra en la sección: {}'.format(fac)
            mensaje=[False,x]
            flash(mensaje)
            return False
class Inscripciones(db.Model):
    __tablename__='inscripciones'

    id=db.Column(db.Integer,primary_key=True)
    tipo=db.Column(db.Integer)
    nombre=db.Column(db.String(120))
    rfc=db.Column(db.String(13))
    curp=db.Column(db.String(18))
    fec_nac=db.Column(db.Date)
    cve_ent=db.Column(db.String(2))
    cve_mun=db.Column(db.String(3))
    dir=db.Column(db.String(120))
    tel=db.Column(db.String(10))
    email=db.Column(db.String(90))
    usuario=db.Column(db.Integer)

    def __init__(self,tipo,nombre,rfc,curp,fec_nac,cve_ent,cve_mun,dir,tel,email):
        self.tipo=tipo
        self.nombre=nombre
        self.rfc=rfc
        self.curp=curp
        fec_nac=datetime.strptime(fec_nac,'%Y-%m-%d')
        self.fec_nac=dt.date(fec_nac.year,fec_nac.month,fec_nac.day)
        self.cve_ent=cve_ent
        self.cve_mun=cve_mun
        self.dir=dir
        self.tel=tel
        self.email=email

    def __repr__(self):
        return "Inscripción realizada correctamente"

    def checar_rfc(self,rfc,curp):
        conexion=sqlite3.connect("data.sqlite")
        cursor=conexion.cursor()
        cursor.execute("SELECT * FROM Inscripciones WHERE rfc='{}' OR curp='{}'".format(rfc,curp))
        r=cursor.fetchall()
        try:
            x=r[0][1]
        except IndexError:
            return True
        else:
            x='El RFC o CURP ya se encuentran dados de alta'
            mensaje=[False,x]
            flash(mensaje)
            return False




class Respuestas(db.Model):
    __tablename__='respuestas'

    id=db.Column(db.Integer,primary_key=True)
    fac_id=db.Column(db.Integer)
    resp=db.Column(db.String(120))
    puntos=db.Column(db.Float)

    def __init__(self,fac_id,resp,puntos):
        self.fac_id=fac_id
        self.resp=resp.strip()
        self.puntos=puntos

    def __repr__(self):
        return f"Se dio de alta una nueva respuesta"

    def checar_resp(self,fac,resp):
        conexion=sqlite3.connect("data.sqlite")
        cursor=conexion.cursor()
        cursor.execute("SELECT * FROM Respuestas WHERE fac_id='{}' AND resp='{}' ".format(fac,resp))
        r=cursor.fetchall()
        try:
            x=r[0][1]
        except IndexError:
            return True
        else:
            x='La respuesta {} ya se encuentra en el menú del factor {}'.format(resp,fac)
            mensaje=[False,x]
            flash(mensaje)
            return False



@login_manager.user_loader
def load_user(usuario_id):
    return Usuarios.query.get(usuario_id)

class Usuarios(db.Model,UserMixin):

    __tablename__='usuarios'

    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(64),unique=True,index=True)
    usuario=db.Column(db.String(64))
    password_hash=db.Column(db.String(128))
    perfil=db.Column(db.String(64))


    def __init__(self,email,usuario,password,perfil='Básico'):
        self.email=email
        self.usuario=usuario
        self.password_hash=generate_password_hash(password)
        self.perfil=perfil


    def __repr__(self):
        return f"El usuario {self.usuario} fue creado correctamente"

    #Método para revisar contraseñas:

    def checar_password(self,password):
        return check_password_hash(self.password_hash,password)

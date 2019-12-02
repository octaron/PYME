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
nombre_BD='MiPYMEBD.sqlite'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, nombre_BD)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
#Conectamos la base de datos (db) con la aplicación (app) para realizar las migraciones (Migrate(app,db))
Migrate(app,db)

login_manager.init_app(app)
login_manager.login_view='login'

################################################ MODELOS:
class Sepomex(db.Model):
    __tablename__='sepomex'

    id=db.Column(db.Integer,primary_key=True)
    d_codigo=db.Column(db.String(5))
    d_asenta=db.Column(db.String(80))
    d_tipo_asenta=db.Column(db.String(60))
    D_mnpio=db.Column(db.String(60))
    d_estado=db.Column(db.String(80))
    d_ciudad=db.Column(db.String(80))
    c_estado=db.Column(db.String(2))
    c_oficina=db.Column(db.String(5))
    c_tipo_asenta=db.Column(db.String(2))
    c_mnpio=db.Column(db.String(3))
    id_asenta_cpcons=db.Column(db.String(4))
    d_zona=db.Column(db.String(10))
    c_cve_ciudad=db.Column(db.String(2))
    xxx=db.Column(db.Integer)

    def __init__(self,d_codigo,d_asenta,d_tipo_asenta,D_mnpio,d_estado,d_ciudad,c_estado,c_oficina,c_tipo_asenta,c_mnpio,id_asenta_cpcons,d_zona,c_cve_ciudad):
        self.d_codigo=d_codigo
        self.d_asenta=d_asenta
        self.d_tipo_asenta=d_tipo_asenta
        self.D_mnpio=D_mnpio
        self.d_estado=d_estado
        self.d_ciudad=d_ciudad
        self.c_estado=c_estado
        self.c_oficina=c_oficina
        self.c_tipo_asenta=c_tipo_asenta
        self.c_mnpio=c_mnpio
        self.id_asenta_cpcons=id_asenta_cpcons
        self.d_zona=d_zona
        self.c_cve_ciudad=c_cve_ciudad

    def __repr__(self):
        return f"Se dio de alta un asentamiento nuevo: {self.d_asenta}"

    def checar_asentamiento(self,d_codigo,id_asenta_cpcons):
        conexion=sqlite3.connect("MiPYMEBD.sqlite")
        cursor=conexion.cursor()
        cursor.execute("SELECT d_codigo,id_asenta_cpcons FROM Sepomex WHERE d_codigo={} AND id_asenta_cpcons='{}' ".format(d_codigo,id_asenta_cpcons))
        r=cursor.fetchall()
        try:
            x=r[0][1]
        except IndexError:
            return True
        else:
            #x='El siguiente factor ya se encuentra en la sección: {}'.format(fac)
            #mensaje=[False,x]
            #flash(mensaje)
            return False


class Solicitudes(db.Model):
    __tablename__='solicitudes'

    id=db.Column(db.Integer,primary_key=True)
    id_usuario=db.Column(db.Integer)
    umbral_k=db.Column(db.Integer)
    usuario=db.Column(db.String(120))
    ap_paterno=db.Column(db.String(120))
    ap_materno=db.Column(db.String(120))
    nombres=db.Column(db.String(120))
    curp=db.Column(db.String(18))
    rfc=db.Column(db.String(13))
    nss=db.Column(db.String(11))
    fec_nac=db.Column(db.Date)
    edo_civil=db.Column(db.String(2))
    c_estado=db.Column(db.String(2))
    c_mnpio=db.Column(db.String(3))

    id_asenta_cpcons=db.Column(db.String(4))
    calle=db.Column(db.String(120))
    n_ext=db.Column(db.String(5))
    n_int=db.Column(db.String(5))
    tel=db.Column(db.String(10))
    email=db.Column(db.String(120))
    fec_solicitud=db.Column(db.Date)
    fec_eval=db.Column(db.Date)
    estatus=db.Column(db.String(20))
    csc = db.Column(db.Integer)
    ip=db.Column(db.String(120))

    def __init__(self,id_usuario,umbral_k,usuario,ap_paterno,ap_materno,nombres,curp,rfc,nss,fec_nac,edo_civil,c_estado,c_mnpio,id_asenta_cpcons,calle,n_ext,n_int,tel,email,ip):

        self.id_usuario=id_usuario
        self.umbral_k=umbral_k
        self.usuario=usuario
        self.ap_paterno=ap_paterno.strip().upper()
        self.ap_materno=ap_materno.strip().upper()
        self.nombres=nombres.strip().upper()
        self.curp=curp.strip().upper()
        self.rfc=rfc.strip().upper()
        self.nss=nss.strip().upper()

        fec_nac=datetime.strptime(fec_nac,'%Y-%m-%d')
        self.fec_nac=dt.date(fec_nac.year,fec_nac.month,fec_nac.day)

        self.edo_civil=edo_civil
        self.c_estado=c_estado
        self.c_mnpio=c_mnpio

        self.id_asenta_cpcons=id_asenta_cpcons
        self.calle=calle.strip().upper()
        self.n_ext=n_ext.strip().upper()
        self.n_int=n_int.strip().upper()
        self.tel=tel
        self.email=email

        self.fec_solicitud=(datetime.now(tz=pytz.UTC) - timedelta(hours=5))
        #self.fec_insc=dt.date(fi.year,fi.month,fi.day)
        self.estatus='En evaluación'
        
        self.ip= ip
        

    def __repr__(self):
        return "Solicitud registrada correctamente"


#################################################
class Umbral_k(db.Model):
    __tablename__='umbral'
    
    id=db.Column(db.Integer,primary_key=True)
    umbral_k=db.Column(db.Float)
    
    def __init__(self, umbral_k):
        self.umbral_k= umbral_k

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
        conexion=sqlite3.connect(nombre_BD)
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
        conexion=sqlite3.connect(nombre_BD)
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

class Csc(db.Model):

    __tablename__='csc'

    id=db.Column(db.Integer,primary_key=True)
    id_sec=db.Column(db.Integer)
    id_fac=db.Column(db.Integer)
    id_resp=db.Column(db.Integer)
    id_solicitud=db.Column(db.Integer)
    id_usuario=db.Column(db.Integer)
    

    def __init__(self,id_sec,id_fac,id_resp,id_solicitud,id_usuario):
        self.id_sec=id_sec
        self.id_fac=id_fac
        self.id_resp=id_resp
        self.id_solicitud=id_solicitud
        self.id_usuario=id_usuario
    
    def __repr__(self):
        return f"La respuesta {self.id_resp} fue registrada correctamente"


@login_manager.user_loader
def load_user(usuario_id):
    return Usuarios.query.get(usuario_id)

class Usuarios(db.Model,UserMixin):

    __tablename__='usuarios'

    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(64),unique=True,index=True)
    usuario=db.Column(db.String(120))
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

class Config_email_inst(db.Model):

    __tablename__='config_email_inst'

    id=db.Column(db.Integer,primary_key=True)
    #nombre=db.Column(db.String)
    email=db.Column(db.String(64))
    password=db.Column(db.String)

    def __init__(self,email,password):
        self.email=email
        self.password=password

class Documentos(db.Model):

    __tablename__='documentos'
    id=db.Column(db.Integer,primary_key=True)
    documento=db.Column(db.String(20))
    tipo=db.Column(db.String(10))


    def __init__(self,documento,tipo):
        self.documento=documento
        self.tipo=tipo


    def checar_cat_doc(self,documento):
        conexion=sqlite3.connect(nombre_BD)
        cursor=conexion.cursor()
        cursor.execute("SELECT * FROM Documentos WHERE documento='{}' ".format(documento))
        r=cursor.fetchall()
        try:
            x=r[0][1]
        except IndexError:
            return True
        else:
            x='El documento {} ya se encuentra en el catálogo. No es necesario darlo de alta otra vez'.format(documento)
            mensaje=[False,x]
            flash(mensaje)
            return False




class Entrega_documentos(db.Model):

    __tablename__='entrega_documentos'

    id=db.Column(db.Integer,primary_key=True)
    documento=db.Column(db.String(40))
    entregado=db.Column(db.Boolean)
    rfc=db.Column(db.String(13))
    id_usuario=db.Column(db.Integer)
    fec_entrega=db.Column(db.Date)
    id_solicitud=db.Column(db.Integer)

    def __init__(self,documento,entregado,rfc,id_usuario,fec_entrega,id_solicitud):
        self.documento=documento
        self.entregado=entregado
        self.rfc=rfc
        self.id_usuario=id_usuario
        self.fec_entrega=fec_entrega
        self.id_solicitud=id_solicitud



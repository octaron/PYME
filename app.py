from modelos import *
import sqlite3
import datetime as dt
from datetime import datetime, timedelta
import pytz
from forms import *
from flask import Flask,render_template,url_for,redirect,flash,abort,request,stream_with_context
from flask_login import login_user,login_required,logout_user,current_user
from autoemail import *
import csv
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response
from io import StringIO
from admin_archivos import *
import pandas as pd
import numpy as np
from crea_solicitud import *
from flask import make_response
from flask import request
import ast

#CREANDO TABLAS:
db.create_all()
nombre_BD='MiPYMEBD.sqlite'
#####
#VISTAS:

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/acceso_denegado')
@login_required

def acceso_denegado():
    return render_template('acceso_denegado.html')

@app.route('/bienvenida')
#@login_required:Decorador que condiciona el acceso a la vista al ingreso de contraseña
@login_required
def bienvenida_usuario():
    return render_template('bienvenida_usuario.html')

@app.route('/salir')
@login_required
def salir():
    logout_user()
    #x='Saliste del sistema.'
    #mensaje=[True,x]

    #flash(mensaje)
    return redirect(url_for('inicio'))

@app.route('/entrar',methods=['GET','POST'])
def entrar():

    entrar=Login_forma()
    if entrar.validate_on_submit():
        usuario=Usuarios.query.filter_by(email=entrar.email.data).first()

        if usuario is None:
            x=[False,'Este usuario no se encuentra registrado. Revise su información o regístrese.']
            flash(x)
        else:
            if usuario.checar_password(entrar.password.data) and usuario is not None:
                login_user(usuario)
                next=request.args.get('next')

                if next==None or not next[0]=='/':
                    next=url_for('bienvenida_usuario')


                return redirect(next)

            else:
                x=[False,'La contraseña es incorrecta.']
                flash(x)

    return render_template('ingresar.html',entrar=entrar)

@app.route('/cambiar_password',methods=['GET','POST'])
def cambiar_password():
    nvo=Cambiar_password_forma()

    if nvo.validate_on_submit():
        try:
            nvo.revisar_email(nvo.email.data)
        except ValidationError:
            x='Este correo no se ha registrado. Favor de revisarlo.'
            mensaje=[False,x]
            flash(mensaje)

        else:

            conexion=sqlite3.connect(nombre_BD)
            cursor=conexion.cursor()
            cursor.execute("SELECT id,usuario,password_hash FROM usuarios WHERE email='{}'".format(nvo.email.data))
            r=cursor.fetchall()
            id=r[0][0]
            usuario=r[0][1]
            password_hash=r[0][2]
            #Si la contraseña proporcionada antes coincide con la almacenada en la BD, entonces...
            if not check_password_hash(password_hash,nvo.ant_password.data):
                x='La contraseña proporcionada no es corecta'
                mensaje=[False,x]
                flash(mensaje)

            else:
                password_hash=generate_password_hash(nvo.nvo_password.data)
                conexion=sqlite3.connect(nombre_BD)
                cursor=conexion.cursor()
                cursor.execute ("UPDATE usuarios SET password_hash='{}' WHERE id={}".format(password_hash,id))
                conexion.commit()
                conexion.close()
                x='Tu contraseña ha sido cambiada'
                mensaje=[True,x]
                flash(mensaje)
                return redirect(url_for('entrar'))

    return render_template('cambiar_password.html',nvo=nvo)

@app.route('/recuperar_password',methods=['GET','POST'])
def recuperar_password():

    recu=Recuperar_password_forma()

    if recu.validate_on_submit():
        try:
            recu.revisar_email(recu.email.data)
        except ValidationError:
            x='Este correo no se ha registrado. Favor de revisarlo.'
            mensaje=[False,x]
            flash(mensaje)

        else:
            conexion=sqlite3.connect(nombre_BD)
            cursor=conexion.cursor()
            cursor.execute("SELECT id,usuario,password_hash FROM usuarios WHERE email='{}'".format(recu.email.data))
            r=cursor.fetchall()
            id=r[0][0]
            usuario=r[0][1]
            #Para simplificar, asignamos como contraseña temporal los últimos 8 dígitos del "password_hash" alojado en BD
            temp_password=r[0][2][-8:]
            #Reemplazamos la contraseña anterior con la contraseña temporal:
            password_hash=generate_password_hash(temp_password)
            cursor.execute ("UPDATE usuarios SET password_hash='{}' WHERE id={}".format(password_hash,id))
            conexion.commit()

            cursor.execute("SELECT * FROM config_email_inst WHERE id=1")
            r=cursor.fetchall()
            remitente=r[0][1]
            password=r[0][2]

            conexion.close()

            destinatario=recu.email.data
            mensaje='Tu contraseña temporal es: '+temp_password+'. Te recomendamos cambiarla.'
            titulo='Restitución de contraseña de SI_DGACyG'

            correo=Auto_email()
            try:
                correo.enviar_correo(destinatario,remitente,password,mensaje,titulo)
            except ValidationError:
                x='La contraseña no pudo enviarse. Revisa tu conexión a internet'
                mensaje=[False,x]
                flash(mensaje)
            else:
                x='La contraseña ha sido enviada al correo con el que te registraste. Te recomendamos cambiarla'
                mensaje=[True,x]
                flash(mensaje)

    return render_template('recuperar_password.html',recu=recu)


@app.route('/registro',methods=['GET','POST'])
def registro():
    registro=Registro_forma()
    #registro.id_inst.choices=lista_inst_ubd

    if registro.validate_on_submit():

        try:
            registro.checar_email(registro.email.data)
        except ValidationError:
            x='Este correo ya fue registrado. Proporciona otro o recupera tu contraseña.'
            mensaje=[False,x]
            flash(mensaje)

        else:
            try:
                registro.checar_usuario(registro.usuario.data)
            except ValidationError:
                x='Este usuario ya fue registrado. Proporciona otro o recupera tu contraseña.'
                mensaje=[False,x]
                flash(mensaje)

            else:
                usuario=Usuarios(email=registro.email.data.strip(),usuario=registro.usuario.data.strip(),password=registro.password.data.strip())
                db.session.add(usuario)
                db.session.commit()


                #Por construcción el primer usuario registrado será un administrador del sistema
                if usuario.id==1:
                    usuario.perfil='Administrador'
                    db.session.commit()

                #db.session.add(usuario)
                #db.session.commit()

                x='Gracias por registrarte. Ahora puedes ingresar.'
                mensaje=[True,x]
                flash(mensaje)
                return redirect(url_for('entrar'))

    return render_template('registro.html',registro=registro)

#############
@app.route('/agregar_sepomex',methods=['GET','POST'])
@login_required

def agregar_sepomex():

    forma=Agregar_sepomex_forma()
    accion=forma.accion.data

    if accion=="Agregar":

        if forma.validate_on_submit():
            carpeta='sepomex'
            archivo=forma.archivo.data
            x=Subir_archivos()
            x.agregar_archivo(carpeta,archivo)
            sepomex=pd.read_csv(x.destino,delimiter='|',encoding = 'ISO-8859-1')
            sepomex['c_cve_ciudad']=sepomex['c_cve_ciudad'].fillna(0)
            sepomex=sepomex.loc[(sepomex['c_estado']<3) | (sepomex['c_estado']==23)]

            ##Una vez almacenada la información en un DataFrame, se borra del servidor el archivo
            ##recién subido
            os.remove(x.destino)

            for i in sepomex.index:
                d_codigo=str(np.where(sepomex['d_codigo'].loc[i]>9999,str(sepomex['d_codigo'].loc[i]),'0'+str(sepomex['d_codigo'].loc[i])))
                c_estado=str(np.where(sepomex['c_estado'].loc[i]>10,str(sepomex['c_estado'].loc[i]),'0'+str(sepomex['c_estado'].loc[i])))
                c_mnpio=str(np.where(sepomex['c_mnpio'].loc[i]<10,'00'+str(sepomex['c_mnpio'].loc[i]),np.where(sepomex['c_mnpio'].loc[i]<100,'0'+str(sepomex['c_mnpio'].loc[i]),str(sepomex['c_mnpio']))))


                c_cve_ciudad=str(np.where(sepomex['c_cve_ciudad'].loc[i]>10,str(int(sepomex['c_cve_ciudad'].loc[i])),'0'+str(int(sepomex['c_cve_ciudad'].loc[i]))))

                d_asenta=sepomex['d_asenta'].loc[i]
                d_tipo_asenta=sepomex['d_tipo_asenta'].loc[i]
                D_mnpio=sepomex['D_mnpio'].loc[i]
                d_estado=sepomex['d_estado'].loc[i]
                d_ciudad=sepomex['d_ciudad'].loc[i]
                d_CP=str(np.where(sepomex['d_CP'].loc[i]>9999,str(sepomex['d_CP'].loc[i]),'0'+str(sepomex['d_CP'].loc[i])))
                c_oficina=str(np.where(sepomex['c_oficina'].loc[i]>9999,str(sepomex['c_oficina'].loc[i]),'0'+str(sepomex['c_oficina'].loc[i])))
                c_tipo_asenta=str(np.where(sepomex['c_tipo_asenta'].loc[i]>10,str(sepomex['c_tipo_asenta'].loc[i]),'0'+str(sepomex['c_tipo_asenta'].loc[i])))
                id_asenta_cpcons=str(np.where(sepomex['id_asenta_cpcons'].loc[i]<10,'000'+str(sepomex['id_asenta_cpcons'].loc[i]),np.where(sepomex['id_asenta_cpcons'].loc[i]<100,'00'+str(sepomex['id_asenta_cpcons'].loc[i]),np.where(sepomex['id_asenta_cpcons'].loc[i]<1000,'0'+str(sepomex['id_asenta_cpcons'].loc[i]),str(sepomex['id_asenta_cpcons'].loc[i])))))
                d_zona=sepomex['d_zona'].loc[i]


                nuevo_sepomex=Sepomex(d_codigo,d_asenta,d_tipo_asenta,D_mnpio,d_estado,d_ciudad,c_estado,c_oficina,c_tipo_asenta,c_mnpio,id_asenta_cpcons,d_zona,c_cve_ciudad)

                if nuevo_sepomex.checar_asentamiento(d_codigo,id_asenta_cpcons):
                    db.session.add(nuevo_sepomex)
                    db.session.commit()
                    db.session.close
                #x='Se registró un nuevo factor: '+nuevo_sepomex.fac
                #mensaje=[True,x]
                #flash(mensaje)

    elif accion=="Eliminar":

        conexion=sqlite3.connect(nombre_BD)
        cursor=conexion.cursor()
        cursor.execute("DELETE FROM Sepomex")
        conexion.commit()
        conexion.close()

        x='El catálogo de SEPOMEX se eliminó exitosamente'
        mensaje=[True,x]
        flash(mensaje)


    if current_user.perfil!='Administrador':
        return redirect(url_for('acceso_denegado'))
    else:
        return render_template('agregar_sepomex.html', forma=forma)


# Ingresar solicitud:
@app.route('/agregar_solicitud',methods=['GET','POST'])
@login_required

def agregar_solicitud():
    
    forma=Agregar_solicitud_forma()

    #Catálogo estados:
    conexion=sqlite3.connect(nombre_BD)
    cursor=conexion.cursor()
    cursor.execute('SELECT DISTINCT c_estado,d_estado FROM Sepomex')
    l_estados=cursor.fetchall()
    forma.c_estado.choices=l_estados
    c_estado=forma.c_estado.data

    ap_paterno=forma.ap_paterno.data
    ap_materno=forma.ap_materno.data
    nombres=forma.nombres.data
    curp=forma.curp.data
    rfc=forma.rfc.data
    nss=forma.nss.data
    edo_civil=forma.edo_civil.data
    dia_nac=forma.dia_nac.data
    mes_nac=forma.mes_nac.data
    anio_nac=forma.anio_nac.data
    fec_nac=anio_nac+'-'+mes_nac+'-'+dia_nac

    accion=forma.accion.data
    

    if accion=='Modificar':
        conexion=sqlite3.connect(nombre_BD)
        cursor=conexion.cursor()
        cursor.execute('SELECT id,sec FROM Secciones')
        lista_sec=cursor.fetchall()
        #IMPORTANTE: convertir a cadena el identificador de la clase.
        #De lo contrario no funcionará la forma de selección, SelectField
        lista_sec=[(str(id),sec) for id,sec in lista_sec]
        forma.sec_mod.choices=lista_sec
        sec_mod=forma.sec_mod.data


    #Catálogo de municipios:
    conexion=sqlite3.connect(nombre_BD)
    cursor=conexion.cursor()
    cursor.execute("SELECT DISTINCT c_mnpio,D_mnpio FROM Sepomex WHERE c_estado='{}' ".format(c_estado))
    l_mun=cursor.fetchall()
    forma.c_mnpio.choices=l_mun
    c_mnpio=forma.c_mnpio.data

    #Catálogo tipo de asentamientos:
    conexion=sqlite3.connect(nombre_BD)
    cursor=conexion.cursor()
    cursor.execute("SELECT DISTINCT c_tipo_asenta,d_tipo_asenta FROM Sepomex WHERE c_estado='{}' AND c_mnpio='{}' ".format(c_estado,c_mnpio))
    l_tipo_asenta=cursor.fetchall()
    forma.c_tipo_asenta.choices=l_tipo_asenta
    c_tipo_asenta=forma.c_tipo_asenta.data

    #Catálogo de asentamientos:
    conexion=sqlite3.connect(nombre_BD)
    cursor=conexion.cursor()
    cursor.execute("SELECT DISTINCT id_asenta_cpcons,d_asenta FROM Sepomex WHERE c_estado='{}' AND c_mnpio='{}' AND c_tipo_asenta='{}' ".format(c_estado,c_mnpio,c_tipo_asenta))
    l_asenta=cursor.fetchall()
    forma.id_asenta_cpcons.choices=l_asenta
    id_asenta_cpcons=forma.id_asenta_cpcons.data
    
    calle=forma.calle.data
    n_ext=forma.n_ext.data
    n_int=forma.n_int.data
    tel=forma.tel.data
    email=forma.email.data
    
    consulta ='SELECT * FROM umbral'
    umbral=pd.read_sql(consulta,conexion)
    
    if len(umbral)>0:
        umbral_k=umbral['umbral_k'][0]
    else:
        umbral_k=0

    #forma.validate_on_submit()=forma.realizar.data
    if forma.validate_on_submit():
        ip=request.remote_addr
        nueva_solicitud=Solicitudes(current_user.id,umbral_k,current_user.usuario,ap_paterno,ap_materno,nombres,curp,rfc,nss,fec_nac,edo_civil,c_estado,c_mnpio,id_asenta_cpcons,calle,n_ext,n_int,tel,email,ip)
        db.session.add(nueva_solicitud)
        db.session.commit()
        db.session.close
        x='Se registró correctamente la solicitud a nombre de: '+nueva_solicitud.nombres+' '+nueva_solicitud.ap_paterno+' '+nueva_solicitud.ap_materno
        mensaje=[True,x]
        flash(mensaje)

        # #Usamos el mètodo strip() para eliminar espacios en blanco antes y después de la cadena de texto
        # sec=forma.sec.data.strip().upper()
        #
        # try:
        #     forma.checar_sec(sec)
        #
        # except ValidationError:
        #     x='Esta sección ya fue registrada anteriormente.'
        #     mensaje=[False,x]
        #     flash(mensaje)
        #
        # else:
        #     if accion=='Agregar':
        #
        #         m=True
        #         if sec=='':
        #             x='Favor de indicar la sección que desea dar de alta'
        #             m0=[False,x]
        #             flash(m0)
        #             m=False
        #
        #         if forma.puntos.data=='':
        #             x='Favor de indicar el puntaje'
        #             m1=[False,x]
        #             flash(m1)
        #             m=False
        #         else:
        #             try:
        #                 puntos=float(forma.puntos.data)
        #             except ValueError:
        #                 m=False
        #                 x='El puntaje debe ser un número'
        #                 m2=[False,x]
        #                 flash(m2)
        #
        #
        #         if m==True:
        #             puntos=float(forma.puntos.data)
        #
        #             nueva_sec=Secciones(sec,puntos)
        #             db.session.add(nueva_sec)
        #             db.session.commit()
        #             db.session.close
        #             x='Se registró una nueva sección: '+nueva_sec.sec
        #             mensaje=[True,x]
        #             flash(mensaje)
        #
        #
        #     elif accion=='Modificar':
        #
        #         conexion=sqlite3.connect("data.sqlite")
        #         cursor=conexion.cursor()
        #         cursor.execute("SELECT * FROM Secciones WHERE id={}".format(sec_mod))
        #         r=cursor.fetchall()
        #
        #         if sec=="":
        #             sec=r[0][1]
        #
        #         if forma.puntos.data=="":
        #             puntos=r[0][2]
        #         else:
        #             try:
        #                 puntos=float(forma.puntos.data)
        #             except ValueError:
        #                 x='El puntaje debe ser un número'
        #                 m3=[False,x]
        #                 flash(m3)
        #
        #
        #
        #         conexion=sqlite3.connect("data.sqlite")
        #         cursor=conexion.cursor()
        #         cursor.execute("UPDATE Secciones SET sec='{}', puntos={}  WHERE id={}".format(sec,puntos,sec_mod))
        #         conexion.commit()
        #         conexion.close()
        #         x='La sección fue modificada'
        #         mensaje=[True,x]
        #         flash(mensaje)
        #
        #     else:
        #         #Dejo este else para incluír la opción de eliminar en caso de ser necesario
        #         pass


    #if current_user.perfil!='Administrador':
    #    return redirect(url_for('acceso_denegado'))
    #else:
    #    return render_template('agregar_solicitud.html', forma=forma)
    return render_template('agregar_solicitud.html', forma=forma)

#############
##  XXXXX
@app.route('/agregar_documentos_exp',methods=['GET','POST'])
@login_required

def agregar_documentos_exp():
    #La clase Credit_score_card_form se define aquí para que se "actualice" con el número de variables
    # cada vez que el usuario pase por la pàgina /csc. Si se dejara en el archivo forms.py
    #tendría que volverse ejecutar la app.py
    class Agregar_documentos_form(FlaskForm):
        try: 
            solicitud=SelectField('RFC del solicitante del crédito:',choices=[('0','')])

            conexion=sqlite3.connect(nombre_BD)
            consulta="SELECT id,documento FROM Documentos"
            documentos=pd.read_sql(consulta,conexion)
            documentos=documentos.set_index('id')
            for d in documentos.index:
                #locals()['doc_{}'.format(d)]=SelectField(documentos['documento'].loc[d],choices=[('0','')])
                locals()['doc_{}'.format(d)]=FileField(documentos['documento'].loc[d], validators=[FileRequired('Seleccione un archivo en formato PDF, JPG, JPEG o PNG'),FileAllowed(['jpg,png,jpeg,pdf'],'El archivo selecionado no es del tipo PDF,JPG,JPEG,PNG')])

            
        except pd.io.sql.DatabaseError:
            pass

        realizar=SubmitField('Enviar documentos')
        #Aquí termina la clase que construye la forma para adjuntar documentos
#######################################################

    conexion=sqlite3.connect(nombre_BD)
    cursor=conexion.cursor()
    cursor.execute("SELECT id,rfc FROM Solicitudes WHERE id_usuario={} AND estatus='En evaluación' ".format(current_user.id))
    lista_solicitudes=cursor.fetchall()
    #IMPORTANTE: convertir a cadena el identificador de la clase.
    # #De lo contrario no funcionará la forma de selección, SelectField
    lista_solicitudes=[(str(id),rfc) for id,rfc in lista_solicitudes]
            

    consulta="SELECT id FROM Documentos"
    documentos=pd.read_sql(consulta,conexion)
    documentos=documentos.set_index('id')

    forma=Agregar_documentos_form()

    forma.solicitud.choices=lista_solicitudes
    solicitud=forma.solicitud.data

    l_doc=[]
    if forma.realizar.data:
        for d in documentos.index:
            formato='jpg'
            q="l_doc.append(({},forma.doc_{}))\ndoc_{}=forma.doc_{}.data\nx=Subir_archivos()\nx.agregar_doc_digital(documentos['documento'].loc[d],documentos['documento'].loc[d],documentos['documento'].loc[d],300,300,'jpg')".format(d,d,d,d)

            #formato='jpg'
            #ine=forma.ine.data
            #x=Subir_archivos()
            #x.agregar_doc_digital(carpeta,ine,nvo_nombre,ancho,alto,formato)

            exec(q)
            if len(documentos.index)==i:
                
                x='Los documentos se registraron correctamente'
                mensaje=[True,x]
                flash(mensaje)
                
                
    return render_template('agregar_documentos_exp.html', forma=forma,l_doc=l_doc)
### XXXXXXXXXXXXX
#############
@app.route('/agregar_documentos',methods=['GET','POST'])
@login_required

def agregar_documentos():

    forma=Agregar_documentos_forma()
    
    if forma.realizar.data:
        print('Uno')
        carpeta='ine'
        nvo_nombre='ine_nombre_2'
        ancho=300
        alto=300
        formato='jpg'
        ine=forma.ine.data
        x=Subir_archivos()
        x.agregar_doc_digital(carpeta,ine,nvo_nombre,ancho,alto,formato)

        print('Dos')
        carpeta='domicilio'
        nvo_nombre='comprobante'
        ancho=300
        alto=300
        formato='pdf'
        comp_domicilio=forma.comp_domicilio.data
        x=Subir_archivos()
        x.agregar_doc_digital(carpeta,comp_domicilio,nvo_nombre,ancho,alto,formato)
        print('LISTO')


    
    if current_user.perfil!='Administrador':
        #return redirect(url_for('acceso_denegado'))
        return render_template('agregar_documentos.html', forma=forma)
        
    else:
        return render_template('agregar_documentos.html', forma=forma)



#############

#Modificar umbral
@app.route('/modificar_umbral',methods=['GET','POST'])
@login_required

def modificar_umbral():
    forma=Umbral_k_forma()

    conexion=sqlite3.connect(nombre_BD)
    consulta='SELECT umbral_k FROM umbral'
    umbral_k=pd.read_sql(consulta,conexion)

    #Si no se ha registrado el umbral, por default se registra con peso 100
    if len(umbral_k) == 0:
            nvo_umbral=Umbral_k(100)
            print('ok')
            db.session.add(nvo_umbral)
            db.session.commit()
            db.session.close()
    
    else:
        if forma.cambiar_umbral.data:
        
            nvo_umbral=float(forma.umbral.data)
            #print(type(nvo_umbral))
            cursor=conexion.cursor()
            cursor.execute("UPDATE umbral SET umbral_k={} WHERE id=1".format(nvo_umbral))

            conexion.commit()
            conexion.close()
    
    conexion=sqlite3.connect(nombre_BD)
    consulta='SELECT umbral_k FROM umbral'
    umbral_k=pd.read_sql(consulta,conexion)

    umbral_actual=umbral_k['umbral_k'][0]
    
    #umbral_actual=1
    return render_template('modificar_umbral.html', forma=forma,umbral_actual=umbral_actual)
    
#Ingresar Secciones:
@app.route('/agregar_secciones',methods=['GET','POST'])
@login_required

def agregar_secciones():

    forma=Agregar_sec_forma()
    accion=forma.accion.data

    if accion=='Modificar':
        conexion=sqlite3.connect(nombre_BD)
        cursor=conexion.cursor()
        cursor.execute('SELECT id,sec FROM Secciones')
        lista_sec=cursor.fetchall()
        #IMPORTANTE: convertir a cadena el identificador de la clase.
        #De lo contrario no funcionará la forma de selección, SelectField
        lista_sec=[(str(id),sec) for id,sec in lista_sec]
        forma.sec_mod.choices=lista_sec
        sec_mod=forma.sec_mod.data
        
    if forma.validate_on_submit():
        #Usamos el mètodo strip() para eliminar espacios en blanco antes y después de la cadena de texto
        sec=forma.sec.data.strip().upper()

        try:
            forma.checar_sec(sec)

        except ValidationError:
            x='Esta sección ya fue registrada anteriormente.'
            mensaje=[False,x]
            flash(mensaje)

        else:
            if accion=='Agregar':

                m=True
                if sec=='':
                    x='Favor de indicar la sección que desea dar de alta'
                    m0=[False,x]
                    flash(m0)
                    m=False

                if forma.puntos.data=='':
                    x='Favor de indicar el puntaje'
                    m1=[False,x]
                    flash(m1)
                    m=False
                else:
                    try:
                        puntos=float(forma.puntos.data)
                    except ValueError:
                        m=False
                        x='El puntaje debe ser un número'
                        m2=[False,x]
                        flash(m2)


                if m==True:
                    puntos=float(forma.puntos.data)

                    nueva_sec=Secciones(sec,puntos)#agrega nueva seccion
                    db.session.add(nueva_sec)
                    db.session.commit()
                    db.session.close
                    x='Se registró una nueva sección: '+nueva_sec.sec
                    mensaje=[True,x]
                    flash(mensaje)


            elif accion=='Modificar':

                conexion=sqlite3.connect(nombre_BD)
                cursor=conexion.cursor()
                cursor.execute("SELECT * FROM Secciones WHERE id={}".format(sec_mod))
                r=cursor.fetchall()

                if sec=="":
                    sec=r[0][1]

                if forma.puntos.data=="":
                    puntos=r[0][2]
                else:
                    try:
                        puntos=float(forma.puntos.data)
                    except ValueError:
                        x='El puntaje debe ser un número'
                        m3=[False,x]
                        flash(m3)



                conexion=sqlite3.connect(nombre_BD)
                cursor=conexion.cursor()
                cursor.execute("UPDATE Secciones SET sec='{}', puntos={}  WHERE id={}".format(sec,puntos,sec_mod))
                conexion.commit()
                conexion.close()
                x='La sección fue modificada'
                mensaje=[True,x]
                flash(mensaje)

            else:
                #Dejo este else para incluír la opción de eliminar en caso de ser necesario
                pass


    if current_user.perfil!='Administrador':
        return redirect(url_for('acceso_denegado'))
    else:
        return render_template('agregar_sec.html', forma=forma)
    


# Ingresar Factores:
@app.route('/agregar_factores',methods=['GET','POST'])
@login_required

def agregar_factores():
    conexion=sqlite3.connect(nombre_BD)
    cursor=conexion.cursor()
    cursor.execute('SELECT id,sec FROM Secciones')
    lista_sec=cursor.fetchall()
    #IMPORTANTE: convertir a cadena el identificador de la clase.
    #De lo contrario no funcionará la forma de selección, SelectField
    lista_sec=[(str(id),sec) for id,sec in lista_sec]

    forma=Agregar_factor_forma()
    accion=forma.accion.data
    forma.sec.choices=lista_sec
    sec=forma.sec.data

    fac=forma.fac.data
    desc=forma.desc.data

    m=True


    if accion=='Modificar':

        conexion=sqlite3.connect(nombre_BD)
        cursor=conexion.cursor()
        cursor.execute('SELECT id,fac FROM factores WHERE sec_id={}'.format(sec))
        lista_fac=cursor.fetchall()
        #IMPORTANTE: convertir a cadena el identificador de la clase.
        #De lo contrario no funcionará la forma de selección, SelectField
        lista_fac=[(str(id),fac) for id,fac in lista_fac]

        forma.fac_mod.choices=lista_fac
        fac_mod=forma.fac_mod.data


    if forma.validate_on_submit():
        if accion=='Agregar':

            if fac=='':
                x='Favor de indicar el factor que desea dar de alta'
                m0=[False,x]
                flash(m0)
                m=False
            else:
                fac=fac.strip().upper()
                desc=desc.strip().upper()
                x=Factores(sec,fac,"x",0)
                if x.checar_fac(sec,fac):
                    pass
                else:
                    m=False

            if forma.puntos.data=='':
                x='Favor de indicar el puntaje'
                m1=[False,x]
                flash(m1)
                m=False
            else:
                try:
                    puntos=float(forma.puntos.data)
                except ValueError:
                    m=False
                    x='El puntaje debe ser un número'
                    m2=[False,x]
                    flash(m2)


            if m==True:
                puntos=float(forma.puntos.data)

                nuevo_fac=Factores(sec,fac,desc,puntos)
                db.session.add(nuevo_fac)
                db.session.commit()
                db.session.close
                x='Se registró un factor nuevo: '+nuevo_fac.fac
                mensaje=[True,x]
                flash(mensaje)


        if accion=='Modificar':

            conexion=sqlite3.connect(nombre_BD)
            cursor=conexion.cursor()
            cursor.execute("SELECT * FROM Factores WHERE id={}".format(fac_mod))
            r=cursor.fetchall()

            if sec=="":
                sec=r[0][1]


            if fac=="":
                fac=r[0][2]

            else:
                fac=fac.strip().upper()
                x=Factores(sec,fac,"x",0)

                if x.checar_fac(sec,fac):
                    pass
                else:
                    m=False


            if desc=="":
                desc=r[0][3]
            else:
                desc=desc.strip().upper()

            if forma.puntos.data=="":
                puntos=r[0][4]

            else:
                try:
                    puntos=float(forma.puntos.data)
                except ValueError:
                    x='El puntaje debe ser un número'
                    m3=[False,x]
                    flash(m3)
                    m=False


            if m==True:

                conexion=sqlite3.connect(nombre_BD)
                cursor=conexion.cursor()
                cursor.execute("UPDATE Factores SET sec_id='{}', fac='{}', desc='{}', puntos={}  WHERE id={}".format(sec,fac,desc,puntos,fac_mod))
                conexion.commit()
                #conexion.close()
                x='El factor fue modificado'
                mensaje=[True,x]
                flash(mensaje)


    if current_user.perfil!='Administrador':
        return redirect(url_for('acceso_denegado'))
    else:
        return render_template('agregar_factores.html', forma=forma)
#Ingresar masivamente catálogo de cuentas
@app.route('/agregar_factores_masivo',methods=['GET','POST'])
@login_required

def agregar_factores_masivo():

    forma=Agregar_factor_forma_masivo()
    accion=forma.accion.data

    if accion=="Agregar":

        if forma.validate_on_submit():
            carpeta='auxiliar'
            archivo=forma.archivo.data
            x=Subir_archivos()
            x.agregar_archivo(carpeta,archivo)
            factores=pd.read_csv(x.destino,encoding = 'latin1')
            factores=factores[['sec_id','fac','desc','puntos']]
            factores=factores.dropna()
            ##Una vez almacenada la información en un DataFrame, se borra del servidor el archivo
            ##recién subido
            os.remove(x.destino)

            for i in factores.index:
                sec=int(factores['sec_id'].loc[i])
                fac=factores['fac'].loc[i].upper()
                desc=factores['desc'].loc[i].upper()
                puntos=float(factores['puntos'].loc[i])

                nuevo_factor=Factores(sec,fac,desc,puntos)


                if nuevo_factor.checar_fac(sec,fac):

                    db.session.add(nuevo_factor)
                    db.session.commit()
                    db.session.close
                    x='Se registró un nuevo factor: '+nuevo_factor.fac
                    mensaje=[True,x]
                    flash(mensaje)

    elif accion=="Eliminar":

        conexion=sqlite3.connect(nombre_BD)
        cursor=conexion.cursor()
        cursor.execute("DELETE FROM Factores")
        conexion.commit()
        conexion.close()

        x='Los factores se eliminaron exitosamente'
        mensaje=[True,x]
        flash(mensaje)


    if current_user.perfil!='Administrador':
        return redirect(url_for('acceso_denegado'))
    else:
        return render_template('agregar_factores_masivo.html', forma=forma)
#Agregar respuestas a factores:
@app.route('/agregar_respuestas',methods=['GET','POST'])
@login_required

def agregar_respuestas():
    conexion=sqlite3.connect(nombre_BD)
    cursor=conexion.cursor()
    cursor.execute('SELECT id,sec FROM Secciones')
    lista_sec=cursor.fetchall()
    lista_sec=[(str(id),sec) for id,sec in lista_sec]


    forma=Agregar_respuesta_forma()
    accion=forma.accion.data
    forma.sec.choices=lista_sec
    sec=forma.sec.data

    conexion=sqlite3.connect(nombre_BD)
    cursor=conexion.cursor()

    try:
        cursor.execute('SELECT id,fac FROM Factores WHERE sec_id={}'.format(sec))
        lista_fac=cursor.fetchall()
        lista_fac=[(str(id),fac) for id,fac in lista_fac]

    except sqlite3.OperationalError:
        cursor.execute('SELECT id,fac FROM Factores')
        lista_fac=cursor.fetchall()
        lista_fac=[(str(id),fac) for id,fac in lista_fac]


    forma.fac.choices=lista_fac
    fac=forma.fac.data



    if accion=='Modificar':
        conexion=sqlite3.connect(nombre_BD)
        cursor=conexion.cursor()
        cursor.execute('SELECT id,resp FROM Respuestas WHERE fac_id={}'.format(fac))
        lista_resp=cursor.fetchall()
        #IMPORTANTE: convertir a cadena el identificador de la clase.
        #De lo contrario no funcionará la forma de selección, SelectField
        lista_resp=[(str(id),resp) for id,resp in lista_resp]
        forma.resp_mod.choices=lista_resp
        resp_mod=forma.resp_mod.data


    if forma.validate_on_submit():
        #Usamos el mètodo strip() para eliminar espacios en blanco antes y después de la cadena de texto
        resp=forma.resp.data.strip().upper()
        m=True

        x=Respuestas(fac,resp,0)
        if x.checar_resp(fac,resp)==False:
            m=False

        else:
            if accion=='Agregar':
                if fac=='':
                    x='Favor de indicar el factor que desea dar de alta'
                    m0=[False,x]
                    flash(m0)
                    m=False

                if resp=='':
                    x='Favor de indicar la respuesta que desea dar de alta'
                    m1=[False,x]
                    flash(m1)
                    m=False

                if forma.puntos.data=='':
                    x='Favor de indicar el puntaje'
                    m2=[False,x]
                    flash(m2)
                    m=False
                else:
                    try:
                        puntos=float(forma.puntos.data)
                    except ValueError:
                        m=False
                        x='El puntaje debe ser un número'
                        m2=[False,x]
                        flash(m2)


                if m==True:
                    puntos=float(forma.puntos.data)

                    nueva_resp=Respuestas(fac,resp,puntos)
                    db.session.add(nueva_resp)
                    db.session.commit()
                    db.session.close
                    x='Se registró una respuesta nueva: '+nueva_resp.resp
                    mensaje=[True,x]
                    flash(mensaje)


            elif accion=='Modificar':
                conexion=sqlite3.connect(nombre_BD)
                cursor=conexion.cursor()
                cursor.execute("SELECT * FROM Respuestas WHERE id={}".format(resp_mod))
                r=cursor.fetchall()

                if fac=="":
                    fac=r[0][1]
                if resp=="":
                    resp=r[0][2]

                if forma.puntos.data=="":
                    puntos=r[0][3]
                else:
                    try:
                        puntos=float(forma.puntos.data)
                    except ValueError:
                        x='El puntaje debe ser un número'
                        m3=[False,x]
                        flash(m3)



                conexion=sqlite3.connect(nombre_BD)
                cursor=conexion.cursor()

                cursor.execute("UPDATE Respuestas SET fac_id={}, resp='{}', puntos={}  WHERE id={}".format(fac,resp,puntos,resp_mod))
                conexion.commit()
                conexion.close()
                x='La respuesta fue modificada'
                mensaje=[True,x]
                flash(mensaje)

            else:
                #Dejo este else para incluír la opción de eliminar en caso de ser necesario
                pass


    if current_user.perfil!='Administrador':
        return redirect(url_for('acceso_denegado'))
    else:
        return render_template('agregar_respuestas.html', forma=forma)
#Carga masiva de respuestas:
@app.route('/agregar_respuestas_masivo',methods=['GET','POST'])
@login_required

def agregar_respuestas_masivo():

    forma=Agregar_respuesta_forma_masivo()
    accion=forma.accion.data

    if accion=="Agregar":

        if forma.validate_on_submit():
            carpeta='auxiliar'
            archivo=forma.archivo.data
            x=Subir_archivos()
            x.agregar_archivo(carpeta,archivo)
            respuestas=pd.read_csv(x.destino,encoding = 'latin1')
            respuestas=respuestas[['fac_id','resp','puntos']]
            respuestas=respuestas.dropna()
            ##Una vez almacenada la información en un DataFrame, se borra del servidor el archivo
            ##recién subido
            os.remove(x.destino)

            for i in respuestas.index:

                fac=int(respuestas['fac_id'].loc[i])
                resp=respuestas['resp'].loc[i].upper()
                puntos=float(respuestas['puntos'].loc[i])

                nueva_respuesta=Respuestas(fac,resp,puntos)

                if nueva_respuesta.checar_resp(fac,resp):

                    db.session.add(nueva_respuesta)
                    db.session.commit()
                    db.session.close
                    x='Se registró una respuesta nueva: '+nueva_respuesta.resp
                    mensaje=[True,x]
                    flash(mensaje)

    elif accion=="Eliminar":

        conexion=sqlite3.connect(nombre_BD)
        cursor=conexion.cursor()
        cursor.execute("DELETE FROM Respuestas")
        conexion.commit()
        conexion.close()

        x='Las resuestas se eliminaron exitosamente'
        mensaje=[True,x]
        flash(mensaje)


    if current_user.perfil!='Administrador':
        return redirect(url_for('acceso_denegado'))
    else:
        return render_template('agregar_respuestas_masivo.html', forma=forma)

#Cuestionario Anexo I:
@app.route('/csc',methods=['GET','POST'])
@login_required


def csc():
    #La clase Credit_score_card_form se define aquí para que se "actualice" con el número de variables
    # cada vez que el usuario pase por la pàgina /csc. Si se dejara en el archivo forms.py
    #tendría que volverse ejecutar la app.py
    class Credit_score_card_form(FlaskForm):
        try:
            
            solicitud=SelectField('RFC del solicitante del crédito:',choices=[('0','')])


            conexion=sqlite3.connect(nombre_BD)
            consulta="SELECT id,sec FROM Secciones"
            secciones=pd.read_sql(consulta,conexion)
            secciones=secciones.set_index('id')
            for s in secciones.index:
                locals()['sec_{}'.format(s)]=SelectField(secciones['sec'].loc[s],choices=[('0','')])


            consulta="SELECT id,fac FROM factores"
            factores=pd.read_sql(consulta,conexion)
            factores=factores.set_index('id')
            for i in factores.index:
                locals()['fac_{}'.format(i)]=SelectField(factores['fac'].loc[i],choices=[('0','')])

        except pd.io.sql.DatabaseError:
            pass

        realizar=SubmitField('Enviar respuestas')
        #Aquí termina la clase que construye la forma de captura de información
#######################################################

    conexion=sqlite3.connect(nombre_BD)
    cursor=conexion.cursor()
    cursor.execute("SELECT id,rfc FROM Solicitudes WHERE id_usuario={} AND estatus='En evaluación' ".format(current_user.id))
    lista_solicitudes=cursor.fetchall()
    #IMPORTANTE: convertir a cadena el identificador de la clase.
    # #De lo contrario no funcionará la forma de selección, SelectField
    lista_solicitudes=[(str(id),rfc) for id,rfc in lista_solicitudes]
            
    
    conexion=sqlite3.connect(nombre_BD)
    consulta="SELECT id,sec_id FROM Factores"
    factores=pd.read_sql(consulta,conexion)
    factores=factores.set_index('id')

    consulta="SELECT id FROM Secciones"
    secciones=pd.read_sql(consulta,conexion)
    secciones=secciones.set_index('id')

    forma=Credit_score_card_form()

    forma.solicitud.choices=lista_solicitudes
    solicitud=forma.solicitud.data

    l_sec=[]
    for s in secciones.index:
        q="l_sec.append(({},forma.sec_{}))".format(s,s)
        exec(q)

    l_fac=[]
    
    for i in factores.index:
        s=factores['sec_id'].loc[i]
        conexion=sqlite3.connect(nombre_BD)
        cursor=conexion.cursor()
        cursor.execute("SELECT id,resp FROM Respuestas WHERE fac_id={}".format(i))
        r=cursor.fetchall()
            
        p="l_resp_{}=[(str(id),resp) for id,resp in r]\nforma.fac_{}.choices=l_resp_{}\nfac_{}=forma.fac_{}.data".format(i,i,i,i,i)
        exec(p)
        p="l_fac.append(({},forma.fac_{}))".format(s,i)
        exec(p)
        
    if forma.realizar.data:
        for i in factores.index:
            s=factores['sec_id'].loc[i] ##CORRECCIÓN
            q="resp=Csc({},{},fac_{},{},{})\nprint(resp)\ndb.session.add(resp)".format(s,i,i,solicitud,current_user.id)
            exec(q)
            db.session.commit()
            db.session.close
            
            
            if len(factores.index)==i:
                conexion=sqlite3.connect(nombre_BD)
                cursor=conexion.cursor()
                cursor.execute ("UPDATE solicitudes SET estatus='CSC' WHERE id={}".format(solicitud))
                conexion.commit()
                
                x='Las respuestas se registraron correctamente'
                mensaje=[True,x]
                flash(mensaje)
        
        ###Agrega el credit score en la tabla de solicitudes al sumar el puntaje de las respuestas registradas en la tabla csc
        consulta="SELECT sum(respuestas.puntos) FROM respuestas,csc WHERE csc.id_solicitud=" + solicitud + " and respuestas.id=csc.id_resp"
        sum_csc=pd.read_sql(consulta,conexion)
        sum_csc=sum_csc['sum(respuestas.puntos)'][0] #como csc es un DataFrame tenemos que indicar con un índice el valor en la tabla que estamos tomando 
        cursor.execute("UPDATE solicitudes SET csc={} WHERE id={}".format(sum_csc,solicitud))
        conexion.commit()
        print(sum_csc)  
        

        ### Cambia estatus de la solucitud dependiendo del score obtenido
        cursor.execute("UPDATE solicitudes SET estatus= 'Aprobada' WHERE id={} AND csc>=umbral_k".format(solicitud))
        conexion.commit()
        
        #else:
        cursor.execute("UPDATE solicitudes SET estatus= 'Rechazada' WHERE id={} AND csc<umbral_k".format(solicitud))
        conexion.commit()
        conexion.close()
            
    return render_template('csc.html', forma=forma,l_fac=l_fac,l_sec=l_sec)
    

@app.route('/config_email',methods=['GET','POST'])
@login_required

def config_email():

    config_email=Config_email_inst_forma()

    if config_email.validate_on_submit():
        email=config_email.email.data
        password=config_email.password.data

        if config_email.checar_email():
            conexion=sqlite3.connect(nombre_BD)
            cursor=conexion.cursor()
            cursor.execute("UPDATE config_email_inst SET email='{}',password='{}' WHERE id=1".format(email,password))
            conexion.commit()
            x='Se modificó la cuenta institucional: {}'.format(email)
            mensaje=[True,x]
            flash(mensaje)

        else:
            nueva_cuenta=Config_email_inst(email,password)
            db.session.add(nueva_cuenta)
            db.session.commit()
            db.session.close
            x='Se registró la cuenta institucional: {}'.format(email)
            mensaje=[True,x]
            flash(mensaje)

    if current_user.perfil!='Administrador':
        return redirect(url_for('acceso_denegado'))
    else:
        return render_template('config_email.html', config_email=config_email)



@app.route('/config_fondo',methods=['GET','POST'])
@login_required

def config_fondo():

    config_fondo=Config_fondo_principal_forma()

    if config_fondo.validate_on_submit():
        if config_fondo.fondo_principal.data:
            fondo_principal=agregar_foto(config_fondo.fondo_principal.data,'fondo_principal','static',0,0)
            x='Si no puede ver los cambios actualice el caché de su navegador: Para Windows/Linux presiones Crtl+F5; para Mac presione Cmd+Shift+R'
            mensaje=[True,x]
            flash(mensaje)


    if current_user.perfil!='Administrador':
        return redirect(url_for('acceso_denegado'))
    else:
        return render_template('config_fondo.html', config_fondo=config_fondo)

# Catálogo de documentos:
@app.route('/catalogo_documentos',methods=['GET','POST'])
@login_required

def catalogo_documentos():
    forma=Cat_doctos_forma()

    conexion=sqlite3.connect(nombre_BD)
    cursor=conexion.cursor()
    cursor.execute('SELECT id,documento FROM documentos')
    lista_doc=cursor.fetchall()
    #IMPORTANTE: convertir a cadena el identificador de la clase.
    #De lo contrario no funcionará la forma de selección, SelectField
    lista_doc=[(str(id),documento) for id,documento in lista_doc]
    forma.documento_mod.choices=lista_doc

    accion=forma.accion.data
    documento=forma.documento.data
    tipo=forma.tipo.data
    
    #if forma.realizar.data:
    if forma.validate_on_submit():
        print('prueba')    
        if accion=='Agregar':
            documento=documento.strip().upper()
            if documento=="":
                x='Debe especificar un documento'
                mensaje=[False,x]
                flash(mensaje)

            else:
                nuevo_doc=Documentos(documento,tipo)
                if nuevo_doc.checar_cat_doc(documento):
                    db.session.add(nuevo_doc)
                    db.session.commit()
                    db.session.close
                    x='Se registró un documento nuevo: '+nuevo_doc.documento
                    mensaje=[True,x]
                    flash(mensaje)
  
    
        elif accion=='Eliminar':
            documento_mod=forma.documento_mod.data
            conexion=sqlite3.connect(nombre_BD)
            cursor=conexion.cursor()
            cursor.execute("DELETE FROM documentos WHERE id={}".format(documento_mod))
            conexion.commit()
            conexion.close()
            x='Se eliminó el documento del catálogo'
            mensaje=[True,x]
            flash(mensaje)


    if current_user.perfil!='Administrador':
        return redirect(url_for('acceso_denegado'))
    else:
        return render_template('catalogo_documentos.html', forma=forma)



############################
#Acá debe ir la vista del registro de clientes:

#############################
#Ingresar Estructura contable (Cuentas padre-hijo)
@app.route('/agregar_estructura_ubd',methods=['GET','POST'])
@login_required

def agregar_estructura_ubd():
    id_inst=current_user.id_inst

    estructura_ubd_forma=Agregar_estructura_ubd_forma()
    accion=estructura_ubd_forma.accion.data

    conexion=sqlite3.connect("data.sqlite")
    cursor=conexion.cursor()
    cursor.execute('SELECT id,concepto FROM Cat_conta_ubd WHERE id_inst={}'.format(id_inst))
    lista_concepto_ubd=cursor.fetchall()
    #IMPORTANTE: convertir a cadena el identificador de la clase.
    #De lo contrario no funcionará la forma de selección, SelectField
    lista_concepto_ubd=[(str(id),concepto) for id,concepto in lista_concepto_ubd]

    estructura_ubd_forma.cuenta.choices=lista_concepto_ubd
    cuenta=estructura_ubd_forma.cuenta.data

    estructura_ubd_forma.cuenta_padre.choices=lista_concepto_ubd
    cuenta_padre=estructura_ubd_forma.cuenta_padre.data

    mult=estructura_ubd_forma.mult.data

    if estructura_ubd_forma.validate_on_submit():
        if accion=='Agregar':

            nueva_rel=Estructura_contable(cuenta,cuenta_padre,id_inst,mult)


            if nueva_rel.checar_relacion(cuenta,cuenta_padre,id_inst):
                db.session.add(nueva_rel)
                db.session.commit()
                db.session.close
                x='Se registró una nueva relación contable'
                mensaje=[True,x]
                flash(mensaje)

            else:
                x='Esta relación contable ya se encuentra definida.'
                mensaje=[False,x]
                flash(mensaje)



        elif accion=='Modificar':
                conexion=sqlite3.connect("data.sqlite")
                cursor=conexion.cursor()
                cursor.execute("UPDATE Estructura_contable SET cuenta_padre={},mult={}  WHERE cuenta={} AND id_inst={}".format(cuenta_padre, mult,cuenta,id_inst))
                conexion.commit()
                conexion.close()
                x='La relación contable fue modificada'
                mensaje=[True,x]
                flash(mensaje)

        else:
            #Dejo este else para incluír la opción de eliminar en caso de ser necesario
            pass


    if current_user.perfil!='Administrador':
        return redirect(url_for('acceso_denegado'))
    else:
        return render_template('agregar_estructura_ubd.html', estructura_ubd_forma=estructura_ubd_forma)
#Agregar estructura masivamente:
@app.route('/agregar_estructura_ubd_masivo',methods=['GET','POST'])
@login_required

def agregar_estructura_ubd_masivo():
    id_inst=current_user.id_inst

    estructura_ubd_forma_masiva=Agregar_masiva_estructura_ubd_forma()
    accion=estructura_ubd_forma_masiva.accion.data

    if accion=='Agregar':
        if estructura_ubd_forma_masiva.validate_on_submit():

            carpeta='auxiliar'
            archivo=estructura_ubd_forma_masiva.archivo.data
            x=Subir_archivos()
            x.agregar_archivo(carpeta,archivo)

            estructura=pd.read_csv(x.destino,encoding = 'latin1')
            estructura=estructura[['cuenta','cuenta_padre','mult']]
            estructura=estructura.dropna()

            ##Una vez almacenada la información en un DataFrame, se borra del servidor el archivo
            ##recién subido
            os.remove(x.destino)

            for i in estructura.index:
                cuenta=int(estructura['cuenta'].loc[i])
                cuenta_padre=int(estructura['cuenta_padre'].loc[i])
                mult=int(estructura['mult'].loc[i])

                nueva_rel=Estructura_contable(cuenta,cuenta_padre,id_inst,mult)

                if nueva_rel.checar_relacion(cuenta,cuenta_padre,id_inst):
                    db.session.add(nueva_rel)
                    db.session.commit()
                    db.session.close
                    x='Se registró una nueva relación contable'
                    mensaje=[True,x]
                    flash(mensaje)

                else:
                    x='Esta relación contable ya se encuentra definida.'
                    mensaje=[False,x]
                    flash(mensaje)

    elif accion=='Eliminar':
        conexion=sqlite3.connect("data.sqlite")
        cursor=conexion.cursor()
        cursor.execute("DELETE FROM Estructura_contable WHERE id_inst=={}".format(id_inst))
        conexion.commit()
        conexion.close()

        x='La estructura contable fue borrada exitosamente'
        mensaje=[True,x]
        flash(mensaje)


    if current_user.perfil!='Administrador':
        return redirect(url_for('acceso_denegado'))
    else:
        return render_template('agregar_estructura_ubd_masivo.html', estructura_ubd_forma_masiva=estructura_ubd_forma_masiva)

#Ingresar valores a los balances
@app.route('/agregar_edos_fin',methods=['GET','POST'])
@login_required

def agregar_edos_fin():
    id_inst=current_user.id_inst

    conexion=sqlite3.connect("data.sqlite")
    cursor=conexion.cursor()
    cursor.execute('SELECT id,nom_com FROM Cat_if')
    lista_if=cursor.fetchall()
    #IMPORTANTE: convertir a cadena el identificador de la clase.
    #De lo contrario no funcionará la forma de selección, SelectField
    lista_if=[(str(id),nom_com) for id,nom_com in lista_if]

    def anio_nac(anio_ini,n_anio):
        l_anios=[]
        a=0
        while a<n_anio:
            x=(str(anio_ini),str(anio_ini))
            l_anios.append(x)
            a=a+1
            anio_ini=anio_ini+1
        return l_anios

    lista_anios=anio_nac(2010,14)

    edos_fin=Agregar_edos_fin_forma()

    accion=edos_fin.accion.data
    edos_fin.anio.choices=lista_anios
    anio=edos_fin.anio.data
    mes=edos_fin.mes.data
    fec_inf=anio+'-'+ mes+'-01'
    edos_fin.id_if.choices=lista_if
    id_if=edos_fin.id_if.data

    if accion=='Agregar':

        if edos_fin.validate_on_submit():
            carpeta='auxiliar'
            archivo=edos_fin.archivo.data
            x=Subir_archivos()
            x.agregar_archivo(carpeta,archivo)

            info_contable=pd.read_csv(x.destino,encoding = 'latin1')
            info_contable=info_contable[['cve_cta','monto']]
            info_contable=info_contable.dropna()
            #Una vez guardada la información en un DataFrame, borramos el archivo para no saturar el servidor
            os.remove(x.destino)
            #Hacemos una copia para la validación:
            info_contable_val=info_contable
            info_contable_val['id_ubd']=id_inst
            info_contable_val=info_contable_val.reset_index()
            #Aquí va la validación contable. Se hace antes de cargar la información.
            conexion=sqlite3.connect("data.sqlite")
            consulta="SELECT * FROM {} WHERE id_inst={}".format('estructura_contable',id_inst)
            estructura=pd.read_sql(consulta,conexion)
            estructura['cve_cta']=estructura['cuenta']
            estructura['id_ubd']=estructura['id_inst']
            estructura=estructura.reset_index()

            info_contable_val=pd.merge(info_contable_val,estructura,how='outer',on=['cve_cta','id_ubd'])
            info_contable_val['val']=info_contable_val['monto']*info_contable_val['mult']
            val=info_contable_val[['cuenta_padre','val']].groupby(['cuenta_padre']).sum()
            val=val.reset_index()
            val['cve_cta']=val['cuenta_padre']
            val['valida']=val['val']
            info_contable_val=pd.merge(info_contable_val,val,how='outer',on=['cve_cta'])
            info_contable_val=info_contable_val.reset_index()
            info_contable_val=info_contable_val[['cve_cta','monto','valida']]
            info_contable_val=info_contable_val.dropna(subset=['valida'],how='all')
            info_contable_val['dif']=np.where(round((info_contable_val['monto']-info_contable_val['valida']),1)==0,'Valor correcto','Error')
            info_contable_val=info_contable_val.reset_index()

            sin_error=True
            for i in info_contable_val.index:
                if info_contable_val['dif'].loc[i]=='Error':
                    sin_error=False
                    x='Hay un descuadre en la cuenta: {}'.format(info_contable_val['cve_cta'].loc[i])
                    mensaje=[False,x]
                    flash(mensaje)

            if sin_error==True:
                for i in info_contable.index:
                    cve_cta=int(info_contable['cve_cta'].loc[i])
                    monto=info_contable['monto'].loc[i]

                    nueva_info=Edo_fin(int(id_if),id_inst,cve_cta,fec_inf,monto)
                    if nueva_info.checar_info(id_if,cve_cta,fec_inf,id_inst):
                        db.session.add(nueva_info)
                        db.session.commit()
                        db.session.close
                        x='Se registró un monto de {} en la cuenta {}'.format(monto,cve_cta)
                        mensaje=[True,x]
                        flash(mensaje)

                    else:
                        x='Esta cuenta ya tiene información.'
                        mensaje=[False,x]
                        flash(mensaje)

    elif accion=='Eliminar':
        conexion=sqlite3.connect("data.sqlite")
        cursor=conexion.cursor()
        cursor.execute("DELETE FROM Edo_fin WHERE id_ubd={} AND id_if={} AND fec_inf='{}'".format(id_inst,id_if,fec_inf))
        conexion.commit()
        conexion.close()

        x='La información contable fue borrada exitosamente'
        mensaje=[True,x]
        flash(mensaje)


    if current_user.perfil!='Administrador':
        return redirect(url_for('acceso_denegado'))
    else:
        return render_template('agregar_edos_fin.html', edos_fin=edos_fin)


@app.route('/descargas/',methods=['GET','POST'])
@login_required

def descarga_solicitud():
    forma=Descargar_solicitud_forma()

    try:
        #Hacer consulta de RFC registrados en base de datos
        conexion=sqlite3.connect(nombre_BD)
        cursor=conexion.cursor()
        cursor.execute("SELECT id,rfc FROM Solicitudes WHERE id_usuario={} ".format(current_user.id))
    
        lista_solicitudes=cursor.fetchall()
    
        #se llena la forma de RFC con la consulta anterior
        lista_solicitudes=[(str(id),rfc) for id,rfc in lista_solicitudes]
        forma.rfc_registrado.choices=lista_solicitudes
    
        #se hace consulta a la tabla de solicitudes
        #consulta="SELECT * FROM solicitudes WHERE solicitudes.id= " +forma.rfc_registrado.data
        consulta="SELECT * FROM solicitudes WHERE solicitudes.id={}".format(forma.rfc_registrado.data) 
        solicitud=pd.read_sql(consulta,conexion)

        #se hace consulta a la tabla de sepomex
        consulta="select d_asenta,id_asenta_cpcons from sepomex "
        asenta=pd.read_sql(consulta,conexion)
    
        consulta="select D_mnpio,c_mnpio from sepomex "
        catalogo_muni=pd.read_sql(consulta,conexion)

        consulta="select d_estado,c_estado from sepomex "
        catalogo_edo=pd.read_sql(consulta,conexion)

    except pd.io.sql.DatabaseError:
        pass

    #Se descarga la solicitud de crédito
    if forma.descargar.data:

        pdf = PDF(format='letter')
        tamano_fuente = 7
        
        ap_paterno=solicitud['ap_paterno'][0]
        ap_materno=solicitud['ap_materno'][0]
        nombres=solicitud['nombres'][0]
        edo_civil=solicitud['edo_civil'][0]
        curp=solicitud['curp'][0]
        rfc=solicitud['rfc'][0]
        nss=solicitud['nss'][0]
        fec_nacimiento=solicitud['fec_nac'][0]
        calle=solicitud['calle'][0]
        n_ext=solicitud['n_ext'][0]
        n_int=solicitud['n_int'][0]
        asentamiento=asenta[asenta['id_asenta_cpcons']==solicitud['id_asenta_cpcons'][0]]['d_asenta'].iloc[0]
        municipio=catalogo_muni[catalogo_muni['c_mnpio']==solicitud['c_mnpio'][0]]['D_mnpio'].iloc[0]
        estado=catalogo_edo[catalogo_edo['c_estado']==solicitud['c_estado'][0]]['d_estado'].iloc[0]
        tel=solicitud['tel'][0]
        email=solicitud['email'][0]
        

        pdf.add_page()
        pdf.datos_credito(tamano_fuente)

        pdf.info_solicitud('INFORMACIÓN DEL SOLICITANTE',ap_paterno,ap_materno,nombres,edo_civil,curp,rfc,nss,fec_nacimiento,calle,n_ext,n_int,asentamiento,municipio,estado,tel,email,tamano_fuente)
                         
        pdf.info_empleo('INFORMACIÓN DE LA EMPRESA',tamano_fuente)
        pdf.ref_personal('REFERENCIAS DEL EMPLEO',tamano_fuente)
        pdf.ref_bancaria('REFERENCIAS BANCARIAS(CUENTA DE NÓMINA)',tamano_fuente)
        pdf.info_crediticia('INFORMACIÓN CREDITICIA',tamano_fuente)
        pdf.aviso_privacidad('AVISO DE PRIVACIDAD',tamano_fuente)


        response = make_response(pdf.output(dest='S').encode('latin-1'))
        response.headers.set('Content-Disposition', 'attachment', filename=rfc + '_solicitud.pdf')
        response.headers.set('Content-Type', 'application/pdf')
        return response
    
    return render_template('descargas.html',forma=forma)

@app.route('/reportes',methods=['GET','POST'])
@login_required

def reportes():
    #Provisional
    #conexion=sqlite3.connect("data.sqlite")
    #cursor=conexion.cursor()
    #cursor.execute("SELECT id,reporte FROM reportes_generales")
    #lista_reportes=cursor.fetchall()
    #lista_reportes=[(str(id),reporte) for id,reporte in lista_reportes]

    generar_reportes=Reportes_forma()
    #generar_reportes.reporte.choices=lista_reportes

    if generar_reportes.validate_on_submit():
        reporte=generar_reportes.reporte.data
        
        #Provisional:
        #conexion=sqlite3.connect(nombre_BD)
        #cursor=conexion.cursor()
        #cursor.execute("SELECT * FROM 'reportes_generales' WHERE id={}".format(reporte))
        #r=cursor.fetchall()
        #tabla=r[0][3]
        #encabezado=r[0][2]
        encabezado="Folio solicitud,ID usuario,Umbral Credit Score,Usuario,Apellido paterno,Apellido materno,Nombres,CURP,RFC,NSS,Fecha de nacimiento,Estado civil,Clave del Estado,Clave del municipio,ID Asentamiento,Calle,Número exterior,Número interior,Teléfono,email,Fecha de solicitud,Fecha de evaluación,Estatus,CSC,Dirección IP"
        #nombre_archivo=r[0][1]
        #nombre_archivo=nombre_archivo+'.csv'
        nombre_archivo='Creditos_autorizados.csv'

### Líneas para editar los reportes a mano:
        #if reporte=='4':
        #    cursor.execute("DELETE FROM materiales WHERE id=39")
        #    cursor.execute("DELETE FROM usuarios WHERE id=6")
        #    cursor.execute("DELETE FROM clases WHERE id=23")
        #    cursor.execute("UPDATE reportes_generales SET encabezados='Identificador de la clase,Clase,Tipo,Estatus,Horario,Precio,Descripción,Identificador del profesor,Profesor,Foto,Opiniones,Temporalidad de la clase' WHERE id=7")
        #    cursor.execute("UPDATE reportes_generales SET encabezados='id,Nombre,Tipo,Usuario que realiza la operación,Tipo de movimiento,Monto,Fecha del movimiento,Concepto,Descripción,Folio recibo' WHERE id=3")
        #    cursor.execute("DELETE FROM movimientos WHERE id=64")


        #    conexion.commit()



        encabezado=tuple(encabezado.split(','))

        #y=[]
        #y.append(encabezado)
        #encabezado=y

        #Consulta de la tabla para hacer un reporte general
        conexion=sqlite3.connect(nombre_BD)
        cursor=conexion.cursor()
        tabla='Solicitudes'
        #cursor.execute("SELECT * FROM '{}'".format(tabla))
        consulta="SELECT * FROM {}".format(tabla)
        df=pd.read_sql(consulta,conexion)

        #r=cursor.fetchall()

        #En lugar de exportar el CSV a una carpeta del servidor se descarga, por eso debo escribir el archivo línea por línea:
        def generar():
            data = StringIO()
            w = csv.writer(data)
            # write header
            #w.writerow(('action', 'timestamp'))
            w.writerow(encabezado)
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)
            # write each log item
            #for item in log:
            #Se usa el método itertuples con index=False para no incluir el índice en el archivo
            for item in df.itertuples(index=False):
                w.writerow(item)
                yield data.getvalue()
                data.seek(0)
                data.truncate(0)

###############################################################################
###ESTA SECCIÓN COMENTADA SIRVE PARA GUARDAR ARCHIVOS LOCALMENTE:
        #for i in range(0,len(r)):
        #    encabezado.append(r[i])

        #archivo=open(ruta+'/'+nombre_archivo+'.csv','w')
        #with archivo:
        #    writer=csv.writer(archivo)
        #    writer.writerows(encabezado)
        #    x='El archivo {} se guardó en la ruta indicada'.format(nombre_archivo)
        #    mensaje=[True,x]
        #    flash(mensaje)
##############################################################################
        # add a filename
        #Comentar desde aquí para pruebas:
        headers = Headers()
        headers.set('Content-Disposition', 'attachment', filename=nombre_archivo)

        # stream the response as the data is generated
        return Response(
            stream_with_context(generar()),
            mimetype='text/csv', headers=headers
        )
###################################################################################
    if current_user.perfil!='Administrador':
        return redirect(url_for('acceso_denegado'))
    else:
        return render_template('reportes.html', generar_reportes=generar_reportes)



###############
#Agregar balanzas de comprobación

######################################################
if __name__=='__main__':
    app.run(debug=True)

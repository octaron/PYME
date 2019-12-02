#FORMS:

from flask_wtf import FlaskForm
#from wtforms_sqlalchemy.fields import QuerySelectField

from wtforms import ValidationError,StringField, IntegerField, SubmitField, IntegerField, FloatField, SelectField, RadioField,TextAreaField,SelectMultipleField,PasswordField
from wtforms.validators import InputRequired,Email,EqualTo,DataRequired
from modelos import *
from flask_wtf.file import FileField,FileAllowed,FileRequired
import pandas as pd
import numpy as np
#(Sirven para ingresar las fotos del background y de las clases)

class Reportes_forma(FlaskForm):
    reporte=SelectField('Selecciona el reporte:',choices=[('1','Créditos autorizados')])
    realizar=SubmitField('Generar reporte')


class Login_forma(FlaskForm):
    email=StringField('Correo electrónico:',validators=[DataRequired(),Email()])
    password=PasswordField('Contraseña:',validators=[DataRequired()])
    ingresar=SubmitField('Ingresar')


class Recuperar_password_forma(FlaskForm):
    email=StringField('Correo electrónico:',validators=[DataRequired(),Email()])
    #password=PasswordField('Contraseña:',validators=[DataRequired()])
    recuperar=SubmitField('Recuperar')

    def revisar_email(self,email):
        if Usuarios.query.filter_by(email=email).first() is None:
            raise ValidationError('Este correo no se ha registrado. Favor de revisarlo.')

class Registro_forma(FlaskForm):
    email=StringField('Correo electrónico:',validators=[DataRequired(),Email()])
    usuario=StringField('Usuario:',validators=[DataRequired()])
    password=PasswordField('Contraseña:',validators=[DataRequired(),EqualTo('confirm_password',message='¡La contraseña debe coincidir!')])
    confirm_password=PasswordField('Confirmar contraseña:',validators=[DataRequired()])
    registrar=SubmitField('Registrarse')

    def checar_email(self,email):
        if Usuarios.query.filter_by(email=email).first():
            raise ValidationError('Este correo ya fue registrado. Proporciona otro o recupera tu contraseña')

    def checar_usuario(self,usuario):
        if Usuarios.query.filter_by(usuario=usuario).first():
            raise ValidationError('Este usuario ya fue registrado. Proporciona otro o recupera tu contraseña')

class Cambiar_password_forma(FlaskForm):
    email=StringField('Correo electrónico:',validators=[DataRequired(),Email()])
    ant_password=PasswordField('Contraseña anterior:',validators=[DataRequired()])
    nvo_password=PasswordField('Contraseña nueva:',validators=[DataRequired(),EqualTo('confirm_nvo_password',message='¡La contraseña nueva debe coincidir!')])
    confirm_nvo_password=PasswordField('Confirmar contraseña nueva:',validators=[DataRequired()])
    cambiar=SubmitField('Cambiar')

    def revisar_email(self,email):
        if Usuarios.query.filter_by(email=email).first() is None:
            raise ValidationError('Este correo no se ha registrado. Favor de revisarlo.')
#########
class Agregar_sepomex_forma(FlaskForm):
    archivo=FileField('Seleccione el archivo con el catálogo de SEPOMEX:', validators=[FileRequired('Seleccione un archivo .TXT'),FileAllowed(['txt'],'El archivo selecionado no es del tipo TXT')])
    accion=RadioField('¿Qué deseas hacer?',choices=[('Eliminar','Eliminar el catálogo'),('Agregar','Agregar catálogo')])
    #fac_mod=SelectField('¿Cuál factor deseas modificar?',choices=[('0','')])
    realizar=SubmitField('Realizar')

class Agregar_solicitud_forma(FlaskForm):

    def anio_nac(anio_ini,n_anio):
        l_anios=[]
        a=0
        while a<n_anio:
            x=(str(anio_ini),str(anio_ini))
            l_anios.append(x)
            a=a+1
            anio_ini=anio_ini+1
        return l_anios

    lista_anios=anio_nac(1950,80)

    ap_paterno=StringField('Apellido paterno:',validators=[DataRequired('Debe proporcionar su primer apellido')])
    ap_materno=StringField('Apellido materno:')
    nombres=StringField('Nombres:',validators=[DataRequired('Debe proporcionar al menos un nombre')])
    curp=StringField('CURP:',validators=[DataRequired('Debe proporcionar su CURP')])
    rfc=StringField('RFC:',validators=[DataRequired('Debe proporcionar su RFC')])
    nss=StringField('Número de Seguridad Social:',validators=[DataRequired('Debe proporcionar su NSS')])
    dia_nac=SelectField('Día de nacimiento:',choices=[('01','01'),('02','02'),('03','03'),('04','04'),('05','05'),('06','06'),('07','07'),('08','08'),('09','09'),('10','10'),('11','11'),('12','12'),('13','13'),('14','14'),('15','15'),('16','16'),('17','17'),('18','18'),('19','19'),('20','20'),('21','21'),('22','22'),('23','23'),('24','24'),('25','25'),('26','26'),('27','27'),('28','28'),('29','29'),('30','30'),('31','31')])
    mes_nac=SelectField('Mes de nacimiento:',choices=[('01','Enero'),('02','Febrero'),('03','Marzo'),('04','Abril'),('05','Mayo'),('06','Junio'),('07','Julio'),('08','Agosto'),('09','Septiembre'),('10','Octubre'),('11','Noviembre'),('12','Diciembre')])
    anio_nac=SelectField('Año de nacimiento:',choices=lista_anios)
    edo_civil=RadioField('Estado civil:',choices=[('S','Soltero'),('C','Casado'),('O','Otro')])

    c_estado=SelectField('Entidad federativa:',choices=[('0','')])
    c_mnpio=SelectField('Municipio:',choices=[('0','')])
    c_tipo_asenta=SelectField('Tipo de asentamiento:',choices=[('0','')])
    id_asenta_cpcons=SelectField('Asentamiento:',choices=[('0','')])
    calle=StringField('Calle:',validators=[DataRequired('Debe especificar la calle donde vive')])
    n_ext=StringField('Número exterior:',validators=[DataRequired('Debe especificar el número o lote de su domicilio')])
    n_int=StringField('Número interior:')
    tel=StringField('Teléfono de contacto:',validators=[DataRequired('Debe proporcionar un teléfono en el cual podamos localizarlo')])
    email=StringField('Correo electrónico:',validators=[DataRequired('Debe proporcionar una dirección electrónica personal'),Email('Dirección no válida')])


    accion=RadioField('¿Qué deseas hacer?',choices=[('Modificar','Modificar una solicitud'),('Agregar','Nueva solicitud')])
    #fac_mod=SelectField('¿Cuál factor deseas modificar?',choices=[('0','')])
    realizar=SubmitField('Realizar')

    buscar_mun=SubmitField('Buscar municipio')
    buscar_tipo_asenta=SubmitField('Buscar tipo de asentamiento')
    buscar_asenta=SubmitField('Buscar asentamiento')


class Agregar_documentos_forma(FlaskForm):
    ine=FileField('Identificación oficial:', validators=[FileRequired('Seleccione un archivo en formato PDF, JPG, JPEG o PNG'),FileAllowed(['jpg'],'El archivo selecionado no es del tipo PDF,JPG,JPEG,PNG')])
    comp_domicilio=FileField('Comprobante de domicilio:', validators=[FileRequired('Seleccione un archivo en formato PDF, JPG, JPEG o PNG'),FileAllowed(['pdf,jpg,jpeg,png'],'El archivo selecionado no es del tipo PDF,JPG,JPEG,PNG')])
    ingresos_1=FileField('Último comprobante de ingresos:', validators=[FileRequired('Seleccione un archivo en formato PDF, JPG, JPEG o PNG'),FileAllowed(['pdf,jpg,jpeg,png'],'El archivo selecionado no es del tipo PDF,JPG,JPEG,PNG')])
    ingresos_2=FileField('Comprobante de ingresos de la quincena anterior:', validators=[FileRequired('Seleccione un archivo en formato PDF, JPG, JPEG o PNG'),FileAllowed(['pdf,jpg,jpeg,png'],'El archivo selecionado no es del tipo PDF,JPG,JPEG,PNG')])
    ingresos_3=FileField('Comprobante de ingresos de la segunda quincena inmediata anterior:', validators=[FileRequired('Seleccione un archivo en formato PDF, JPG, JPEG o PNG'),FileAllowed(['pdf,jpg,jpeg,png'],'El archivo selecionado no es del tipo PDF,JPG,JPEG,PNG')])
    ingresos_4=FileField('Comprobante de ingresos de la tercera quincena inmediata anterio:', validators=[FileRequired('Seleccione un archivo en formato PDF, JPG, JPEG o PNG'),FileAllowed(['pdf,jpg,jpeg,png'],'El archivo selecionado no es del tipo PDF,JPG,JPEG,PNG')])

    #accion=RadioField('¿Qué deseas hacer?',choices=[('Eliminar','Eliminar el catálogo'),('Agregar','Agregar catálogo')])
    #fac_mod=SelectField('¿Cuál factor deseas modificar?',choices=[('0','')])
    realizar=SubmitField('Enviar')


###############################################################################################
class Umbral_k_forma(FlaskForm):
    umbral=StringField('Actualizar umbral:')
    
    cambiar_umbral=SubmitField('Modificar umbral de crédito')
    
    #agregar_umbral=SubmitField('Agregar umbral de crédito')


class Agregar_sec_forma(FlaskForm):
    sec= StringField('Indica el nombre de la sección:')
    puntos=StringField('Peso:')
    sec_mod=SelectField('Indica la sección que deseas modificar:',choices=[('0','')])
    umbral=StringField('Umbral de crédito:')
    accion=RadioField('¿Qué deseas hacer?',choices=[('Modificar','Modificar sección'),('Agregar','Nueva sección')])


    realizar=SubmitField('Realizar')
    
    cambiar_umbral=SubmitField('Modificar umbral de crédito')
    agregar_umbral=SubmitField('Agregar umbral de crédito')

    def checar_sec(self,sec):
        if Secciones.query.filter_by(sec=sec).first():
            raise ValidationError('Esta sección ya fue registrada anteriormente. No es necesario que lo vuelva a hacer.')

class Agregar_factor_forma(FlaskForm):
    sec=SelectField('Indica la sección a la que pertenece la pregunta:',choices=[('0','')])
    fac= StringField('Factor:')
    desc= TextAreaField('Descripción del factor:')
    puntos=StringField('Puntaje:')
    accion=RadioField('¿Qué deseas hacer?',choices=[('Modificar','Modificar un factor existente'),('Agregar','Agregar un factor nuevo')])
    fac_mod=SelectField('¿Cuál factor deseas modificar?',choices=[('0','')])
    realizar=SubmitField('Realizar')

    def checar_fac(self,fac):
        if Factores.query.filter_by(fac=fac).first():
            raise ValidationError('Esta factor ya fue registrado anteriormente. No es necesario que lo vuelva a hacer.')

class Agregar_factor_forma_masivo(FlaskForm):
    #sec=SelectField('Indica la sección a la que pertenece la pregunta:',choices=[('0','')])
    archivo=FileField('Seleccione el archivo con los factores:', validators=[FileRequired('Seleccione un archivo .CSV'),FileAllowed(['csv'],'El archivo selecionado no es del tipo CSV')])
    accion=RadioField('¿Qué deseas hacer?',choices=[('Eliminar','Eliminar todos los factores'),('Agregar','Agregar factores')])
    #fac_mod=SelectField('¿Cuál factor deseas modificar?',choices=[('0','')])
    realizar=SubmitField('Realizar')

    def checar_fac(self,fac):
        if Factores.query.filter_by(fac=fac).first():
            raise ValidationError('Esta factor ya fue registrado anteriormente. No es necesario que lo vuelva a hacer.')


class Agregar_respuesta_forma(FlaskForm):
    sec=SelectField('Indica la sección:',choices=[('0','')])
    fac= SelectField('Indica el factor (pregunta) al que pertenece la respuesta:',choices=[('0','')])
    resp=StringField('Indica la respuesta que deseas agregar')
    puntos=StringField('Puntaje:')
    resp_mod=SelectField('¿Cuál respuesta deseas modificar?',choices=[('0','')])
    accion=RadioField('¿Qué deseas hacer?',choices=[('Modificar','Modificar una respuesta'),('Agregar','Agregar una respuesta')])

    realizar=SubmitField('Realizar')

class Agregar_respuesta_forma_masivo(FlaskForm):
    #sec=SelectField('Indica la sección a la que pertenece la pregunta:',choices=[('0','')])
    archivo=FileField('Seleccione el archivo con las respuestas:', validators=[FileRequired('Seleccione un archivo .CSV'),FileAllowed(['csv'],'El archivo selecionado no es del tipo CSV')])
    accion=RadioField('¿Qué deseas hacer?',choices=[('Eliminar','Eliminar todos las respuestas'),('Agregar','Agregar respuestas')])
    #fac_mod=SelectField('¿Cuál factor deseas modificar?',choices=[('0','')])
    realizar=SubmitField('Realizar')

class Config_email_inst_forma(FlaskForm):
    email=StringField('Correo electrónico de la administración:',validators=[DataRequired('Indique la dirección de correo institucional'),Email('Cuenta incorrecta')])
    password=PasswordField('Contraseña',validators=[InputRequired('Indique la contraseña')])
    realizar=SubmitField('Agregar/Modificar')

    def checar_email(self):
        if Config_email_inst.query.first():
            return True
        else:
            return False

class Config_fondo_principal_forma(FlaskForm):
    fondo_principal=FileField('Indique la imagen del fondo principal del sitio:', validators=[FileAllowed(['jpg','png','pdf'])])
    actualizar=SubmitField('Actualizar')

class Cat_doctos_forma(FlaskForm):
    accion=RadioField('¿Qué deseas hacer?',choices=[('Agregar','Agregar documento'),('Eliminar','Eliminar nuevo documento')])
    documento=StringField('Nombre del documento:')
    documento_mod=SelectField('Indica el documento que deseas eliminar',choices=[('0','')])
    tipo=SelectField('Documento propio del:',choices=[('1','Solicitante'),('2','Crédito')])
    
    realizar=SubmitField('Realizar')


# class Credit_score_card_model(FlaskForm):
#     try:
#         conexion=sqlite3.connect("data.sqlite")
#         consulta="SELECT id,fac FROM factores"
#         factores=pd.read_sql(consulta,conexion)
#         factores=factores.set_index('id')
#         print(factores)
#         for i in factores.index:
#             locals()['fac_{}'.format(i)]=SelectField(factores['fac'].loc[i],choices=[('0','X')])
#
#     except pd.io.sql.DatabaseError:
#         pass
#
#     realizar=SubmitField('Enviar respuestas')

##############################

class Agregar_inscripcion_forma(FlaskForm):
    tipo=RadioField('Tipo de contribuyente:',choices=[('1','RIF'),('2','Personas físicas con actividad empresarial'),('3','Personas morales')])
    nombres=StringField('Nombres:')
    ap_pat=StringField('Apellido paterno')
    ap_mat=StringField('Apellido materno')
    rfc=StringField('Clave del Registro Federal de Contribuyentes')
    curp=StringField('Clave Ùnica de Registro de Población')
    dia_nac=SelectField('Día de nacimiento:',choices=[('01','01'),('02','02'),('03','03'),('04','04'),('05','05'),('06','06'),('07','07'),('08','08'),('09','09'),('10','10'),('11','11'),('12','12'),('13','13'),('14','14'),('15','15'),('16','16'),('17','17'),('18','18'),('19','19'),('20','20'),('21','21'),('22','22'),('23','23'),('24','24'),('25','25'),('26','26'),('27','27'),('28','28'),('29','29'),('30','30'),('31','31')])
    mes_nac=SelectField('Mes de nacimiento:',choices=[('01','Enero'),('02','Febrero'),('03','Marzo'),('04','Abril'),('05','Mayo'),('06','Junio'),('07','Julio'),('08','Agosto'),('09','Septiembre'),('10','Octubre'),('11','Noviembre'),('12','Diciembre')])
    anio_nac=SelectField('Año de nacimiento:',choices=[('','')])
    email=StringField('Correo electrónico:')
    tel=StringField('Teléfono móvil:')
    dir=TextAreaField('Dirección')
    cve_ent=SelectField('Entidad federativa:',choices=[('0','Indica un Estado')])
    cve_mun=SelectField('Municipio:',choices=[('0','Indica un Municipio')])
    accion=RadioField('¿Qué deseas hacer?',choices=[('Modificar','Modificar inscripción'),('Agregar','Realizar inscripción')])

    rfc_mod=SelectField('Indica el RFC de la persona cuya información deseas modificar',choices=[('0','')])
    realizar=SubmitField('Realizar')






#############################
class Agregar_masiva_if_forma(FlaskForm):
    archivo=FileField('Seleccione el archivo con la información:', validators=[FileRequired('Seleccione un archivo .CSV'),FileAllowed(['csv'],'El archivo selecionado no es del tipo CSV')])
    cargar=SubmitField('Cargar')

class Agregar_cat_conta_ubd_forma(FlaskForm):
    concepto= StringField('Concepto contable:')
    #id_inst= SelectField('Institución de la UBD:',choices=[('0','')])

    accion=RadioField('¿Qué deseas hacer?',choices=[('Modificar','Modificar un catálogo contable'),('Agregar','Agregar un nuevo concepto')])
    concepto_mod=SelectField('¿Cuál concepto desea modificar?',choices=[('0','')])
    realizar=SubmitField('Realizar')

    def checar_concepto(self,concepto):
        if Cat_conta_ubd.query.filter_by(concepto=concepto).first():
            raise ValidationError('Esta concepto ya fue registrado anteriormente. No es necesario que lo vuelva a hacer.')

class Agregar_masiva_cat_conta_ubd_forma(FlaskForm):
    accion=RadioField('¿Qué deseas hacer?',choices=[('Eliminar','Eliminar catálogo contable'),('Agregar','Agregar un nuevo catálogo')])
    #id_inst=SelectField('Indica la institución:',choices=[('0','')])
    archivo=FileField('Seleccione el archivo con la información:', validators=[FileRequired('Seleccione un archivo .CSV'),FileAllowed(['csv'],'El archivo selecionado no es del tipo CSV')])
    cargar=SubmitField('Realizar')

class Agregar_estructura_ubd_forma(FlaskForm):
    cuenta= SelectField('Concepto contable:',choices=[('0','')])
    cuenta_padre= SelectField('Pertenece a:',choices=[('0','')])
    mult=RadioField('¿Cómo se afecta al rubro mayor (cuenta padre)?',choices=[('1','Suma'),('-1','Resta')])
    accion=RadioField('¿Qué deseas hacer?',choices=[('Modificar','Modificar una relación contable'),('Agregar','Agregar un nueva relación contable')])

    realizar=SubmitField('Realizar')

class Agregar_masiva_estructura_ubd_forma(FlaskForm):
    accion=RadioField('¿Qué deseas hacer?',choices=[('Eliminar','Eliminar estructura contable'),('Agregar','Agregar nueva estructura contable')])
    archivo=FileField('Seleccione el archivo con la información:', validators=[FileRequired('Seleccione un archivo .CSV'),FileAllowed(['csv'],'El archivo selecionado no es del tipo CSV')])
    realizar=SubmitField('Realizar')

class Agregar_edos_fin_forma(FlaskForm):
    id_if= SelectField('intermedirio financiero:',choices=[('0','')])
    anio= SelectField('Año:',choices=[('0','')])
    mes= SelectField('Mes:',choices=[('01','Enero'),('02','Febrero'),('03','Marzo'),('04','Abril'),('05','Mayo'),('06','Junio'),('07','Julio'),('08','Agosto'),('09','Septiembre'),('10','Octubre'),('11','Noviembre'),('12','Diciembre')])
    archivo=FileField('Seleccione el archivo con la información:', validators=[FileRequired('Seleccione un archivo .CSV'),FileAllowed(['csv'],'El archivo selecionado no es del tipo CSV')])
    accion=RadioField('¿Qué deseas hacer?',choices=[('Eliminar','Eliminar los estados financieros de un intermediario'),('Agregar','Agregar información contable')])

    realizar=SubmitField('Realizar')

class Descargar_solicitud_forma(FlaskForm):
    #Descargar solicitud
    rfc_registrado=SelectField('Seleccione un RFC:',choices=[('0','')])
    descargar=SubmitField('Descargar solicitud')

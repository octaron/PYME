
import os
#(pip install pillow para poder importar Image)
from PIL import Image
from flask import url_for, current_app, request, flash
import pandas as pd

#Parámetros:
#selec_foto:foto seleccionada
#nvo_nombre:nombre con el que se va a guardar la foto en el servidor
#ruta_app:ruta en la que se guardará la foto en el servidor (app; ejemplo:/static/fotos_clases)
#ancho: ancho en pixeles con el que se guarda la foto
#alto: alto en pixeles con el que se guarda la foto
class Subir_archivos():
    #Nota: Si ancho==0 and alto==0, la foto se guarda en su tamaño original.
    def agregar_foto(selec_foto,nvo_nombre,ruta_app,ancho,alto):
        nombre_archivo=selec_foto.filename
        ext_tipo=nombre_archivo.split('.')[-1]
        nombre_almacenamiento=str(nvo_nombre)+'.'+ext_tipo
        ruta=os.path.join(current_app.root_path,ruta_app,nombre_almacenamiento)

        if ancho==0 and alto==0:
            foto=Image.open(selec_foto)
        else:
            output_size=(ancho,alto)
            foto=Image.open(selec_foto)
            foto.thumbnail(output_size)
            ##output_size=(ancho,alto)
            #foto=Image.open(selec_foto)
            ##foto.thumbnail(output_size)
            foto.save(ruta)

        return nombre_almacenamiento

    def agregar_archivo(self,carpeta,archivo):
        self.carpeta=carpeta+"/"
        #self.archivo=archivo

        APP_ROOT=os.path.dirname(os.path.abspath(__file__))
        self.target=os.path.join(APP_ROOT,self.carpeta)

        if not os.path.isdir(self.target):
            os.mkdir(self.target)

        self.nombre_archivo=archivo.filename
        self.destino="/".join([self.target,self.nombre_archivo])
        archivo.save(self.destino)
        self.x='Archivo subido al servidor'
        self.mensaje=[True,self.x]
        #flash(mensaje)


#Una vez almacenada la información en un DataFrame, se borra del servidor el archivo
#recién subido
    #os.remove(destino)
    def agregar_doc_digital(self,carpeta,archivo,nvo_nombre,ancho,alto,formato):
        #nombre_archivo=archivo.filename
        #ext_tipo=nombre_archivo.split('.')[-1]
        nombre_almacenamiento=str(nvo_nombre)+'.'+formato
        print(nombre_almacenamiento)

        self.carpeta=carpeta
        #self.archivo=archivo

        APP_ROOT=os.path.dirname(os.path.abspath(__file__))
        self.target=os.path.join(APP_ROOT,self.carpeta)

        if not os.path.isdir(self.target):
            os.mkdir(self.target)

        self.nombre_archivo=nombre_almacenamiento
        print(self.nombre_archivo)
        self.destino="/".join([self.target,self.nombre_archivo])
        print(self.destino)
        #output_size=(ancho,alto)
        #doc=Image.open(archivo)
        #doc.thumbnail(output_size)
        try:
            archivo.save(self.destino)
        except AttributeError:
            pass
        else:
            self.x='Archivo subido al servidor'
            self.mensaje=[True,self.x]

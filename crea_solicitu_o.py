from fpdf import FPDF
import requests
from api_key import *

        
class PDF(FPDF):
    
    def header(self):
        # Logo
        #self.image('C:/Users/ollin.davila/Documents/REFIN/static/logo.png', 15, 10, 33)
        self.image('./static/logo.png',15,10,50)
        # Arial bold 15
        self.set_font('Arial', 'B', 8)
        # Calcular ancho del texto (title) y establecer posición
        w = self.get_string_width('SOLICITUD DE CRÉDITO') + 6
        self.set_x((210 - w) / 2)
        # Colores del marco, fondo y texto
        self.set_draw_color(188, 149, 91)
        self.set_fill_color(28, 91, 77)
        self.set_text_color(255,255,255)
        # Grosor del marco (1 mm)
        self.set_line_width(1)
        # Titulo
        self.cell(w, 9, 'SOLICITUD DE CRÉDITO', 1, 1, 'C', 1)
        # Salto de línea
        self.ln(10)
    '''
    def footer(self):
        # Posición a 1.5 cm desde abajo
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Color de texto en gris
        self.set_text_color(128)
        # Numero de pagina
        self.cell(0, 10, 'Página ' + str(self.page_no()), 0, 0, 'C')

    '''
    
    def section_title(self, label):
        # Arial 12
        self.set_font('Arial', 'B', 7.5)
        # Color de fondo
        self.set_fill_color(28, 91, 77)
        #Color de fuente
        #self.set_text_color(188,149,91)
        self.set_text_color(255,255,255)
        # Titulo
        self.cell(0, 4, '%s' % (label), 0, 1, 'C', 1)
        # Salto de línea
        self.ln(2)

    
    def datos_credito(self,tamano_fuente):
        epw = self.w - 2*self.l_margin
        self.set_font('Arial', '', tamano_fuente)
        th = self.font_size
        
        #Color de texto
        self.set_text_color(0,0,0)
        self.cell(epw/2, 2*th, 'Folio:',0)
        self.cell(epw/2, 2*th, 'Promoción:',0)
        self.ln(2*th)
        
        self.cell(epw/3, 2*th, 'Importe del crédito:',0)
        self.cell(epw/3, 2*th, 'Importe total del crédito:',0)
        self.cell(epw/3, 2*th, 'Tasa mensual:',0)
        self.ln(2*th)
        
        self.cell(epw/3, 2*th, 'Importe de c/u  de los pagos del plazo:',0)
        self.cell(epw/3, 2*th, 'Sucursal:',0)
        self.cell(epw/3, 2*th, 'Asesor:',0)
        self.ln(2*th)
        
        self.cell(epw/4, 2*th, 'Crédito:',0)
        self.ln(2*th)

    def crea_mapa(direccion,guardar_como):
        url_maps = "https://maps.googleapis.com/maps/api/staticmap?"
        center = direccion
        zoom = "18"
        size = '600x300'
        format ='PNG'

        params={'center':center,'zoom':zoom,'size': size,'key':api_key}

        ubicacion=requests.get(url_maps,params=params)
        print(ubicacion.url)
        img_data= ubicacion.content
        
        with open('C:/Users/octavio.salazar/Desktop/MiPYME/mapa_ubicacion/'+guardar_como +'.PNG', 'wb') as handler:
            handler.write(img_data)

    def info_solicitud(self,title_solicitante,
    ap_paterno,
    ap_materno,
    nombres,
    edo_civil,
    curp,
    rfc,
    nss,
    fec_nacimiento,
    calle,
    n_ext,
    n_int,
    asentamiento,
    municipio,
    estado,
    tel,
    email,
    tamano_fuente):
        self.section_title(title_solicitante)
        epw = self.w - 2*self.l_margin
        self.set_font('Arial', '', tamano_fuente)
        th = self.font_size
        
        #Color de texto
        self.set_text_color(0,0,0)
        self.cell(epw/2, 2*th, 'Apellido paterno: '+ ap_paterno,0)
        self.cell(epw/2, 2*th, 'Apellido materno: '+ ap_materno,0)
        self.ln(2*th)
        
        self.cell(epw/3, 2*th, 'Nombres: '+ nombres,0)
        self.cell(epw/3, 2*th, 'Estado civil: '+edo_civil,0)
        self.cell(epw/3, 2*th, 'CURP: '+curp,0)
        self.ln(2*th)
        
        self.cell(epw/3, 2*th, 'RFC: '+rfc,0)
        self.cell(epw/3, 2*th, 'Número de seguridad social: '+nss,0)
        self.cell(epw/3, 2*th, 'País de nacimiento: ',0)
        self.ln(2*th)
        
        self.cell(epw/4, 2*th, 'Nacionalidad: ',0)
        self.cell(epw/4, 2*th, 'Entidad federativa de nacimiento: ',0)
        self.cell(epw/4, 2*th, 'Fecha de nacimiento: '+fec_nacimiento,0)
        self.cell(epw/4, 2*th, 'Género: ',0)
        self.ln(2*th)
        
        self.cell(epw/4, 2*th, 'Domicilio actual calle: '+calle,0)
        self.cell(epw/4, 2*th, 'Número ext: '+n_ext,0)
        self.cell(epw/4, 2*th, 'Número int: '+n_int,0)
        self.cell(epw/4, 2*th, 'Ciudad: ',0)
        self.ln(2*th)
        
        self.cell(epw/4, 2*th, 'Colonia: '+asentamiento,0)
        self.cell(epw/4, 2*th, 'Alcaldía o municipio: '+municipio,0)
        self.cell(epw/4, 2*th, 'Estado: '+estado,0)
        self.cell(epw/4, 2*th, 'CP: ',0)
        self.ln(2*th)
        
        self.cell(epw/3, 2*th, 'Entre calles: ',0)
        self.ln(2*th)
        
        self.cell(epw/4, 2*th, 'Teléfono con lada: ',0)
        self.cell(epw/4, 2*th, 'Teléfono celular: '+tel,0)
        self.cell(epw/4, 2*th, 'e-mail personal: '+email,0)
        self.cell(epw/4, 2*th, 'e-mail laboral: ',0)
        self.ln(2*th)
        
        self.cell(epw/3, 2*th, 'Tipo de vivienda: ',0)
        self.cell(epw/3, 2*th, '# dependientes económicos: ',0)
        self.cell(epw/3, 2*th, 'Años residencia: ',0)
        self.ln(2*th)

        #PDF.crea_mapa(calle +' ' + n_ext+ ' ' +n_int+' ' +asentamiento+ ' '+ municipio+ ' '+ estado , 'ubicacion_'+rfc)
        #self.image('C:/Users/octavio.salazar/Desktop/MiPYME/mapa_ubicacion/ubicacion_'+rfc+'.PNG',15,10,50)
        
    def info_empleo(self,title_empleo,tamano_fuente):
        self.section_title(title_empleo)
        epw = self.w - 2*self.l_margin
        self.set_font('Arial', '', tamano_fuente)
        th = self.font_size
        
        #Color de texto
        self.set_text_color(0,0,0)
        self.cell(epw/2, 2*th, 'Empresa en la que labora:',0)
        self.ln(2*th)    
        
        self.cell(epw/3, 2*th, 'Antigüedad:',0)
        self.cell(epw/3, 2*th, 'Años:',0)
        self.cell(epw/3, 2*th, 'Meses:',0)
        self.ln(2*th)    
        
        self.cell(epw/3, 2*th, 'Departamento o área en la que labora:',0)
        self.cell(epw/3, 2*th, 'Puesto:',0)
        self.cell(epw/3, 2*th, 'Jefe inmediato:',0)
        self.ln(2*th)    
        
        self.cell(epw/3, 2*th, 'Domicilio calle:',0)
        self.cell(epw/3, 2*th, 'No. exterior:',0)
        self.cell(epw/3, 2*th, 'No. interior:',0)
        self.ln(2*th)    
        
        self.cell(epw/4, 2*th, 'CP:',0)
        self.cell(epw/4, 2*th, 'Número de empleado:',0)
        self.cell(epw/4, 2*th, 'Colonia:',0)
        self.cell(epw/4, 2*th, 'Alcaldía o municipio:',0)
        self.ln(2*th)
        
        self.cell(epw/3, 2*th, 'Ingreso mensual:',0)
        self.cell(epw/3, 2*th, 'Ciudad o estado:',0)
        self.cell(epw/3, 2*th, 'Tel. con lada:',0)
        self.ln(2*th)
        
    def ref_personal(self,title_referencias,tamano_fuente):
        self.section_title(title_referencias)
        epw = self.w - 2*self.l_margin
        self.set_font('Arial', '', tamano_fuente)
        th = self.font_size
        
        #Color de texto
        self.set_text_color(0,0,0)
        self.cell(3*epw/4, 2*th, 'Nombre:',0)
        self.cell(epw/4, 2*th, 'Teléfono:',0)
        self.ln(2*th)    
        
        self.cell(3*epw/4, 2*th, 'Nombre:',0)
        self.cell(epw/4, 2*th, 'Teléfono:',0)
        self.ln(2*th)    
    
    def ref_bancaria(self,title_ref_bancaria,tamano_fuente):
        self.section_title(title_ref_bancaria)
        epw = self.w - 2*self.l_margin
        self.set_font('Arial', '', tamano_fuente)
        th = self.font_size
        
        #Color de texto
        self.set_text_color(0,0,0)
        self.cell(epw/2, 2*th, 'Banco:',0)
        self.cell(epw/2, 2*th, 'Nombre del titular de la cuenta:',0)
        self.ln(2*th)
        
        self.cell(epw/2, 2*th, 'Número de cuenta:',0)
        self.cell(epw/2, 2*th, 'Número de cuenta clave:',0)
        self.ln(2*th)
        
    def info_crediticia(self,title_info_crediticia,tamano_fuente):
        self.section_title(title_info_crediticia)
        epw = self.w - 2*self.l_margin
        self.set_font('Arial', '', tamano_fuente-2)
        th = self.font_size
        
        #Color de texto
        self.set_text_color(0,0,0)
        
        #Agregar textos desde archivo txt
        #with open('aviso_privacidad.txt', 'rb') as autorizacion:
        #    txt = autorizacion.read().decode('latin-1')
        #self.multi_cell(epw, 1.2*th, txt ,0,1)
        self.ln(2*th)
        
        self.cell(epw, 2*th, 'Nombre del solicitante:',0,1)
        self.cell(epw, 2*th, 'RFC o CURP del solicitante:',0,1)
        self.cell(2*epw/3, 2*th, 'Lugar y fecha en que se firma la autorización:',0)
        self.cell(epw/3, 2*th, '__________________________________',0,1,'C')
        self.cell(2*epw/3, 2*th, 'Nombre de la persona que recaba la autorización:',0)
        self.cell(epw/3, 2*th, 'Firma del (de la) solicitante',0,1,'C')
        self.cell(epw/4, 2*th, 'Fecha de consulta BC:',0,1)
        self.cell(epw/4, 2*th, 'Folio de consulta BC:',0,1)
        
        self.ln(2*th)
        
    def aviso_privacidad(self,title_aviso_privacidad,tamano_fuente):
        self.section_title(title_aviso_privacidad)
        epw = self.w - 2*self.l_margin
        self.set_font('Arial', '', tamano_fuente-3)
        th = self.font_size
        
        #Color de texto
        self.set_text_color(0,0,0)
        
        #Agregar textos desde archivo txt
        with open('aviso_privacidad.txt', 'rb') as autorizacion:
            txt = autorizacion.read().decode('latin-1')
        self.multi_cell(epw, 1.2*th, txt ,0,1)
        self.ln(2*th)
        
        self.cell(epw/2, 2*th, '______________________________________________',0,0,'C')
        self.cell(epw/2, 2*th, '_________________________________',0,1,'C')

        self.cell(epw/2, 2*th, 'Lugar y fecha de firma de aviso de privacidad',0,0,'C')
        self.cell(epw/2, 2*th, 'Firma del (de la) titular',0,0,'C')


'''        
    def print_datos_credito(self,
                            title_solicitante,ap_paterno,ap_materno,nombres,edo_civil,curp,rfc,nss,fec_nacimiento,calle,n_ext,n_int,asentamiento,municipio,estado,tel,email,
                            title_empleo,
                            title_referencias,
                            title_ref_bancaria,
                            title_info_crediticia,
                            title_aviso_privacidad,
                            tamano_fuente):
        self.add_page()
        self.datos_credito(tamano_fuente)
        self.info_solicitud(title_solicitante,ap_paterno,ap_materno,nombres,edo_civil,curp,rfc,nss,fec_nacimiento,calle,n_ext,n_int,asentamiento,municipio,estado,tel,email,tamano_fuente)
        self.info_empleo(title_empleo,tamano_fuente)
        self.ref_personal(title_referencias,tamano_fuente)
        self.ref_bancaria(title_ref_bancaria,tamano_fuente)
        self.info_crediticia(title_info_crediticia,tamano_fuente)
        self.aviso_privacidad(title_aviso_privacidad,tamano_fuente)


pdf = PDF(format='letter')
tamano_fuente = 7
pdf.print_datos_credito('INFORMACIÓN DEL SOLICITANTE',
                        'INFORMACIÓN DEL EMPLEO',
                        'REFERENCIAS DEL EMPLEO',
                        'REFERENCIAS BANCARIAS(CUENTA DE NÓMINA)',
                        'INFORMACIÓN CREDITICIA',
                        'AVISO DE PRIVACIDAD',
                        tamano_fuente)
pdf.output('tuto4.pdf', 'D')
'''
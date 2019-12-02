import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


class Auto_email():
    def enviar_correo(self,destinatario,remitente,password,mensaje,titulo):
        ## "Instanciando" el mensaje:
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = titulo
        ## Agregando el mensaje en el cuerpo del correo:
        msg.attach(MIMEText(mensaje, 'plain'))
        #Indicando el servidor y el puerto:
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.starttls()
        # Ingresando credenciales para enviar el correo
        server.login(msg['From'], password)
        # Enviando el mensaje a través del "server".
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
        #print "successfully sent email to %s:" % (msg['To'])
        print('Ya acabó')

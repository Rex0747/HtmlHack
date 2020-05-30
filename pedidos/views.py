from django.shortcuts import render
import os, random
from configuraciones.models import articulos, configurations , hospitales, gfhs , dispositivos
import datetime
from pedidos.models import pedidos, pedidos_ident, usuarios
from django.db import connection
from configuraciones.excell import Excell
from HtmlHack.settings import MEDIA_ROOT
from HtmlHack.settings import STATIC_ROOT

# Create your views here.
global hospital, disp, user, gfh

def pedido( request ):
    global gfh, hospital, disp, user
    pedid='' ; pedido='' ; lista=[] ; codes={}
    if request.method == 'POST':

        clavesDescartar = ['csrfmiddlewaretoken', 'hospital', 'gfh', 'disp', 'pboton', 'tped', 'user']
        claves = request.POST.keys()
        for i in claves:
            if i in clavesDescartar:
                pass
            else:
                lista.append(i)
        #print('lista: '+ str(lista))
        for i in lista:
            if int(request.POST[i]) > 0:
                codes[i] = request.POST[i] 

        


        if request.POST['gfh'] and request.POST['hospital'] and request.POST['disp'] and request.POST['user']:
            hospital = request.POST['hospital']
            gfh = request.POST['gfh']
            disp = request.POST['disp']
            user = request.POST['user']
            print('User: ' + user + '\t'+ 'disp: ' + disp + '\t'+ 'gfh: ' + gfh + '\t'+ 'hosp: ' + hospital )



            cursor = connection.cursor()
            cursor.execute('SELECT gfh_id FROM configuraciones_dispositivos WHERE nombre = %s ', [ disp ])
            gfh_id = cursor.fetchone()[0]
            print('gfh_id: '+str(gfh_id))
            cursor.execute('SELECT gfh FROM configuraciones_gfhs WHERE id = %s ', [ gfh_id ])
            gfh = cursor.fetchone()[0]
            print('gfh: '+str(gfh))
            cursor.execute('SELECT id FROM configuraciones_dispositivos WHERE nombre = %s', [ disp ])
            disp_id = cursor.fetchone()[0]
            print('disp_id:'+str(disp_id))
            cursor.execute('SELECT id from pedidos_usuarios WHERE ident = %s', [ user ]) 
            user_id = cursor.fetchone()[0]
            print('disp_id:'+str(user_id))

            datos = configurations.objects.filter(gfh=gfh_id, disp=disp_id, hosp_id=2).order_by('modulo','estanteria','ubicacion')
            #consulta = 'SELECT * FROM configuraciones_configurations WHERE gfh ='+str(gfh_id)+' and disp =' +str(disp_id)+ ' and hosp_id = 2'
            #cursor.execute( consulta)
            #datos = cursor.fetchone()[0]
            
            print('Type: '+ str(type(datos)))
            print(str( datos ))

            return render( request, 'pedidos.html',{ 'hospital': hospital, 'gfh': gfh, 'disp': disp, 'user': user, 'datos': datos })


        if request.method == 'POST':
            print(str(codes.keys()) + '\t' + str(codes.values()))
        """ A partir de aqui queda pendiente:
              crear hoja de excel con pedido, solo se usaran los campos codigo, nombre, cantidad
              insertar pedido en bd.
              mandar correo adjunto al correo de Emil automaticamente editado y con el excel adjuno.
              el nombre del excel sera el gfh + _ + dispositivo + _ + fecha   ejemplo  H2NB_IZL013_12042020.xlsx
              este fichero se descargara en una carpeta colgando de media/pedidos/
        """
        #BORRAR
      
        #___________________________

        rnd= ''
        l1 = 'A','B','C','D','E','F','X','Y','Z'
        for i in range(3):
            rnd += random.choice(l1)
        nr = random.randrange(10000,99999)
        rnd += str(nr)
        rnd += random.choice(l1)
        rnd += random.choice(l1)
        # rnd Numero de pedido
        tiempo = str(int(datetime.datetime.now().timestamp()))
        filexcel = 'pedidos/'+gfh+'_'+disp+'_' + tiempo 
        excel = Excell( filexcel )
        head = ['codigo','nombre','cantidad']
        excel.insertar_rangofila( head ,1 ,1 )
        dbped_ident=pedidos_ident()
        indx = 2
        for i, j in codes.items():
            i = i[ : i.find('*')]
            print('CODIGO: ' + i )
            art=articulos.objects.filter( codigo=i )
            print( i + '\t' + art[0].nombre + '\t' + str( j ) )
            #dbped = pedidos( hospitales.objects.get( codigo= hospital ) ,gfhs.objects.get(gfh=gfh), dispositivos.objects.get(nombre=disp), articulos.objects.get(codigo=i), cantidad=j)
            #dbped = pedidos( hospital=hospital ,gfh=gfh, disp=disp, codigo=i, cantidad=j)

            dbped = pedidos()
            dbped.npedido=rnd
            dbped.hospital=hospitales.objects.get( codigo= hospital )
            dbped.gfh=gfhs.objects.get(nombre=disp)
            dbped.disp=dispositivos.objects.get(nombre=disp)
            dbped.codigo=articulos.objects.get(codigo=i)
            dbped.cantidad=j
            dbped.save()

            
            dbped_ident.pedido=rnd
            dbped_ident.user=usuarios.objects.get(ident=user)
            

            lt = ( i, art[0].nombre, j )
            excel.insertar_rangofila( lt , indx, 1)
            indx += 1

        excel.salvarexcell2()
        dbped_ident.save()

        """ dic = { 'remcorreo' : 'peli0747@gmail.com',
                'passwd' : 'Pelikano_0747',
                'destcorreo' : 'peli0747@gmail.com',
                'fileadjunto' : filexcel +'.xlsx',
                'subject' : 'Pedido H6NA',
                'mensaje' : 'Buenos dias adjunto fichero a pedir',
                } """
        """
        envcorreogmail( remcorreo='pedro.luis.jimenez.rico@gmail.com',
        passwd='Pelikano_0747', destcorreo='peli0747@gmail.com',
        fileadjunto=filexcel +'.xlsx', subject='Pedido H6NA',
        mensaje='Buenos dias adjunto fichero a pedir',)
        """

        return render( request, 'pedido2.html',{ 'hospital': hospital, 'gfh': gfh, 'disp': disp, 'user': user }) 

    else:

        return render( request, 'pedidos.html')


def envcorreogmail( remcorreo, passwd, destcorreo, fileadjunto, subject, mensaje ):
    # send_attachment.py
    # import necessary packages
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase  #MIMEImage import MIMEImage
    from email.mime.text import MIMEText
    import smtplib
    from email import encoders
    
    # create message object instance
    msg = MIMEMultipart()
    
    archivo = open( MEDIA_ROOT+'/'+fileadjunto, 'rb')
    # setup the parameters of the message
    password = passwd
    msg['From'] = remcorreo
    msg['To'] = destcorreo

    msg['Subject'] = subject
    
    # attach image to message body
    #msg.attach(MIMEBase( file( fileadjunto ).read()) )

    adjunto_MIME = MIMEBase('application', 'octet-stream')
    # Y le cargamos el archivo adjunto
    adjunto_MIME.set_payload((archivo).read())
    # Codificamos el objeto en BASE64
    encoders.encode_base64(adjunto_MIME)
    # Agregamos una cabecera al objeto
    adjunto_MIME.add_header('Content-Disposition', "attachment; filename= %s" % fileadjunto )
    # Y finalmente lo agregamos al mensaje
    msg.attach(adjunto_MIME)


    msg.attach(MIMEText( mensaje, 'plain') )
    # create server
    server=smtplib.SMTP('smtp.gmail.com: 587') #587
    server.ehlo()
    server.starttls()
    server.ehlo()
    
    # Login Credentials for sending the mail
    server.login(msg['From'], password)
    
    
    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    
    server.quit()
    
    print("successfully sent email to %s:" % (msg['To']))
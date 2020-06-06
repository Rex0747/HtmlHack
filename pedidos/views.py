from django.shortcuts import render
import os, random
from configuraciones.models import articulos, configurations , hospitales, gfhs , dispositivos
import datetime
from pedidos.models import pedidos, pedidos_ident, usuarios
from django.db import connection
from configuraciones.excell import Excell
from configuraciones.views import getIdDB
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

            gfh_id, disp_id, user_id = GetDatos( disp, user )
            datos = configurations.objects.filter( disp=disp_id, hosp_id=2).order_by('modulo','estanteria','ubicacion')
            print('Type: '+ str(type(datos)))
            print(str( datos ))

            return render( request, 'pedidos.html',{ 'hospital': hospital, 'gfh': gfh, 'disp': disp, 'user': user, 'datos': datos })


        if request.method == 'POST':
            print(str(codes.keys()) + '\t' + str(codes.values()))

        rnd = GenNumPedido()
        tiempo = str(int(datetime.datetime.now().timestamp()))
        filexcel = 'pedidos/'+gfh+'_'+disp+'_' + tiempo 
        excel = Excell( filexcel )
        head = ['codigo','nombre','cantidad','gfh','dispositivo','usuario']
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
            

            lt = ( i, art[0].nombre, j , gfh, disp, user )
            excel.insertar_rangofila( lt , indx, 1)
            indx += 1

        excel.salvarexcell2()
        dbped_ident.save()

        """
        envcorreogmail( remcorreo='pedro.luis.jimenez.rico@gmail.com',
        passwd='Pe******7', destcorreo='peli0747@gmail.com',
        fileadjunto=filexcel +'.xlsx', subject='Pedido H6NA',
        mensaje=r'Buenos dias adjunto fichero con material a pedir.\nUn saludo',)
        """

        return render( request, 'pedido2.html',{ 'hospital': hospital, 'gfh': gfh, 'disp': disp, 'user': user }) 

    else:

        return render( request, 'pedidos.html')


def envcorreogmail( remcorreo, passwd, destcorreo, fileadjunto, subject, mensaje ):
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase  #MIMEImage import MIMEImage
    from email.mime.text import MIMEText
    import smtplib
    from email import encoders
    
    msg = MIMEMultipart()
    archivo = open( MEDIA_ROOT+'/'+fileadjunto, 'rb')
    password = passwd
    msg['From'] = remcorreo
    msg['To'] = destcorreo
    msg['Subject'] = subject

    adjunto_MIME = MIMEBase('application', 'octet-stream')
    adjunto_MIME.set_payload((archivo).read())
    encoders.encode_base64(adjunto_MIME)
    adjunto_MIME.add_header('Content-Disposition', "attachment; filename= %s" % fileadjunto )
    msg.attach(adjunto_MIME)

    msg.attach(MIMEText( mensaje, 'plain') )
    server=smtplib.SMTP('smtp.gmail.com: 587') #587
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(msg['From'], password)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    print("Enviado email a %s:" % (msg['To']))



def GenNumPedido():
    rnd= ''
    l1 = 'A','B','C','D','E','F','X','Y','Z'
    for i in range(3):
        rnd += random.choice(l1)
    nr = random.randrange(10000,99999)
    rnd += str(nr)
    rnd += random.choice(l1)
    rnd += random.choice(l1)
    return rnd


def GetDatos( disp, user ):
    gfh_id = getIdDB(dispositivos.objects.filter(nombre=disp),'gfh_id')
    print('gfh_id: '+str(gfh_id))

    gfh = getIdDB(gfhs.objects.filter(id=gfh_id), 'gfh')
    print('gfh: '+str(gfh))

    disp_id = getIdDB(dispositivos.objects.filter(nombre=disp), 'id')
    print('disp_id:'+str(disp_id))

    user_id = getIdDB(usuarios.objects.filter(ident=user),'id')
    print('disp_id:'+str(user_id))

    return gfh_id, disp_id, user_id




"""
    rnd = GenNumPedido()

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



"""
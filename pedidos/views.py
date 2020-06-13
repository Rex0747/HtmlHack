from django.shortcuts import render
from django.http import HttpResponse
import os, random
from configuraciones.models import articulos, configurations , hospitales, gfhs , dispositivos
import datetime
from pedidos.models import pedidos, pedidos_ident, pedidos_temp, usuarios
from django.db import connection
from configuraciones.excell import Excell
from configuraciones.views import getIdDB
from HtmlHack.settings import MEDIA_ROOT
from HtmlHack.settings import STATIC_ROOT
from django.db import connection


# Create your views here.
global hospital, disp, user, gfh

def pedido( request ):
    global gfh, hospital, disp, user
    pedid='' ; pedido='' ; lista=[] ; codes={}
    if request.method == 'POST':
        
        if request.POST.get('txenviar', False):         #request.POST.get('is_private', False)
            datos = None
            filas = None
            #numpedido = None
            #user_temp = None
            #hospital=None;npedido=None;gfh=None;dispositivo=None;codigo=None;cantidad=None
            #ndisp_tmp = -1
            #ped_temp = pedidos_temp.objects.all().values('hospital','gfh','disp','codigo','cantidad','user_temp').order_by('id')
            with connection.cursor() as conn:
                data = 'SELECT  DISTINCT disp_id FROM [pedidos_pedidos_temp] ORDER BY [id] ASC'
                datos = conn.execute(data)
                datos = datos.fetchall()
            #print(str(len(datos)))
            for i in datos:
                fila = 'SELECT * FROM [pedidos_pedidos_temp]  WHERE disp_id='+ str(i[0])
                #fila = pedidos_temp.objects.filter(disp_id=).values('hospital','gfh','disp','codigo','cantidad','user_temp').order_by('id')
                #filas = pedidos_temp.objects.filter(disp_id=i).order_by('id')
                with connection.cursor() as conn:
                    filas = conn.execute(fila)
                    res = filas.fetchall()
                    InsertarPedido(res)
                print('---------------------------------')

            #ped_temp = pedidos_temp.objects.filter(disp_id=).values('hospital','gfh','disp','codigo','cantidad','user_temp').order_by('id')


            """for i in range(len(ped_temp))
                ndisp = ped_temp[i]['disp']
                if ndisp_tmp == -1:
                    ndisp_tmp = ndisp
                    numpedido = GenNumPedido()
                if ndisp == ndisp_tmp:
                    #crear dic con datos de ese pedido
                    hospital = ped_temp[i]['hospital']; gfh = ped_temp[i]['gfh']; dispositivo = ped_temp[i]['disp']
                    codigo = ped_temp[i]['codigo']; cantidad = ped_temp[i]['cantidad']; user_temp = ped_temp[i]['user_temp']
                    npedido = numpedido

                    insertarPedido( hospital, npedido, gfh, dispositivo, codigo, cantidad )
                    
                else:
                    insertarPedido( hospital, npedido, gfh, dispositivo, codigo, cantidad )
                    insertarNumPedido( numpedido, user_temp )
                    numpedido = GenNumPedido()
                    ndisp_tmp = ndisp """


               

            return HttpResponse("Pedido enviado")

        clavesDescartar = ['csrfmiddlewaretoken', 'hospital', 'gfh', 'disp', 'pboton', 'tped', 'user']
        claves = request.POST.keys()
        for i in claves:
            if i in clavesDescartar:
                pass
            else:
                lista.append(i)

        print('lista: '+ str(lista))

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

        Insert_temp( codes, hospital, disp )


        """
        envcorreogmail( remcorreo='pedro.luis.jimenez.rico@gmail.com',
        passwd='Pe******7', destcorreo='peli0747@gmail.com',
        fileadjunto=filexcel +'.xlsx', subject='Pedido H6NA',
        mensaje=r'Buenos dias adjunto fichero con material a pedir.\nUn saludo',)
        """

        return render( request, 'pedido2.html',{ 'hospital': hospital, 'gfh': gfh, 'disp': disp, 'user': user }) 

    else:

        return render( request, 'pedidos.html')

def insertarNumPedido(numpedido, user_temp ):

    dbped_ident=pedidos_ident()
    dbped_ident.pedido=numpedido
    dbped_ident.user=usuarios.objects.get(id=user_temp)
    dbped_ident.save()


def InsertarPedido( datos ):
    #print(str(valor))
    #datos = valor.fetchall()
    user_temp = -1
    npedido = GenNumPedido()
    for i in datos:
        print(str(i))
        hospital = i[5]; gfh = i[4]; dispositivo = i[3]
        codigo = i[2]; cantidad = i[1]; user_temp = i[6]
        ped = pedidos()
        ped.hospital=hospitales.objects.get( id=hospital )
        ped.npedido=npedido
        ped.gfh=gfhs.objects.get(id=gfh)
        ped.disp=dispositivos.objects.get(id=dispositivo)
        ped.codigo=articulos.objects.get(idsel=codigo)
        ped.cantidad=cantidad
        ped.save()
        
    dbped_ident=pedidos_ident()
    dbped_ident.pedido=npedido
    dbped_ident.user=usuarios.objects.get(id=user_temp)
    dbped_ident.save()

    deltem = pedidos_temp.objects.filter(disp=dispositivo).delete()
    


def Insert_temp( codes , hospital, disp ):
    for i, j in codes.items():
        i = i[ : i.find('*')]
        print('CODIGO: ' + i )
        art=articulos.objects.filter( codigo=i )
        print( i + '\t' + art[0].nombre + '\t' + str( j ) )
        dbped = pedidos_temp()
        dbped.hospital=hospitales.objects.get( codigo= hospital )
        dbped.gfh=gfhs.objects.get(nombre=disp)
        dbped.disp=dispositivos.objects.get(nombre=disp)
        dbped.codigo=articulos.objects.get(codigo=i)
        dbped.cantidad=j
        dbped.user_temp=usuarios.objects.get(ident=user)
        dbped.save()


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
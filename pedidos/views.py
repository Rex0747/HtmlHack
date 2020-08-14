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
    lista=[] ; codes={}
    if request.method == 'POST':
        
        if request.POST.get('txenviar', False):         #request.POST.get('is_private', False)
            datos = None
            filas = None
            npedido = None
            user_temp = request.POST['txenviar']  #usuarios.objects.get(ident=user).pk 
            #print(str(user_temp))
            user_temp = usuarios.objects.get(ident=user_temp).pk
            #print(str(user_temp))
            #hospital=None;npedido=None;gfh=None;dispositivo=None;codigo=None;cantidad=None
            #ndisp_tmp = -1
            #ped_temp = pedidos_temp.objects.all().values('hospital','gfh','disp','codigo','cantidad','user_temp').order_by('id')
            with connection.cursor() as conn:
                data = 'SELECT  DISTINCT disp_id FROM [pedidos_pedidos_temp] ORDER BY [id] ASC'
                datos = conn.execute(data)
                datos = datos.fetchall()
            #print(str(len(datos)))
            tmpPed = True
            #npedido = GenNumPedido()
            while(tmpPed == True):
                npedido = GenNumPedido()
                tmpPed = pedidos_ident.objects.filter(pedido=npedido).exists()
                
            filexcel = CrearFicheroExcel()
            for i in datos:
                fila = 'SELECT * FROM [pedidos_pedidos_temp]  WHERE disp_id='+ str(i[0]) +' and user_temp_id =' + str(user_temp) 
                #fila = pedidos_temp.objects.filter(disp_id=).values('hospital','gfh','disp','codigo','cantidad','user_temp').order_by('id')
                #filas = pedidos_temp.objects.filter(disp_id=i).order_by('id')
                with connection.cursor() as conn:
                    filas = conn.execute(fila)
                    res = filas.fetchall()
                    InsertarPedido(res, npedido)
                #print('---------------------------------')
            InsertarAlbaranPedido(user_temp, npedido )
            deltem = pedidos_temp.objects.filter(user_temp_id=user_temp).delete()
            """
            envcorreogmail( remcorreo='pedro.luis.jimenez.rico@gmail.com',
            passwd='R***7', destcorreo='peli0747@gmail.com',
            fileadjunto=filexcel +'.xlsx', subject='Pedido material.',
            mensaje=r'Buenos dias adjunto fichero con material a pedir.\nUn saludo',)
            """
            #ped_temp = pedidos_temp.objects.filter(disp_id=).values('hospital','gfh','disp','codigo','cantidad','user_temp').order_by('id')

            #return HttpResponse("Pedido enviado")
            return render( request, 'pedidos.html' )

        clavesDescartar = ['csrfmiddlewaretoken', 'hospital', 'gfh', 'disp', 'pboton', 'tped', 'user']
        claves = request.POST.keys()
        for i in claves:
            if i in clavesDescartar:
                pass
            else:
                lista.append(i)

        print('lista: '+ str(lista))  #Comentar de nuevo

        for i in lista:
            if int(request.POST[i]) > 0:
                codes[i] = request.POST[i] 

        if request.POST['gfh'] and request.POST['hospital'] and request.POST['disp'] and request.POST['user']:
            hospital = request.POST['hospital']
            gfh = request.POST['gfh']
            disp = request.POST['disp']
            user = request.POST['user']

            userres = usuarios.objects.filter(ident=user).exists()
            print(str(userres))
            if userres == False:
                return HttpResponse("Usuario no valido.")

            #print('User: ' + user + '\t'+ 'disp: ' + disp + '\t'+ 'gfh: ' + gfh + '\t'+ 'hosp: ' + hospital )

            gfh_id, disp_id, user_id, hospital_id = GetDatos( disp, user)
            datos = configurations.objects.filter( disp=disp_id, hosp_id=hospital_id).order_by('modulo','estanteria','ubicacion')
            #print('Type: '+ str(type(datos)))
            #print(str( datos ))
            for i in datos:
                tmp = i.nombre
                i.nombre.nombre = tmp.nombre[0:15]

            return render( request, 'pedidos.html',{ 'hospital': hospital, 'gfh': gfh, 'disp': disp, 'user': user, 'datos': datos })


        if request.method == 'POST':
            print(str(codes.keys()) + '\t' + str(codes.values()))

        Insert_temp( codes, hospital, disp )


        return render( request, 'pedido2.html',{ 'hospital': hospital, 'gfh': gfh, 'disp': disp, 'user': user }) 

    else:

        return render( request, 'pedidos.html')

def insertarNumPedido(numpedido, user_temp ):

    dbped_ident=pedidos_ident()
    dbped_ident.pedido=numpedido
    dbped_ident.user=usuarios.objects.get(id=user_temp)
    dbped_ident.save()


def InsertarPedido( datos, npedido ):
    for i in datos:
        print(str(i))
        hospital = i[5]; gfh = i[4]; dispositivo = i[3]
        codigo = i[2]; cantidad = i[1]; user_temp = i[6]
        ped = pedidos()
        ped.hospital=hospitales.objects.get(id=hospital)
        ped.npedido=npedido
        ped.gfh=gfhs.objects.get(id=gfh)
        ped.disp=dispositivos.objects.get(id=dispositivo)
        ped.codigo=articulos.objects.get(idsel=codigo)
        ped.cantidad=cantidad
        ped.save()
        CrearExcel( codigo, cantidad, gfh, dispositivo, hospital )
        
        
def InsertarAlbaranPedido( user_temp , npedido ):
    dbped_ident=pedidos_ident()
    dbped_ident.pedido=npedido
    dbped_ident.user=usuarios.objects.get(id=user_temp)
    dbped_ident.save()
    #deltem = pedidos_temp.objects.filter(disp_id=disp_id).delete()

    
def CrearExcel(codigo, cantidad, gfh, dispositivo, hospital):
    tiempo = datetime.datetime.now()
    tiempo = str(tiempo.day)+str(tiempo.month)+str(tiempo.year)
    
    filexcel = MEDIA_ROOT + '/pedidos/'+'data' + tiempo + '.xlsx'
    excel = Excell( filexcel )
    excel.cambiar_hoja('data')

    codigo_r = articulos.objects.get(idsel=codigo)
    print('CODIGO_R: '+ str(codigo_r))
    hospital_r = hospitales.objects.get( id=hospital )
    gfh_r = gfhs.objects.get(id=gfh)
    disp_r = dispositivos.objects.get(id=dispositivo)
    nombre_r = articulos.objects.get(codigo=codigo_r.codigo, hospital_id=hospital_r.pk) #Insertar hospital para filtrar
    cantidad_r = cantidad

    nfilas = excel.getnumerofilas()
    lt = (codigo_r.codigo, nombre_r.nombre, cantidad_r, gfh_r.gfh, disp_r.nombre)
    excel.insertar_rangofila( lt , nfilas + 1, 1)
    excel.salvarexcell()


def CrearFicheroExcel():
    tiempo = datetime.datetime.now()
    tiempo = str(tiempo.day)+str(tiempo.month)+str(tiempo.year)
    filexcel = 'pedidos/'+'data' + tiempo
    print( 'fileexcel: '+ filexcel)
    excel = Excell( filexcel )
    excel.createsheet('data')
    excel.cambiar_hoja('data')
    head = ['codigo','nombre','cantidad','gfh','dispositivo']
    excel.insertar_rangofila( head ,1 ,1 )
    excel.deleteSheet('Sheet')
    excel.salvarexcell2()
    return filexcel

def Insert_temp( codes , hospital, disp ):
    for i, j in codes.items():
        i = i[ : i.find('*')]
        print('CODIGO: ' + i )
        hospital_id = getIdDB(gfhs.objects.filter(nombre=disp), 'hp_id_id')
        art=articulos.objects.filter( codigo=i )
        print( i + '\t' + art[0].nombre + '\t' + str( j ) )
        dbped = pedidos_temp()
        dbped.hospital=hospitales.objects.get( codigo= hospital )
        dbped.gfh=gfhs.objects.get(nombre=disp)
        dbped.disp=dispositivos.objects.get(nombre=disp)
        dbped.codigo=articulos.objects.get(codigo=i , hospital_id=hospital_id)
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

    hospital_id = getIdDB(gfhs.objects.filter(gfh=gfh), 'hp_id_id')
    print('hospital_id:'+str(hospital_id))

    return gfh_id, disp_id, user_id, hospital_id

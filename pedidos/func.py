import os, random
from configuraciones.models import articulos, configurations , hospitales, gfhs , dispositivos
import datetime
from pedidos.models import pedidos, pedidos_ident, pedidos_temp, usuarios, pedidos_dc, pedidos_ident_dc
from django.db import connection
from configuraciones.excell import Excell
from configuraciones.views import getIdDB
from HtmlHack.settings import MEDIA_ROOT
from HtmlHack.settings import STATIC_ROOT
from django.db import connection

class funciones:

    #def __init__(self):
        #pass

    @staticmethod
    def getEtiquetas2( code , gfh):
        mtx = code.split('|')
        #print('Code: ', code)
        #print('mtx: ', str(mtx))
        filexcel = funciones.CrearFicheroExcel(gfh)

        listaM = []
        for i in mtx:
            listaT = []
            m = getIdDB( configurations.objects.filter(id=i),'modulo')
            e = getIdDB( configurations.objects.filter(id=i),'estanteria')
            u = getIdDB( configurations.objects.filter(id=i),'ubicacion')
            d = getIdDB( configurations.objects.filter(id=i),'division')
            
            listaT.append( getIdDB( configurations.objects.filter(id=i),'hosp_id') )#1
            listaT.append( getIdDB( configurations.objects.filter(id=i),'gfh') )#4
            gfh = getIdDB(gfhs.objects.filter(id=listaT[1]), 'gfh')
            listaT.append( getIdDB(configurations.objects.filter(id=i),'disp') )#5
            codigo = getIdDB( configurations.objects.filter(id=i),'codigo')
            listaT.append( getIdDB( articulos.objects.filter(codigo=codigo),'idsel') )#2
            listaT.append( getIdDB( configurations.objects.filter(id=i),'pacto') )#3
            #print('rfid: ', str(i))
            #print('codigo_id:', codigo)
            #print('codigo:', codigo_id)

            idnombre = getIdDB( configurations.objects.filter(id=i),'nombre_id')
            nombre = getIdDB(articulos.objects.filter(idsel=idnombre , hospital_id=listaT[0] ), 'nombre')
            
            dispo = getIdDB(dispositivos.objects.filter(id=listaT[2]), 'nombre')
            listaT.append( i ) #6  idconf
            listaT.append( m + '.' + e + '.' + u + '.' + d ) #0
            listaM.append( listaT )
        
                            #2        3       4      5       1            6         0
            #CrearExcel( codigo_id, pacto, gfhid, dispid, hospital_id, idconf, ubicacion )
        file = funciones.CrearExcel_2(listaM , filexcel)

        # envcorreogmail( remcorreo='pedro.*.rico@gmail.com',
        # passwd='yuquspczcabheluw', destcorreo='peli0747@gmail.com',
        # fileadjunto=filexcel +'.xlsx', subject='Pedido material.',
        # mensaje=r'Buenos dias adjunto fichero con material a pedir.\nUn saludo',)
        #yuquspczcabheluw

        return file
        #return HttpResponse('OK')
        #return render(request,'etiquetas.html',{'hospital': hospital_id, 'nombre': nombre ,'codigo': codigo, 'pacto': pacto, 'gfh': gfh, 'disp': dispo })    

    @staticmethod
    def GetDatos( disp, user ):
        gfh_id = getIdDB(dispositivos.objects.filter(nombre=disp),'gfh_id')
        #print('gfh_id: '+str(gfh_id))

        gfh = getIdDB(gfhs.objects.filter(id=gfh_id), 'gfh')
        #print('gfh: '+str(gfh))

        disp_id = getIdDB(dispositivos.objects.filter(nombre=disp), 'id')
        #print('disp_id:'+str(disp_id))

        user_id = getIdDB(usuarios.objects.filter(ident=user),'id')
        #print('disp_id:'+str(user_id))

        hospital_id = getIdDB(gfhs.objects.filter(gfh=gfh), 'hp_id_id')
        #print('hospital_id:'+str(hospital_id))

        return gfh_id, disp_id, user_id, hospital_id

    @staticmethod
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

    @staticmethod
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
        #print("Enviado email a %s:" % (msg['To']))

    @staticmethod
    def Insert_temp( codes , hospital, disp , user ):
        for i, j in codes.items():
            i = i[ : i.find('*')]
            #print('CODIGO: ' + i )
            hospital_id = getIdDB(gfhs.objects.filter(nombre=disp), 'hp_id_id')
            art=articulos.objects.filter( codigo=i )
            #print( i + '\t' + art[0].nombre + '\t' + str( j ) )
            dbped = pedidos_temp()
            dbped.hospital=hospitales.objects.get( codigo= hospital )
            dbped.gfh=gfhs.objects.get(nombre=disp)
            dbped.disp=dispositivos.objects.get(nombre=disp)
            dbped.codigo=articulos.objects.get(codigo=i , hospital_id=hospital_id)
            dbped.cantidad=j
            dbped.user_temp=usuarios.objects.get(ident=user)
            dbped.save()

    @staticmethod
    def CrearFicheroExcel(nombre= None):
        filexcel = None
        tiempo = datetime.datetime.now()
        tiempo = str(tiempo.day)+str(tiempo.month)+str(tiempo.year)
        if nombre:
            filexcel = 'pedidos/'+ nombre + tiempo
        else:
            filexcel = 'pedidos/'+'data' + tiempo
        print( 'fileexcel: '+ filexcel)
        excel = Excell( filexcel )
        excel.createsheet('data')
        excel.cambiar_hoja('data')
        head = ['codigo','nombre','cantidad','gfh','dispositivo','rfid','ubicacion']
        excel.insertar_rangofila( head ,1 ,1 )
        excel.deleteSheet('Sheet')
        excel.salvarexcell2()
        return filexcel

    @staticmethod
    def CrearExcel_2( lista, filexcel=None ):
        print( 'CrearExcel_2_Array: ', str(lista))
        tiempo = datetime.datetime.now()
        tiempo = str(tiempo.day)+str(tiempo.month)+str(tiempo.year)
        if filexcel is None:
            filexcel = MEDIA_ROOT + '/pedidos/'+ 'data' + tiempo + '.xlsx'
        else:
            gfh_temp = gfhs.objects.get( id=lista[0][2] )
            print('GFH: ', gfh_temp.gfh)
            filexcel = MEDIA_ROOT + '/pedidos/'+ gfh_temp.gfh + tiempo + '.xlsx'
        
        print('FileExcel: ', filexcel)
        excel = Excell( filexcel )

        #excel.cambiar_hoja('data')
        
        for i in lista:
                            #2        3       4      5       1            6         0
            #CrearExcel( codigo_id, pacto, gfhid, dispid, hospital_id, idconf, ubicacion )
            #print('CODIGO_ID: ', i[2])
            codigo_r = articulos.objects.get(idsel=i[3] , hospital_id=i[0]) #
            #print('CODIGO_R: '+ str(codigo_r))
            hospital_r = hospitales.objects.get( id=i[0] )
            gfh_r = gfhs.objects.get(id=i[1])
            disp_r = dispositivos.objects.get(id=i[2])
            nombre_r = articulos.objects.get(codigo=codigo_r.codigo, hospital_id=hospital_r.pk) #Insertar hospital para filtrar
            cantidad_r = i[4]
            lt = None
            nfilas = excel.getnumerofilas()
            if len( i ) == 7:
                lt = (codigo_r.codigo, nombre_r.nombre, cantidad_r, gfh_r.gfh, disp_r.nombre, i[5], i[6] )
            else:
                lt = (codigo_r.codigo, nombre_r.nombre, cantidad_r, gfh_r.gfh, disp_r.nombre )
            excel.insertar_rangofila( lt , nfilas + 1, 1)
        excel.salvarexcell()
        return filexcel

    @staticmethod
    def InsertarAlbaranPedido_dc( npedido ):
        dbped_ident=pedidos_ident_dc()
        dbped_ident.pedido=npedido
        dbped_ident.save()

    @staticmethod
    def InsertarAlbaranPedido( user_temp , npedido ):
        dbped_ident=pedidos_ident()
        dbped_ident.pedido=npedido
        dbped_ident.user=usuarios.objects.get(id=user_temp)
        dbped_ident.save()
        #deltem = pedidos_temp.objects.filter(disp_id=disp_id).delete()

    @staticmethod
    def InsertarPedido_dc( datos, npedido = None ):
        print('InsertarPedido DC: ', str(datos))
        nomExcel = 'data'
        listaM = []
        for i in datos:
            #print(str(i))
            listaT = []
            listaT.append( i[0] ) #hospital        0
            listaT.append( i[1] ) #gfh             1
            listaT.append( i[2] ) #disp            2
            listaT.append( i[3] ) #codigo          3
            listaT.append( i[4] ) #cantidad        4
            listaT.append( i[5] ) #codigo          5
            listaT.append( i[6] ) #ubicacion       6
            listaM.append(listaT)
            #user_temp = i[6] 
            if npedido != None:
                ped = pedidos_dc()
                ped.hospital=hospitales.objects.get(id=i[0])
                ped.npedido=npedido
                ped.gfh=gfhs.objects.get(id=i[1])
                #ped.disp=dispositivos.objects.get(id=listaT[2])
                ped.codigo=articulos.objects.get(idsel=i[3])
                ped.cantidad=i[4]
                ped.save()
                #CrearExcel( codigo, cantidad, gfh, dispositivo, hospital )
        filexcel = funciones.CrearFicheroExcel(nomExcel)
        funciones.CrearExcel_2( listaM )

    @staticmethod
    def InsertarPedido( datos, npedido ):
        print('InsertarPedido: ', str(datos))
        listaM = []
        for i in datos:
            #print(str(i))
            listaT = []
            listaT.append( i[5] ) #hospital        0
            listaT.append( i[4] ) #gfh             1
            listaT.append( i[3] ) #dispositivo     2
            listaT.append( i[2] ) #codigo          3
            listaT.append( i[1] ) #cantidad        4
            listaM.append(listaT)

            user_temp = i[6] 
            ped = pedidos()
            ped.hospital=hospitales.objects.get(id=listaT[0])
            ped.npedido=npedido
            ped.gfh=gfhs.objects.get(id=listaT[1])
            ped.disp=dispositivos.objects.get(id=listaT[2])
            ped.codigo=articulos.objects.get(idsel=listaT[3])
            ped.cantidad=listaT[4]
            ped.save()
            #CrearExcel( codigo, cantidad, gfh, dispositivo, hospital )
        funciones.CrearExcel_2( listaM )

    @staticmethod
    def insertarNumPedido(numpedido, user_temp ):
        dbped_ident=pedidos_ident()
        dbped_ident.pedido=numpedido
        dbped_ident.user=usuarios.objects.get(id=user_temp)
        dbped_ident.save()


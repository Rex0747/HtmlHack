import os, random
from configuraciones.models import articulos, configurations , hospitales, gfhs , dispositivos
import datetime
from pedidos.models import pedidos, pedidos_ident, pedidos_temp, usuarios, \
            pedidos_dc, pedidos_ident_dc, datos_email
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
    def splitdatos(mtx, dlm):
        datos = mtx.split(dlm)
        return datos

    @staticmethod
    def getEtiquetas2( code , gfh):     #0 ubic  1 cod  2 nombre 3 pacto  4 gfh  5 disp  6 hosp 7 rfid
        #print('Code: ', code)
        mtx = code.split('|')
        print('mtx: ', str(mtx))
        datos = []
        listaM = []
        for i in mtx:
            datos = i.split('~')
            listaT = []
            listaT.append( datos[0])
            listaT.append( datos[1])
            listaT.append( datos[2])
            listaT.append( datos[3])
            listaT.append( datos[4])
            listaT.append( datos[5])
            listaT.append( datos[6])
            listaT.append( i )
            listaM.append( listaT )

        filexcel = funciones.CrearFicheroExcel(gfh)
        file = funciones.CrearExcel_2(listaM , filexcel)
        
        #funciones.envcorreogmail(fileadjunto=filexcel +'.xlsx', subject='Pedido material.',\
            #mensaje=r'Buenos dias adjunto fichero con material a pedir.\nUn saludo',)
    #    #ifwehvkeekzbcrok
        return file

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
    def envcorreogmail( fileadjunto, subject, mensaje ):
        dataCorreo = datos_email.objects.all()
        remcorreo = dataCorreo[0].ucorreo
        destcorreo = dataCorreo[1].ucorreo
        passwd = dataCorreo[2].ucorreo[ : 16 ]

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
        print('Nombre Fila: ' + str(nombre))
        if nombre:
            filexcel = 'pedidos/'+ nombre + tiempo
        else:
            filexcel = 'pedidos/'+'data' + tiempo
        print( 'fileexcel: '+ filexcel)
        excel = Excell( filexcel )
        excel.createsheet('data')
        excel.cambiar_hoja('data')
        head = ['Ubicacion','Codigo','Nombre','Cantidad','Gfh','Dispositivo','Hospital','Rfid']
        excel.insertar_rangofila( head ,1 ,1 )
        excel.deleteSheet('Sheet')
        excel.salvarexcell2()
        return filexcel

    @staticmethod
    def CrearExcel_2( lista, filexcel=None ): #0 ubic  1 cod  2 nombre 3 pacto  4 gfh  5 disp  6 hosp
        print( 'CrearExcel_2_Array: ', str(lista))
        tiempo = datetime.datetime.now()
        tiempo = str(tiempo.day)+str(tiempo.month)+str(tiempo.year)
        if filexcel is None:
            filexcel = MEDIA_ROOT + '/pedidos/'+ 'data' + tiempo + '.xlsx'
        else:
            print('GFH: ', lista[1])
            filexcel = MEDIA_ROOT + '/pedidos/'+ lista[0][4] + tiempo + '.xlsx'
        
        print('FileExcel: ', filexcel)
        excel = Excell( filexcel )
        #print('Datos Hospital : ', str(lista))
        for i in lista:

            nfilas = excel.getnumerofilas()
            excel.insertar_rangofila( i , nfilas + 1, 1 )
            #print('Se Insert: ' + str(i))
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
            listaT.append( i[5] ) #                5
            listaT.append( i[6] ) #ubicacion       6
            listaM.append(listaT)
            #user_temp = i[6] 
            if npedido != None:
                ped = pedidos_dc()
                ped.hospital= hospitales.objects.get(codigo=i[6]) #hospitales.objects.get(id=i[0])
                ped.npedido=npedido
                ped.gfh = gfhs.objects.get(gfh=i[4])  #gfhs.objects.get(id=i[1])
                #ped.disp=dispositivos.objects.get(id=listaT[2])
                ped.codigo= articulos.objects.get(codigo=i[1], hospital_id=ped.hospital.id ) #articulos.objects.get(idsel=i[3])
                ped.cantidad= i[3] #i[4]
                ped.save()
                #CrearExcel( codigo, cantidad, gfh, dispositivo, hospital )
        filexcel = funciones.CrearFicheroExcel(nomExcel)
        print('Fichero Excel: ', filexcel)
        funciones.CrearExcel_2( listaM )
        #funciones.envcorreogmail(fileadjunto=filexcel, subject='Pedido material.',\
        # mensaje=r'Buenos dias adjunto fichero con material a pedir.\nUn saludo',)
    #    #ifwehvkeekzbcrok
        return filexcel


    @staticmethod
    def InsertarPedido( datos, npedido ):
        print('InsertarPedido: ', str(datos))
        
        listaM = []
        for i in datos:
            print('Hospital: ', i.hospital.pk)
            print('Codigo: ', i.codigo.nombre )
            #print('Ubicacion: ',str(configurations.objects.get(codigo=i.codigo.codigo, hosp=i.hospital.id )))
            #tmp = configurations.objects.get(codigo=i.codigo.codigo, gfh=i.gfh.id, hosp=i.hospital.id )
            listaT = []
            listaT.append( '####')#tmp.modulo+"-"+tmp.estanteria+"-"+tmp.ubicacion+"-"+tmp.division )
            listaT.append( i.codigo.codigo) #codigo         
            listaT.append( i.codigo.nombre)#nombre
            listaT.append( i.cantidad ) #cantidad  
            listaT.append( i.gfh.gfh ) #gfh           
            listaT.append( i.disp.nombre ) #dispositivo   
            listaT.append( i.hospital.codigo ) #hospital      
            listaM.append(listaT)

            user_temp = i.user_temp 
            ped = pedidos()
            ped.hospital= i.hospital
            ped.npedido=npedido
            ped.gfh= i.gfh
            ped.disp= i.disp
            ped.codigo= i.codigo
            ped.cantidad= i.cantidad
            ped.save()
            #CrearExcel( codigo, cantidad, gfh, dispositivo, hospital )
            print('ListaM: ', str(listaM))
        funciones.CrearExcel_2( listaM )

    @staticmethod
    def insertarNumPedido(numpedido, user_temp ):
        dbped_ident=pedidos_ident()
        dbped_ident.pedido=numpedido
        dbped_ident.user=usuarios.objects.get(id=user_temp)
        dbped_ident.save()


from django.shortcuts import render
from django.http import HttpResponse
import os, random
from configuraciones.models import articulos, configurations , hospitales, gfhs , dispositivos, excel
import datetime
from pedidos.models import pedidos, pedidos_ident, pedidos_temp, usuarios, pedidos_dc, pedidos_ident_dc
from django.db import connection
from configuraciones.excell import Excell
from configuraciones.views import getIdDB
from HtmlHack.settings import MEDIA_ROOT
from HtmlHack.settings import STATIC_ROOT
from django.db import connection
import json
#__________________________________________________________
from pedidos.func import funciones

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
                npedido = funciones.GenNumPedido()
                tmpPed = pedidos_ident.objects.filter(pedido=npedido).exists()
                
            filexcel = funciones.CrearFicheroExcel()
            for i in datos:
                #fila = 'SELECT * FROM [pedidos_pedidos_temp]  WHERE disp_id='+ str(i[0]) +' and user_temp_id =' + str(user_temp) 
                pedi = pedidos_temp.objects.filter(disp_id=i[0], user_temp_id=user_temp).select_related('gfh','disp','codigo','user_temp')

                with connection.cursor() as conn:
                    #filas = conn.execute(fila)
                    #res = filas.fetchall()

                    funciones.InsertarPedido(pedi, npedido)
                #print('---------------------------------')
            funciones.InsertarAlbaranPedido(user_temp, npedido )
            deltem = pedidos_temp.objects.filter(user_temp_id=user_temp).delete()
            print('Fichero Excel2: ', filexcel)
            funciones.envcorreogmail( fileadjunto=filexcel +'.xlsx', subject='Pedido material.',\
                    mensaje=r'Buenos dias adjunto fichero con material a pedir.\nUn saludo',)

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

        #print('lista: '+ str(lista))  #Comentar de nuevo

        for i in lista:
            if int(request.POST[i]) > 0:
                codes[i] = request.POST[i] 

        if request.POST['gfh'] and request.POST['hospital'] and request.POST['disp'] and request.POST['user']:
            hospital = request.POST['hospital']
            gfh = request.POST['gfh']
            disp = request.POST['disp']
            user = request.POST['user']
            
            userres = usuarios.objects.filter(ident=user).exists()
            #print(str(userres))
            if userres == False:
                return HttpResponse("Usuario no valido.")

            #print('User: ' + user + '\t'+ 'disp: ' + disp + '\t'+ 'gfh: ' + gfh + '\t'+ 'hosp: ' + hospital )

            gfh_id, disp_id, user_id, hospital_id = funciones.GetDatos( disp, user)
            datos = excel.objects.filter( disp=disp_id, hosp_id=hospital_id).order_by('modulo','estanteria','ubicacion')
            #print('Type: '+ str(type(datos)))
            #print(str( datos ))
            
            for i in datos:
                tmp = i.nombre
                i.nombre.nombre = tmp.nombre[0:15]

            return render( request, 'pedidos.html',{ 'hospital': hospital, 'gfh': gfh, 'disp': disp, 'user': user, 'datos': datos })


        if request.method == 'POST':
            print(str(codes.keys()) + '\t' + str(codes.values()))

        funciones.Insert_temp( codes, hospital, disp , user )


        return render( request, 'pedido2.html',{ 'hospital': hospital, 'gfh': gfh, 'disp': disp, 'user': user }) 

    else:

        return render( request, 'pedidos.html')

def imprimirEtiquetas( request, disp):
    try:
        objGfh = gfhs.objects.get(nombre=disp)
        #print('GFH_ID: ', objGfh)
    except Exception as e:
        return HttpResponse('El dispositivo '+ disp + ' no existe o no tiene cargada la configuracion.')
    
    mtx = None
    try:
        mtx = excel.objects.filter(gfh=objGfh.pk) #, hosp_id=1) #poner bien id hospital
    except Exception as e:
        print('Fallo en seleccion de ids.', e)

    csv = ''
    for i in mtx:

        m = str(i.modulo)
        e = str(i.estanteria)
        u = str(i.ubicacion)
        d = str(i.division)
        codigo = str(str(i.codigo))
        nombre = str(i.nombre.nombre)
        pacto = str(i.pacto)
        gfh = i.gfh
        disp = i.disp
        hosp = i.hosp

        ubic = m + "-" + e + "-" + u +"-" + d
        csv += '|' + ubic + '~' + codigo + '~' + nombre + '~' + pacto + '~' + gfh.gfh + '~' + disp.nombre + '~' + hosp.codigo     #str(i.id)
    csv = csv[1 : ]
    #print(csv)
    #print('Gfh: ', str(gfh))

    fila = funciones.getEtiquetas2( csv, gfh.gfh)
    response = None
    with open( fila , 'rb') as fh:
            print('ENTRO')
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename( fila )
    return response
    #return HttpResponse( 'Final' )

def pedidodc( request, data ):
    mtx = json.loads( data )
    print('TYPE: ',type(mtx))
    #print('MTX: ', mtx)
    listaM = []

    for i in mtx:         #va a hacer falta el codigo ubicacion dispositivo gfh hospital
        try:
            listaT = []
            listaT.append(i['ubicacion'])
            listaT.append(i['codigo'])
            articulo = articulos.objects.get(codigo=listaT[1] , hospital_id=hospitales.objects.get(codigo=i['hospital']).id )
            listaT.insert( 2 , articulo.nombre )
            listaT.append(i['pacto'])
            listaT.append(i['gfh'])
            listaT.append(i['dispositivo'])
            listaT.append(i['hospital'])
            listaM.append(listaT)    
            listaT = []
            
        except Exception as e:
            print('Exception ', str(e))

    #print('ListaM: ' + str(listaM))
    try:
        npedido = funciones.GenNumPedido()
        funciones.InsertarPedido_dc(listaM,npedido)
        funciones.InsertarAlbaranPedido_dc( npedido )
    except Exception as e:
        print('Exception Insertar pedido DC', str(e))
        HttpResponse.status_code = 400
        print('HttpResponseFail: ', HttpResponse.status_code )

    print('HttpResponse: ', HttpResponse.status_code )
    return HttpResponse(HttpResponse.status_code)

def pedidodcCsv( request, data ):
    mtx = data.split('|')
    revisar = mtx[-1]
    #print('data: ', str(data))
    print('mtx: ', str(mtx))
    listaM = []
    for i in mtx:         #va a hacer falta el codigo ubicacion dispositivo gfh hospital
        
        try:
            listaT = i.split('~')
            articulo = articulos.objects.get(codigo=listaT[1] , hospital_id=hospitales.objects.get(codigo=listaT[5]) )
            listaT.insert( 2 , articulo.nombre )
            listaM.append(listaT)
            print(str(listaT))
            listaT = []
            
        except Exception as e:
            print('Exception ', str(e))

    #print('ListaM: ' + str(listaM))
    try:
        npedido = funciones.GenNumPedido()
        funciones.InsertarPedido_dc(listaM,npedido)
        funciones.InsertarAlbaranPedido_dc( npedido )
    except Exception as e:
        print('Exception Insertar pedido DC', str(e))
        HttpResponse.status_code = 400
        print('HttpResponseFail: ', HttpResponse.status_code )

    print('HttpResponse: ', HttpResponse.status_code )
    return HttpResponse(HttpResponse.status_code)
            
            
def imprimirGfh( request):
    gfh = 'expgfh/'
    if request.method == 'POST':
        if request.POST['tbenlace']:
            gfh += request.POST['tbenlace']
    print('LINK: ', gfh)
    return render( request, 'imprimirGfh.html', {'gfh': gfh})


#__________________Prueba DataGrid______________________________


#region
# from datagrid.grids import *
# from blogango.models import BlogEntry

# def grid_data_func(value):
#     return value.upper() 

# def slug_link_func(obj, value):
#     # return  args[0]
#     return 'http://google.com/404/'

# def non_db_col_value(obj):
#     return obj.title

# class BlogGrid(DataGrid):
#     created_by = Column(sortable=True, link=True, cell_clickable=True, css_class='red')
    
#     created_on = DateTimeColumn("created on", format='d b, Y', sortable=True, link=False)
    
#     created_on_since = DateTimeSinceColumn("created on ", sortable=True, db_field='created_on')
    
#     slug = Column("Slug", sortable=False, link=False, link_func=slug_link_func, image_url='/site_media/blogango/images/date_icon.png')
    
#     title = Column("Title", sortable=True, link=False, db_field='title', image_url='http://media.agiliq.com/images/terminal.png', image_width=20, image_height=20, image_alt='foo bar', data_func=grid_data_func)
    
#     blog_title = NonDatabaseColumn("Second Title", sortable=True, link=True, data_func=non_db_col_value)
#     col1 = NonDatabaseColumn(sortable=True, link=True, data_func=non_db_col_value)

# def blog_grid(request):
#     posts = BlogEntry.objects.all()
#     blog_grid = BlogGrid(request=request, queryset=posts, title='Blog Grid View')

#     return blog_grid.render_to_response('blog_grid/blog_grid.html', {'blog_grid': blog_grid})
#endregion

#region

# def insertarNumPedido(numpedido, user_temp ):

#     dbped_ident=pedidos_ident()
#     dbped_ident.pedido=numpedido
#     dbped_ident.user=usuarios.objects.get(id=user_temp)
#     dbped_ident.save()


# def InsertarPedido( datos, npedido ):
#     print('InsertarPedido: ', str(datos))
#     listaM = []
#     for i in datos:
#         #print(str(i))
#         listaT = []
#         listaT.append( i[5] ) #hospital        0
#         listaT.append( i[4] ) #gfh             1
#         listaT.append( i[3] ) #dispositivo     2
#         listaT.append( i[2] ) #codigo          3
#         listaT.append( i[1] ) #cantidad        4
#         listaM.append(listaT)

#         user_temp = i[6] 
#         ped = pedidos()
#         ped.hospital=hospitales.objects.get(id=listaT[0])
#         ped.npedido=npedido
#         ped.gfh=gfhs.objects.get(id=listaT[1])
#         ped.disp=dispositivos.objects.get(id=listaT[2])
#         ped.codigo=articulos.objects.get(idsel=listaT[3])
#         ped.cantidad=listaT[4]
#         ped.save()
#         #CrearExcel( codigo, cantidad, gfh, dispositivo, hospital )
#     CrearExcel_2( listaM )

# def InsertarPedido_dc( datos, npedido ):
#     print('InsertarPedido DC: ', str(datos))
#     listaM = []
#     for i in datos:
#         #print(str(i))
#         listaT = []
#         listaT.append( i[0] ) #hospital        0
#         listaT.append( i[1] ) #gfh             1
#         listaT.append( i[2] ) #disp            2
#         listaT.append( i[3] ) #codigo          3
#         listaT.append( i[4] ) #cantidad        4

#         listaT.append( i[5] ) #codigo          5
#         listaT.append( i[6] ) #ubicacion       6
#         listaM.append(listaT)
#         #user_temp = i[6] 

#         ped = pedidos_dc()
#         ped.hospital=hospitales.objects.get(id=i[0])
#         ped.npedido=npedido
#         ped.gfh=gfhs.objects.get(id=i[1])
#         #ped.disp=dispositivos.objects.get(id=listaT[2])
#         ped.codigo=articulos.objects.get(idsel=i[3])
#         ped.cantidad=i[4]
#         ped.save()
#         #CrearExcel( codigo, cantidad, gfh, dispositivo, hospital )
#     filexcel = CrearFicheroExcel('data')
#     CrearExcel_2( listaM )
        
# def InsertarAlbaranPedido( user_temp , npedido ):
#     dbped_ident=pedidos_ident()
#     dbped_ident.pedido=npedido
#     dbped_ident.user=usuarios.objects.get(id=user_temp)
#     dbped_ident.save()
    #deltem = pedidos_temp.objects.filter(disp_id=disp_id).delete()

# def InsertarAlbaranPedido_dc( npedido ):
#     dbped_ident=pedidos_ident_dc()
#     dbped_ident.pedido=npedido
#     dbped_ident.save()

# def CrearExcel_2( lista, filexcel=None ):
#     print( 'CrearExcel_2_Array: ', str(lista))
#     tiempo = datetime.datetime.now()
#     tiempo = str(tiempo.day)+str(tiempo.month)+str(tiempo.year)
#     if filexcel is None:
#         filexcel = MEDIA_ROOT + '/pedidos/'+ 'data' + tiempo + '.xlsx'
#     else:
#         gfh_temp = gfhs.objects.get( id=lista[0][2] )
#         print('GFH: ', gfh_temp.gfh)
#         filexcel = MEDIA_ROOT + '/pedidos/'+ gfh_temp.gfh + tiempo + '.xlsx'
    
#     print('FileExcel: ', filexcel)
#     excel = Excell( filexcel )

#     #excel.cambiar_hoja('data')
    
#     for i in lista:
#                         #2        3       4      5       1            6         0
#         #CrearExcel( codigo_id, pacto, gfhid, dispid, hospital_id, idconf, ubicacion )
#         #print('CODIGO_ID: ', i[2])
#         codigo_r = articulos.objects.get(idsel=i[3] , hospital_id=i[0]) #
#         #print('CODIGO_R: '+ str(codigo_r))
#         hospital_r = hospitales.objects.get( id=i[0] )
#         gfh_r = gfhs.objects.get(id=i[1])
#         disp_r = dispositivos.objects.get(id=i[2])
#         nombre_r = articulos.objects.get(codigo=codigo_r.codigo, hospital_id=hospital_r.pk) #Insertar hospital para filtrar
#         cantidad_r = i[4]
#         lt = None
#         nfilas = excel.getnumerofilas()
#         if len( i ) == 7:
#             lt = (codigo_r.codigo, nombre_r.nombre, cantidad_r, gfh_r.gfh, disp_r.nombre, i[5], i[6] )
#         else:
#             lt = (codigo_r.codigo, nombre_r.nombre, cantidad_r, gfh_r.gfh, disp_r.nombre )
#         excel.insertar_rangofila( lt , nfilas + 1, 1)
#     excel.salvarexcell()
#     return filexcel

# def CrearFicheroExcel(nombre= None):
#     filexcel = None
#     tiempo = datetime.datetime.now()
#     tiempo = str(tiempo.day)+str(tiempo.month)+str(tiempo.year)
#     if nombre:
#         filexcel = 'pedidos/'+ nombre + tiempo
#     else:
#         filexcel = 'pedidos/'+'data' + tiempo
#     print( 'fileexcel: '+ filexcel)
#     excel = Excell( filexcel )
#     excel.createsheet('data')
#     excel.cambiar_hoja('data')
#     head = ['codigo','nombre','cantidad','gfh','dispositivo','rfid','ubicacion']
#     excel.insertar_rangofila( head ,1 ,1 )
#     excel.deleteSheet('Sheet')
#     excel.salvarexcell2()
#     return filexcel

# def Insert_temp( codes , hospital, disp ):
#     for i, j in codes.items():
#         i = i[ : i.find('*')]
#         #print('CODIGO: ' + i )
#         hospital_id = getIdDB(gfhs.objects.filter(nombre=disp), 'hp_id_id')
#         art=articulos.objects.filter( codigo=i )
#         #print( i + '\t' + art[0].nombre + '\t' + str( j ) )
#         dbped = pedidos_temp()
#         dbped.hospital=hospitales.objects.get( codigo= hospital )
#         dbped.gfh=gfhs.objects.get(nombre=disp)
#         dbped.disp=dispositivos.objects.get(nombre=disp)
#         dbped.codigo=articulos.objects.get(codigo=i , hospital_id=hospital_id)
#         dbped.cantidad=j
#         dbped.user_temp=usuarios.objects.get(ident=user)
#         dbped.save()

# def envcorreogmail( remcorreo, passwd, destcorreo, fileadjunto, subject, mensaje ):
#     from email.mime.multipart import MIMEMultipart
#     from email.mime.base import MIMEBase  #MIMEImage import MIMEImage
#     from email.mime.text import MIMEText
#     import smtplib
#     from email import encoders
    
#     msg = MIMEMultipart()
#     archivo = open( MEDIA_ROOT+'/'+fileadjunto, 'rb')
#     password = passwd
#     msg['From'] = remcorreo
#     msg['To'] = destcorreo
#     msg['Subject'] = subject

#     adjunto_MIME = MIMEBase('application', 'octet-stream')
#     adjunto_MIME.set_payload((archivo).read())
#     encoders.encode_base64(adjunto_MIME)
#     adjunto_MIME.add_header('Content-Disposition', "attachment; filename= %s" % fileadjunto )
#     msg.attach(adjunto_MIME)

#     msg.attach(MIMEText( mensaje, 'plain') )
#     server=smtplib.SMTP('smtp.gmail.com: 587') #587
#     server.ehlo()
#     server.starttls()
#     server.ehlo()
#     server.login(msg['From'], password)
#     server.sendmail(msg['From'], msg['To'], msg.as_string())
#     server.quit()
#     #print("Enviado email a %s:" % (msg['To']))

# def GenNumPedido():
#     rnd= ''
#     l1 = 'A','B','C','D','E','F','X','Y','Z'
#     for i in range(3):
#         rnd += random.choice(l1)
#     nr = random.randrange(10000,99999)
#     rnd += str(nr)
#     rnd += random.choice(l1)
#     rnd += random.choice(l1)
    
#     return rnd

# def GetDatos( disp, user ):
#     gfh_id = getIdDB(dispositivos.objects.filter(nombre=disp),'gfh_id')
#     #print('gfh_id: '+str(gfh_id))

#     gfh = getIdDB(gfhs.objects.filter(id=gfh_id), 'gfh')
#     #print('gfh: '+str(gfh))

#     disp_id = getIdDB(dispositivos.objects.filter(nombre=disp), 'id')
#     #print('disp_id:'+str(disp_id))

#     user_id = getIdDB(usuarios.objects.filter(ident=user),'id')
#     #print('disp_id:'+str(user_id))

#     hospital_id = getIdDB(gfhs.objects.filter(gfh=gfh), 'hp_id_id')
#     #print('hospital_id:'+str(hospital_id))

#     return gfh_id, disp_id, user_id, hospital_id
#endregion
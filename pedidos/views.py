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
from django.db import transaction
global hospital, disp, user, gfh


@transaction.atomic
def pedido( request ):
    global gfh, hospital, disp, user
    lista=[] ; codes={}
    hospi = hospitales.objects.all()

    if request.method == 'POST':
        
        if request.POST.get('txenviar', False):         #request.POST.get('is_private', False)
            datos = None
            filas = None
            npedido = None
            user_temp = request.POST['txenviar']  #usuarios.objects.get(ident=user).pk 
            #print(str(user_temp))
            user_temp = usuarios.objects.get(ident=user_temp).pk
            #print(str(user_temp))
            
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

                funciones.InsertarPedido(pedi, npedido)
                #print('---------------------------------')
            funciones.InsertarAlbaranPedido(user_temp, npedido )
            deltem = pedidos_temp.objects.filter(user_temp_id=user_temp).delete()
            print('Fichero Excel2: ', filexcel)
            funciones.envcorreogmail( fileadjunto=filexcel +'.xlsx', subject='Pedido material.',\
                    mensaje=r'Buenos dias adjunto fichero con material a pedir.\nUn saludo',)

            return render( request, 'pedidos.html')


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

        if request.POST['hospital'] and request.POST['gfh'] and request.POST['disp'] and request.POST['user']:
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
            #print('Datos: ', str( datos ))
            
            for i in datos:
                tmp = i.nombre
                i.nombre.nombre = tmp.nombre[0:15]

            return render( request, 'pedidos.html',{ 'hospital': hospital, 'gfh': gfh, 'disp': disp, 'user': user, 'datos': datos })


        #if request.method == 'POST':
            #print(str(codes.keys()) + '\t' + str(codes.values()))

        funciones.Insert_temp( codes, hospital, disp , user )


        return render( request, 'pedido2.html',{ 'hospital': hospital, 'gfh': gfh, 'disp': disp, 'user': user }) 

    else:

        return render( request, 'pedidos.html', {'hospitales': hospi })

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

@transaction.atomic
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

@transaction.atomic
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

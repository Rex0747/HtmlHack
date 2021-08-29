from django.shortcuts import render, redirect
from django.http import HttpResponse
import os, random
from configuraciones.models import articulos, configurations , hospitales, gfhs , dispositivos, excel
import datetime
from pedidos.models import pedidos, pedidos_ident, pedidos_temp, usuarios, pedidos_dc, pedidos_ident_dc, addRefPedido #addLineaPedido
from django.db import connection
from django.http import HttpResponseRedirect
from configuraciones.excell import Excell
from configuraciones.views import getIdDB
from HtmlHack.settings import MEDIA_ROOT
from HtmlHack.settings import STATIC_ROOT
from django.db import connection
import json
from configuraciones.func import funcConf
from hashlib import blake2b
from pedidos.forms import formGpedidos
#__________________________________________________________
from pedidos.func import funciones
from django.db import transaction
global hospital, disp, user, gfh
#______________RESTFULL_______________
from rest_framework import viewsets
from rest_framework import permissions
from pedidos.serializers import ret_pedidos


@transaction.atomic
def pedido( request ):
    print('Entro en pedido')
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    else:
        request.session.set_expiry (request.session['tiempo'])
        print('TIEMPO SESION: ', str(request.session.get_expiry_age()))

    global gfh, hospital , disp, user, passwd, user_pk
    #gfh=""; hospital=request.session['hospitalCodigo']; disp=""; user=""; passwd=""; user_pk=""
    lista=[] ; codes={}
    hospital = request.session['hospitalCodigo']

    if request.method == 'POST':
        if request.POST.get('usuario', False):         #request.POST.get('is_private', False)
            print('Paso por 1º')
            print(request.POST)
            datos = None
            filas = None
            npedido = None
            user_temp = request.POST['usuario']        #usuarios.objects.get(ident=user).pk
            #hospi_ = request.POST['hosp']
            #user_passwd = request.POST['passwd']
            try:
                #print(str(user_temp))
                user_pk = usuarios.objects.get(ident=user_temp).pk
                #user_Dbpassw = usuarios.objects.get(ident=user_temp).passwd

                #passwd = h.hexdigest()

                #if user_Dbpassw != passwd:
                if user_pk == None:
                    return HttpResponse("Usuario no valido.")
            except Exception as e:
                return HttpResponse("Error. "+str(e))

            #print(str(user_temp))
            #___________________ #POSTGRESS__________________________
            #datos = pedidos_temp.objects.all().distinct('disp_id').order_by('disp_id')   #POSTGRESS
            #print('DT: ', datos[0].disp_id )
            #print('DT: ', datos[1].disp_id )
            #print("Consulta: ",datos.query)

            #_______________________SQLITE_________________________________
            
            with connection.cursor() as conn:
                #data = 'SELECT  DISTINCT disp_id FROM [pedidos_pedidos_temp] ORDER BY [id] ASC' #SQLITE
                data = 'SELECT  DISTINCT  disp_id FROM pedidos_pedidos_temp' #postgress
                datos = conn.execute(data)
                print("Datos: ", datos)
                datos = datos.fetchall()
            #print(str(len(datos)))
            
            tmpPed = True
            #npedido = GenNumPedido()
            while(tmpPed == True):
                npedido = funciones.GenNumPedido()
                tmpPed = pedidos_ident.objects.filter(pedido=npedido).exists()
                
            filexcel = funciones.CrearFicheroExcel()
            for i in datos:
                pedido = pedidos_temp.objects.filter(disp_id=i[0], user_temp_id=user_pk).select_related('gfh','disp','codigo','user_temp') # SQLITE
                #pedido = pedidos_temp.objects.filter(disp_id=dispositivos.objects.get(id=i.disp_id), user_temp_id=user_pk).select_related('gfh','disp','codigo','user_temp') #POSTGRESS

                funciones.InsertarPedido(pedido, npedido)
                #print('---------------------------------')
            funciones.InsertarAlbaranPedido(user_pk, npedido )
            deltem = pedidos_temp.objects.filter(user_temp_id=user_pk).delete()
            print('Fichero Excel2: ', filexcel)

            #Activar en produccion
            funciones.envcorreogmail( fileadjunto=filexcel +'.xlsx', subject='Pedido material.',\
                    mensaje=r'Buenos dias adjunto fichero con material a pedir.\nUn saludo',)

            return render( request, 'pedidos.html') #, { 'hospitales': hospi })

        
        clavesDescartar = ['csrfmiddlewaretoken', 'hospital', 'gfh', 'disp', 'pboton', 'tped', 'user', 'passwd']
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

        
        if request.POST.get('gfh', False) and request.POST['disp'] and request.POST['user'] and request.POST['passwd']:  #request.POST['hospital'] and 
            print('Paso por 2º')
            #hospital =  request.session['hospitalCodigo'] #request.POST['hospital']
            gfh = request.POST['gfh']
            disp = request.POST['disp']
            user = request.POST['user']
            passw = request.POST['passwd']

            h = blake2b(digest_size=25)
            h.update( passw.encode() )
            passwd = h.hexdigest()

            try:
                user_Dbpassw = usuarios.objects.get(ident=user).passwd
            except Exception as e:
                return HttpResponse("Usuario incorrecto.")

            if user_Dbpassw != passwd:
                return HttpResponse("Usuario incorrecto o contraseña incorrecta.")
                
            # userres = usuarios.objects.filter(ident=user).exists()
            # if userres == False:
            #     return HttpResponse("Usuario no valido.")

            #print('User: ' + user + '\t'+ 'disp: ' + disp + '\t'+ 'gfh: ' + gfh + '\t'+ 'hosp: ' + hospital )

            gfh_id, disp_id, user_id, hospital_id = funciones.GetDatos( disp, user)
            datos = excel.objects.filter( disp=disp_id, hosp_id=hospital_id).order_by('modulo','estanteria','ubicacion')
            #print('Type: '+ str(type(datos)))
            #print('Datos: ', str( datos ))
            if (datos[0].dc == "0" or datos[0].dc == "1"):
                return render( request, 'pedidos.html',{'mensaje': 'No se puede pedir DC por este medio, Consulte con empresa de gestion.'})
            
            for i in datos:
                tmp = i.nombre
                i.nombre.nombre = tmp.nombre[0:26]

            return render( request, 'pedidos.html',{  'gfh': gfh, 'disp': disp, 'datos': datos, 'passwd': passwd })


        #if request.method == 'POST':
            #print(str(codes.keys()) + '\t' + str(codes.values()))
        print('Paso por 3º')
        print('USER: ', user)
        funciones.Insert_temp( codes, hospital, disp , user )

        return render( request, 'pedido2.html',{ 'hospital': hospital,'userPed': user, 'gfh': gfh, 'disp': disp }) 

    else:
        print('Paso por 4º')
        return render( request, 'pedidos.html') #, {'hospitales': hospi })

def getPedido( request ):  #Nueva implantacion por ajax de la funcion pedido AUN NO FUNCIONA

    # clavesDescartar = ['csrfmiddlewaretoken', 'hospital', 'gfh', 'disp', 'pboton', 'tped', 'user', 'passwd']
    #     claves = request.POST.keys()
    #     for i in claves:
    #         if i in clavesDescartar:
    #             pass
    #         else:
    #             lista.append(i)

    #     #print('lista: '+ str(lista))  #Comentar de nuevo

    #     for i in lista:
    #         if int(request.POST[i]) > 0:
    #             codes[i] = request.POST[i] 
        res = None
        txtJson = None
        bloque = "["
        
        if request.method == 'GET':  #request.POST['gfh'] and request.POST['disp'] and request.POST['user'] and request.POST['passwd']:  #request.POST['hospital'] and 
            print('Paso por 2º')
            hospital =  request.session['hospitalCodigo'] #request.POST['hospital']
            gfh = request.GET['gfh']
            disp = request.GET['disp']
            user = request.GET['user']
            passw = request.GET['passwd']

            h = blake2b(digest_size=25)
            h.update( passw.encode() )
            passwd = h.hexdigest()
            user_Dbpassw = usuarios.objects.get(ident=user).passwd

            if user_Dbpassw != passwd:
                bloque += '{"error": %i}'#( -2 )
                res = bloque + ']'
                print('JSON: ', res)
                j = json.loads(res)
                txtJson = json.dumps(j)
                return HttpResponse( txtJson ) # Usuario no valido
                

            gfh_id, disp_id, user_id, hospital_id = funciones.GetDatos( disp, user)
            datos = excel.objects.filter( disp=disp_id, hosp_id=hospital_id).order_by('modulo','estanteria','ubicacion')
            #print('Type: '+ str(type(datos)))
            #print('Datos: ', str( datos ))
            
            for i in datos:
                tmp = i.nombre
                i.nombre.nombre = tmp.nombre[0:15]
                # bloque += '{"albaran": "%s","fecha": "%s", "hospital": "%s"},' %( i.pedido,

            return render( request, 'pedidos.html',{  'gfh': gfh, 'disp': disp, 'user': user, 'datos': datos, 'passwd': passwd })


        #if request.method == 'POST':
            #print(str(codes.keys()) + '\t' + str(codes.values()))
        print('Paso por 3º')
        funciones.Insert_temp( codes, hospital, disp , user )

        return render( request, 'pedido2.html',{ 'hospital': hospital, 'gfh': gfh, 'disp': disp, 'user': user }) 

    # else:
    #     print('Paso por 4º')
    #     return render( request, 'pedidos.html') #, {'hospitales': hospi })


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
        csv += '|' + ubic + '*' + codigo + '*' + nombre + '*' + pacto + '*' + gfh.gfh + '*' + disp.nombre + '*' + hosp.codigo     #str(i.id)
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
    print('Lista: ', mtx)
    listaM = []
    hospital = ''
    for i in mtx:         #va a hacer falta el codigo ubicacion dispositivo gfh hospital
        try:
            listaT = []
            listaT.append(i['ubicacion'])
            listaT.append(i['codigo'])
            articulo = articulos.objects.get(codigo=i['codigo'] , hospital_id=hospitales.objects.get(codigo=i['hospital']).id )
            listaT.insert( 2 , articulo.nombre )
            listaT.append(i['pacto'])
            listaT.append(i['gfh'])
            listaT.append(i['dispositivo'])
            listaT.append(i['hospital'])
            listaM.append(listaT)
            hospital = i['hospital']
            listaT = []
            #print('PASOOO.')
        except Exception as e:
            print('Exception ', str(e))

    #print('ListaM: ' + str(listaM))
    try:
        npedido = funciones.GenNumPedido()
        funciones.InsertarPedido_dc(listaM,npedido)
        funciones.InsertarAlbaranPedido_dc( npedido, hospital )
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
    #print('mtx: ', str(mtx))
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

def addLineaEtiqueta( request ):

    hospital = hospitales.objects.all()
    if request.method == 'POST':
        pass


    return render(request, 'addetiqueta.html',{'hospitales': hospital})

def getLineas(request): 
    lista = []
    mtx = []
    txtJson = None
    bloque = "["
    txtJson = None
    if request.method == 'GET':
        ubicacion = request.GET.get('ubicacion', False)
        codigo = request.GET.get('codigo', False)
        nombre = request.GET.get('nombre', False)
        pacto = float(request.GET.get('pacto', False))
        dc = request.GET.get('dc', False)
        gfh = request.GET.get('gfh', False)
        disp = request.GET.get('disp', False)
        hospital = request.GET.get('hospital', False)

        #bloque = """{"mensaje": ""  """
        #f_json = Json(bloque)
        try:
            res = addRefPedido(ubicacion=ubicacion,codigo=codigo,nombre=nombre,pacto=pacto,dc=dc,gfh=gfh,disp=disp,hospital=hospital)
            res.save()
            mtx.append('Linea insertada correctamente.')
            lista.append(mtx)
            #print('Resultado OK: ', str(txtJson))
            
        except Exception as e:
            mtx.append('Hubo un error al insertar datos. ' + str(e) )
            lista.append(mtx)
            print('Error: ', str(e))
            #print('Resultado KO: ', str(txtJson))

        finally:    
            #txtJson = f_json.crearJson(lista)
            bloque += '{"mensaje": "%s"  ' %( lista[0] )
            res = bloque[ :-1] + "]"
            j = json.loads(res)
            txtJson = json.dumps(j)
            
        return HttpResponse(txtJson)    

    return HttpResponse('null')

def getPedTemp( request ):
    txtJson = None
    bloque = "["
    #bloque = """{"hospital": "","gfh": "","disp": "","codigo": "","nombre": "","cantidad": ""  """

    if request.method == 'GET':
        hosp = request.session['hospitalCodigo']
        user = request.GET['user']
        hospi = hospitales.objects.get(codigo=hosp)
        usuario = usuarios.objects.get(ident=user)
        res = pedidos_temp.objects.filter(hospital=hospi.id,user_temp=usuario.id).select_related().order_by('gfh','disp')
        print('USER: ',usuario.id)
        print('HOSP: ',hospi.id)
        for i in res:
            bloque += '{"hospital": "%s","gfh": "%s","disp": "%s","codigo": "%s","nombre": "%s","cantidad": "%s"},' %( i.hospital.codigo, i.gfh.gfh, i.disp.nombre, i.codigo.codigo, i.codigo.nombre, i.cantidad )
        res = bloque[ :-1] + "]"
        j = json.loads(res)
        txtJson = json.dumps(j)

        return HttpResponse(txtJson)

def gestPedidos( request ):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    else:
        request.session.set_expiry (request.session['tiempo'])
        print('TIEMPO SESION: ', str(request.session.get_expiry_age()))

    hospi = hospitales.objects.all()

    if request.method == 'POST':
        pass
        # formGest = formGpedidos(request.POST)
        # if formGest.is_valid():
        #     info = formGest.cleaned_data
        #     albaran = info['albaran']
        #     usuario = info['usuario']
        #     fecha = info['fecha']
            
        #     Thospital = None; Tusuarios = None; Tgfhs = None; Tarticulos = None; Tusuarios = None

        #     if usuario:
        #         Tusuarios = usuarios.objects.get(ident=usuario)
            
        #     pedidoFilas = pedidos.objects.filter(npedido=albaran).select_related()
        #     pedidoIdent = pedidos_ident.objects.filter(pedido=albaran)
            
        #     print(str(info))
        #     print('Cuantos: ', len(pedidoFilas))
            
        #     return render( request, 'gestPedidos.html',{'datos': pedidoFilas, 'npedido': pedidoIdent})
    else:

        formGest = formGpedidos()

    return render( request, 'gestPedidos.html', {'formulario': formGest, 'hospitales': hospi})

def getAlbaranes( request ):
    txtJson = None
    bloque = "["
    if request.method == 'GET':
        cal_ini = request.GET['cal_ini']
        cal_fin = request.GET['cal_fin']

        #bloque = """{"albaran": "","fecha": ""  """
        res = pedidos_ident.objects.filter(fecha__range=[ cal_ini, cal_fin])
        for i in res:
            bloque += '{"albaran": "%s","fecha": "%s"},' %( i.pedido, i.fecha.strftime("%d/%m/%Y %H:%M:%S") )
        res = bloque[ :-1] + "]"
        j = json.loads(res)
        txtJson = json.dumps(j)
        
        return HttpResponse(txtJson)

def getAlbaranesdc( request ):
    res = None
    txtJson = None
    bloque = "["
    if request.method == 'GET':
        cal_ini = request.GET['cal_ini']
        cal_fin = request.GET['cal_fin']
        hospital = request.session['hospitalCodigo'] #request.GET['hospital']
        #print('Hospital: ', hospital)
        res = pedidos_ident_dc.objects.filter(fecha__range=[ cal_ini, cal_fin],hospital=hospitales.objects.get(codigo=hospital))
        
        if len(res) > 0:
            for i in res:
                bloque += '{"albaran": "%s","fecha": "%s", "hospital": "%s"},' %( i.pedido, i.fecha.strftime("%d/%m/%Y %H:%M:%S"), i.hospital.nombre)
                #print('Fecha: ', str(i.fecha.strftime("%d/%m/%Y %H:%M:%S")), ' Tipo: ', type(i.fecha.strftime("%d/%m/%Y %H:%M:%S")))
            res = bloque[ :-1] + "]"
            #print('JSON: ', res)
            j = json.loads(res)
            txtJson = json.dumps(j)
        else:
            txtJson = "-1"
        
        return HttpResponse(txtJson)

def gpedidos( request ):

    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    else:
        request.session.set_expiry (request.session['tiempo'])
        print('TIEMPO SESION: ', str(request.session.get_expiry_age()))
    
    albaran = ''
    if request.method == 'GET':
        albaran = request.GET['albaran']
        print('Res: ', albaran)
        pedidoFilas = pedidos.objects.filter(npedido=albaran).select_related()
        pedidoIdent = pedidos_ident.objects.filter(pedido=albaran)

        return render( request, 'gpedidos.html',{'datos': pedidoFilas, 'npedido': pedidoIdent})

    return HttpResponse(None)

def gpedidosdc( request ):

    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    else:
        request.session.set_expiry (request.session['tiempo'])
        print('TIEMPO SESION: ', str(request.session.get_expiry_age()))

    albaran = ''
    if request.method == 'GET':
        albaran = request.GET['albaran']
        print('Res: ', albaran)
        pedidoFilas = pedidos_dc.objects.filter(npedido=albaran).select_related().order_by('gfh')
        pedidoIdent = pedidos_ident_dc.objects.filter(pedido=albaran)

        return render( request, 'gpedidosdc.html',{'datos': pedidoFilas, 'npedido': pedidoIdent})

    return HttpResponse(None)

def impresion( request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    else:
        request.session.set_expiry (request.session['tiempo'])
        print('TIEMPO SESION: ', str(request.session.get_expiry_age()))

    filas = addRefPedido.objects.all()
    nfilas = None
    if request.method == 'POST':
        if 'remove' in request.POST:
            pass
            nfilas = addRefPedido.objects.all().delete()[0]

        if 'upload' in request.POST:
            excel = Excell( 'data-xlsx' )
            ret = ['ubicacion','codigo','nombre','pacto','gfh']
            excel.insertar_rangofila( ret , 1 , 1 )
            excel.salvarexcell2()
            lista = []
            ultimaFila = 2
            for i in filas:
                lista.append(i.ubicacion)
                lista.append(i.codigo)
                lista.append(i.nombre)
                lista.append(i.pacto)
                lista.append(i.gfh)
                excel.insertar_rangofila( lista , ultimaFila , 1 )
                lista.clear()
                ultimaFila += 1
            excel.salvarexcell2()

            import os
            fila = MEDIA_ROOT +'/data-xlsx.xlsx' 
            with open( fila , 'rb') as fh:
                #print('ENTRO')
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename( fila )
                return response
            
    return render(request,'impresion.html',{ 'filas': filas, 'nfilas': nfilas })

def gestPedidosDC(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    else:
        request.session.set_expiry (request.session['tiempo'])
        print('TIEMPO SESION: ', str(request.session.get_expiry_age()))

    #hospi = hospitales.objects.all()

    return render(request,'gestPedidosdc.html')

def addLineaPedidoDc( request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    else:
        request.session.set_expiry (request.session['tiempo'])
        print('TIEMPO SESION: ', str(request.session.get_expiry_age()))

    hospital = ''
    fecha = ''
    txtJson = None
    bloque = "["
    # if request.method == 'POST':
    #     print('POST')
    #     if request.POST.get('fecha', False):
    #         fecha = request.POST['fecha']
    #         print("Fecha: ", fecha)
    #         return render(request, 'addLineaPedidoDc.html')

    #else:
    if request.method == 'GET' and request.GET.get('cal_ini', False):
        hospital = request.GET['hospital']
        fecha = request.GET['cal_ini']
        print(fecha)
        print(hospital)
        hosp = hospitales.objects.get(codigo=hospital).pk
        res = pedidos_ident_dc.objects.filter(fecha__range=[fecha, datetime.datetime.now()],hospital=hosp).select_related()
        
        print('RES: ', res)
        for i in res:
            bloque += '{"albaran": "%s","fecha": "%s", "hospital": "%s"},' %( i.pedido, i.fecha.strftime("%d/%m/%Y %H:%M:%S"),i.hospital.codigo )
        if len(res) == 0:    
            res = bloque[ : ] + "]"
        else:
            res = bloque[ :-1 ] + "]"
        print( 'REX: ' ,res )
        j = json.loads(res)
        txtJson = json.dumps(j)
        
        return HttpResponse(txtJson)

            
    return render(request, 'addLineaPedidoDc.html')




class PedidosViewSet(viewsets.ModelViewSet):
    #permissions_classes = (permissions.IsAuthenticated,)
    serializer_class = ret_pedidos
    
    def retPedido():
        res = pedidos.objects.all().order_by('npedido')
        print('Ret: ', str(res))
        return res



    


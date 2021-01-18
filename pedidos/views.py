from django.shortcuts import render
from django.http import HttpResponse
import os, random
from configuraciones.models import articulos, configurations , hospitales, gfhs , dispositivos, excel
import datetime
from pedidos.models import pedidos, pedidos_ident, pedidos_temp, usuarios, pedidos_dc, pedidos_ident_dc, addRefPedido #addLineaPedido
from django.db import connection
from configuraciones.excell import Excell
from configuraciones.views import getIdDB
from HtmlHack.settings import MEDIA_ROOT
from HtmlHack.settings import STATIC_ROOT
from django.db import connection
import json
from configuraciones.func import funcConf, Json
from hashlib import blake2b
from pedidos.forms import formGpedidos
#__________________________________________________________
from pedidos.func import funciones
from django.db import transaction
global hospital, disp, user, gfh


@transaction.atomic
def pedido( request ):
    global gfh, hospital, disp, user, passwd, user_pk
    lista=[] ; codes={}
    hospi = hospitales.objects.all()

    if request.method == 'POST':
        
        
        if request.POST.get('usuario', False):         #request.POST.get('is_private', False)
            print('Paso por 1º')
            datos = None
            filas = None
            npedido = None
            user_temp = request.POST['usuario']  #usuarios.objects.get(ident=user).pk
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
                pedi = pedidos_temp.objects.filter(disp_id=i[0], user_temp_id=user_pk).select_related('gfh','disp','codigo','user_temp')

                funciones.InsertarPedido(pedi, npedido)
                #print('---------------------------------')
            funciones.InsertarAlbaranPedido(user_pk, npedido )
            deltem = pedidos_temp.objects.filter(user_temp_id=user_pk).delete()
            print('Fichero Excel2: ', filexcel)
            #Activar en produccion
            #funciones.envcorreogmail( fileadjunto=filexcel +'.xlsx', subject='Pedido material.',\
                    #mensaje=r'Buenos dias adjunto fichero con material a pedir.\nUn saludo',)

            return render( request, 'pedidos.html', { 'hospitales': hospi })

        
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

        
        if request.POST['hospital'] and request.POST['gfh'] and request.POST['disp'] and request.POST['user'] and request.POST['passwd']:
            print('Paso por 2º')
            hospital = request.POST['hospital']
            gfh = request.POST['gfh']
            disp = request.POST['disp']
            user = request.POST['user']
            passw = request.POST['passwd']

            h = blake2b(digest_size=25)
            h.update( passw.encode() )
            passwd = h.hexdigest()

            user_Dbpassw = usuarios.objects.get(ident=user).passwd


            if user_Dbpassw != passwd:
                return HttpResponse("Usuario no valido.")
                
            # userres = usuarios.objects.filter(ident=user).exists()
            # if userres == False:
            #     return HttpResponse("Usuario no valido.")

            #print('User: ' + user + '\t'+ 'disp: ' + disp + '\t'+ 'gfh: ' + gfh + '\t'+ 'hosp: ' + hospital )

            gfh_id, disp_id, user_id, hospital_id = funciones.GetDatos( disp, user)
            datos = excel.objects.filter( disp=disp_id, hosp_id=hospital_id).order_by('modulo','estanteria','ubicacion')
            #print('Type: '+ str(type(datos)))
            #print('Datos: ', str( datos ))
            
            for i in datos:
                tmp = i.nombre
                i.nombre.nombre = tmp.nombre[0:15]

            return render( request, 'pedidos.html',{ 'hospital': hospital, 'gfh': gfh, 'disp': disp, 'user': user, 'datos': datos, 'passwd': passwd })


        #if request.method == 'POST':
            #print(str(codes.keys()) + '\t' + str(codes.values()))
        print('Paso por 3º')
        funciones.Insert_temp( codes, hospital, disp , user )

        return render( request, 'pedido2.html',{ 'hospital': hospital, 'gfh': gfh, 'disp': disp, 'user': user }) 

    else:
        print('Paso por 4º')
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
            articulo = articulos.objects.get(codigo=listaT[1] , hospital_id=hospitales.objects.get(codigo=i['hospital']).id )
            listaT.insert( 2 , articulo.nombre )
            listaT.append(i['pacto'])
            listaT.append(i['gfh'])
            listaT.append(i['dispositivo'])
            listaT.append(i['hospital'])
            listaM.append(listaT)
            hospital = i['hospital']
            listaT = []
            print('PASOOO.')
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
    if request.method == 'GET':
        ubicacion = request.GET.get('ubicacion', False)
        codigo = request.GET.get('codigo', False)
        nombre = request.GET.get('nombre', False)
        pacto = float(request.GET.get('pacto', False))
        dc = request.GET.get('dc', False)
        gfh = request.GET.get('gfh', False)
        disp = request.GET.get('disp', False)
        hospital = request.GET.get('hospital', False)

        bloque = """{"mensaje": ""  """
        f_json = Json(bloque)
        try:
            res = addRefPedido(ubicacion=ubicacion,codigo=codigo,nombre=nombre,pacto=pacto,dc=dc,gfh=gfh,disp=disp,hospital=hospital)
            res.save()
            mtx.append('Linea insertada correctamente.')
            lista.append(mtx)
            print('Resultado OK: ', str(txtJson))
            
        except Exception as e:
            mtx.append('Hubo un error al insertar datos. ' + str(e) )
            lista.append(mtx)
            print('Error: ', str(e))
            print('Resultado KO: ', str(txtJson))

        finally:    
            txtJson = f_json.crearJson(lista)
            
        return HttpResponse(txtJson)    

    return HttpResponse('null')
            
# def imprimirGfh( request):  #borrar .....
#     gfh = 'expgfh/'
#     if request.method == 'POST':
#         if request.POST['tbenlace']:
#             gfh += request.POST['tbenlace']
#     print('LINK: ', gfh)
#     return render( request, 'imprimirGfh.html', {'gfh': gfh})

def getPedTemp( request ):
    lista = []
    mtx = []
    bloque = """{"hospital": "","gfh": "","disp": "","codigo": "","nombre": "","cantidad": ""  """

    if request.method == 'GET':
        hosp = request.GET['hospital']
        #gfh = request.GET['gfh']
        #disp = request.GET['dispositivo']
        user = request.GET['user']

        hospi = hospitales.objects.get(codigo=hosp)
        #gfh = gfhs.objects.get(gfh=gfh,nombre=disp,hp_id=hospital.pk)
        #dispo = dispositivos.objects.get(nombre=disp,gfh=gfh.pk)
        usuario = usuarios.objects.get(ident=user)

        res = pedidos_temp.objects.filter(hospital=hospi.id,user_temp=usuario.id).select_related()
        #print('Resultado: ', str(res))
        f_json = Json(bloque)
        for i in res:
            mtx.append(i.hospital.codigo)
            mtx.append(i.gfh.gfh)
            mtx.append(i.disp.nombre)
            mtx.append(i.codigo.codigo)
            mtx.append(i.codigo.nombre)
            mtx.append(i.cantidad)
            lista.append(mtx)
            print(i.hospital.codigo)
            print(i.gfh.gfh)
            print(i.disp.nombre)
            print(i.codigo.nombre)
            print(i.codigo.codigo)

            mtx = []
        #print('LISTA: ', str(lista))
        txtJson = f_json.crearJson(lista)


        return HttpResponse(txtJson)

def gestPedidos( request ):
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
    lista = []
    mtx = []
    if request.method == 'GET':
        cal_ini = request.GET['cal_ini']
        cal_fin = request.GET['cal_fin']

        bloque = """{"albaran": "","fecha": ""  """
        res = pedidos_ident.objects.filter(fecha__range=[ cal_ini, cal_fin])
        #print('QueriSet: ', str(res))
        f_json = Json(bloque)
        for i in res:
            mtx.append(i.pedido)
            mtx.append(str(i.fecha.date()))
            #print('typo: ',type(i.fecha))
            lista.append(mtx)
            mtx = []

        txtJson = f_json.crearJson(lista)
        print('Resultado: ', str(txtJson))
        return HttpResponse(txtJson)

def getAlbaranesdc( request ):
    lista = []
    mtx = []
    if request.method == 'GET':
        cal_ini = request.GET['cal_ini']
        cal_fin = request.GET['cal_fin']
        hospital = request.GET['hospital']

        bloque = """{"albaran": "","fecha": "","hospital": ""  """
        res = pedidos_ident_dc.objects.filter(fecha__range=[ cal_ini, cal_fin],hospital=hospitales.objects.get(codigo=hospital))
        #print('QueriSet: ', str(res))
        f_json = Json(bloque)
        for i in res:
            mtx.append(i.pedido)
            mtx.append(str(i.fecha.date()))
            mtx.append(hospital)
            #print('typo: ',type(i.fecha))
            lista.append(mtx)
            mtx = []

        txtJson = f_json.crearJson(lista)
        print('ResultadoDC: ', str(txtJson))
        return HttpResponse(txtJson)

def gpedidos( request ):
    albaran = ''
    if request.method == 'GET':
        albaran = request.GET['albaran']
        print('Res: ', albaran)
        pedidoFilas = pedidos.objects.filter(npedido=albaran).select_related()
        pedidoIdent = pedidos_ident.objects.filter(pedido=albaran)

        return render( request, 'gpedidos.html',{'datos': pedidoFilas, 'npedido': pedidoIdent})

    return HttpResponse(None)

def gpedidosdc( request ):
    albaran = ''
    if request.method == 'GET':
        albaran = request.GET['albaran']
        print('Res: ', albaran)
        pedidoFilas = pedidos_dc.objects.filter(npedido=albaran).select_related()
        pedidoIdent = pedidos_ident_dc.objects.filter(pedido=albaran)

        return render( request, 'gpedidosdc.html',{'datos': pedidoFilas, 'npedido': pedidoIdent})

    return HttpResponse(None)

def impresion( request):

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
    hospi = hospitales.objects.all()

    return render(request,'gestPedidosdc.html', {'hospitales': hospi})


